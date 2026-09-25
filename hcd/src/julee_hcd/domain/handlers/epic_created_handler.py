"""Handler protocol for coarse-grained post-creation epic orchestration."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.epic import Epic


@runtime_checkable
class EpicCreatedHandler(Protocol):
    """Coarse-grained handler for post-creation orchestration.

    Alternative to fine-grained handlers. Called after any epic creation/update.
    The handler inspects the epic and decides what orchestration is needed.
    """

    async def handle(self, epic: Epic) -> Acknowledgement:
        """Handle a newly created/updated epic."""
        ...
