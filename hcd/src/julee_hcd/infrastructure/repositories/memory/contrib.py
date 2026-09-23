"""Memory implementation of ContribRepository."""

from julee_hcd.domain.models.contrib import ContribModule
from julee_hcd.domain.repositories.contrib import ContribRepository

from .base import MemoryHcdRepository


class MemoryContribRepository(MemoryHcdRepository[ContribModule], ContribRepository):
    """In-memory implementation of ContribRepository."""

    def __init__(self) -> None:
        """Start empty."""
        super().__init__("ContribModule")

    async def list_for_solution(self, solution_slug: str) -> list[ContribModule]:
        """Every contrib module belonging to one solution."""
        return [
            module
            for module in self.storage_dict.values()
            if module.solution_slug == solution_slug
        ]
