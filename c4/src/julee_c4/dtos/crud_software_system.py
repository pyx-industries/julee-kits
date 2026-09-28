"""Generated CRUD messages for SoftwareSystem.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.software_system import SoftwareSystem, SystemType


class GetSoftwareSystemRequest(BaseModel):
    """Request for getting a SoftwareSystem by slug."""

    slug: str


class GetSoftwareSystemResponse(BaseModel):
    """Response for getting a SoftwareSystem."""

    software_system: SoftwareSystem


class ListSoftwareSystemsRequest(BaseModel):
    """Request for listing all SoftwareSystems."""


class ListSoftwareSystemsResponse(BaseModel):
    """Response for listing all SoftwareSystems."""

    software_systems: list[SoftwareSystem]
    total_count: int


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

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateSoftwareSystemResponse(BaseModel):
    """Response for updating a SoftwareSystem."""

    software_system: SoftwareSystem


class DeleteSoftwareSystemRequest(BaseModel):
    """Request for deleting a SoftwareSystem by slug."""

    slug: str


class DeleteSoftwareSystemResponse(BaseModel):
    """Response for deleting a SoftwareSystem."""

    deleted: bool
