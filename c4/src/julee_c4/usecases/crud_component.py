"""Generated CRUD use cases for Component.

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

from julee_c4.domain.models.component import Component
from julee_c4.domain.repositories.component import ComponentRepository


class GetComponentRequest(BaseModel):
    """Request for getting a Component by slug."""

    slug: str


class GetComponentResponse(BaseModel):
    """Response for getting a Component."""

    component: Component


class GetComponentUseCase(GetUseCase[Component, ComponentRepository]):
    """Get a Component by slug."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: GetComponentRequest) -> GetComponentResponse:
        """Execute the get component use case."""
        entity = await self._get_by_id(request.slug)
        return GetComponentResponse(component=entity)


class ListComponentsRequest(BaseModel):
    """Request for listing all Components."""


class ListComponentsResponse(BaseModel):
    """Response for listing all Components."""

    components: list[Component]
    total_count: int


class ListComponentsUseCase(ListUseCase[Component, ComponentRepository]):
    """List all Components."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: ListComponentsRequest) -> ListComponentsResponse:
        """Execute the list components use case."""
        entities = await self._list_all()
        return ListComponentsResponse(components=entities, total_count=len(entities))


class CreateComponentRequest(BaseModel):
    """Request for creating a Component."""

    slug: str
    name: str
    container_slug: str
    system_slug: str
    description: str = ""
    technology: str = ""
    interface: str = ""
    code_path: str = ""
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateComponentResponse(BaseModel):
    """Response for creating a Component."""

    component: Component


class CreateComponentUseCase(CreateUseCase[Component, ComponentRepository]):
    """Create a new Component."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Component:
        """Construct a Component from a generated ID and request fields."""
        return Component(slug=entity_id, **kwargs)

    async def execute(self, request: CreateComponentRequest) -> CreateComponentResponse:
        """Execute the create component use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            container_slug=request.container_slug,
            system_slug=request.system_slug,
            description=request.description,
            technology=request.technology,
            interface=request.interface,
            code_path=request.code_path,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateComponentResponse(component=entity)


class UpdateComponentRequest(BaseModel):
    """Request for updating a Component.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    container_slug: str | None = None
    system_slug: str | None = None
    description: str | None = None
    technology: str | None = None
    interface: str | None = None
    code_path: str | None = None
    tags: tuple[str, ...] | None = None
    docname: str | None = None


class UpdateComponentResponse(BaseModel):
    """Response for updating a Component."""

    component: Component


class UpdateComponentUseCase(UpdateUseCase[Component, ComponentRepository]):
    """Update a Component."""

    def __init__(self, repo: ComponentRepository) -> None:
        """Initialise with the component repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateComponentRequest) -> UpdateComponentResponse:
        """Execute the update component use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateComponentResponse(component=entity)
