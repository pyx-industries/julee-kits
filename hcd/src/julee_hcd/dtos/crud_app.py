"""Generated CRUD messages for App.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.app import App, AppInterface, AppType


class AppMessage(BaseModel):
    """What a App is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    solution_slug: str
    docname: str
    page_title: str
    preamble_rst: str
    epilogue_rst: str
    slug: str
    name: str
    app_type: AppType
    status: str | None
    description: str
    interface: AppInterface
    technology: str
    accelerators: tuple[str, ...]
    manifest_path: str

    @classmethod
    def of(cls, entity: App) -> "AppMessage":
        """The message for one app."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            slug=str(entity.slug),
            name=str(entity.name),
            app_type=entity.app_type,
            status=entity.status,
            description=entity.description,
            interface=entity.interface,
            technology=entity.technology,
            accelerators=entity.accelerators,
            manifest_path=entity.manifest_path,
        )


class GetAppRequest(BaseModel):
    """Request for getting a App by slug."""

    slug: str


class GetAppResponse(BaseModel):
    """Response for getting a App."""

    app: AppMessage

    @classmethod
    def of(cls, entity: App) -> "GetAppResponse":
        """The response for the app that was found."""
        return cls(app=AppMessage.of(entity))


class ListAppsRequest(BaseModel):
    """Request for listing all Apps."""


class ListAppsResponse(BaseModel):
    """Response for listing all Apps.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    apps: list[AppMessage]

    @classmethod
    def of(cls, entities: list[App]) -> "ListAppsResponse":
        """The response for the apps that were found."""
        return cls(apps=[AppMessage.of(entity) for entity in entities])


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

    app: AppMessage

    @classmethod
    def of(cls, entity: App) -> "CreateAppResponse":
        """The response for the app that was created."""
        return cls(app=AppMessage.of(entity))


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
        return {
            name: getattr(self, name)
            for name in self.model_fields_set
            if name != "slug"
        }


class UpdateAppResponse(BaseModel):
    """Response for updating a App."""

    app: AppMessage

    @classmethod
    def of(cls, entity: App) -> "UpdateAppResponse":
        """The response for the app as it now is."""
        return cls(app=AppMessage.of(entity))


class DeleteAppRequest(BaseModel):
    """Request for deleting a App by slug."""

    slug: str


class DeleteAppResponse(BaseModel):
    """Response for deleting a App."""

    deleted: bool
