"""The messages GetDynamicDiagramUseCase takes and returns.

Pydantic lives here and nowhere else in the bounded context (ADR 001).
"""

from pydantic import BaseModel, Field

from julee_c4.domain.values.diagrams import DynamicDiagram


class GetDynamicDiagramRequest(BaseModel):
    """Request for generating a dynamic diagram."""

    sequence_name: str = Field(description="Dynamic sequence to show")
    format: str = Field(
        default="plantuml", description="Output format: plantuml, structurizr, data"
    )


class GetDynamicDiagramResponse(BaseModel):
    """Response from computing a dynamic diagram."""

    diagram: DynamicDiagram | None
