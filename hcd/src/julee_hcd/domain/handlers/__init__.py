"""Handler protocols for HCD domain conditions.

Use cases that detect a domain condition — an empty epic, a story with
an unrecognised persona — hand off to one of these rather than deciding
for themselves what should happen next. Each protocol is one condition,
in its own file, so a look at the filename says what it is for.
"""

from .empty_epic_handler import EmptyEpicHandler
from .empty_journey_handler import EmptyJourneyHandler
from .epic_created_handler import EpicCreatedHandler
from .journey_created_handler import JourneyCreatedHandler
from .orphan_story_handler import OrphanStoryHandler
from .story_created_handler import StoryCreatedHandler
from .unknown_journey_epic_ref_handler import UnknownJourneyEpicRefHandler
from .unknown_journey_persona_handler import UnknownJourneyPersonaHandler
from .unknown_journey_story_ref_handler import UnknownJourneyStoryRefHandler
from .unknown_persona_handler import UnknownPersonaHandler
from .unknown_story_ref_handler import UnknownStoryRefHandler

__all__ = [
    "EmptyEpicHandler",
    "EmptyJourneyHandler",
    "EpicCreatedHandler",
    "JourneyCreatedHandler",
    "OrphanStoryHandler",
    "StoryCreatedHandler",
    "UnknownJourneyEpicRefHandler",
    "UnknownJourneyPersonaHandler",
    "UnknownJourneyStoryRefHandler",
    "UnknownPersonaHandler",
    "UnknownStoryRefHandler",
]
