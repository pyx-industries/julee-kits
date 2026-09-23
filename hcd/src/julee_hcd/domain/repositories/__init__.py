"""Repository protocols for the HCD entities.

Each names the queries its entity is actually asked for, on top of the
document-backed behaviour every HCD repository shares.
"""

from .accelerator import AcceleratorRepository
from .app import AppRepository
from .base import HcdRepository
from .code_info import CodeInfoRepository
from .contrib import ContribRepository
from .epic import EpicRepository
from .integration import IntegrationRepository
from .journey import JourneyRepository
from .persona import PersonaRepository
from .story import StoryRepository

__all__ = [
    "AcceleratorRepository",
    "AppRepository",
    "CodeInfoRepository",
    "ContribRepository",
    "EpicRepository",
    "HcdRepository",
    "IntegrationRepository",
    "JourneyRepository",
    "PersonaRepository",
    "StoryRepository",
]
