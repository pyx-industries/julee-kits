"""The messages GetDeploymentDiagramUseCase takes and returns.

Pydantic lives here and nowhere else in the bounded context (ADR 001).
"""

from pydantic import BaseModel, Field

from julee_c4.domain.values.diagrams import DeploymentDiagram


class GetDeploymentDiagramRequest(BaseModel):
    """Request for generating a deployment diagram."""

    environment: str = Field(description="Deployment environment to show")
    format: str = Field(
        default="plantuml", description="Output format: plantuml, structurizr, data"
    )


class GetDeploymentDiagramResponse(BaseModel):
    """Response from computing a deployment diagram."""

    diagram: DeploymentDiagram
