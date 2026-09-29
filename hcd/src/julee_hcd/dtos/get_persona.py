"""The messages get persona takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel, Field

from julee_hcd.domain.models.persona import Persona


class GetPersonaRequest(BaseModel):
    """Request for getting a persona by name."""

    name: str = Field(description="Persona name to search for")


class GetPersonaResponse(BaseModel):
    """Response from getting a persona by name."""

    persona: Persona | None
