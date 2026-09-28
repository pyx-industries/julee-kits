"""Generated CRUD use cases for SoftwareSystem.

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

from julee_c4.domain.models.software_system import SoftwareSystem
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository

from ..dtos.crud_software_system import (
    CreateSoftwareSystemRequest,
    CreateSoftwareSystemResponse,
    DeleteSoftwareSystemRequest,
    DeleteSoftwareSystemResponse,
    GetSoftwareSystemRequest,
    GetSoftwareSystemResponse,
    ListSoftwareSystemsRequest,
    ListSoftwareSystemsResponse,
    UpdateSoftwareSystemRequest,
    UpdateSoftwareSystemResponse,
)


class GetSoftwareSystemUseCase(GetUseCase[SoftwareSystem, SoftwareSystemRepository]):
    """Get a SoftwareSystem by slug."""

    def __init__(self, repo: SoftwareSystemRepository) -> None:
        """Initialise with the software_system repository."""
        super().__init__(repo)

    async def execute(
        self, request: GetSoftwareSystemRequest
    ) -> GetSoftwareSystemResponse:
        """Execute the get software_system use case."""
        entity = await self._get_by_id(request.slug)
        return GetSoftwareSystemResponse(software_system=entity)


class ListSoftwareSystemsUseCase(ListUseCase[SoftwareSystem, SoftwareSystemRepository]):
    """List all SoftwareSystems."""

    def __init__(self, repo: SoftwareSystemRepository) -> None:
        """Initialise with the software_system repository."""
        super().__init__(repo)

    async def execute(
        self, request: ListSoftwareSystemsRequest
    ) -> ListSoftwareSystemsResponse:
        """Execute the list software_systems use case."""
        entities = await self._list_all()
        return ListSoftwareSystemsResponse(
            software_systems=entities, total_count=len(entities)
        )


class CreateSoftwareSystemUseCase(
    CreateUseCase[SoftwareSystem, SoftwareSystemRepository]
):
    """Create a new SoftwareSystem."""

    def __init__(self, repo: SoftwareSystemRepository) -> None:
        """Initialise with the software_system repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> SoftwareSystem:
        """Construct a SoftwareSystem from a generated ID and request fields."""
        return SoftwareSystem(slug=Slug(entity_id), **kwargs)

    async def execute(
        self, request: CreateSoftwareSystemRequest
    ) -> CreateSoftwareSystemResponse:
        """Execute the create software_system use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            description=request.description,
            system_type=request.system_type,
            owner=request.owner,
            technology=request.technology,
            url=request.url,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateSoftwareSystemResponse(software_system=entity)


class UpdateSoftwareSystemUseCase(
    UpdateUseCase[SoftwareSystem, SoftwareSystemRepository]
):
    """Update a SoftwareSystem."""

    def __init__(self, repo: SoftwareSystemRepository) -> None:
        """Initialise with the software_system repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateSoftwareSystemRequest
    ) -> UpdateSoftwareSystemResponse:
        """Execute the update software_system use case."""
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateSoftwareSystemResponse(software_system=entity)


class DeleteSoftwareSystemUseCase(
    DeleteUseCase[SoftwareSystem, SoftwareSystemRepository]
):
    """Delete a SoftwareSystem by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: SoftwareSystemRepository) -> None:
        """Initialise with the software_system repository."""
        super().__init__(repo)

    async def execute(
        self, request: DeleteSoftwareSystemRequest
    ) -> DeleteSoftwareSystemResponse:
        """Execute the delete software_system use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteSoftwareSystemResponse(deleted=deleted)
