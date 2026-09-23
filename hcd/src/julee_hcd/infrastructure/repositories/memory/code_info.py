"""Memory implementation of CodeInfoRepository."""

import logging

from julee.core.entities.bounded_context_info import BoundedContextInfo
from julee.repositories.memory import MemoryRepositoryMixin

from julee_hcd.domain.repositories.code_info import CodeInfoRepository

logger = logging.getLogger(__name__)


class MemoryCodeInfoRepository(
    MemoryRepositoryMixin[BoundedContextInfo], CodeInfoRepository
):
    """In-memory implementation of CodeInfoRepository.

    Bounded context info is stored in a dictionary keyed by slug. This implementation
    is used during Sphinx builds where code info is populated at builder-inited
    by scanning src/ directories.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self.storage_dict: dict[str, BoundedContextInfo] = {}
        self.logger = logger
        self.entity_name = "BoundedContextInfo"
        self.id_field = "slug"

    # BoundedContextInfo is discovered by scanning code, not authored, so
    # this does not use MemoryHcdRepository and spells the surface out.

    async def get(self, entity_id: str) -> BoundedContextInfo | None:
        """The bounded context with this slug, or None."""
        return self.get_entity(entity_id)

    async def get_many(
        self, entity_ids: list[str]
    ) -> dict[str, BoundedContextInfo | None]:
        """These slugs mapped to their contexts, or None where absent."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: BoundedContextInfo) -> None:
        """Store the bounded context under its slug."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[BoundedContextInfo]:
        """Every bounded context found."""
        return list(self.storage_dict.values())

    async def delete(self, entity_id: str) -> bool:
        """Remove one bounded context, saying whether there was one."""
        return self.storage_dict.pop(entity_id, None) is not None

    async def clear(self) -> None:
        """Forget everything, for a fresh scan."""
        self.storage_dict.clear()

    async def get_by_code_dir(self, code_dir: str) -> BoundedContextInfo | None:
        """Get bounded context info by its code directory name."""
        for info in self.storage_dict.values():
            if info.code_dir == code_dir:
                return info
        return None

    async def get_with_entities(self) -> list[BoundedContextInfo]:
        """Get all bounded contexts that have domain entities."""
        return [info for info in self.storage_dict.values() if info.has_entities]

    async def get_with_use_cases(self) -> list[BoundedContextInfo]:
        """Get all bounded contexts that have use cases."""
        return [info for info in self.storage_dict.values() if info.has_use_cases]

    async def get_with_infrastructure(self) -> list[BoundedContextInfo]:
        """Get all bounded contexts that have infrastructure."""
        return [info for info in self.storage_dict.values() if info.has_infrastructure]

    async def get_all_entity_names(self) -> set[str]:
        """Get all unique entity class names across all bounded contexts."""
        names: set[str] = set()
        for info in self.storage_dict.values():
            names.update(info.get_entity_names())
        return names

    async def get_all_use_case_names(self) -> set[str]:
        """Get all unique use case class names across all bounded contexts."""
        names: set[str] = set()
        for info in self.storage_dict.values():
            names.update(info.get_use_case_names())
        return names
