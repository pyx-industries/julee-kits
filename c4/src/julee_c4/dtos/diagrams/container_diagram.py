"""The messages GetContainerDiagramUseCase takes and returns.

Pydantic lives here and nowhere else in the bounded context (ADR 001).
"""

from pydantic import BaseModel, Field

from julee_c4.domain.values.diagrams import ContainerDiagram


class GetContainerDiagramRequest(BaseModel):
    """Request for generating a container diagram."""

    system_slug: str = Field(description="Software system to show containers for")
    format: str = Field(
        default="plantuml", description="Output format: plantuml, structurizr, data"
    )


class GetContainerDiagramResponse(BaseModel):
    """Response from computing a container diagram."""

    diagram: ContainerDiagram | None
