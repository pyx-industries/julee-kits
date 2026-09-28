"""Generated CRUD messages for Relationship.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.relationship import ElementType, Relationship


class GetRelationshipRequest(BaseModel):
    """Request for getting a Relationship by slug."""

    slug: str


class GetRelationshipResponse(BaseModel):
    """Response for getting a Relationship."""

    relationship: Relationship


class ListRelationshipsRequest(BaseModel):
    """Request for listing all Relationships."""


class ListRelationshipsResponse(BaseModel):
    """Response for listing all Relationships."""

    relationships: list[Relationship]
    total_count: int


class CreateRelationshipRequest(BaseModel):
    """Request for creating a Relationship."""

    slug: str = ""
    source_type: ElementType
    source_slug: str
    destination_type: ElementType
    destination_slug: str
    description: str = "Uses"
    technology: str = ""
    tags: tuple[str, ...] = ()
    bidirectional: bool = False
    docname: str = ""


class CreateRelationshipResponse(BaseModel):
    """Response for creating a Relationship."""

    relationship: Relationship


class UpdateRelationshipRequest(BaseModel):
    """Request for updating a Relationship.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    source_type: ElementType | None = None
    source_slug: str | None = None
    destination_type: ElementType | None = None
    destination_slug: str | None = None
    description: str | None = None
    technology: str | None = None
    tags: tuple[str, ...] | None = None
    bidirectional: bool | None = None
    docname: str | None = None

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateRelationshipResponse(BaseModel):
    """Response for updating a Relationship."""

    relationship: Relationship


class DeleteRelationshipRequest(BaseModel):
    """Request for deleting a Relationship by slug."""

    slug: str


class DeleteRelationshipResponse(BaseModel):
    """Response for deleting a Relationship."""

    deleted: bool
