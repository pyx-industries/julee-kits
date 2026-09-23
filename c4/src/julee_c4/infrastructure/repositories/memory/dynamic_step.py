"""In-memory DynamicStep repository implementation."""

import logging

from julee.repositories.memory import MemoryRepositoryMixin

from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType
from julee_c4.domain.repositories.dynamic_step import DynamicStepRepository

logger = logging.getLogger(__name__)


class MemoryDynamicStepRepository(
    MemoryRepositoryMixin[DynamicStep], DynamicStepRepository
):
    """In-memory implementation of DynamicStepRepository.

    Stores dynamic steps in a dictionary keyed by slug.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self.storage_dict: dict[str, DynamicStep] = {}
        self.logger = logger
        self.entity_name = "DynamicStep"
        self.id_field = "slug"

    # -------------------------------------------------------------------------
    # BaseRepository implementation (delegating to protected helpers)
    # -------------------------------------------------------------------------

    async def get(self, entity_id: str) -> DynamicStep | None:
        """Get a dynamic step by slug."""
        return self.get_entity(entity_id)

    async def get_many(self, entity_ids: list[str]) -> dict[str, DynamicStep | None]:
        """Get multiple dynamic steps by slug."""
        return self.get_many_entities(entity_ids)

    async def save(self, entity: DynamicStep) -> None:
        """Save a dynamic step."""
        self.save_entity(entity, self.id_field)

    async def list_all(self) -> list[DynamicStep]:
        """List all dynamic steps."""
        return list(self.storage_dict.values())

    async def delete(self, entity_id: str) -> bool:
        """Delete a dynamic step by slug."""
        return self.storage_dict.pop(entity_id, None) is not None

    async def clear(self) -> None:
        """Clear all dynamic steps."""
        self.storage_dict.clear()

    # -------------------------------------------------------------------------
    # DynamicStepRepository-specific queries
    # -------------------------------------------------------------------------

    async def get_by_sequence(self, sequence_name: str) -> list[DynamicStep]:
        """Get all steps in a sequence, ordered by step_number."""
        steps = [
            s for s in self.storage_dict.values() if s.sequence_name == sequence_name
        ]
        return sorted(steps, key=lambda s: s.step_number)

    async def get_sequences(self) -> list[str]:
        """Get all unique sequence names."""
        return list({s.sequence_name for s in self.storage_dict.values()})

    async def get_for_element(
        self,
        element_type: ElementType,
        element_slug: str,
    ) -> list[DynamicStep]:
        """Get all steps involving an element."""
        return [
            s
            for s in self.storage_dict.values()
            if s.involves_element(element_type, element_slug)
        ]

    async def get_step(
        self, sequence_name: str, step_number: int
    ) -> DynamicStep | None:
        """Get a specific step by sequence and number."""
        for step in self.storage_dict.values():
            if step.sequence_name == sequence_name and step.step_number == step_number:
                return step
        return None

    async def get_by_docname(self, docname: str) -> list[DynamicStep]:
        """Get steps defined in a specific document."""
        return [s for s in self.storage_dict.values() if s.docname == docname]

    async def clear_by_docname(self, docname: str) -> int:
        """Clear steps defined in a specific document."""
        to_remove = [
            slug for slug, s in self.storage_dict.items() if s.docname == docname
        ]
        for slug in to_remove:
            del self.storage_dict[slug]
        return len(to_remove)
