"""Generated CRUD use cases for Relationship.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_c4.domain.models.relationship import ElementType, Relationship
from julee_c4.domain.repositories.relationship import RelationshipRepository


class GetRelationshipRequest(BaseModel):
    """Request for getting a Relationship by slug."""

    slug: str


class GetRelationshipResponse(BaseModel):
    """Response for getting a Relationship."""

    relationship: Relationship


class GetRelationshipUseCase(GetUseCase[Relationship, RelationshipRepository]):
    """Get a Relationship by slug."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(self, request: GetRelationshipRequest) -> GetRelationshipResponse:
        """Execute the get relationship use case."""
        entity = await self._get_by_id(request.slug)
        return GetRelationshipResponse(relationship=entity)


class ListRelationshipsRequest(BaseModel):
    """Request for listing all Relationships."""


class ListRelationshipsResponse(BaseModel):
    """Response for listing all Relationships."""

    relationships: list[Relationship]
    total_count: int


class ListRelationshipsUseCase(ListUseCase[Relationship, RelationshipRepository]):
    """List all Relationships."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(
        self, request: ListRelationshipsRequest
    ) -> ListRelationshipsResponse:
        """Execute the list relationships use case."""
        entities = await self._list_all()
        return ListRelationshipsResponse(
            relationships=entities, total_count=len(entities)
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

    relationship: Relationship


class CreateRelationshipUseCase(CreateUseCase[Relationship, RelationshipRepository]):
    """Create a new Relationship."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Relationship:
        """Construct a Relationship from a generated ID and request fields."""
        return Relationship(slug=entity_id, **kwargs)

    async def execute(
        self, request: CreateRelationshipRequest
    ) -> CreateRelationshipResponse:
        """Execute the create relationship use case."""
        entity = await self._create(
            entity_id=request.slug,
            source_type=request.source_type,
            source_slug=request.source_slug,
            destination_type=request.destination_type,
            destination_slug=request.destination_slug,
            description=request.description,
            technology=request.technology,
            tags=request.tags,
            bidirectional=request.bidirectional,
            docname=request.docname,
        )
        return CreateRelationshipResponse(relationship=entity)


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


class UpdateRelationshipResponse(BaseModel):
    """Response for updating a Relationship."""

    relationship: Relationship


class UpdateRelationshipUseCase(UpdateUseCase[Relationship, RelationshipRepository]):
    """Update a Relationship."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateRelationshipRequest
    ) -> UpdateRelationshipResponse:
        """Execute the update relationship use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateRelationshipResponse(relationship=entity)


class DeleteRelationshipRequest(BaseModel):
    """Request for deleting a Relationship by slug."""

    slug: str


class DeleteRelationshipResponse(BaseModel):
    """Response for deleting a Relationship."""

    deleted: bool


class DeleteRelationshipUseCase(DeleteUseCase[Relationship, RelationshipRepository]):
    """Delete a Relationship by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(
        self, request: DeleteRelationshipRequest
    ) -> DeleteRelationshipResponse:
        """Execute the delete relationship use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteRelationshipResponse(deleted=deleted)
