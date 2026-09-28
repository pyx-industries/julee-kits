"""Generated CRUD use cases for Container.

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

from julee_c4.domain.models.container import Container
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
        return GetContainerResponse(container=entity)


class ListContainersUseCase(ListUseCase[Container, ContainerRepository]):
    """List all Containers."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: ListContainersRequest) -> ListContainersResponse:
        """Execute the list containers use case."""
        entities = await self._list_all()
        return ListContainersResponse(containers=entities, total_count=len(entities))


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


class UpdateContainerUseCase(UpdateUseCase[Container, ContainerRepository]):
    """Update a Container."""

    def __init__(self, repo: ContainerRepository) -> None:
        """Initialise with the container repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateContainerRequest) -> UpdateContainerResponse:
        """Execute the update container use case."""
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateContainerResponse(container=entity)


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
