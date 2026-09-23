"""In-memory Component repository implementation."""

import logging

from julee.repositories.memory import MemoryRepositoryMixin

from julee_c4.domain.models.component import Component
from julee_c4.domain.repositories.component import ComponentRepository

logger = logging.getLogger(__name__)


class MemoryComponentRepository(MemoryRepositoryMixin[Component], ComponentRepository):
    """In-memory implementation of ComponentRepository.

    Stores components in a dictionary keyed by slug.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self.storage_dict: dict[str, Component] = {}
        self.logger = logger
        self.entity_name = "Component"
        self.id_field = "slug"

    # -------------------------------------------------------------------------
    # BaseRepository implementation (delegating to protected helpers)
    # -------------------------------------------------------------------------

    async def get(self, entity_id: str) -> Component | None:
        """Get a component by slug."""
        return self.get_entity(entity_id)

    async def get_many(self, entity_ids: list[str]) -> dict[str, Component | None]:
        """Get multiple components by slug."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: Component) -> None:
        """Save a component."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[Component]:
        """List all components."""
        return list(self.storage_dict.values())

    async def delete(self, entity_id: str) -> bool:
        """Delete a component by slug."""
        return self.storage_dict.pop(entity_id, None) is not None

    async def clear(self) -> None:
        """Clear all components."""
        self.storage_dict.clear()

    # -------------------------------------------------------------------------
    # ComponentRepository-specific queries
    # -------------------------------------------------------------------------

    async def get_by_container(self, container_slug: str) -> list[Component]:
        """Get all components within a container."""
        return [
            c for c in self.storage_dict.values() if c.container_slug == container_slug
        ]

    async def get_by_system(self, system_slug: str) -> list[Component]:
        """Get all components within a software system."""
        return [c for c in self.storage_dict.values() if c.system_slug == system_slug]

    async def get_with_code(self) -> list[Component]:
        """Get components that have linked code paths."""
        return [c for c in self.storage_dict.values() if c.has_code]

    async def get_by_tag(self, tag: str) -> list[Component]:
        """Get components with a specific tag."""
        return [c for c in self.storage_dict.values() if c.has_tag(tag)]

    async def get_by_docname(self, docname: str) -> list[Component]:
        """Get components defined in a specific document."""
        return [c for c in self.storage_dict.values() if c.docname == docname]

    async def clear_by_docname(self, docname: str) -> int:
        """Clear components defined in a specific document."""
        to_remove = [
            slug for slug, c in self.storage_dict.items() if c.docname == docname
        ]
        for slug in to_remove:
            del self.storage_dict[slug]
        return len(to_remove)
