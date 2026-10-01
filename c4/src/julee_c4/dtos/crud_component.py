"""Generated CRUD messages for Component.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.component import Component


class ComponentMessage(BaseModel):
    """What a Component is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    slug: str
    name: str
    container_slug: str
    system_slug: str
    description: str
    technology: str
    interface: str
    code_path: str
    tags: tuple[str, ...]
    docname: str

    @classmethod
    def of(cls, entity: Component) -> "ComponentMessage":
        """The message for one component."""
        return cls(
            slug=str(entity.slug),
            name=str(entity.name),
            container_slug=str(entity.container_slug),
            system_slug=str(entity.system_slug),
            description=entity.description,
            technology=entity.technology,
            interface=entity.interface,
            code_path=entity.code_path,
            tags=entity.tags,
            docname=entity.docname,
        )


class GetComponentRequest(BaseModel):
    """Request for getting a Component by slug."""

    slug: str


class GetComponentResponse(BaseModel):
    """Response for getting a Component."""

    component: ComponentMessage

    @classmethod
    def of(cls, entity: Component) -> "GetComponentResponse":
        """The response for the component that was found."""
        return cls(component=ComponentMessage.of(entity))


class ListComponentsRequest(BaseModel):
    """Request for listing all Components."""


class ListComponentsResponse(BaseModel):
    """Response for listing all Components.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    components: list[ComponentMessage]

    @classmethod
    def of(cls, entities: list[Component]) -> "ListComponentsResponse":
        """The response for the components that were found."""
        return cls(components=[ComponentMessage.of(entity) for entity in entities])


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

    component: ComponentMessage

    @classmethod
    def of(cls, entity: Component) -> "CreateComponentResponse":
        """The response for the component that was created."""
        return cls(component=ComponentMessage.of(entity))


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
        return {
            name: getattr(self, name)
            for name in self.model_fields_set
            if name != "slug"
        }


class UpdateComponentResponse(BaseModel):
    """Response for updating a Component."""

    component: ComponentMessage

    @classmethod
    def of(cls, entity: Component) -> "UpdateComponentResponse":
        """The response for the component as it now is."""
        return cls(component=ComponentMessage.of(entity))


class DeleteComponentRequest(BaseModel):
    """Request for deleting a Component by slug."""

    slug: str


class DeleteComponentResponse(BaseModel):
    """Response for deleting a Component."""

    deleted: bool
