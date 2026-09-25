"""Handler protocol for journeys referencing an unknown persona."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.journey import Journey


@runtime_checkable
class UnknownJourneyPersonaHandler(Protocol):
    """Handler for journeys referencing an unknown persona.

    Called when a journey's persona doesn't match any known Persona entity.
    The handler decides what to do: create persona, suggest match, flag for review.
    """

    async def handle(self, journey: Journey, persona_name: str) -> Acknowledgement:
        """Handle a journey with unknown persona."""
        ...
