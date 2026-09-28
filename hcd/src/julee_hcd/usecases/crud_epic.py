"""Generated CRUD use cases for Epic.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.repositories.epic import EpicRepository

from ..dtos.crud_epic import (
    CreateEpicRequest,
    CreateEpicResponse,
    DeleteEpicRequest,
    DeleteEpicResponse,
    GetEpicRequest,
    GetEpicResponse,
    ListEpicsRequest,
    ListEpicsResponse,
    UpdateEpicRequest,
    UpdateEpicResponse,
)


class GetEpicUseCase(GetUseCase[Epic, EpicRepository]):
    """Get a Epic by slug."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: GetEpicRequest) -> GetEpicResponse:
        """Execute the get epic use case."""
        entity = await self._get_by_id(request.slug)
        return GetEpicResponse(epic=entity)


class ListEpicsUseCase(ListUseCase[Epic, EpicRepository]):
    """List all Epics."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: ListEpicsRequest) -> ListEpicsResponse:
        """Execute the list epics use case."""
        entities = await self._list_all()
        return ListEpicsResponse(epics=entities, total_count=len(entities))


class CreateEpicUseCase(CreateUseCase[Epic, EpicRepository]):
    """Create a new Epic."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Epic:
        """Construct a Epic from a generated ID and request fields."""
        return Epic(slug=Slug(entity_id), **kwargs)

    async def execute(self, request: CreateEpicRequest) -> CreateEpicResponse:
        """Execute the create epic use case."""
        entity = await self._create(
            entity_id=request.slug,
            description=request.description,
            story_refs=request.story_refs,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateEpicResponse(epic=entity)


class UpdateEpicUseCase(UpdateUseCase[Epic, EpicRepository]):
    """Update a Epic."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateEpicRequest) -> UpdateEpicResponse:
        """Execute the update epic use case."""
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateEpicResponse(epic=entity)


class DeleteEpicUseCase(DeleteUseCase[Epic, EpicRepository]):
    """Delete a Epic by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: DeleteEpicRequest) -> DeleteEpicResponse:
        """Execute the delete epic use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteEpicResponse(deleted=deleted)
