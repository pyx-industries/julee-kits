"""What every in-memory HCD repository does, done once.

julee's MemoryRepositoryMixin handles storage, logging and timestamps,
but it describes a store that is written to and read from, so it has no
delete, no clear and no list_all. HcdRepository asks for all of those,
plus the two document queries an incremental build needs, and the answer
is the same for every entity: they all live in one dict keyed by slug,
and they all carry a docname.

So the whole shared surface is implemented here, and an entity's own
repository is left with only the queries that are actually about that
entity.
"""

import logging
from typing import Generic, TypeVar

from julee.repositories.memory import MemoryRepositoryMixin

from julee_hcd.domain.models.base import Authored

T = TypeVar("T", bound=Authored)

logger = logging.getLogger(__name__)


class MemoryHcdRepository(MemoryRepositoryMixin[T], Generic[T]):
    """In-memory storage for one kind of authored HCD entity.

    Subclasses set entity_name in __init__ and add their own queries.
    """

    def __init__(self, entity_name: str) -> None:
        """Start empty.

        Args:
            entity_name: The entity's class name, used in log messages
        """
        self.storage_dict: dict[str, T] = {}
        self.logger = logger
        self.entity_name = entity_name
        self.id_field = "slug"

    async def get(self, entity_id: str) -> T | None:
        """The entity with this slug, or None."""
        return self.get_entity(entity_id)

    async def get_many(self, entity_ids: list[str]) -> dict[str, T | None]:
        """These slugs mapped to their entities, or None where absent."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: T) -> None:
        """Store the entity under its slug, replacing any it had."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[T]:
        """Every entity held, in insertion order."""
        return list(self.storage_dict.values())

    async def clear(self) -> None:
        """Forget everything."""
        self.storage_dict.clear()

    async def get_by_docname(self, docname: str) -> list[T]:
        """Every entity read out of one document."""
        return [e for e in self.storage_dict.values() if e.docname == docname]

    async def clear_by_docname(self, docname: str) -> int:
        """Forget everything one document defined, and say how many."""
        gone = [s for s, e in self.storage_dict.items() if e.docname == docname]
        for slug in gone:
            del self.storage_dict[slug]
        return len(gone)
