"""Use cases over the HCD entities.

CRUD is generated from the entities (ADR 008) and committed, because a
kit ships as a wheel. Deleting is hand-written: the generator does not
emit it yet (julee#198).
"""

from .derive_personas import (
    DerivePersonasRequest,
    DerivePersonasResponse,
    DerivePersonasUseCase,
    derive_personas_by_app_type,
    derive_personas_from_stories,
    get_apps_for_persona,
    get_epics_for_persona,
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
from .resolve_app_references import (
    ResolveAppReferencesRequest,
    ResolveAppReferencesResponse,
    ResolveAppReferencesUseCase,
    get_epics_for_app,
    get_journeys_for_app,
    get_personas_for_app,
    get_stories_for_app,
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
    "ResolveAppReferencesRequest",
    "ResolveAppReferencesResponse",
    "ResolveAppReferencesUseCase",
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
    "derive_personas_by_app_type",
    "derive_personas_from_stories",
    "get_apps_for_accelerator",
    "get_apps_for_persona",
    "get_code_info_for_accelerator",
    "get_dependent_accelerators",
    "get_epics_for_app",
    "get_epics_for_persona",
    "get_epics_for_story",
    "get_fed_by_accelerators",
    "get_journeys_for_accelerator",
    "get_journeys_for_app",
    "get_journeys_for_story",
    "get_personas_for_app",
    "get_publish_integrations",
    "get_related_stories",
    "get_source_integrations",
    "get_stories_for_accelerator",
    "get_stories_for_app",
]
