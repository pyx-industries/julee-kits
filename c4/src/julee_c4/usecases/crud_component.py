"""Generated CRUD use cases for Component.

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

from julee_c4.domain.models.component import Component
from julee_c4.domain.repositories.component import ComponentRepository

from ..dtos.crud_component import (
    CreateComponentRequest,
    CreateComponentResponse,
    DeleteComponentRequest,
    DeleteComponentResponse,
    GetComponentRequest,
    GetComponentResponse,
    ListComponentsRequest,
    ListComponentsResponse,
    UpdateComponentRequest,
    UpdateComponentResponse,
)


class GetComponentUseCase(GetUseCase[Component, ComponentRepository]):
    """Get a Component by slug."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: GetComponentRequest) -> GetComponentResponse:
        """Execute the get component use case."""
        entity = await self._get_by_id(request.slug)
        return GetComponentResponse.of(entity)


class ListComponentsUseCase(ListUseCase[Component, ComponentRepository]):
    """List all Components."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: ListComponentsRequest) -> ListComponentsResponse:
        """Execute the list components use case."""
        entities = await self._list_all()
        return ListComponentsResponse.of(entities)


class CreateComponentUseCase(CreateUseCase[Component, ComponentRepository]):
    """Create a new Component."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Component:
        """Construct a Component from a generated ID and request fields."""
        return Component(slug=Slug(entity_id), **kwargs)

    async def execute(self, request: CreateComponentRequest) -> CreateComponentResponse:
        """Execute the create component use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=Name(request.name),
            container_slug=Slug(request.container_slug),
            system_slug=Slug(request.system_slug),
            description=request.description,
            technology=request.technology,
            interface=request.interface,
            code_path=request.code_path,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateComponentResponse.of(entity)


class UpdateComponentUseCase(UpdateUseCase[Component, ComponentRepository]):
    """Update a Component."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateComponentRequest) -> UpdateComponentResponse:
        """Execute the update component use case."""
        changes = request.changes()
        if changes.get("container_slug") is not None:
            changes["container_slug"] = Slug(changes["container_slug"])
        if changes.get("name") is not None:
            changes["name"] = Name(changes["name"])
        if changes.get("system_slug") is not None:
            changes["system_slug"] = Slug(changes["system_slug"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateComponentResponse.of(entity)


class DeleteComponentUseCase(DeleteUseCase[Component, ComponentRepository]):
    """Delete a Component by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: DeleteComponentRequest) -> DeleteComponentResponse:
        """Execute the delete component use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteComponentResponse(deleted=deleted)
