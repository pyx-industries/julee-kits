"""Generated CRUD use cases for Relationship.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from julee.core.values.text import Slug

from julee_c4.domain.models.relationship import ElementType, Relationship
from julee_c4.domain.repositories.relationship import RelationshipRepository

from ..dtos.crud_relationship import (
    CreateRelationshipRequest,
    CreateRelationshipResponse,
    DeleteRelationshipRequest,
    DeleteRelationshipResponse,
    GetRelationshipRequest,
    GetRelationshipResponse,
    ListRelationshipsRequest,
    ListRelationshipsResponse,
    UpdateRelationshipRequest,
    UpdateRelationshipResponse,
)


class GetRelationshipUseCase(GetUseCase[Relationship, RelationshipRepository]):
    """Get a Relationship by slug."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(self, request: GetRelationshipRequest) -> GetRelationshipResponse:
        """Execute the get relationship use case."""
        entity = await self._get_by_id(request.slug)
        return GetRelationshipResponse.of(entity)


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
        return ListRelationshipsResponse.of(entities)


class CreateRelationshipUseCase(CreateUseCase[Relationship, RelationshipRepository]):
    """Create a new Relationship."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Relationship:
        """Construct a Relationship from a generated ID and request fields.

        A request that names no slug leaves the entity to work
        one out, so the field is left out rather than passed empty.
        """
        if not entity_id:
            return Relationship(**kwargs)

        return Relationship(slug=Slug(entity_id), **kwargs)

    async def execute(
        self, request: CreateRelationshipRequest
    ) -> CreateRelationshipResponse:
        """Execute the create relationship use case."""
        entity = await self._create(
            entity_id=request.slug,
            source_type=ElementType(request.source_type),
            source_slug=Slug(request.source_slug),
            destination_type=ElementType(request.destination_type),
            destination_slug=Slug(request.destination_slug),
            description=request.description,
            technology=request.technology,
            tags=request.tags,
            bidirectional=request.bidirectional,
            docname=request.docname,
        )
        return CreateRelationshipResponse.of(entity)


class UpdateRelationshipUseCase(UpdateUseCase[Relationship, RelationshipRepository]):
    """Update a Relationship."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateRelationshipRequest
    ) -> UpdateRelationshipResponse:
        """Execute the update relationship use case."""
        changes = request.changes()
        if changes.get("destination_slug") is not None:
            changes["destination_slug"] = Slug(changes["destination_slug"])
        if changes.get("destination_type") is not None:
            changes["destination_type"] = ElementType(changes["destination_type"])
        if changes.get("source_slug") is not None:
            changes["source_slug"] = Slug(changes["source_slug"])
        if changes.get("source_type") is not None:
            changes["source_type"] = ElementType(changes["source_type"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateRelationshipResponse.of(entity)


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
