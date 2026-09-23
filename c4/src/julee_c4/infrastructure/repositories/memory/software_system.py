"""In-memory SoftwareSystem repository implementation."""

import logging

from julee.core.utils import normalize_name
from julee.repositories.memory import MemoryRepositoryMixin

from julee_c4.domain.models.software_system import SoftwareSystem, SystemType
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository

logger = logging.getLogger(__name__)


class MemorySoftwareSystemRepository(
    MemoryRepositoryMixin[SoftwareSystem], SoftwareSystemRepository
):
    """In-memory implementation of SoftwareSystemRepository.

    Stores software systems in a dictionary keyed by slug.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self.storage_dict: dict[str, SoftwareSystem] = {}
        self.logger = logger
        self.entity_name = "SoftwareSystem"
        self.id_field = "slug"

    # -------------------------------------------------------------------------
    # BaseRepository implementation (delegating to protected helpers)
    # -------------------------------------------------------------------------

    async def get(self, entity_id: str) -> SoftwareSystem | None:
        """Get a software system by slug."""
        return self.get_entity(entity_id)

    async def get_many(self, entity_ids: list[str]) -> dict[str, SoftwareSystem | None]:
        """Get multiple software systems by slug."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: SoftwareSystem) -> None:
        """Save a software system."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[SoftwareSystem]:
        """List all software systems."""
        return list(self.storage_dict.values())

    async def delete(self, entity_id: str) -> bool:
        """Delete a software system by slug."""
        return self.storage_dict.pop(entity_id, None) is not None

    async def clear(self) -> None:
        """Clear all software systems."""
        self.storage_dict.clear()

    # -------------------------------------------------------------------------
    # SoftwareSystemRepository-specific queries
    # -------------------------------------------------------------------------

    async def get_by_type(self, system_type: SystemType) -> list[SoftwareSystem]:
        """Get all systems of a specific type."""
        return [s for s in self.storage_dict.values() if s.system_type == system_type]

    async def get_internal_systems(self) -> list[SoftwareSystem]:
        """Get all internal (owned) systems."""
        return await self.get_by_type(SystemType.INTERNAL)

    async def get_external_systems(self) -> list[SoftwareSystem]:
        """Get all external systems."""
        return await self.get_by_type(SystemType.EXTERNAL)

    async def get_by_tag(self, tag: str) -> list[SoftwareSystem]:
        """Get systems with a specific tag."""
        return [s for s in self.storage_dict.values() if s.has_tag(tag)]

    async def get_by_owner(self, owner: str) -> list[SoftwareSystem]:
        """Get systems owned by a specific team."""
        owner_normalized = normalize_name(owner)
        return [
            s
            for s in self.storage_dict.values()
            if normalize_name(s.owner) == owner_normalized
        ]

    async def get_by_docname(self, docname: str) -> list[SoftwareSystem]:
        """Get systems defined in a specific document."""
        return [s for s in self.storage_dict.values() if s.docname == docname]

    async def clear_by_docname(self, docname: str) -> int:
        """Clear systems defined in a specific document."""
        to_remove = [
            slug for slug, s in self.storage_dict.items() if s.docname == docname
        ]
        for slug in to_remove:
            del self.storage_dict[slug]
        return len(to_remove)
