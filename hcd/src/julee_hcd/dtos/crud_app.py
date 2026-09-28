"""Generated CRUD messages for App.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.app import App, AppInterface, AppType


class GetAppRequest(BaseModel):
    """Request for getting a App by slug."""

    slug: str


class GetAppResponse(BaseModel):
    """Response for getting a App."""

    app: App


class ListAppsRequest(BaseModel):
    """Request for listing all Apps."""


class ListAppsResponse(BaseModel):
    """Response for listing all Apps."""

    apps: list[App]
    total_count: int


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

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateAppResponse(BaseModel):
    """Response for updating a App."""

    app: App


class DeleteAppRequest(BaseModel):
    """Request for deleting a App by slug."""

    slug: str


class DeleteAppResponse(BaseModel):
    """Response for deleting a App."""

    deleted: bool
