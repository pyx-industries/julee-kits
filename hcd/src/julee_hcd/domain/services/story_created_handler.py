"""Handler protocol for coarse-grained post-creation story orchestration."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.story import Story


@runtime_checkable
class StoryCreatedHandler(Protocol):
    """Coarse-grained handler for post-creation orchestration.

    Alternative to fine-grained handlers. Called after any story creation.
    The handler inspects the story and decides what orchestration is needed.
    """

    async def handle(self, story: Story) -> Acknowledgement:
        """Handle a newly created story."""
        ...
