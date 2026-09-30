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
from .resolve_accelerator_references import (
    ResolveAcceleratorReferencesRequest,
    ResolveAcceleratorReferencesResponse,
    ResolveAcceleratorReferencesUseCase,
    get_apps_for_accelerator,
    get_code_info_for_accelerator,
    get_dependent_accelerators,
    get_fed_by_accelerators,
    get_journeys_for_accelerator,
    get_publish_integrations,
    get_source_integrations,
    get_stories_for_accelerator,
)
from .resolve_story_references import (
    ResolveStoryReferencesRequest,
    ResolveStoryReferencesResponse,
    ResolveStoryReferencesUseCase,
    get_epics_for_story,
    get_journeys_for_story,
    get_related_stories,
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
    "ResolveAcceleratorReferencesRequest",
    "ResolveAcceleratorReferencesResponse",
    "ResolveAcceleratorReferencesUseCase",
    "ResolveStoryReferencesRequest",
    "ResolveStoryReferencesResponse",
    "ResolveStoryReferencesUseCase",
    "StoryCondition",
    "StoryOrchestrationRequest",
    "StoryOrchestrationResponse",
    "StoryOrchestrationUseCase",
    "SuggestionRepositories",
    "ValidateAcceleratorsRequest",
    "ValidateAcceleratorsResponse",
    "ValidateAcceleratorsUseCase",
    "get_apps_for_accelerator",
    "get_code_info_for_accelerator",
    "get_dependent_accelerators",
    "get_epics_for_story",
    "get_fed_by_accelerators",
    "get_journeys_for_accelerator",
    "get_journeys_for_story",
    "get_publish_integrations",
    "get_related_stories",
    "get_source_integrations",
    "get_stories_for_accelerator",
]
