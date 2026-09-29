"""The messages GetSystemContextDiagramUseCase takes and returns.

Pydantic lives here and nowhere else in the bounded context (ADR 001).
"""

from pydantic import BaseModel, Field

from julee_c4.domain.values.diagrams import SystemContextDiagram


class GetSystemContextDiagramRequest(BaseModel):
    """Request for generating a system context diagram."""

    system_slug: str = Field(description="Software system to show context for")
    format: str = Field(
        default="plantuml", description="Output format: plantuml, structurizr, data"
    )


class GetSystemContextDiagramResponse(BaseModel):
    """Response from computing a system context diagram."""

    diagram: SystemContextDiagram | None
