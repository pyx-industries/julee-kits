"""Generated CRUD messages for DeploymentNode.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.deployment_node import DeploymentNode, NodeType


class GetDeploymentNodeRequest(BaseModel):
    """Request for getting a DeploymentNode by slug."""

    slug: str


class GetDeploymentNodeResponse(BaseModel):
    """Response for getting a DeploymentNode."""

    deployment_node: DeploymentNode


class ListDeploymentNodesRequest(BaseModel):
    """Request for listing all DeploymentNodes."""


class ListDeploymentNodesResponse(BaseModel):
    """Response for listing all DeploymentNodes."""

    deployment_nodes: list[DeploymentNode]
    total_count: int


class CreateDeploymentNodeRequest(BaseModel):
    """Request for creating a DeploymentNode."""

    slug: str
    name: str
    environment: str = "production"
    node_type: NodeType = NodeType.OTHER
    description: str = ""
    technology: str = ""
    instances: int = 1
    parent_slug: str | None = None
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateDeploymentNodeResponse(BaseModel):
    """Response for creating a DeploymentNode."""

    deployment_node: DeploymentNode


class UpdateDeploymentNodeRequest(BaseModel):
    """Request for updating a DeploymentNode.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    environment: str | None = None
    node_type: NodeType | None = None
    description: str | None = None
    technology: str | None = None
    instances: int | None = None
    parent_slug: str | None = None
    tags: tuple[str, ...] | None = None
    docname: str | None = None

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateDeploymentNodeResponse(BaseModel):
    """Response for updating a DeploymentNode."""

    deployment_node: DeploymentNode


class DeleteDeploymentNodeRequest(BaseModel):
    """Request for deleting a DeploymentNode by slug."""

    slug: str


class DeleteDeploymentNodeResponse(BaseModel):
    """Response for deleting a DeploymentNode."""

    deleted: bool
