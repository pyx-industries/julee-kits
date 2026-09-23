"""Handler protocol for journeys referencing unknown stories."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.journey import Journey


@runtime_checkable
class UnknownJourneyStoryRefHandler(Protocol):
    """Handler for journeys referencing unknown stories.

    Called when a journey's story steps reference titles not found in StoryRepository.
    The handler decides what to do: warn, suggest corrections, etc.
    """

    async def handle(
        self, journey: Journey, unknown_refs: list[str]
    ) -> Acknowledgement:
        """Handle a journey with unknown story references."""
        ...
