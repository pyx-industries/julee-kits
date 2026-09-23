"""Handlers: what else should happen when an entity changes.

A repository stores an entity. Anything that must follow from storing it
— rewriting an index, telling another document it has a new member —
belongs to a handler, so the repository does not grow opinions about the
rest of the documentation.
"""

from .base import EntityHandler
from .epic_orchestration import EpicOrchestrationHandler
from .journey_orchestration import JourneyOrchestrationHandler
from .null_handlers import (
    LoggingEmptyEpicHandler,
    LoggingEmptyJourneyHandler,
    LoggingOrphanStoryHandler,
    LoggingUnknownJourneyEpicRefHandler,
    LoggingUnknownJourneyPersonaHandler,
    LoggingUnknownJourneyStoryRefHandler,
    LoggingUnknownPersonaHandler,
    LoggingUnknownStoryRefHandler,
    NullEmptyEpicHandler,
    NullEmptyJourneyHandler,
    NullEpicCreatedHandler,
    NullJourneyCreatedHandler,
    NullOrphanStoryHandler,
    NullStoryCreatedHandler,
    NullUnknownJourneyEpicRefHandler,
    NullUnknownJourneyPersonaHandler,
    NullUnknownJourneyStoryRefHandler,
    NullUnknownPersonaHandler,
    NullUnknownStoryRefHandler,
)
from .story_orchestration import StoryOrchestrationHandler

__all__ = [
    "EntityHandler",
    "EpicOrchestrationHandler",
    "JourneyOrchestrationHandler",
    "LoggingEmptyEpicHandler",
    "LoggingEmptyJourneyHandler",
    "LoggingOrphanStoryHandler",
    "LoggingUnknownJourneyEpicRefHandler",
    "LoggingUnknownJourneyPersonaHandler",
    "LoggingUnknownJourneyStoryRefHandler",
    "LoggingUnknownPersonaHandler",
    "LoggingUnknownStoryRefHandler",
    "NullEmptyEpicHandler",
    "NullEmptyJourneyHandler",
    "NullEpicCreatedHandler",
    "NullJourneyCreatedHandler",
    "NullOrphanStoryHandler",
    "NullStoryCreatedHandler",
    "NullUnknownJourneyEpicRefHandler",
    "NullUnknownJourneyPersonaHandler",
    "NullUnknownJourneyStoryRefHandler",
    "NullUnknownPersonaHandler",
    "NullUnknownStoryRefHandler",
    "StoryOrchestrationHandler",
]
