"""Generated CRUD use cases for Integration.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Name, NonEmptyText, Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_hcd.domain.models.integration import (
    Direction,
    Integration,
)
from julee_hcd.domain.repositories.integration import IntegrationRepository

from ..dtos.crud_integration import (
    CreateIntegrationRequest,
    CreateIntegrationResponse,
    DeleteIntegrationRequest,
    DeleteIntegrationResponse,
    GetIntegrationRequest,
    GetIntegrationResponse,
    ListIntegrationsRequest,
    ListIntegrationsResponse,
    UpdateIntegrationRequest,
    UpdateIntegrationResponse,
)


class GetIntegrationUseCase(GetUseCase[Integration, IntegrationRepository]):
    """Get a Integration by slug."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    async def execute(self, request: GetIntegrationRequest) -> GetIntegrationResponse:
        """Execute the get integration use case."""
        entity = await self._get_by_id(request.slug)
        return GetIntegrationResponse(integration=entity)


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


class CreateIntegrationUseCase(CreateUseCase[Integration, IntegrationRepository]):
    """Create a new Integration."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Integration:
        """Construct a Integration from a generated ID and request fields."""
        return Integration(slug=Slug(entity_id), **kwargs)

    async def execute(
        self, request: CreateIntegrationRequest
    ) -> CreateIntegrationResponse:
        """Execute the create integration use case."""
        entity = await self._create(
            entity_id=request.slug,
            module=NonEmptyText(request.module),
            name=Name(request.name),
            description=request.description,
            direction=Direction(request.direction),
            depends_on=request.depends_on,
            manifest_path=request.manifest_path,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateIntegrationResponse(integration=entity)


class UpdateIntegrationUseCase(UpdateUseCase[Integration, IntegrationRepository]):
    """Update a Integration."""

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateIntegrationRequest
    ) -> UpdateIntegrationResponse:
        """Execute the update integration use case."""
        changes = request.changes()
        if changes.get("direction") is not None:
            changes["direction"] = Direction(changes["direction"])
        if changes.get("module") is not None:
            changes["module"] = NonEmptyText(changes["module"])
        if changes.get("name") is not None:
            changes["name"] = Name(changes["name"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateIntegrationResponse(integration=entity)


class DeleteIntegrationUseCase(DeleteUseCase[Integration, IntegrationRepository]):
    """Delete a Integration by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: IntegrationRepository) -> None:
        """Initialise with the integration repository."""
        super().__init__(repo)

    async def execute(
        self, request: DeleteIntegrationRequest
    ) -> DeleteIntegrationResponse:
        """Execute the delete integration use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteIntegrationResponse(deleted=deleted)
