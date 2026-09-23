"""AcceleratorRepository protocol.

Accelerator lives in the kernel rather than in this kit, so that HCD and
the private supply-chain work — which cannot see each other — agree on
what an accelerator is. The repository over it is still the contract of
whoever reads accelerators, which is why it is here.

It does not extend HcdRepository: an accelerator carries a docname but
not the rest of the authored block, so it is document-backed without
being one of this kit's own authored entities.
"""

from typing import Protocol, runtime_checkable

from julee.core.entities.accelerator import Accelerator
from julee.repositories.base import BaseRepository


@runtime_checkable
class AcceleratorRepository(BaseRepository[Accelerator], Protocol):
    """Repository protocol for Accelerator entities.

    Accelerators are written up in RST documents, so a build can ask which
    ones a document defined and tell the repository to forget them when it
    is re-read.
    """

    async def get_by_status(self, status: str) -> list[Accelerator]:
        """Get all accelerators with a specific status.

        Args:
            status: Status to filter by (case-insensitive)

        Returns:
            List of accelerators with matching status
        """
        ...

    async def get_by_docname(self, docname: str) -> list[Accelerator]:
        """Get all accelerators defined in a specific document.

        Args:
            docname: RST document name

        Returns:
            List of accelerators from that document
        """
        ...

    async def clear_by_docname(self, docname: str) -> int:
        """Remove all accelerators defined in a specific document.

        Used during incremental builds when a document is re-read.

        Args:
            docname: RST document name

        Returns:
            Number of accelerators removed
        """
        ...

    async def get_by_integration(
        self, integration_slug: str, relationship: str
    ) -> list[Accelerator]:
        """Get accelerators that have a relationship with an integration.

        Args:
            integration_slug: Integration slug to search for
            relationship: Either "sources_from" or "publishes_to"

        Returns:
            List of accelerators with this integration relationship
        """
        ...

    async def get_dependents(self, accelerator_slug: str) -> list[Accelerator]:
        """Get accelerators that depend on a specific accelerator.

        Args:
            accelerator_slug: Slug of the accelerator to find dependents of

        Returns:
            List of accelerators that have this accelerator in depends_on
        """
        ...

    async def get_fed_by(self, accelerator_slug: str) -> list[Accelerator]:
        """Get accelerators that feed into a specific accelerator.

        Args:
            accelerator_slug: Slug of the accelerator

        Returns:
            List of accelerators that have this accelerator in feeds_into
        """
        ...

    async def get_all_statuses(self) -> set[str]:
        """Get all unique statuses across all accelerators.

        Returns:
            Set of status strings (normalized to lowercase)
        """
        ...

    async def delete(self, entity_id: str) -> bool:
        """Remove one accelerator, saying whether there was one."""
        ...

    async def clear(self) -> None:
        """Forget every accelerator."""
        ...
