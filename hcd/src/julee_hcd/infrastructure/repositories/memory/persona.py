"""Memory implementation of PersonaRepository."""

from julee.core.utils import normalize_name

from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.repositories.persona import PersonaRepository

from .base import MemoryHcdRepository


class MemoryPersonaRepository(MemoryHcdRepository[Persona], PersonaRepository):
    """In-memory implementation of PersonaRepository.

    Personas are keyed by slug, but stories name them by display name, so
    the lookups that matter here go the other way.
    """

    def __init__(self) -> None:
        """Start empty."""
        super().__init__("Persona")

    async def get_by_name(self, name: str) -> Persona | None:
        """The persona with exactly this display name."""
        for persona in self.storage_dict.values():
            if persona.name == name:
                return persona
        return None

    async def get_by_normalized_name(self, normalized_name: str) -> Persona | None:
        """The persona whose name matches, ignoring case and separators."""
        wanted = normalize_name(normalized_name)
        for persona in self.storage_dict.values():
            if persona.normalized_name == wanted:
                return persona
        return None

    async def list_defined(self) -> list[Persona]:
        """Only the personas somebody wrote up."""
        return [p for p in self.storage_dict.values() if p.is_defined]
