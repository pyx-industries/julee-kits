"""PersonaRepository protocol."""

from typing import Protocol, runtime_checkable

from julee_hcd.domain.models.persona import Persona

from .base import HcdRepository


@runtime_checkable
class PersonaRepository(HcdRepository[Persona], Protocol):
    """Repository protocol for Persona entities.

    Personas are looked up by slug like everything else, but a story names
    its persona by display name — the "As a [persona]" — so finding one by
    name, exactly or normalised, is the lookup this repository exists for.
    """

    async def get_by_name(self, name: str) -> Persona | None:
        """The persona with this display name.

        Args:
            name: Display name as written, e.g. "Knowledge Curator"

        Returns:
            The persona, or None if no persona has that name
        """
        ...

    async def get_by_normalized_name(self, normalized_name: str) -> Persona | None:
        """The persona whose name matches, ignoring case and separators.

        What a story calls a persona and what a definition calls it rarely
        agree on capitalisation, so matching is done on the normalised form.

        Args:
            normalized_name: Name already passed through normalize_name

        Returns:
            The persona, or None if none matches
        """
        ...

    async def list_defined(self) -> list[Persona]:
        """Only the personas somebody wrote up.

        Returns:
            Personas with goals, frustrations, jobs or context; not the
            ones derived from a story's "As a ..." alone
        """
        ...
