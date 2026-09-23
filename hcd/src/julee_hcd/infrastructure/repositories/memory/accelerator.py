"""Memory implementation of AcceleratorRepository."""

import logging

from julee.core.entities.accelerator import Accelerator
from julee.repositories.memory import MemoryRepositoryMixin

from julee_hcd.domain.repositories.accelerator import AcceleratorRepository

logger = logging.getLogger(__name__)


class MemoryAcceleratorRepository(
    MemoryRepositoryMixin[Accelerator], AcceleratorRepository
):
    """In-memory implementation of AcceleratorRepository.

    Accelerators are stored in a dictionary keyed by slug. This implementation
    is used during Sphinx builds where accelerators are populated during doctree
    processing and support incremental builds via docname tracking.
    """

    def __init__(self) -> None:
        """Start empty."""
        self.storage_dict: dict[str, Accelerator] = {}
        self.logger = logger
        self.entity_name = "Accelerator"
        self.id_field = "slug"

    # An accelerator carries a docname but not the rest of the authored
    # block, so it cannot use MemoryHcdRepository, and this surface is
    # spelled out here rather than inherited.

    async def get(self, entity_id: str) -> Accelerator | None:
        """The accelerator with this slug, or None."""
        return self.get_entity(entity_id)

    async def get_many(self, entity_ids: list[str]) -> dict[str, Accelerator | None]:
        """These slugs mapped to their accelerators, or None where absent."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: Accelerator) -> None:
        """Store the accelerator under its slug."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[Accelerator]:
        """Every accelerator held."""
        return list(self.storage_dict.values())

    async def delete(self, entity_id: str) -> bool:
        """Remove one accelerator, saying whether there was one."""
        return self.storage_dict.pop(entity_id, None) is not None

    async def clear(self) -> None:
        """Forget every accelerator."""
        self.storage_dict.clear()

    async def get_by_status(self, status: str) -> list[Accelerator]:
        """Get all accelerators with a specific status."""
        status_normalized = status.lower().strip()
        return [
            accel
            for accel in self.storage_dict.values()
            if accel.status_normalized == status_normalized
        ]

    async def get_by_docname(self, docname: str) -> list[Accelerator]:
        """Get all accelerators defined in a specific document."""
        return [
            accel for accel in self.storage_dict.values() if accel.docname == docname
        ]

    async def clear_by_docname(self, docname: str) -> int:
        """Remove all accelerators defined in a specific document."""
        to_remove = [
            slug
            for slug, accel in self.storage_dict.items()
            if accel.docname == docname
        ]
        for slug in to_remove:
            del self.storage_dict[slug]
        return len(to_remove)

    async def get_by_integration(
        self, integration_slug: str, relationship: str
    ) -> list[Accelerator]:
        """Get accelerators that have a relationship with an integration."""
        result = []
        for accel in self.storage_dict.values():
            if relationship == "sources_from":
                if integration_slug in accel.get_sources_from_slugs():
                    result.append(accel)
            elif relationship == "publishes_to":
                if integration_slug in accel.get_publishes_to_slugs():
                    result.append(accel)
        return result

    async def get_dependents(self, accelerator_slug: str) -> list[Accelerator]:
        """Get accelerators that depend on a specific accelerator."""
        return [
            accel
            for accel in self.storage_dict.values()
            if accelerator_slug in accel.depends_on
        ]

    async def get_fed_by(self, accelerator_slug: str) -> list[Accelerator]:
        """Get accelerators that feed into a specific accelerator."""
        return [
            accel
            for accel in self.storage_dict.values()
            if accelerator_slug in accel.feeds_into
        ]

    async def get_all_statuses(self) -> set[str]:
        """Get all unique statuses across all accelerators."""
        return {
            accel.status_normalized
            for accel in self.storage_dict.values()
            if accel.status_normalized
        }
