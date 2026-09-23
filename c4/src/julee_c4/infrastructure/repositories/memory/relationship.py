"""In-memory Relationship repository implementation."""

import logging

from julee.repositories.memory import MemoryRepositoryMixin

from julee_c4.domain.models.relationship import ElementType, Relationship
from julee_c4.domain.repositories.relationship import RelationshipRepository

logger = logging.getLogger(__name__)


class MemoryRelationshipRepository(
    MemoryRepositoryMixin[Relationship], RelationshipRepository
):
    """In-memory implementation of RelationshipRepository.

    Stores relationships in a dictionary keyed by slug.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self.storage_dict: dict[str, Relationship] = {}
        self.logger = logger
        self.entity_name = "Relationship"
        self.id_field = "slug"

    # -------------------------------------------------------------------------
    # BaseRepository implementation (delegating to protected helpers)
    # -------------------------------------------------------------------------

    async def get(self, entity_id: str) -> Relationship | None:
        """Get a relationship by slug."""
        return self.get_entity(entity_id)

    async def get_many(self, entity_ids: list[str]) -> dict[str, Relationship | None]:
        """Get multiple relationships by slug."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: Relationship) -> None:
        """Save a relationship."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[Relationship]:
        """List all relationships."""
        return list(self.storage_dict.values())

    async def delete(self, entity_id: str) -> bool:
        """Delete a relationship by slug."""
        return self.storage_dict.pop(entity_id, None) is not None

    async def clear(self) -> None:
        """Clear all relationships."""
        self.storage_dict.clear()

    # -------------------------------------------------------------------------
    # RelationshipRepository-specific queries
    # -------------------------------------------------------------------------

    async def get_for_element(
        self,
        element_type: ElementType,
        element_slug: str,
    ) -> list[Relationship]:
        """Get all relationships involving an element."""
        return [
            r
            for r in self.storage_dict.values()
            if r.involves_element(element_type, element_slug)
        ]

    async def get_outgoing(
        self,
        element_type: ElementType,
        element_slug: str,
    ) -> list[Relationship]:
        """Get relationships where element is the source."""
        return [
            r
            for r in self.storage_dict.values()
            if r.source_type == element_type and r.source_slug == element_slug
        ]

    async def get_incoming(
        self,
        element_type: ElementType,
        element_slug: str,
    ) -> list[Relationship]:
        """Get relationships where element is the destination."""
        return [
            r
            for r in self.storage_dict.values()
            if r.destination_type == element_type and r.destination_slug == element_slug
        ]

    async def get_person_relationships(self) -> list[Relationship]:
        """Get all relationships involving persons."""
        return [r for r in self.storage_dict.values() if r.is_person_relationship]

    async def get_cross_system_relationships(self) -> list[Relationship]:
        """Get relationships between different systems."""
        return [r for r in self.storage_dict.values() if r.is_cross_system]

    async def get_between_containers(self, system_slug: str) -> list[Relationship]:
        """Get relationships between containers within a system.

        Note: This requires knowing which containers belong to the system.
        For simplicity, we filter relationships where both source and destination
        are containers. The caller should ensure containers are from the same system.
        """
        return [
            r
            for r in self.storage_dict.values()
            if r.source_type == ElementType.CONTAINER
            and r.destination_type == ElementType.CONTAINER
        ]

    async def get_between_components(self, container_slug: str) -> list[Relationship]:
        """Get relationships between components within a container.

        Note: Similar to get_between_containers, we return component-to-component
        relationships. The caller should filter by container context.
        """
        return [
            r
            for r in self.storage_dict.values()
            if r.source_type == ElementType.COMPONENT
            and r.destination_type == ElementType.COMPONENT
        ]

    async def get_by_docname(self, docname: str) -> list[Relationship]:
        """Get relationships defined in a specific document."""
        return [r for r in self.storage_dict.values() if r.docname == docname]

    async def clear_by_docname(self, docname: str) -> int:
        """Clear relationships defined in a specific document."""
        to_remove = [
            slug for slug, r in self.storage_dict.items() if r.docname == docname
        ]
        for slug in to_remove:
            del self.storage_dict[slug]
        return len(to_remove)
