"""Epic orchestration use case.

Business logic for post-creation/update epic orchestration.
Detects domain conditions (empty epic, unknown story refs) and
reports them for handler delegation.
"""

from julee.core.utils import normalize_name

from julee_hcd.domain.repositories.story import StoryRepository

from ..dtos.epic_orchestration import (
    EpicCondition,
    EpicOrchestrationRequest,
    EpicOrchestrationResponse,
)


class EpicOrchestrationUseCase:
    """Detect orchestration conditions for an epic.

    Checks for domain conditions that may require follow-up action:
    1. Empty epic - epic has no story_refs
    2. Unknown story refs - story_refs not found in StoryRepository

    Returns detected conditions for handler delegation.
    """

    def __init__(self, story_repo: StoryRepository) -> None:
        """Initialize with repositories for condition detection.

        Args:
            story_repo: Repository for story lookups
        """
        self._story_repo = story_repo

    async def execute(
        self, request: EpicOrchestrationRequest
    ) -> EpicOrchestrationResponse:
        """Execute orchestration condition detection.

        Args:
            request: Contains the epic to check

        Returns:
            Response with detected conditions
        """
        epic = request.epic
        conditions: list[EpicCondition] = []

        # Condition 1: Empty epic (no story refs)
        if not epic.story_refs:
            conditions.append(
                EpicCondition(
                    condition="empty_epic",
                    epic_slug=epic.slug,
                    details={"description": epic.description},
                )
            )

        # Condition 2: Unknown story refs
        if epic.story_refs:
            all_stories = await self._story_repo.list_all()
            known_titles = {normalize_name(s.feature_title) for s in all_stories}

            unknown_refs = [
                ref
                for ref in epic.story_refs
                if normalize_name(ref) not in known_titles
            ]

            if unknown_refs:
                conditions.append(
                    EpicCondition(
                        condition="unknown_story_refs",
                        epic_slug=epic.slug,
                        details={"unknown_refs": unknown_refs},
                    )
                )

        return EpicOrchestrationResponse(epic=epic, conditions=conditions)
