"""Generated CRUD use cases for Integration.

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

from julee_hcd.domain.models.integration import (
    Direction,
    ExternalDependency,
    Integration,
)
from julee_hcd.domain.repositories.integration import IntegrationRepository


class GetIntegrationRequest(BaseModel):
    """Request for getting a Integration by slug."""

    slug: str


class GetIntegrationResponse(BaseModel):
    """Response for getting a Integration."""

    integration: Integration


class GetIntegrationUseCase(GetUseCase[Integration, IntegrationRepository]):
    """Get a Integration by slug."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    async def execute(self, request: GetIntegrationRequest) -> GetIntegrationResponse:
        """Execute the get integration use case."""
        entity = await self._get_by_id(request.slug)
        return GetIntegrationResponse(integration=entity)


class ListIntegrationsRequest(BaseModel):
    """Request for listing all Integrations."""


class ListIntegrationsResponse(BaseModel):
    """Response for listing all Integrations."""

    integrations: list[Integration]
    total_count: int


class ListIntegrationsUseCase(ListUseCase[Integration, IntegrationRepository]):
    """List all Integrations."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    async def execute(
        self, request: ListIntegrationsRequest
    ) -> ListIntegrationsResponse:
        """Execute the list integrations use case."""
        entities = await self._list_all()
        return ListIntegrationsResponse(
            integrations=entities, total_count=len(entities)
        )


class CreateIntegrationRequest(BaseModel):
    """Request for creating a Integration."""

    slug: str
    module: str
    name: str
    description: str = ""
    direction: Direction = Direction.BIDIRECTIONAL
    depends_on: tuple[ExternalDependency, ...] = ()
    manifest_path: str = ""
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateIntegrationResponse(BaseModel):
    """Response for creating a Integration."""

    integration: Integration


class CreateIntegrationUseCase(CreateUseCase[Integration, IntegrationRepository]):
    """Create a new Integration."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Integration:
        """Construct a Integration from a generated ID and request fields."""
        return Integration(slug=entity_id, **kwargs)

    async def execute(
        self, request: CreateIntegrationRequest
    ) -> CreateIntegrationResponse:
        """Execute the create integration use case."""
        entity = await self._create(
            entity_id=request.slug,
            module=request.module,
            name=request.name,
            description=request.description,
            direction=request.direction,
            depends_on=request.depends_on,
            manifest_path=request.manifest_path,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateIntegrationResponse(integration=entity)


class UpdateIntegrationRequest(BaseModel):
    """Request for updating a Integration.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    module: str | None = None
    name: str | None = None
    description: str | None = None
    direction: Direction | None = None
    depends_on: tuple[ExternalDependency, ...] | None = None
    manifest_path: str | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdateIntegrationResponse(BaseModel):
    """Response for updating a Integration."""

    integration: Integration


class UpdateIntegrationUseCase(UpdateUseCase[Integration, IntegrationRepository]):
    """Update a Integration."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateIntegrationRequest
    ) -> UpdateIntegrationResponse:
        """Execute the update integration use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateIntegrationResponse(integration=entity)
