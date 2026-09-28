"""
Temporal workflows for polling operations in the Julee polling contrib module.

This module contains workflows that orchestrate polling operations with
Temporal's durability guarantees, providing retry logic, state management,
and reliable execution for endpoint polling and change detection.
"""

import logging
from abc import abstractmethod
from typing import Any

from temporalio import workflow

from julee_polling.domain.calculators.new_data import NewDataCalculator
from julee_polling.domain.handlers.polling_result_handler import (
    PollingResultHandler,
)
from julee_polling.domain.models.handoff import Handoff
from julee_polling.domain.models.polling_config import PollingConfig
from julee_polling.dtos.poll_data import PollDataRequest
from julee_polling.infrastructure.temporal.proxies import (
    WorkflowPollerServiceProxy,
)
from julee_polling.usecases.poll_data import PollDataUseCase

logger = logging.getLogger(__name__)


def _what_was_seen_last_time(
    previous_completion: dict[str, Any] | None,
) -> tuple[str | None, bytes | None]:
    """Read the last run's baseline out of Temporal's completion result.

    The shape of that dict is this pipeline's own business — it wrote
    it — so reading it happens here rather than in the use case.

    Args:
        previous_completion: What the last run returned, if there was one

    Returns:
        The hash and the content last seen, either of which may be None
    """
    if not previous_completion or "polling_result" not in previous_completion:
        return None, None

    polling_result = previous_completion["polling_result"]
    content = polling_result.get("content")
    return polling_result.get("content_hash"), (
        content.encode("utf-8") if content else None
    )


@workflow.defn
class NewDataDetectionPipeline:
    """
    Temporal workflow for endpoint polling with new data detection.

    This workflow:
    1. Polls an endpoint using the configured polling service
    2. Compares result with previous completion to detect changes
    3. Runs the calculator to identify new item IDs (if provided)
    4. Hands off to result handler when new data is detected
    5. Returns completion result for next scheduled execution

    The workflow uses Temporal's schedule last completion result feature
    to automatically receive the previous execution's result for comparison.

    Subclasses must implement get_handler() and get_calculator() to supply the
    appropriate objects for each polling use case (credential, product, etc.).
    """

    def __init__(self) -> None:
        self.current_step = "initialized"
        self.endpoint_id: str | None = None
        self.has_new_data: bool = False

    @abstractmethod
    def get_handler(self) -> PollingResultHandler:
        """Return the PollingResultHandler for this pipeline."""
        ...

    @abstractmethod
    def get_calculator(self) -> NewDataCalculator:
        """Return the NewDataCalculator for this pipeline."""
        ...

    @workflow.query
    def get_current_step(self) -> str:
        """Query method to get the current workflow step."""
        return self.current_step

    @workflow.query
    def get_endpoint_id(self) -> str | None:
        """Query method to get the endpoint ID being polled."""
        return self.endpoint_id

    @workflow.query
    def get_has_new_data(self) -> bool:
        """Query method to check if new data was detected."""
        return self.has_new_data

    @workflow.run
    async def run(
        self,
        config: PollingConfig | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the new data detection workflow.

        Args:
            config: Configuration for the polling operation (PollingConfig or dict
                    from Temporal schedule serialisation)

        Returns:
            Completion result containing polling result and detection metadata

        Raises:
            RuntimeError: If polling fails after retries
        """
        # Temporal schedules serialise arguments as dicts, so accept either
        # and work with the validated entity from here on.
        polling_config = (
            PollingConfig.model_validate(config) if isinstance(config, dict) else config
        )

        self.endpoint_id = polling_config.endpoint_identifier

        previous_completion = workflow.get_last_completion_result()

        workflow.logger.info(
            "Starting new data detection pipeline",
            extra={
                "endpoint_id": self.endpoint_id,
                "polling_protocol": polling_config.polling_protocol.value,
                "has_previous_completion": previous_completion is not None,
                "workflow_id": workflow.info().workflow_id,
                "run_id": workflow.info().run_id,
            },
        )

        self.current_step = "polling_endpoint"

        try:
            seen = _what_was_seen_last_time(previous_completion)
            request = PollDataRequest(
                config=polling_config,
                previous_hash=seen[0],
                previous_content=seen[1],
            )
            use_case = PollDataUseCase(
                poller=WorkflowPollerServiceProxy(),  # type: ignore[abstract]
                handler=self.get_handler(),
                calculator=self.get_calculator(),
            )
            response = await use_case.execute(request)

            self.endpoint_id = response.endpoint_id
            self.has_new_data = response.new_items_found
            self.current_step = "completed"

            # The use case reports and does not log. This is the one
            # place that has both what it reported and the execution
            # the observability stack is following, so this is where
            # what happened gets written down.
            told = {
                "endpoint_id": response.endpoint_id,
                "has_new_data": response.new_items_found,
                "polled_successfully": response.polled_successfully,
                "handoff": response.handoff.value,
                "items_notified": response.items_notified,
                "handoff_info": list(response.handoff_info),
            }
            if response.handoff is Handoff.FAILED:
                workflow.logger.error(
                    "Nobody was told there was new data; the obligation stands "
                    "and the baseline is held back so the next run tries again",
                    extra=told,
                )
            elif not response.polled_successfully:
                workflow.logger.warning(
                    "The endpoint could not be polled; the baseline is held back",
                    extra=told,
                )
            else:
                workflow.logger.info(
                    "New data detection pipeline completed successfully",
                    extra=told,
                )

            # What gets recorded is this pipeline's decision, not the
            # use case's. A poll that failed saw nothing, and a handoff
            # that failed left the obligation standing, so in both cases
            # the previous baseline is kept and the next run tries again
            # rather than comparing against something nobody acted on.
            keep_previous = (
                not response.polled_successfully or response.handoff is Handoff.FAILED
            )
            recorded_hash = seen[0] if keep_previous else response.content_hash
            recorded_content = (
                (seen[1].decode("utf-8", errors="ignore") if seen[1] else "")
                if keep_previous
                else response.content
            )

            return {
                "polling_result": {
                    "content_hash": recorded_hash,
                    "content": recorded_content,
                    "polled_at": response.polled_at,
                },
                "detection_result": {
                    "has_new_data": response.new_items_found,
                    "current_hash": recorded_hash,
                    "handoff": response.handoff.value,
                    "handoff_info": list(response.handoff_info),
                },
                "endpoint_id": response.endpoint_id,
                "completed_at": workflow.now().isoformat(),
            }

        except Exception as e:
            self.current_step = "failed"

            workflow.logger.error(
                "New data detection pipeline failed",
                extra={
                    "endpoint_id": self.endpoint_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "current_step": self.current_step,
                },
                exc_info=True,
            )

            raise
