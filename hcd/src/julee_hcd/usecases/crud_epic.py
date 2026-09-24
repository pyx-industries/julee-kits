"""Generated CRUD use cases for Epic.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.repositories.epic import EpicRepository


class GetEpicRequest(BaseModel):
    """Request for getting a Epic by slug."""

    slug: str


class GetEpicResponse(BaseModel):
    """Response for getting a Epic."""

    epic: Epic


class GetEpicUseCase(GetUseCase[Epic, EpicRepository]):
    """Get a Epic by slug."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: GetEpicRequest) -> GetEpicResponse:
        """Execute the get epic use case."""
        entity = await self._get_by_id(request.slug)
        return GetEpicResponse(epic=entity)


class ListEpicsRequest(BaseModel):
    """Request for listing all Epics."""


class ListEpicsResponse(BaseModel):
    """Response for listing all Epics."""

    epics: list[Epic]
    total_count: int


class ListEpicsUseCase(ListUseCase[Epic, EpicRepository]):
    """List all Epics."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: ListEpicsRequest) -> ListEpicsResponse:
        """Execute the list epics use case."""
        entities = await self._list_all()
        return ListEpicsResponse(epics=entities, total_count=len(entities))


class CreateEpicRequest(BaseModel):
    """Request for creating a Epic."""

    slug: str
    description: str = ""
    story_refs: tuple[str, ...] = ()
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateEpicResponse(BaseModel):
    """Response for creating a Epic."""

    epic: Epic


class CreateEpicUseCase(CreateUseCase[Epic, EpicRepository]):
    """Create a new Epic."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Epic:
        """Construct a Epic from a generated ID and request fields."""
        return Epic(slug=entity_id, **kwargs)

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


class UpdateEpicRequest(BaseModel):
    """Request for updating a Epic.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    description: str | None = None
    story_refs: tuple[str, ...] | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdateEpicResponse(BaseModel):
    """Response for updating a Epic."""

    epic: Epic


class UpdateEpicUseCase(UpdateUseCase[Epic, EpicRepository]):
    """Update a Epic."""

    def __init__(self, repo: EpicRepository) -> None:
        """Initialise with the epic repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateEpicRequest) -> UpdateEpicResponse:
        """Execute the update epic use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateEpicResponse(epic=entity)


class DeleteEpicRequest(BaseModel):
    """Request for deleting a Epic by slug."""

    slug: str


class DeleteEpicResponse(BaseModel):
    """Response for deleting a Epic."""

    deleted: bool


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
