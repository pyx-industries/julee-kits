"""Generated CRUD use cases for Persona.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Name, Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.repositories.persona import PersonaRepository

from ..dtos.crud_persona import (
    CreatePersonaRequest,
    CreatePersonaResponse,
    DeletePersonaRequest,
    DeletePersonaResponse,
    GetPersonaRequest,
    GetPersonaResponse,
    ListPersonasRequest,
    ListPersonasResponse,
    UpdatePersonaRequest,
    UpdatePersonaResponse,
)


class GetPersonaUseCase(GetUseCase[Persona, PersonaRepository]):
    """Get a Persona by slug."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: GetPersonaRequest) -> GetPersonaResponse:
        """Execute the get persona use case."""
        entity = await self._get_by_id(request.slug)
        return GetPersonaResponse(persona=entity)


class ListPersonasUseCase(ListUseCase[Persona, PersonaRepository]):
    """List all Personas."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: ListPersonasRequest) -> ListPersonasResponse:
        """Execute the list personas use case."""
        entities = await self._list_all()
        return ListPersonasResponse(personas=entities, total_count=len(entities))


class CreatePersonaUseCase(CreateUseCase[Persona, PersonaRepository]):
    """Create a new Persona."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Persona:
        """Construct a Persona from a generated ID and request fields.

        A request that names no slug leaves the entity to work
        one out, so the field is left out rather than passed empty.
        """
        if not entity_id:
            return Persona(**kwargs)

        return Persona(slug=Slug(entity_id), **kwargs)

    async def execute(self, request: CreatePersonaRequest) -> CreatePersonaResponse:
        """Execute the create persona use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=Name(request.name),
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


class UpdatePersonaUseCase(UpdateUseCase[Persona, PersonaRepository]):
    """Update a Persona."""

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: UpdatePersonaRequest) -> UpdatePersonaResponse:
        """Execute the update persona use case."""
        changes = request.changes()
        if changes.get("name") is not None:
            changes["name"] = Name(changes["name"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdatePersonaResponse(persona=entity)


class DeletePersonaUseCase(DeleteUseCase[Persona, PersonaRepository]):
    """Delete a Persona by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: PersonaRepository) -> None:
        """Initialise with the persona repository."""
        super().__init__(repo)

    async def execute(self, request: DeletePersonaRequest) -> DeletePersonaResponse:
        """Execute the delete persona use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeletePersonaResponse(deleted=deleted)
