"""Generated CRUD messages for Integration.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.integration import (
    Direction,
    ExternalDependency,
    Integration,
)


class GetIntegrationRequest(BaseModel):
    """Request for getting a Integration by slug."""

    slug: str


class GetIntegrationResponse(BaseModel):
    """Response for getting a Integration."""

    integration: Integration


class ListIntegrationsRequest(BaseModel):
    """Request for listing all Integrations."""


class ListIntegrationsResponse(BaseModel):
    """Response for listing all Integrations."""

    integrations: list[Integration]
    total_count: int


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

    integration: Integration


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
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateIntegrationResponse(BaseModel):
    """Response for updating a Integration."""

    integration: Integration


class DeleteIntegrationRequest(BaseModel):
    """Request for deleting a Integration by slug."""

    slug: str


class DeleteIntegrationResponse(BaseModel):
    """Response for deleting a Integration."""

    deleted: bool
