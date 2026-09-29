"""Generated CRUD use cases for Container.

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

from julee_c4.domain.models.container import Container, ContainerType
from julee_c4.domain.repositories.container import ContainerRepository

from ..dtos.crud_container import (
    CreateContainerRequest,
    CreateContainerResponse,
    DeleteContainerRequest,
    DeleteContainerResponse,
    GetContainerRequest,
    GetContainerResponse,
    ListContainersRequest,
    ListContainersResponse,
    UpdateContainerRequest,
    UpdateContainerResponse,
)


class GetContainerUseCase(GetUseCase[Container, ContainerRepository]):
    """Get a Container by slug."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: GetContainerRequest) -> GetContainerResponse:
        """Execute the get container use case."""
        entity = await self._get_by_id(request.slug)
        return GetContainerResponse.of(entity)


class ListContainersUseCase(ListUseCase[Container, ContainerRepository]):
    """List all Containers."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: ListContainersRequest) -> ListContainersResponse:
        """Execute the list containers use case."""
        entities = await self._list_all()
        return ListContainersResponse.of(entities)


class CreateContainerUseCase(CreateUseCase[Container, ContainerRepository]):
    """Create a new Container."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Container:
        """Construct a Container from a generated ID and request fields."""
        return Container(slug=Slug(entity_id), **kwargs)

    async def execute(self, request: CreateContainerRequest) -> CreateContainerResponse:
        """Execute the create container use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=Name(request.name),
            system_slug=Slug(request.system_slug),
            description=request.description,
            container_type=ContainerType(request.container_type),
            technology=request.technology,
            url=request.url,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateContainerResponse.of(entity)


class UpdateContainerUseCase(UpdateUseCase[Container, ContainerRepository]):
    """Update a Container."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateContainerRequest) -> UpdateContainerResponse:
        """Execute the update container use case."""
        changes = request.changes()
        if changes.get("container_type") is not None:
            changes["container_type"] = ContainerType(changes["container_type"])
        if changes.get("name") is not None:
            changes["name"] = Name(changes["name"])
        if changes.get("system_slug") is not None:
            changes["system_slug"] = Slug(changes["system_slug"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateContainerResponse.of(entity)


class DeleteContainerUseCase(DeleteUseCase[Container, ContainerRepository]):
    """Delete a Container by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: DeleteContainerRequest) -> DeleteContainerResponse:
        """Execute the delete container use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteContainerResponse(deleted=deleted)
