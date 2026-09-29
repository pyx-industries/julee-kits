"""DerivePersonasUseCase with co-located request/response.

Use case for deriving personas from stories and epics.

Supports two persona sources:
1. Defined personas: Explicitly created via define-persona directive
2. Derived personas: Extracted from user story "As a..." clauses

Defined personas are authoritative and get enriched with story data.
Derived personas fill gaps when stories reference undefined personas.

The derivation itself is in domain/calculators/personas.py. It was
here, and GetPersonaUseCase imported this module to reach it.
"""

from julee_hcd.domain.models.persona import merge_personas
from julee_hcd.domain.repositories.epic import EpicRepository
from julee_hcd.domain.repositories.persona import PersonaRepository
from julee_hcd.domain.repositories.story import StoryRepository

from ..dtos.derive_personas import (
    DerivePersonasRequest,
    DerivePersonasResponse,
)


class DerivePersonasUseCase:
    """Derive and merge personas.

    Combines defined personas (from PersonaRepository) with derived
    personas (from stories). Defined personas are authoritative and
    get enriched with app_slugs/epic_slugs from their stories.
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

    async def execute(self, request: DerivePersonasRequest) -> DerivePersonasResponse:
        """Derive and merge personas from all sources.

        Process:
        1. Fetch defined personas from PersonaRepository (if available)
        2. Derive personas from stories (extract from "As a..." clauses)
        3. Merge: defined personas get enriched with app_slugs/epic_slugs
        4. Derived personas without definitions are included as fallback

        Args:
            request: Derive personas request (extensible for filtering)

        Returns:
            Response containing merged list of personas
        """
        stories = await self.story_repo.list_all()
        epics = await self.epic_repo.list_all()
        defined = await self.persona_repo.list_all() if self.persona_repo else []

        return DerivePersonasResponse(personas=merge_personas(defined, stories, epics))
