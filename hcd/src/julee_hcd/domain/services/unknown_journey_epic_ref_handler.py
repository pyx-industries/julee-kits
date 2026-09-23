"""Handler protocol for journeys referencing unknown epics."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.journey import Journey


@runtime_checkable
class UnknownJourneyEpicRefHandler(Protocol):
    """Handler for journeys referencing unknown epics.

    Called when a journey's epic steps reference slugs not found in EpicRepository.
    The handler decides what to do: warn, suggest corrections, etc.
    """

    async def handle(
        self, journey: Journey, unknown_refs: list[str]
    ) -> Acknowledgement:
        """Handle a journey with unknown epic references."""
        ...
