"""Journey orchestration use case.

Business logic for post-creation/update journey orchestration.
Detects domain conditions (unknown persona, unknown story/epic refs, empty journey)
and reports them for handler delegation.
"""

from julee.core.utils import normalize_name

from julee_hcd.domain.repositories.epic import EpicRepository
from julee_hcd.domain.repositories.persona import PersonaRepository
from julee_hcd.domain.repositories.story import StoryRepository

from ..dtos.journey_orchestration import (
    JourneyCondition,
    JourneyOrchestrationRequest,
    JourneyOrchestrationResponse,
)


class JourneyOrchestrationUseCase:
    """Detect orchestration conditions for a journey.

    Checks for domain conditions that may require follow-up action:
    1. Unknown persona - journey.persona not found in PersonaRepository
    2. Unknown story refs - story steps not found in StoryRepository
    3. Unknown epic refs - epic steps not found in EpicRepository
    4. Empty journey - journey has no steps

    Returns detected conditions for handler delegation.
    """

    def __init__(
        self,
        persona_repo: PersonaRepository,
        story_repo: StoryRepository,
        epic_repo: EpicRepository,
    ) -> None:
        """Initialize with repositories for condition detection.

        Args:
            persona_repo: Repository for persona lookups
            story_repo: Repository for story lookups
            epic_repo: Repository for epic lookups
        """
        self._persona_repo = persona_repo
        self._story_repo = story_repo
        self._epic_repo = epic_repo

    async def execute(
        self, request: JourneyOrchestrationRequest
    ) -> JourneyOrchestrationResponse:
        """Execute orchestration condition detection.

        Args:
            request: Contains the journey to check

        Returns:
            Response with detected conditions
        """
        journey = request.journey
        conditions: list[JourneyCondition] = []

        # Condition 1: Unknown persona
        if journey.persona and journey.persona != "unknown":
            persona = await self._persona_repo.get_by_normalized_name(
                journey.persona_normalized
            )
            if persona is None:
                conditions.append(
                    JourneyCondition(
                        condition="unknown_persona",
                        journey_slug=journey.slug,
                        details={"persona_name": journey.persona},
                    )
                )

        # Condition 2: Empty journey (no steps)
        if not journey.steps:
            conditions.append(
                JourneyCondition(
                    condition="empty_journey",
                    journey_slug=journey.slug,
                    details={"persona": journey.persona},
                )
            )

        # Condition 3: Unknown story refs in steps
        story_refs = journey.get_story_refs()
        if story_refs:
            all_stories = await self._story_repo.list_all()
            known_titles = {normalize_name(s.feature_title) for s in all_stories}

            unknown_story_refs = [
                ref for ref in story_refs if normalize_name(ref) not in known_titles
            ]

            if unknown_story_refs:
                conditions.append(
                    JourneyCondition(
                        condition="unknown_story_refs",
                        journey_slug=journey.slug,
                        details={"unknown_refs": unknown_story_refs},
                    )
                )

        # Condition 4: Unknown epic refs in steps
        epic_refs = journey.get_epic_refs()
        if epic_refs:
            all_epics = await self._epic_repo.list_all()
            known_slugs = {e.slug for e in all_epics}

            unknown_epic_refs = [ref for ref in epic_refs if ref not in known_slugs]

            if unknown_epic_refs:
                conditions.append(
                    JourneyCondition(
                        condition="unknown_epic_refs",
                        journey_slug=journey.slug,
                        details={"unknown_refs": unknown_epic_refs},
                    )
                )

        return JourneyOrchestrationResponse(journey=journey, conditions=conditions)
