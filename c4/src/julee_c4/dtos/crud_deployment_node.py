"""Generated CRUD messages for DeploymentNode.

Do not edit — regenerate with generate-crud.sh.
"""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.deployment_node import DeploymentNode, NodeType
from julee_c4.domain.values.container_instance import ContainerInstance


class DeploymentNodeMessage(BaseModel):
    """What a DeploymentNode is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    slug: str
    name: str
    environment: str
    node_type: NodeType
    description: str
    technology: str
    instances: int
    parent_slug: str | None
    container_instances: tuple[ContainerInstance, ...]
    properties: Mapping[str, str]
    tags: tuple[str, ...]
    docname: str

    @classmethod
    def of(cls, entity: DeploymentNode) -> "DeploymentNodeMessage":
        """The message for one deployment_node."""
        return cls(
            slug=str(entity.slug),
            name=str(entity.name),
            environment=entity.environment,
            node_type=entity.node_type,
            description=entity.description,
            technology=entity.technology,
            instances=entity.instances,
            parent_slug=None if entity.parent_slug is None else str(entity.parent_slug),
            container_instances=entity.container_instances,
            properties=entity.properties,
            tags=entity.tags,
            docname=entity.docname,
        )


class GetDeploymentNodeRequest(BaseModel):
    """Request for getting a DeploymentNode by slug."""

    slug: str


class GetDeploymentNodeResponse(BaseModel):
    """Response for getting a DeploymentNode."""

    deployment_node: DeploymentNodeMessage

    @classmethod
    def of(cls, entity: DeploymentNode) -> "GetDeploymentNodeResponse":
        """The response for the deployment_node that was found."""
        return cls(deployment_node=DeploymentNodeMessage.of(entity))


class ListDeploymentNodesRequest(BaseModel):
    """Request for listing all DeploymentNodes."""


class ListDeploymentNodesResponse(BaseModel):
    """Response for listing all DeploymentNodes.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    deployment_nodes: list[DeploymentNodeMessage]

    @classmethod
    def of(cls, entities: list[DeploymentNode]) -> "ListDeploymentNodesResponse":
        """The response for the deployment_nodes that were found."""
        return cls(
            deployment_nodes=[DeploymentNodeMessage.of(entity) for entity in entities]
        )


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

    deployment_node: DeploymentNodeMessage

    @classmethod
    def of(cls, entity: DeploymentNode) -> "CreateDeploymentNodeResponse":
        """The response for the deployment_node that was created."""
        return cls(deployment_node=DeploymentNodeMessage.of(entity))


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

    deployment_node: DeploymentNodeMessage

    @classmethod
    def of(cls, entity: DeploymentNode) -> "UpdateDeploymentNodeResponse":
        """The response for the deployment_node as it now is."""
        return cls(deployment_node=DeploymentNodeMessage.of(entity))


class DeleteDeploymentNodeRequest(BaseModel):
    """Request for deleting a DeploymentNode by slug."""

    slug: str


class DeleteDeploymentNodeResponse(BaseModel):
    """Response for deleting a DeploymentNode."""

    deleted: bool
