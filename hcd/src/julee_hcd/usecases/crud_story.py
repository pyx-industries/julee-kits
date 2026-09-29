"""Generated CRUD use cases for Story.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from julee.core.values.text import Name, NonEmptyText, Slug

from julee_hcd.domain.models.story import Story
from julee_hcd.domain.repositories.story import StoryRepository

from ..dtos.crud_story import (
    CreateStoryRequest,
    CreateStoryResponse,
    DeleteStoryRequest,
    DeleteStoryResponse,
    GetStoryRequest,
    GetStoryResponse,
    ListStoriesRequest,
    ListStoriesResponse,
    UpdateStoryRequest,
    UpdateStoryResponse,
)


class GetStoryUseCase(GetUseCase[Story, StoryRepository]):
    """Get a Story by slug."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: GetStoryRequest) -> GetStoryResponse:
        """Execute the get story use case."""
        entity = await self._get_by_id(request.slug)
        return GetStoryResponse.of(entity)


class ListStoriesUseCase(ListUseCase[Story, StoryRepository]):
    """List all Stories."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: ListStoriesRequest) -> ListStoriesResponse:
        """Execute the list stories use case."""
        entities = await self._list_all()
        return ListStoriesResponse.of(entities)


class CreateStoryUseCase(CreateUseCase[Story, StoryRepository]):
    """Create a new Story."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Story:
        """Construct a Story from a generated ID and request fields."""
        return Story(slug=NonEmptyText(entity_id), **kwargs)

    async def execute(self, request: CreateStoryRequest) -> CreateStoryResponse:
        """Execute the create story use case."""
        entity = await self._create(
            entity_id=request.slug,
            feature_title=Name(request.feature_title),
            persona=Name(request.persona),
            i_want=request.i_want,
            so_that=request.so_that,
            app_slug=Slug(request.app_slug),
            file_path=request.file_path,
            abs_path=request.abs_path,
            gherkin_snippet=request.gherkin_snippet,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateStoryResponse.of(entity)


class UpdateStoryUseCase(UpdateUseCase[Story, StoryRepository]):
    """Update a Story."""

    def __init__(self, repo: StoryRepository) -> None:
        """Initialise with the story repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateStoryRequest) -> UpdateStoryResponse:
        """Execute the update story use case."""
        changes = request.changes()
        if changes.get("app_slug") is not None:
            changes["app_slug"] = Slug(changes["app_slug"])
        if changes.get("feature_title") is not None:
            changes["feature_title"] = Name(changes["feature_title"])
        if changes.get("persona") is not None:
            changes["persona"] = Name(changes["persona"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateStoryResponse.of(entity)


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
