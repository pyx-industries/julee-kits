"""Generated CRUD use cases for Container.

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

from julee_c4.domain.models.container import Container, ContainerType
from julee_c4.domain.repositories.container import ContainerRepository


class GetContainerRequest(BaseModel):
    """Request for getting a Container by slug."""

    slug: str


class GetContainerResponse(BaseModel):
    """Response for getting a Container."""

    container: Container


class GetContainerUseCase(GetUseCase[Container, ContainerRepository]):
    """Get a Container by slug."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: GetContainerRequest) -> GetContainerResponse:
        """Execute the get container use case."""
        entity = await self._get_by_id(request.slug)
        return GetContainerResponse(container=entity)


class ListContainersRequest(BaseModel):
    """Request for listing all Containers."""


class ListContainersResponse(BaseModel):
    """Response for listing all Containers."""

    containers: list[Container]
    total_count: int


class ListContainersUseCase(ListUseCase[Container, ContainerRepository]):
    """List all Containers."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: ListContainersRequest) -> ListContainersResponse:
        """Execute the list containers use case."""
        entities = await self._list_all()
        return ListContainersResponse(containers=entities, total_count=len(entities))


class CreateContainerRequest(BaseModel):
    """Request for creating a Container."""

    slug: str
    name: str
    system_slug: str
    description: str = ""
    container_type: ContainerType = ContainerType.OTHER
    technology: str = ""
    url: str = ""
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateContainerResponse(BaseModel):
    """Response for creating a Container."""

    container: Container


class CreateContainerUseCase(CreateUseCase[Container, ContainerRepository]):
    """Create a new Container."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Container:
        """Construct a Container from a generated ID and request fields."""
        return Container(slug=entity_id, **kwargs)

    async def execute(self, request: CreateContainerRequest) -> CreateContainerResponse:
        """Execute the create container use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            system_slug=request.system_slug,
            description=request.description,
            container_type=request.container_type,
            technology=request.technology,
            url=request.url,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateContainerResponse(container=entity)


class UpdateContainerRequest(BaseModel):
    """Request for updating a Container.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    system_slug: str | None = None
    description: str | None = None
    container_type: ContainerType | None = None
    technology: str | None = None
    url: str | None = None
    tags: tuple[str, ...] | None = None
    docname: str | None = None


class UpdateContainerResponse(BaseModel):
    """Response for updating a Container."""

    container: Container


class UpdateContainerUseCase(UpdateUseCase[Container, ContainerRepository]):
    """Update a Container."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateContainerRequest) -> UpdateContainerResponse:
        """Execute the update container use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateContainerResponse(container=entity)
