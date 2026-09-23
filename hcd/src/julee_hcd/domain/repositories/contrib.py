"""ContribRepository protocol."""

from typing import Protocol, runtime_checkable

from julee_hcd.domain.models.contrib import ContribModule

from .base import HcdRepository


@runtime_checkable
class ContribRepository(HcdRepository[ContribModule], Protocol):
    """Repository protocol for ContribModule entities.

    Contrib modules are scoped to a solution, because a site may document
    more than one and a utility belongs to the solution that ships it.
    """

    async def list_for_solution(self, solution_slug: str) -> list[ContribModule]:
        """Every contrib module belonging to one solution.

        Args:
            solution_slug: Solution to list for

        Returns:
            The modules that solution ships
        """
        ...
