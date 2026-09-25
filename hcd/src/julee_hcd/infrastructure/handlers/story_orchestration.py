"""Story orchestration handler implementation.

Coarse-grained handler that wraps StoryOrchestrationUseCase.
Translates domain objects to use case requests, executes the use case,
and delegates detected conditions to fine-grained handlers.
"""

import logging
from typing import TYPE_CHECKING

from julee.core.entities.acknowledgement import Acknowledgement

from julee_hcd.domain.models.story import Story
from julee_hcd.usecases.story_orchestration import (
    StoryOrchestrationRequest,
    StoryOrchestrationUseCase,
)

if TYPE_CHECKING:
    from julee_hcd.domain.handlers.orphan_story_handler import OrphanStoryHandler
    from julee_hcd.domain.handlers.unknown_persona_handler import (
        UnknownPersonaHandler,
    )

logger = logging.getLogger(__name__)


class StoryOrchestrationHandler:
    """Coarse-grained handler for story orchestration.

    Wraps StoryOrchestrationUseCase. Translates domain objects to requests,
    executes the use case, and delegates detected conditions to fine-grained
    handlers.
    """

    def __init__(
        self,
        orchestration_use_case: StoryOrchestrationUseCase,
        orphan_handler: "OrphanStoryHandler",
        unknown_persona_handler: "UnknownPersonaHandler",
    ) -> None:
        """Initialize with internal use case and fine-grained handlers.

        Args:
            orchestration_use_case: Use case for condition detection
            orphan_handler: Handler for orphan story condition
            unknown_persona_handler: Handler for unknown persona condition
        """
        self._use_case = orchestration_use_case
        self._orphan_handler = orphan_handler
        self._unknown_persona_handler = unknown_persona_handler

    async def handle(self, story: Story) -> Acknowledgement:
        """Handle story orchestration.

        Translates story to request, executes use case, delegates conditions.

        Args:
            story: The story to orchestrate

        Returns:
            Acknowledgement with aggregated handler results
        """
        # Translate domain object to request
        request = StoryOrchestrationRequest(story=story)

        # Execute internal use case
        response = await self._use_case.execute(request)

        # Process response - delegate to fine-grained handlers
        info: list[str] = []

        for condition in response.conditions:
            if condition.condition == "unknown_persona":
                logger.info(
                    "Delegating unknown persona condition",
                    extra={
                        "story_slug": condition.story_slug,
                        "persona": condition.details.get("persona_name"),
                    },
                )
                ack = await self._unknown_persona_handler.handle(
                    story, condition.details["persona_name"]
                )
                info.extend(ack.info)

            elif condition.condition == "orphan_story":
                logger.info(
                    "Delegating orphan story condition",
                    extra={
                        "story_slug": condition.story_slug,
                        "feature_title": condition.details.get("feature_title"),
                    },
                )
                ack = await self._orphan_handler.handle(story)
                info.extend(ack.info)

        return Acknowledgement.wilco(info=info)
