"""The messages resolve app references takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel

from julee_hcd.domain.models.app import App
from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.models.journey import Journey
from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.models.story import Story


class ResolveAppReferencesRequest(BaseModel):
    """What an app's references are resolved against."""

    app: App
    stories: tuple[Story, ...] = ()
    epics: tuple[Epic, ...] = ()
    journeys: tuple[Journey, ...] = ()


class ResolveAppReferencesResponse(BaseModel):
    """Everything an app is connected to."""

    stories: tuple[Story, ...] = ()
    personas: tuple[Persona, ...] = ()
    journeys: tuple[Journey, ...] = ()
    epics: tuple[Epic, ...] = ()
