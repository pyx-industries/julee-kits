"""Generated CRUD use cases for App.

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

from julee_hcd.domain.models.app import App, AppInterface, AppType
from julee_hcd.domain.repositories.app import AppRepository

from ..dtos.crud_app import (
    CreateAppRequest,
    CreateAppResponse,
    DeleteAppRequest,
    DeleteAppResponse,
    GetAppRequest,
    GetAppResponse,
    ListAppsRequest,
    ListAppsResponse,
    UpdateAppRequest,
    UpdateAppResponse,
)


class GetAppUseCase(GetUseCase[App, AppRepository]):
    """Get a App by slug."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: GetAppRequest) -> GetAppResponse:
        """Execute the get app use case."""
        entity = await self._get_by_id(request.slug)
        return GetAppResponse.of(entity)


class ListAppsUseCase(ListUseCase[App, AppRepository]):
    """List all Apps."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: ListAppsRequest) -> ListAppsResponse:
        """Execute the list apps use case."""
        entities = await self._list_all()
        return ListAppsResponse.of(entities)


class CreateAppUseCase(CreateUseCase[App, AppRepository]):
    """Create a new App."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> App:
        """Construct a App from a generated ID and request fields."""
        return App(slug=Slug(entity_id), **kwargs)

    async def execute(self, request: CreateAppRequest) -> CreateAppResponse:
        """Execute the create app use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=Name(request.name),
            app_type=AppType(request.app_type),
            status=request.status,
            description=request.description,
            interface=AppInterface(request.interface),
            technology=request.technology,
            accelerators=request.accelerators,
            manifest_path=request.manifest_path,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateAppResponse.of(entity)


class UpdateAppUseCase(UpdateUseCase[App, AppRepository]):
    """Update a App."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateAppRequest) -> UpdateAppResponse:
        """Execute the update app use case."""
        changes = request.changes()
        if changes.get("app_type") is not None:
            changes["app_type"] = AppType(changes["app_type"])
        if changes.get("interface") is not None:
            changes["interface"] = AppInterface(changes["interface"])
        if changes.get("name") is not None:
            changes["name"] = Name(changes["name"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateAppResponse.of(entity)


class DeleteAppUseCase(DeleteUseCase[App, AppRepository]):
    """Delete a App by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: DeleteAppRequest) -> DeleteAppResponse:
        """Execute the delete app use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteAppResponse(deleted=deleted)
