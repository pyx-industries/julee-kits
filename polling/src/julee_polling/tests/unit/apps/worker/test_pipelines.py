"""
Integration tests for polling worker pipelines.

These run NewDataDetectionPipeline through Temporal's time-skipping test
environment: the poll_endpoint activity is a stand-in, and the workflow
orchestration around it is real.

NewDataDetectionPipeline is abstract - a solution subclasses it to supply
a handler and an calculator - so the tests run a subclass of their own,
whose handler records what it is given.

Every workflow is started with an execution timeout. A workflow that
raises anything other than a Temporal failure does not fail: Temporal
retries the workflow task for ever, and a test awaiting its result never
returns. With the timeout, that mistake is a failing test.
"""

import hashlib
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest
from julee.core.entities.acknowledgement import Acknowledgement
from pydantic import TypeAdapter
from temporalio import activity, workflow
from temporalio.client import WorkflowFailureError, WorkflowHandle
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from julee_polling.apps.worker.completion import PipelineCompletion
from julee_polling.apps.worker.pipelines import NewDataDetectionPipeline
from julee_polling.domain.values.handoff import Handoff
from julee_polling.domain.values.polling_config import (
    HttpConnection,
    PollingConfig,
    PollingProtocol,
    PollingResult,
)

# Each test starts a Temporal test server, so these are not unit tests.
pytestmark = pytest.mark.integration

TASK_QUEUE = "test-queue"
EXECUTION_TIMEOUT = timedelta(seconds=30)

FIRST_CONTENT = b"first response data"
CHANGED_CONTENT = b"changed response data"


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class RecordingHandler:
    """A PollingResultHandler that remembers what it was handed."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def handle_new_data(
        self,
        endpoint_id: str,
        new_item_ids: list[str],
        content_hash: str,
    ) -> Acknowledgement:
        self.calls.append(
            {
                "endpoint_id": endpoint_id,
                "new_item_ids": new_item_ids,
                "content_hash": content_hash,
            }
        )
        return Acknowledgement.wilco(info=[f"queued {len(new_item_ids)}"])


class FailingHandler:
    """A PollingResultHandler that cannot cope."""

    async def handle_new_data(
        self,
        endpoint_id: str,
        new_item_ids: list[str],
        content_hash: str,
    ) -> Acknowledgement:
        raise RuntimeError("Handler failed")


class WholePayloadCalculator:
    """A NewDataCalculator that treats each payload as a single item."""

    async def identify_new_items(
        self,
        previous_data: bytes | None,
        new_data: bytes,
    ) -> list[str]:
        return [new_data.decode()]


@workflow.defn
class RecordingPipeline(NewDataDetectionPipeline):
    """The pipeline as a solution would subclass it, with a query to see
    what reached the handler."""

    def __init__(self) -> None:
        super().__init__()
        self._handler = RecordingHandler()

    def get_handler(self) -> RecordingHandler:
        return self._handler

    def get_calculator(self) -> WholePayloadCalculator:
        return WholePayloadCalculator()

    @workflow.run
    async def run(self, config: PollingConfig | dict[str, Any]) -> PipelineCompletion:
        return await super().run(config)

    @workflow.query
    def get_handled(self) -> list[dict[str, Any]]:
        return self._handler.calls


@workflow.defn
class FailingHandlerPipeline(NewDataDetectionPipeline):
    """The pipeline with a handler that raises."""

    def get_handler(self) -> FailingHandler:
        return FailingHandler()

    def get_calculator(self) -> WholePayloadCalculator:
        return WholePayloadCalculator()

    @workflow.run
    async def run(self, config: PollingConfig | dict[str, Any]) -> PipelineCompletion:
        return await super().run(config)


def poll_endpoint_returning(*contents: bytes) -> Any:
    """A poll_endpoint activity that returns each content in turn, then
    goes on returning the last."""
    remaining = list(contents)

    @activity.defn(name="julee_polling.poll_endpoint")
    async def poll_endpoint(config: PollingConfig) -> PollingResult:
        content = remaining.pop(0) if len(remaining) > 1 else remaining[0]
        return PollingResult(
            success=True,
            content=content,
            polled_at=datetime.now(UTC),
            content_hash=content_hash(content),
        )

    return poll_endpoint


def poll_endpoint_failing() -> Any:
    """A poll_endpoint activity for an endpoint that could not be reached.

    The adapter returns a PollingResult rather than raising: an
    unreachable endpoint is an answer about the endpoint, not a fault
    in the polling.
    """

    @activity.defn(name="julee_polling.poll_endpoint")
    async def poll_endpoint(config: PollingConfig) -> PollingResult:
        return PollingResult(
            success=False,
            content=b"",
            polled_at=datetime.now(UTC),
            error_message="connection refused",
        )

    return poll_endpoint


def completion_for(content: bytes) -> dict[str, Any]:
    """What an earlier run that polled this content would have returned."""
    return {
        "polling_result": {
            "content_hash": content_hash(content),
            "content": content.decode(),
            "polled_at": "2023-01-01T00:00:00+00:00",
        },
        "detection_result": {
            "has_new_data": True,
            "current_hash": content_hash(content),
        },
        "endpoint_id": "test-api",
        "completed_at": "2023-01-01T00:00:00+00:00",
    }


def last_completion(completion: dict[str, Any] | None) -> Any:
    """Have the workflow see this as the schedule's last completion result."""
    return patch(
        "temporalio.workflow.get_last_completion_result",
        return_value=completion,
    )


async def start_pipeline(
    env: WorkflowEnvironment,
    config: PollingConfig,
    pipeline: type[NewDataDetectionPipeline] = RecordingPipeline,
) -> WorkflowHandle[Any, PipelineCompletion]:
    return await env.client.start_workflow(
        pipeline.run,
        config,
        id=str(uuid.uuid4()),
        task_queue=TASK_QUEUE,
        execution_timeout=EXECUTION_TIMEOUT,
    )


async def run_pipeline(
    env: WorkflowEnvironment,
    config: PollingConfig,
    previous_completion: dict[str, Any] | None = None,
) -> tuple[PipelineCompletion, list[dict[str, Any]]]:
    """Run RecordingPipeline as the run after previous_completion, and
    return its result with what reached the handler.

    The handler is asked about while the last completion result is still
    patched. A query on a finished workflow replays it, and a replay that
    saw a different last completion would take a different path.
    """
    with last_completion(previous_completion):
        handle = await start_pipeline(env, config)
        result = await handle.result()
        handled = await handle.query(RecordingPipeline.get_handled)
    return result, handled


@pytest.fixture
async def workflow_env():
    """Provide a Temporal test environment with time skipping."""
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        yield env


@pytest.fixture
def sample_config():
    """Provide a sample PollingConfig for testing."""
    return PollingConfig(
        endpoint_identifier="test-api",
        polling_protocol=PollingProtocol.HTTP,
        connection_params=HttpConnection(url="https://api.example.com/data"),
        timeout_seconds=30,
    )


def worker(env: WorkflowEnvironment, poll_endpoint: Any) -> Worker:
    return Worker(
        env.client,
        task_queue=TASK_QUEUE,
        workflows=[RecordingPipeline, FailingHandlerPipeline],
        activities=[poll_endpoint],
    )


class TestNewDataDetectionPipelineFirstRun:
    """Test first run scenarios (no previous completion)."""

    async def test_first_run_detects_new_data(self, workflow_env, sample_config):
        """With nothing to compare against, whatever is polled is new."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            result, _ = await run_pipeline(workflow_env, sample_config)

        assert result.detection_result.has_new_data is True
        assert result.detection_result.current_hash == content_hash(FIRST_CONTENT)
        assert result.endpoint_id == "test-api"

    async def test_completion_carries_what_the_next_run_compares(
        self, workflow_env, sample_config
    ):
        """The result is the next run's last completion result, so it holds
        the content and its hash."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            result, _ = await run_pipeline(workflow_env, sample_config)

        polling_result = result.polling_result
        assert polling_result.content_hash == content_hash(FIRST_CONTENT)
        assert polling_result.content == FIRST_CONTENT.decode()
        assert polling_result.polled_at
        assert result.completed_at

    async def test_first_run_hands_new_items_to_handler(
        self, workflow_env, sample_config
    ):
        """The handler gets the calculator's item IDs, not the raw bytes."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            _, handled = await run_pipeline(workflow_env, sample_config)

        assert handled == [
            {
                "endpoint_id": "test-api",
                "new_item_ids": [FIRST_CONTENT.decode()],
                "content_hash": content_hash(FIRST_CONTENT),
            }
        ]

    async def test_config_may_arrive_as_dict(self, workflow_env, sample_config):
        """A Temporal schedule serialises its args, so config comes as a dict."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            with last_completion(None):
                result = await workflow_env.client.execute_workflow(
                    RecordingPipeline.run,
                    TypeAdapter(PollingConfig).dump_python(sample_config, mode="json"),
                    id=str(uuid.uuid4()),
                    task_queue=TASK_QUEUE,
                    execution_timeout=EXECUTION_TIMEOUT,
                )

        assert result.endpoint_id == "test-api"


class TestNewDataDetectionPipelineSubsequentRuns:
    """Test subsequent runs with previous completion data."""

    async def test_no_changes_detected(self, workflow_env, sample_config):
        """The same content as last time is not new, and the handler is
        left alone."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            result, handled = await run_pipeline(
                workflow_env, sample_config, completion_for(FIRST_CONTENT)
            )

        assert result.detection_result.has_new_data is False
        assert handled == []

    async def test_changes_detected(self, workflow_env, sample_config):
        """Different content from last time is new, and goes to the handler."""
        async with worker(workflow_env, poll_endpoint_returning(CHANGED_CONTENT)):
            result, handled = await run_pipeline(
                workflow_env, sample_config, completion_for(FIRST_CONTENT)
            )

        assert result.detection_result.has_new_data is True
        assert result.detection_result.current_hash == content_hash(CHANGED_CONTENT)
        assert [call["new_item_ids"] for call in handled] == [
            [CHANGED_CONTENT.decode()]
        ]

    async def test_a_completion_it_cannot_read_is_said_to_be_no_baseline(
        self, workflow_env, sample_config, caplog
    ):
        """The warning is the point, not the starting over.

        This is the shape a completion written by a version that named
        the baseline differently would have. Read with .get() it came
        back as None and the run reported new data -- which is what
        happens here too, so the only thing telling the two apart is
        that this one says so. Starting over costs one duplicate
        notification; the silent reading cost it on every run.
        """
        stored = completion_for(FIRST_CONTENT)
        stored["polling_result"]["hash"] = stored["polling_result"].pop("content_hash")

        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            with caplog.at_level(logging.WARNING):
                result, handled = await run_pipeline(
                    workflow_env, sample_config, stored
                )

        assert [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
        assert any(
            "no baseline" in r.getMessage()
            for r in caplog.records
            if r.levelno >= logging.WARNING
        )
        assert result.detection_result.has_new_data is True
        assert handled != []


class TestNewDataDetectionPipelineWorkflowQueries:
    """Test workflow query methods."""

    async def test_workflow_queries(self, workflow_env, sample_config):
        """The queries report where the workflow got to and what it found."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            with last_completion(None):
                handle = await start_pipeline(workflow_env, sample_config)
                await handle.result()

                step = await handle.query(NewDataDetectionPipeline.get_current_step)
                endpoint_id = await handle.query(
                    NewDataDetectionPipeline.get_endpoint_id
                )
                has_new_data = await handle.query(
                    NewDataDetectionPipeline.get_has_new_data
                )

        assert step == "completed"
        assert endpoint_id == "test-api"
        assert has_new_data is True


class TestNewDataDetectionPipelineErrorHandling:
    """Test error handling and failure scenarios."""

    async def test_polling_activity_failure(self, workflow_env, sample_config):
        """When polling keeps failing, the workflow fails."""

        @activity.defn(name="julee_polling.poll_endpoint")
        async def failing_poll_endpoint(config: PollingConfig) -> PollingResult:
            raise RuntimeError("Polling failed")

        async with worker(workflow_env, failing_poll_endpoint):
            with last_completion(None):
                handle = await start_pipeline(workflow_env, sample_config)
                with pytest.raises(WorkflowFailureError):
                    await handle.result()

    async def test_handler_failure_does_not_fail_workflow(
        self, workflow_env, sample_config
    ):
        """A handler that raises does not fail the run, and does not
        advance the baseline either.

        Nobody was told, so the obligation stands. Recording the new
        hash would say it had been discharged, and the next run would
        see no change and never try again.
        """
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            with last_completion(None):
                handle = await start_pipeline(
                    workflow_env, sample_config, FailingHandlerPipeline
                )
                result = await handle.result()

        assert result.detection_result.has_new_data is True
        assert result.detection_result.handoff == Handoff.FAILED.value
        assert result.polling_result.content_hash is None

    async def test_a_failed_handoff_is_written_down(
        self, workflow_env, sample_config, caplog
    ):
        """The use case reports and does not log, so this is the only
        place a failed handoff is recorded.

        Pinned because it was lost once already: the use case's
        logger.error went when the acknowledgement started being read,
        and nothing replaced it, because nothing was asserting it.
        """
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            with last_completion(None), caplog.at_level(logging.ERROR):
                handle = await start_pipeline(
                    workflow_env, sample_config, FailingHandlerPipeline
                )
                await handle.result()

        errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert errors, "a failed handoff was not written down anywhere"
        assert any(
            "Handler failed" in str(r.__dict__.get("handoff_info", "")) for r in errors
        ), (
            f"the reason was not carried: {[r.__dict__.get('handoff_info') for r in errors]}"
        )

    async def test_a_failed_handoff_is_tried_again_next_run(
        self, workflow_env, sample_config
    ):
        """The point of not advancing the baseline.

        A run whose handler failed leaves the content unseen, so the
        next run over the same content still finds it new and hands it
        over. Before the baseline was held back, the second run
        compared against a hash nobody had acted on and did nothing.
        """
        async with worker(
            workflow_env, poll_endpoint_returning(FIRST_CONTENT, FIRST_CONTENT)
        ):
            with last_completion(None):
                handle = await start_pipeline(
                    workflow_env, sample_config, FailingHandlerPipeline
                )
                failed = await handle.result()

            # Temporal hands the next run a dict, not the model, so that is
            # what this passes -- the round trip is the thing under test.
            second, handled = await run_pipeline(
                workflow_env, sample_config, failed.model_dump(mode="json")
            )

        assert second.detection_result.has_new_data is True
        assert [call["content_hash"] for call in handled] == [
            content_hash(FIRST_CONTENT)
        ]


class TestAPollThatFailed:
    """An endpoint that could not be reached.

    Untested until now, which is how it stayed broken: before the
    baseline was held back, a failed poll hashed b"" and the resulting
    hash differed from the last one, so the run reported new data and
    ran change detection over nothing.
    """

    async def test_a_failed_poll_is_not_new_data(self, workflow_env, sample_config):
        """Nothing was seen, so nothing is new."""
        async with worker(workflow_env, poll_endpoint_failing()):
            result, handled = await run_pipeline(
                workflow_env, sample_config, completion_for(FIRST_CONTENT)
            )

        assert result.detection_result.has_new_data is False
        assert result.detection_result.handoff == Handoff.NOT_NEEDED.value

    async def test_a_failed_poll_tells_nobody(self, workflow_env, sample_config):
        """There is nothing to tell."""
        async with worker(workflow_env, poll_endpoint_failing()):
            _, handled = await run_pipeline(
                workflow_env, sample_config, completion_for(FIRST_CONTENT)
            )

        assert handled == []

    async def test_a_failed_poll_keeps_the_previous_baseline(
        self, workflow_env, sample_config
    ):
        """A poll that saw nothing may not overwrite what was seen before.

        Recording the empty content's hash would make the next run
        compare against something no endpoint ever returned.
        """
        previous = completion_for(FIRST_CONTENT)

        async with worker(workflow_env, poll_endpoint_failing()):
            result, _ = await run_pipeline(workflow_env, sample_config, previous)

        assert result.polling_result.content_hash == content_hash(FIRST_CONTENT)

    async def test_the_content_is_handed_over_once_polling_recovers(
        self, workflow_env, sample_config
    ):
        """The point of keeping the baseline: a failed poll costs nothing."""
        async with worker(workflow_env, poll_endpoint_failing()):
            failed, _ = await run_pipeline(workflow_env, sample_config)

        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            recovered, handled = await run_pipeline(
                workflow_env, sample_config, failed.model_dump(mode="json")
            )

        assert recovered.detection_result.has_new_data is True
        assert [call["content_hash"] for call in handled] == [
            content_hash(FIRST_CONTENT)
        ]


class TestWhatTheHandoffReports:
    """What comes back when the handler was told and answered.

    Asserted because none of it was: the reporting contract was only
    ever checked on the path where the handoff failed.
    """

    async def test_a_handoff_that_happened_is_reported_as_discharged(
        self, workflow_env, sample_config
    ):
        """Wilco means they were told and will act."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            result, _ = await run_pipeline(workflow_env, sample_config)

        assert result.detection_result.handoff == Handoff.DISCHARGED.value

    async def test_what_the_handler_said_travels_back(
        self, workflow_env, sample_config
    ):
        """The acknowledgement carries the handler's only payload."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            result, _ = await run_pipeline(workflow_env, sample_config)

        assert result.detection_result.handoff_info == ("queued 1",)

    async def test_nothing_new_is_reported_as_nothing_to_do(
        self, workflow_env, sample_config
    ):
        """Unchanged content puts nobody under an obligation."""
        async with worker(workflow_env, poll_endpoint_returning(FIRST_CONTENT)):
            result, handled = await run_pipeline(
                workflow_env, sample_config, completion_for(FIRST_CONTENT)
            )

        assert result.detection_result.handoff == Handoff.NOT_NEEDED.value
        assert handled == []


class TestNewDataDetectionPipelineIntegration:
    """Test a sequence of runs, each fed the one before."""

    async def test_complete_polling_cycle(self, workflow_env, sample_config):
        """First run, then no change, then a change."""
        poll_endpoint = poll_endpoint_returning(
            FIRST_CONTENT, FIRST_CONTENT, CHANGED_CONTENT
        )

        async with worker(workflow_env, poll_endpoint):
            first, _ = await run_pipeline(workflow_env, sample_config)
            second, _ = await run_pipeline(
                workflow_env, sample_config, first.model_dump(mode="json")
            )
            third, _ = await run_pipeline(
                workflow_env, sample_config, second.model_dump(mode="json")
            )

        assert first.detection_result.has_new_data is True
        assert second.detection_result.has_new_data is False
        assert third.detection_result.has_new_data is True
