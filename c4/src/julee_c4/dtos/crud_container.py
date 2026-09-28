"""Generated CRUD messages for Container.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.container import Container, ContainerType


class GetContainerRequest(BaseModel):
    """Request for getting a Container by slug."""

    slug: str


class GetContainerResponse(BaseModel):
    """Response for getting a Container."""

    container: Container


class ListContainersRequest(BaseModel):
    """Request for listing all Containers."""


class ListContainersResponse(BaseModel):
    """Response for listing all Containers."""

    containers: list[Container]
    total_count: int


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

    container: Container


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

    container: Container


class DeleteContainerRequest(BaseModel):
    """Request for deleting a Container by slug."""

    slug: str


class DeleteContainerResponse(BaseModel):
    """Response for deleting a Container."""

    deleted: bool
