"""Generated CRUD use cases for Persona.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.repositories.persona import PersonaRepository


class GetPersonaRequest(BaseModel):
    """Request for getting a Persona by slug."""

    slug: str


class GetPersonaResponse(BaseModel):
    """Response for getting a Persona."""

    persona: Persona


class GetPersonaUseCase(GetUseCase[Persona, PersonaRepository]):
    """Get a Persona by slug."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: GetPersonaRequest) -> GetPersonaResponse:
        """Execute the get persona use case."""
        entity = await self._get_by_id(request.slug)
        return GetPersonaResponse(persona=entity)


class ListPersonasRequest(BaseModel):
    """Request for listing all Personas."""


class ListPersonasResponse(BaseModel):
    """Response for listing all Personas."""

    personas: list[Persona]
    total_count: int


class ListPersonasUseCase(ListUseCase[Persona, PersonaRepository]):
    """List all Personas."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: ListPersonasRequest) -> ListPersonasResponse:
        """Execute the list personas use case."""
        entities = await self._list_all()
        return ListPersonasResponse(personas=entities, total_count=len(entities))


class CreatePersonaRequest(BaseModel):
    """Request for creating a Persona."""

    slug: str = ""
    name: str
    goals: tuple[str, ...] = ()
    frustrations: tuple[str, ...] = ()
    jobs_to_be_done: tuple[str, ...] = ()
    context: str = ""
    app_slugs: tuple[str, ...] = ()
    epic_slugs: tuple[str, ...] = ()
    accelerator_slugs: tuple[str, ...] = ()
    contrib_slugs: tuple[str, ...] = ()
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreatePersonaResponse(BaseModel):
    """Response for creating a Persona."""

    persona: Persona


class CreatePersonaUseCase(CreateUseCase[Persona, PersonaRepository]):
    """Create a new Persona."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Persona:
        """Construct a Persona from a generated ID and request fields."""
        return Persona(slug=entity_id, **kwargs)

    async def execute(self, request: CreatePersonaRequest) -> CreatePersonaResponse:
        """Execute the create persona use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            goals=request.goals,
            frustrations=request.frustrations,
            jobs_to_be_done=request.jobs_to_be_done,
            context=request.context,
            app_slugs=request.app_slugs,
            epic_slugs=request.epic_slugs,
            accelerator_slugs=request.accelerator_slugs,
            contrib_slugs=request.contrib_slugs,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreatePersonaResponse(persona=entity)


class UpdatePersonaRequest(BaseModel):
    """Request for updating a Persona.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    goals: tuple[str, ...] | None = None
    frustrations: tuple[str, ...] | None = None
    jobs_to_be_done: tuple[str, ...] | None = None
    context: str | None = None
    app_slugs: tuple[str, ...] | None = None
    epic_slugs: tuple[str, ...] | None = None
    accelerator_slugs: tuple[str, ...] | None = None
    contrib_slugs: tuple[str, ...] | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdatePersonaResponse(BaseModel):
    """Response for updating a Persona."""

    persona: Persona


class UpdatePersonaUseCase(UpdateUseCase[Persona, PersonaRepository]):
    """Update a Persona."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: UpdatePersonaRequest) -> UpdatePersonaResponse:
        """Execute the update persona use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdatePersonaResponse(persona=entity)
