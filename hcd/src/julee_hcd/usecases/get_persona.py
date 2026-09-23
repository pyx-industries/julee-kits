"""GetPersonaUseCase with co-located request/response.

Use case for getting a persona by name.
"""

from julee.core.utils import normalize_name
from pydantic import BaseModel, Field

from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.repositories.epic import EpicRepository
from julee_hcd.domain.repositories.persona import PersonaRepository
from julee_hcd.domain.repositories.story import StoryRepository

from .derive_personas import DerivePersonasRequest, DerivePersonasUseCase


class GetPersonaRequest(BaseModel):
    """Request for getting a persona by name."""

    name: str = Field(description="Persona name to search for")


class GetPersonaResponse(BaseModel):
    """Response from getting a persona by name."""

    persona: Persona | None


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
        derive_use_case = DerivePersonasUseCase(
            self.story_repo, self.epic_repo, self.persona_repo
        )
        derive_response = await derive_use_case.execute(DerivePersonasRequest())

        normalized_search = normalize_name(request.name)
        for persona in derive_response.personas:
            if persona.normalized_name == normalized_search:
                return GetPersonaResponse(persona=persona)

        return GetPersonaResponse(persona=None)
