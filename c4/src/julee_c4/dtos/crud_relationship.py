"""Generated CRUD messages for Relationship.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.relationship import ElementType, Relationship


class RelationshipMessage(BaseModel):
    """What a Relationship is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    source_type: ElementType
    source_slug: str
    destination_type: ElementType
    destination_slug: str
    description: str
    technology: str
    tags: tuple[str, ...]
    bidirectional: bool
    docname: str
    slug: str

    @classmethod
    def of(cls, entity: Relationship) -> "RelationshipMessage":
        """The message for one relationship."""
        return cls(
            source_type=entity.source_type,
            source_slug=str(entity.source_slug),
            destination_type=entity.destination_type,
            destination_slug=str(entity.destination_slug),
            description=entity.description,
            technology=entity.technology,
            tags=entity.tags,
            bidirectional=entity.bidirectional,
            docname=entity.docname,
            slug=str(entity.slug),
        )


class GetRelationshipRequest(BaseModel):
    """Request for getting a Relationship by slug."""

    slug: str


class GetRelationshipResponse(BaseModel):
    """Response for getting a Relationship."""

    relationship: RelationshipMessage

    @classmethod
    def of(cls, entity: Relationship) -> "GetRelationshipResponse":
        """The response for the relationship that was found."""
        return cls(relationship=RelationshipMessage.of(entity))


class ListRelationshipsRequest(BaseModel):
    """Request for listing all Relationships."""


class ListRelationshipsResponse(BaseModel):
    """Response for listing all Relationships.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    relationships: list[RelationshipMessage]

    @classmethod
    def of(cls, entities: list[Relationship]) -> "ListRelationshipsResponse":
        """The response for the relationships that were found."""
        return cls(
            relationships=[RelationshipMessage.of(entity) for entity in entities]
        )


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

    relationship: RelationshipMessage

    @classmethod
    def of(cls, entity: Relationship) -> "CreateRelationshipResponse":
        """The response for the relationship that was created."""
        return cls(relationship=RelationshipMessage.of(entity))


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
        return {
            name: getattr(self, name)
            for name in self.model_fields_set
            if name != "slug"
        }


class UpdateRelationshipResponse(BaseModel):
    """Response for updating a Relationship."""

    relationship: RelationshipMessage

    @classmethod
    def of(cls, entity: Relationship) -> "UpdateRelationshipResponse":
        """The response for the relationship as it now is."""
        return cls(relationship=RelationshipMessage.of(entity))


class DeleteRelationshipRequest(BaseModel):
    """Request for deleting a Relationship by slug."""

    slug: str


class DeleteRelationshipResponse(BaseModel):
    """Response for deleting a Relationship."""

    deleted: bool
