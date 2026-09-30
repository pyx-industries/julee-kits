"""Use cases over the HCD entities.

CRUD is generated from the entities (ADR 008) and committed, because a
kit ships as a wheel. Deleting is hand-written: the generator does not
emit it yet (julee#198).

The persona calculations used to be re-exported from here. They are in
domain/calculators/personas.py now, and callers reach them there: a
calculation is not a use case, and an adapter asking this package for
one was how it came to look like two use cases were calling each other.
"""

from .derive_personas import (
    DerivePersonasRequest,
    DerivePersonasResponse,
    DerivePersonasUseCase,
)
from .epic_orchestration import (
    EpicCondition,
    EpicOrchestrationRequest,
    EpicOrchestrationResponse,
    EpicOrchestrationUseCase,
)
from .get_persona import (
    GetPersonaRequest,
    GetPersonaResponse,
    GetPersonaUseCase,
)
from .journey_orchestration import (
    JourneyCondition,
    JourneyOrchestrationRequest,
    JourneyOrchestrationResponse,
    JourneyOrchestrationUseCase,
)
from .story_orchestration import (
    StoryCondition,
    StoryOrchestrationRequest,
    StoryOrchestrationResponse,
    StoryOrchestrationUseCase,
)
from .suggestions import (
    SuggestionRepositories,
)
from .validate_accelerators import (
    ValidateAcceleratorsRequest,
    ValidateAcceleratorsResponse,
    ValidateAcceleratorsUseCase,
)

__all__ = [
    "DerivePersonasRequest",
    "DerivePersonasResponse",
    "DerivePersonasUseCase",
    "EpicCondition",
    "EpicOrchestrationRequest",
    "EpicOrchestrationResponse",
    "EpicOrchestrationUseCase",
    "GetPersonaRequest",
    "GetPersonaResponse",
    "GetPersonaUseCase",
    "JourneyCondition",
    "JourneyOrchestrationRequest",
    "JourneyOrchestrationResponse",
    "JourneyOrchestrationUseCase",
    "StoryCondition",
    "StoryOrchestrationRequest",
    "StoryOrchestrationResponse",
    "StoryOrchestrationUseCase",
    "SuggestionRepositories",
    "ValidateAcceleratorsRequest",
    "ValidateAcceleratorsResponse",
    "ValidateAcceleratorsUseCase",
]
