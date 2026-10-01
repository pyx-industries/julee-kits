"""The messages find persona by name takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel, Field

from julee_hcd.domain.models.persona import Persona


class FindPersonaByNameRequest(BaseModel):
    """Request for finding a persona by name."""

    name: str = Field(description="Persona name to search for")


class FindPersonaByNameResponse(BaseModel):
    """Response from finding a persona by name."""

    persona: Persona | None
