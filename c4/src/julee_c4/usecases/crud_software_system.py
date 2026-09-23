"""Generated CRUD use cases for SoftwareSystem.

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

from julee_c4.domain.models.software_system import SoftwareSystem, SystemType
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository


class GetSoftwareSystemRequest(BaseModel):
    """Request for getting a SoftwareSystem by slug."""

    slug: str


class GetSoftwareSystemResponse(BaseModel):
    """Response for getting a SoftwareSystem."""

    software_system: SoftwareSystem


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


class ListSoftwareSystemsRequest(BaseModel):
    """Request for listing all SoftwareSystems."""


class ListSoftwareSystemsResponse(BaseModel):
    """Response for listing all SoftwareSystems."""

    software_systems: list[SoftwareSystem]
    total_count: int


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


class CreateSoftwareSystemRequest(BaseModel):
    """Request for creating a SoftwareSystem."""

    slug: str
    name: str
    description: str = ""
    system_type: SystemType = SystemType.INTERNAL
    owner: str = ""
    technology: str = ""
    url: str = ""
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateSoftwareSystemResponse(BaseModel):
    """Response for creating a SoftwareSystem."""

    software_system: SoftwareSystem


class CreateSoftwareSystemUseCase(
    CreateUseCase[SoftwareSystem, SoftwareSystemRepository]
):
    """Create a new SoftwareSystem."""

    def __init__(self, repo: SoftwareSystemRepository) -> None:
        """Initialise with the software_system repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> SoftwareSystem:
        """Construct a SoftwareSystem from a generated ID and request fields."""
        return SoftwareSystem(slug=entity_id, **kwargs)

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


class UpdateSoftwareSystemRequest(BaseModel):
    """Request for updating a SoftwareSystem.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    description: str | None = None
    system_type: SystemType | None = None
    owner: str | None = None
    technology: str | None = None
    url: str | None = None
    tags: tuple[str, ...] | None = None
    docname: str | None = None


class UpdateSoftwareSystemResponse(BaseModel):
    """Response for updating a SoftwareSystem."""

    software_system: SoftwareSystem


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
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateSoftwareSystemResponse(software_system=entity)
