"""Handler protocol for coarse-grained post-creation journey orchestration."""

from typing import Protocol, runtime_checkable

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.journey import Journey


@runtime_checkable
class JourneyCreatedHandler(Protocol):
    """Coarse-grained handler for post-creation orchestration.

    Alternative to fine-grained handlers. Called after any journey creation/update.
    The handler inspects the journey and decides what orchestration is needed.
    """

    async def handle(self, journey: Journey) -> Acknowledgement:
        """Handle a newly created/updated journey."""
        ...
