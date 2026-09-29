"""GetPersonaUseCase with co-located request/response.

Use case for getting a persona by name.
"""

from julee.core.utils import normalize_name

from julee_hcd.domain.models.persona import merge_personas
from julee_hcd.domain.repositories.epic import EpicRepository
from julee_hcd.domain.repositories.persona import PersonaRepository
from julee_hcd.domain.repositories.story import StoryRepository

from ..dtos.get_persona import (
    GetPersonaRequest,
    GetPersonaResponse,
)


class GetPersonaUseCase:
    """Get a persona by name.

    Searches both defined and derived personas, returning merged results.
    """

    def __init__(
        self,
        story_repo: StoryRepository,
        epic_repo: EpicRepository,
        persona_repo: PersonaRepository | None = None,
    ) -> None:
        """Initialize with repository dependencies.

        Args:
            story_repo: Story repository instance
            epic_repo: Epic repository instance
            persona_repo: Optional persona repository for defined personas
        """
        self.story_repo = story_repo
        self.epic_repo = epic_repo
        self.persona_repo = persona_repo

    async def execute(self, request: GetPersonaRequest) -> GetPersonaResponse:
        """Get a persona by name (case-insensitive).

        Searches merged personas (defined + derived) and returns
        the matching persona if found.

        Args:
            request: Request containing the persona name

        Returns:
            Response containing the persona if found, or None
        """
        stories = await self.story_repo.list_all()
        epics = await self.epic_repo.list_all()
        defined = await self.persona_repo.list_all() if self.persona_repo else []

        normalized_search = normalize_name(request.name)
        for persona in merge_personas(defined, stories, epics):
            if persona.normalized_name == normalized_search:
                return GetPersonaResponse(persona=persona)

        return GetPersonaResponse(persona=None)
