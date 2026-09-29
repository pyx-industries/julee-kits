"""What one run of the pipeline leaves for the next one.

The baseline crosses deploys through Temporal's workflow history, so
what matters is which changes are loud and which are survivable. It was
``dict[str, Any]`` read with ``.get()``, where every change was silent
and read back as no baseline -- which makes a run report new data and
notify again.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from julee_polling.apps.worker.completion import (
    DetectionRecord,
    PipelineCompletion,
    PollingRecord,
)

pytestmark = pytest.mark.unit

COMPLETION = TypeAdapter(PipelineCompletion)

A_RUN = PipelineCompletion(
    polling_result=PollingRecord(
        content_hash="abc123",
        content="hello",
        polled_at="2023-01-01T00:00:00+00:00",
    ),
    detection_result=DetectionRecord(
        has_new_data=True,
        current_hash="abc123",
        handoff="discharged",
        handoff_info=("queued 1",),
    ),
    endpoint_id="test-api",
    completed_at="2023-01-01T00:00:01+00:00",
)


class TestTheShapeItIsStoredAs:
    """Temporal holds JSON, so the round trip is the contract."""

    def test_it_survives_the_round_trip(self) -> None:
        """Through the dict Temporal actually hands back."""
        assert COMPLETION.validate_python(A_RUN.model_dump(mode="json")) == A_RUN

    def test_the_keys_are_the_ones_that_were_written_before(self) -> None:
        """Renaming one orphans every completion already in history."""
        stored = A_RUN.model_dump(mode="json")

        assert tuple(stored) == (
            "polling_result",
            "detection_result",
            "endpoint_id",
            "completed_at",
        )
        assert tuple(stored["polling_result"]) == (
            "content_hash",
            "content",
            "polled_at",
        )


class TestWhatItToleratesFromAnOlderRun:
    """Lenient about the half nothing reads back."""

    def test_a_completion_with_no_detection_half_still_loads(self) -> None:
        """Only polling_result is read, so only it is required."""
        found = COMPLETION.validate_python(
            {"polling_result": A_RUN.polling_result.model_dump(mode="json")}
        )

        assert found.polling_result.content_hash == "abc123"

    def test_a_detection_half_written_before_handoff_existed_still_loads(self) -> None:
        """handoff was added to this pipeline after it shipped."""
        stored = A_RUN.model_dump(mode="json")
        del stored["detection_result"]["handoff"]
        del stored["detection_result"]["handoff_info"]

        found = COMPLETION.validate_python(stored)

        assert found.polling_result.content_hash == "abc123"
        assert found.detection_result.handoff == ""

    def test_a_run_that_saw_nothing_loads(self) -> None:
        """A failed poll records no hash and empty content."""
        found = COMPLETION.validate_python(
            {
                "polling_result": {
                    "content_hash": None,
                    "content": "",
                    "polled_at": "2023-01-01T00:00:00+00:00",
                }
            }
        )

        assert found.polling_result.content_hash is None


class TestWhatItRefuses:
    """Strict about the half that is read back."""

    def test_a_completion_with_no_baseline_at_all_is_refused(self) -> None:
        """Rather than read as a run that saw nothing, which is a
        different thing and would hold the baseline back for ever."""
        with pytest.raises(ValidationError):
            COMPLETION.validate_python({"endpoint_id": "test-api"})

    def test_a_renamed_baseline_key_is_refused(self) -> None:
        """The silent failure this type exists to make loud.

        Read with .get() this came back as None, the pipeline started
        from no baseline, and every run reported new data.
        """
        stored = A_RUN.model_dump(mode="json")
        stored["polling_result"]["hash"] = stored["polling_result"].pop("content_hash")

        with pytest.raises(ValidationError):
            COMPLETION.validate_python(stored)
