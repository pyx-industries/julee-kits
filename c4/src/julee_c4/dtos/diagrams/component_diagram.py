"""The messages GetComponentDiagramUseCase takes and returns.

Pydantic lives here and nowhere else in the bounded context (ADR 001).
"""

from pydantic import BaseModel, Field

from julee_c4.domain.values.diagrams import ComponentDiagram


class GetComponentDiagramRequest(BaseModel):
    """Request for generating a component diagram."""

    container_slug: str = Field(description="Container to show components for")
    format: str = Field(
        default="plantuml", description="Output format: plantuml, structurizr, data"
    )


class GetComponentDiagramResponse(BaseModel):
    """Response from computing a component diagram."""

    diagram: ComponentDiagram | None
