"""Generated CRUD messages for Container.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.container import Container, ContainerType


class ContainerMessage(BaseModel):
    """What a Container is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    slug: str
    name: str
    system_slug: str
    description: str
    container_type: ContainerType
    technology: str
    url: str
    tags: tuple[str, ...]
    docname: str

    @classmethod
    def of(cls, entity: Container) -> "ContainerMessage":
        """The message for one container."""
        return cls(
            slug=str(entity.slug),
            name=str(entity.name),
            system_slug=str(entity.system_slug),
            description=entity.description,
            container_type=entity.container_type,
            technology=entity.technology,
            url=entity.url,
            tags=entity.tags,
            docname=entity.docname,
        )


class GetContainerRequest(BaseModel):
    """Request for getting a Container by slug."""

    slug: str


class GetContainerResponse(BaseModel):
    """Response for getting a Container."""

    container: ContainerMessage

    @classmethod
    def of(cls, entity: Container) -> "GetContainerResponse":
        """The response for the container that was found."""
        return cls(container=ContainerMessage.of(entity))


class ListContainersRequest(BaseModel):
    """Request for listing all Containers."""


class ListContainersResponse(BaseModel):
    """Response for listing all Containers.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    containers: list[ContainerMessage]

    @classmethod
    def of(cls, entities: list[Container]) -> "ListContainersResponse":
        """The response for the containers that were found."""
        return cls(containers=[ContainerMessage.of(entity) for entity in entities])


class CreateContainerRequest(BaseModel):
    """Request for creating a Container."""

    slug: str
    name: str
    system_slug: str
    description: str = ""
    container_type: ContainerType = ContainerType.OTHER
    technology: str = ""
    url: str = ""
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateContainerResponse(BaseModel):
    """Response for creating a Container."""

    container: ContainerMessage

    @classmethod
    def of(cls, entity: Container) -> "CreateContainerResponse":
        """The response for the container that was created."""
        return cls(container=ContainerMessage.of(entity))


class UpdateContainerRequest(BaseModel):
    """Request for updating a Container.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    system_slug: str | None = None
    description: str | None = None
    container_type: ContainerType | None = None
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


class UpdateContainerResponse(BaseModel):
    """Response for updating a Container."""

    container: ContainerMessage

    @classmethod
    def of(cls, entity: Container) -> "UpdateContainerResponse":
        """The response for the container as it now is."""
        return cls(container=ContainerMessage.of(entity))


class DeleteContainerRequest(BaseModel):
    """Request for deleting a Container by slug."""

    slug: str


class DeleteContainerResponse(BaseModel):
    """Response for deleting a Container."""

    deleted: bool
