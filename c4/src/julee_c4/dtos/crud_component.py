"""Generated CRUD messages for Component.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.component import Component


class GetComponentRequest(BaseModel):
    """Request for getting a Component by slug."""

    slug: str


class GetComponentResponse(BaseModel):
    """Response for getting a Component."""

    component: Component


class ListComponentsRequest(BaseModel):
    """Request for listing all Components."""


class ListComponentsResponse(BaseModel):
    """Response for listing all Components."""

    components: list[Component]
    total_count: int


class CreateComponentRequest(BaseModel):
    """Request for creating a Component."""

    slug: str
    name: str
    container_slug: str
    system_slug: str
    description: str = ""
    technology: str = ""
    interface: str = ""
    code_path: str = ""
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateComponentResponse(BaseModel):
    """Response for creating a Component."""

    component: Component


class UpdateComponentRequest(BaseModel):
    """Request for updating a Component.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    container_slug: str | None = None
    system_slug: str | None = None
    description: str | None = None
    technology: str | None = None
    interface: str | None = None
    code_path: str | None = None
    tags: tuple[str, ...] | None = None
    docname: str | None = None

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateComponentResponse(BaseModel):
    """Response for updating a Component."""

    component: Component


class DeleteComponentRequest(BaseModel):
    """Request for deleting a Component by slug."""

    slug: str


class DeleteComponentResponse(BaseModel):
    """Response for deleting a Component."""

    deleted: bool
