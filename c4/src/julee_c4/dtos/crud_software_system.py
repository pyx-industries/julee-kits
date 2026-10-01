"""Generated CRUD messages for SoftwareSystem.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.software_system import SoftwareSystem, SystemType


class SoftwareSystemMessage(BaseModel):
    """What a SoftwareSystem is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    slug: str
    name: str
    description: str
    system_type: SystemType
    owner: str
    technology: str
    url: str
    tags: tuple[str, ...]
    docname: str

    @classmethod
    def of(cls, entity: SoftwareSystem) -> "SoftwareSystemMessage":
        """The message for one software_system."""
        return cls(
            slug=str(entity.slug),
            name=str(entity.name),
            description=entity.description,
            system_type=entity.system_type,
            owner=entity.owner,
            technology=entity.technology,
            url=entity.url,
            tags=entity.tags,
            docname=entity.docname,
        )


class GetSoftwareSystemRequest(BaseModel):
    """Request for getting a SoftwareSystem by slug."""

    slug: str


class GetSoftwareSystemResponse(BaseModel):
    """Response for getting a SoftwareSystem."""

    software_system: SoftwareSystemMessage

    @classmethod
    def of(cls, entity: SoftwareSystem) -> "GetSoftwareSystemResponse":
        """The response for the software_system that was found."""
        return cls(software_system=SoftwareSystemMessage.of(entity))


class ListSoftwareSystemsRequest(BaseModel):
    """Request for listing all SoftwareSystems."""


class ListSoftwareSystemsResponse(BaseModel):
    """Response for listing all SoftwareSystems.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    software_systems: list[SoftwareSystemMessage]

    @classmethod
    def of(cls, entities: list[SoftwareSystem]) -> "ListSoftwareSystemsResponse":
        """The response for the software_systems that were found."""
        return cls(
            software_systems=[SoftwareSystemMessage.of(entity) for entity in entities]
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

    software_system: SoftwareSystemMessage

    @classmethod
    def of(cls, entity: SoftwareSystem) -> "CreateSoftwareSystemResponse":
        """The response for the software_system that was created."""
        return cls(software_system=SoftwareSystemMessage.of(entity))


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
        return {
            name: getattr(self, name)
            for name in self.model_fields_set
            if name != "slug"
        }


class UpdateSoftwareSystemResponse(BaseModel):
    """Response for updating a SoftwareSystem."""

    software_system: SoftwareSystemMessage

    @classmethod
    def of(cls, entity: SoftwareSystem) -> "UpdateSoftwareSystemResponse":
        """The response for the software_system as it now is."""
        return cls(software_system=SoftwareSystemMessage.of(entity))


class DeleteSoftwareSystemRequest(BaseModel):
    """Request for deleting a SoftwareSystem by slug."""

    slug: str


class DeleteSoftwareSystemResponse(BaseModel):
    """Response for deleting a SoftwareSystem."""

    deleted: bool
