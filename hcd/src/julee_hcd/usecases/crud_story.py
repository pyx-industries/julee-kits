"""Generated CRUD use cases for Story.

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

from julee_hcd.domain.models.story import Story
from julee_hcd.domain.repositories.story import StoryRepository


class GetStoryRequest(BaseModel):
    """Request for getting a Story by slug."""

    slug: str


class GetStoryResponse(BaseModel):
    """Response for getting a Story."""

    story: Story


class GetStoryUseCase(GetUseCase[Story, StoryRepository]):
    """Get a Story by slug."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: GetStoryRequest) -> GetStoryResponse:
        """Execute the get story use case."""
        entity = await self._get_by_id(request.slug)
        return GetStoryResponse(story=entity)


class ListStoriesRequest(BaseModel):
    """Request for listing all Stories."""


class ListStoriesResponse(BaseModel):
    """Response for listing all Stories."""

    stories: list[Story]
    total_count: int


class ListStoriesUseCase(ListUseCase[Story, StoryRepository]):
    """List all Stories."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: ListStoriesRequest) -> ListStoriesResponse:
        """Execute the list stories use case."""
        entities = await self._list_all()
        return ListStoriesResponse(stories=entities, total_count=len(entities))


class CreateStoryRequest(BaseModel):
    """Request for creating a Story."""

    slug: str
    feature_title: str
    persona: str
    i_want: str
    so_that: str
    app_slug: str
    file_path: str
    abs_path: str = ""
    gherkin_snippet: str = ""
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateStoryResponse(BaseModel):
    """Response for creating a Story."""

    story: Story


class CreateStoryUseCase(CreateUseCase[Story, StoryRepository]):
    """Create a new Story."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Story:
        """Construct a Story from a generated ID and request fields."""
        return Story(slug=entity_id, **kwargs)

    async def execute(self, request: CreateStoryRequest) -> CreateStoryResponse:
        """Execute the create story use case."""
        entity = await self._create(
            entity_id=request.slug,
            feature_title=request.feature_title,
            persona=request.persona,
            i_want=request.i_want,
            so_that=request.so_that,
            app_slug=request.app_slug,
            file_path=request.file_path,
            abs_path=request.abs_path,
            gherkin_snippet=request.gherkin_snippet,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateStoryResponse(story=entity)


class UpdateStoryRequest(BaseModel):
    """Request for updating a Story.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    feature_title: str | None = None
    persona: str | None = None
    i_want: str | None = None
    so_that: str | None = None
    app_slug: str | None = None
    file_path: str | None = None
    abs_path: str | None = None
    gherkin_snippet: str | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdateStoryResponse(BaseModel):
    """Response for updating a Story."""

    story: Story


class UpdateStoryUseCase(UpdateUseCase[Story, StoryRepository]):
    """Update a Story."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateStoryRequest) -> UpdateStoryResponse:
        """Execute the update story use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateStoryResponse(story=entity)


class DeleteStoryRequest(BaseModel):
    """Request for deleting a Story by slug."""

    slug: str


class DeleteStoryResponse(BaseModel):
    """Response for deleting a Story."""

    deleted: bool


class DeleteStoryUseCase(DeleteUseCase[Story, StoryRepository]):
    """Delete a Story by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: DeleteStoryRequest) -> DeleteStoryResponse:
        """Execute the delete story use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteStoryResponse(deleted=deleted)
