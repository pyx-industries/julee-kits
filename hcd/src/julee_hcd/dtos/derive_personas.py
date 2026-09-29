"""The messages derive personas takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel

from julee_hcd.domain.models.persona import Persona


class DerivePersonasRequest(BaseModel):
    """Request for deriving personas from stories and epics."""


class DerivePersonasResponse(BaseModel):
    """Response from deriving personas."""

    personas: list[Persona]
