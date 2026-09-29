"""The messages resolve accelerator references takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from julee.core.entities.accelerator import Accelerator
from julee.core.entities.bounded_context_info import BoundedContextInfo
from pydantic import BaseModel

from julee_hcd.domain.models.app import App
from julee_hcd.domain.models.integration import Integration
from julee_hcd.domain.models.journey import Journey
from julee_hcd.domain.models.story import Story


class ResolveAcceleratorReferencesRequest(BaseModel):
    """What an accelerator's references are resolved against."""

    accelerator: Accelerator
    accelerators: tuple[Accelerator, ...] = ()
    apps: tuple[App, ...] = ()
    stories: tuple[Story, ...] = ()
    journeys: tuple[Journey, ...] = ()
    integrations: tuple[Integration, ...] = ()
    code_infos: tuple[BoundedContextInfo, ...] = ()


class ResolveAcceleratorReferencesResponse(BaseModel):
    """Everything an accelerator is connected to."""

    apps: tuple[App, ...] = ()
    stories: tuple[Story, ...] = ()
    journeys: tuple[Journey, ...] = ()
    source_integrations: tuple[Integration, ...] = ()
    publish_integrations: tuple[Integration, ...] = ()
    dependents: tuple[Accelerator, ...] = ()
    fed_by: tuple[Accelerator, ...] = ()
    code_info: BoundedContextInfo | None = None
