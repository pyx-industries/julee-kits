"""In-memory repositories, which is what a Sphinx build uses.

A documentation build reads every document into memory, renders, and
exits; nothing outlives the process, so there is nothing to persist.
"""

from .app import MemoryAppRepository
from .base import MemoryHcdRepository
from .contrib import MemoryContribRepository
from .epic import MemoryEpicRepository
from .integration import MemoryIntegrationRepository
from .journey import MemoryJourneyRepository
from .persona import MemoryPersonaRepository
from .story import MemoryStoryRepository

__all__ = [
    "MemoryAppRepository",
    "MemoryContribRepository",
    "MemoryEpicRepository",
    "MemoryHcdRepository",
    "MemoryIntegrationRepository",
    "MemoryJourneyRepository",
    "MemoryPersonaRepository",
    "MemoryStoryRepository",
]
