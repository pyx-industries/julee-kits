"""Handler protocol for journeys created without any steps."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.journey import Journey


@runtime_checkable
class EmptyJourneyHandler(Protocol):
    """Handler for journeys created without any steps.

    Called when a journey is created/updated and has no steps.
    The handler decides what to do: warn, suggest steps, etc.
    """

    async def handle(self, journey: Journey) -> Acknowledgement:
        """Handle an empty journey."""
        ...
