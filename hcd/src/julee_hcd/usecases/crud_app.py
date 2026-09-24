"""Generated CRUD use cases for App.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_hcd.domain.models.app import App, AppInterface, AppType
from julee_hcd.domain.repositories.app import AppRepository


class GetAppRequest(BaseModel):
    """Request for getting a App by slug."""

    slug: str


class GetAppResponse(BaseModel):
    """Response for getting a App."""

    app: App


class GetAppUseCase(GetUseCase[App, AppRepository]):
    """Get a App by slug."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: GetAppRequest) -> GetAppResponse:
        """Execute the get app use case."""
        entity = await self._get_by_id(request.slug)
        return GetAppResponse(app=entity)


class ListAppsRequest(BaseModel):
    """Request for listing all Apps."""


class ListAppsResponse(BaseModel):
    """Response for listing all Apps."""

    apps: list[App]
    total_count: int


class ListAppsUseCase(ListUseCase[App, AppRepository]):
    """List all Apps."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: ListAppsRequest) -> ListAppsResponse:
        """Execute the list apps use case."""
        entities = await self._list_all()
        return ListAppsResponse(apps=entities, total_count=len(entities))


class CreateAppRequest(BaseModel):
    """Request for creating a App."""

    slug: str
    name: str
    app_type: AppType = AppType.UNKNOWN
    status: str | None = None
    description: str = ""
    interface: AppInterface = AppInterface.UNKNOWN
    technology: str = ""
    accelerators: tuple[str, ...] = ()
    manifest_path: str = ""
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateAppResponse(BaseModel):
    """Response for creating a App."""

    app: App


class CreateAppUseCase(CreateUseCase[App, AppRepository]):
    """Create a new App."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> App:
        """Construct a App from a generated ID and request fields."""
        return App(slug=entity_id, **kwargs)

    async def execute(self, request: CreateAppRequest) -> CreateAppResponse:
        """Execute the create app use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            app_type=request.app_type,
            status=request.status,
            description=request.description,
            interface=request.interface,
            technology=request.technology,
            accelerators=request.accelerators,
            manifest_path=request.manifest_path,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateAppResponse(app=entity)


class UpdateAppRequest(BaseModel):
    """Request for updating a App.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    app_type: AppType | None = None
    status: str | None = None
    description: str | None = None
    interface: AppInterface | None = None
    technology: str | None = None
    accelerators: tuple[str, ...] | None = None
    manifest_path: str | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdateAppResponse(BaseModel):
    """Response for updating a App."""

    app: App


class UpdateAppUseCase(UpdateUseCase[App, AppRepository]):
    """Update a App."""

    def __init__(self, repo: AppRepository) -> None:
        """Initialise with the app repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateAppRequest) -> UpdateAppResponse:
        """Execute the update app use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateAppResponse(app=entity)


class DeleteAppRequest(BaseModel):
    """Request for deleting a App by slug."""

    slug: str


class DeleteAppResponse(BaseModel):
    """Response for deleting a App."""

    deleted: bool


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
