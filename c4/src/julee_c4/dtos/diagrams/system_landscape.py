"""The messages GetSystemLandscapeDiagramUseCase takes and returns.

Pydantic lives here and nowhere else in the bounded context (ADR 001).
"""

from pydantic import BaseModel, Field

from julee_c4.domain.models.diagrams import SystemLandscapeDiagram


class GetSystemLandscapeDiagramRequest(BaseModel):
    """Request for generating a system landscape diagram."""

    format: str = Field(
        default="plantuml", description="Output format: plantuml, structurizr, data"
    )


class GetSystemLandscapeDiagramResponse(BaseModel):
    """Response from computing a system landscape diagram."""

    diagram: SystemLandscapeDiagram
