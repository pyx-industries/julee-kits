"""Handler protocol for stories referencing an unknown persona."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.story import Story


@runtime_checkable
class UnknownPersonaHandler(Protocol):
    """Handler for stories referencing an unknown persona.

    Called when a story's persona doesn't match any known Persona entity.
    The handler decides what to do: create persona, suggest match, flag for review.
    """

    async def handle(self, story: Story, persona_name: str) -> Acknowledgement:
        """Handle a story with unknown persona."""
        ...
