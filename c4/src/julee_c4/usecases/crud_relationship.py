"""Generated CRUD use cases for Relationship.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_c4.domain.models.relationship import Relationship
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
        return GetRelationshipResponse(relationship=entity)


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


class UpdateRelationshipUseCase(UpdateUseCase[Relationship, RelationshipRepository]):
    """Update a Relationship."""

    def __init__(self, repo: RelationshipRepository) -> None:
        """Initialise with the relationship repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateRelationshipRequest
    ) -> UpdateRelationshipResponse:
        """Execute the update relationship use case."""
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateRelationshipResponse(relationship=entity)


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
