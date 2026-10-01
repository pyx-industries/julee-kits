"""Generated CRUD messages for Integration.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.integration import Direction, Integration
from julee_hcd.domain.values.external_dependency import ExternalDependency


class IntegrationMessage(BaseModel):
    """What a Integration is, as a use case reports it.

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
    module: str
    name: str
    description: str
    direction: Direction
    depends_on: tuple[ExternalDependency, ...]
    manifest_path: str

    @classmethod
    def of(cls, entity: Integration) -> "IntegrationMessage":
        """The message for one integration."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            slug=str(entity.slug),
            module=str(entity.module),
            name=str(entity.name),
            description=entity.description,
            direction=entity.direction,
            depends_on=entity.depends_on,
            manifest_path=entity.manifest_path,
        )


class GetIntegrationRequest(BaseModel):
    """Request for getting a Integration by slug."""

    slug: str


class GetIntegrationResponse(BaseModel):
    """Response for getting a Integration."""

    integration: IntegrationMessage

    @classmethod
    def of(cls, entity: Integration) -> "GetIntegrationResponse":
        """The response for the integration that was found."""
        return cls(integration=IntegrationMessage.of(entity))


class ListIntegrationsRequest(BaseModel):
    """Request for listing all Integrations."""


class ListIntegrationsResponse(BaseModel):
    """Response for listing all Integrations.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    integrations: list[IntegrationMessage]

    @classmethod
    def of(cls, entities: list[Integration]) -> "ListIntegrationsResponse":
        """The response for the integrations that were found."""
        return cls(integrations=[IntegrationMessage.of(entity) for entity in entities])


class CreateIntegrationRequest(BaseModel):
    """Request for creating a Integration."""

    slug: str
    module: str
    name: str
    description: str = ""
    direction: Direction = Direction.BIDIRECTIONAL
    depends_on: tuple[ExternalDependency, ...] = ()
    manifest_path: str = ""
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateIntegrationResponse(BaseModel):
    """Response for creating a Integration."""

    integration: IntegrationMessage

    @classmethod
    def of(cls, entity: Integration) -> "CreateIntegrationResponse":
        """The response for the integration that was created."""
        return cls(integration=IntegrationMessage.of(entity))


class UpdateIntegrationRequest(BaseModel):
    """Request for updating a Integration.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    module: str | None = None
    name: str | None = None
    description: str | None = None
    direction: Direction | None = None
    depends_on: tuple[ExternalDependency, ...] | None = None
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


class UpdateIntegrationResponse(BaseModel):
    """Response for updating a Integration."""

    integration: IntegrationMessage

    @classmethod
    def of(cls, entity: Integration) -> "UpdateIntegrationResponse":
        """The response for the integration as it now is."""
        return cls(integration=IntegrationMessage.of(entity))


class DeleteIntegrationRequest(BaseModel):
    """Request for deleting a Integration by slug."""

    slug: str


class DeleteIntegrationResponse(BaseModel):
    """Response for deleting a Integration."""

    deleted: bool
