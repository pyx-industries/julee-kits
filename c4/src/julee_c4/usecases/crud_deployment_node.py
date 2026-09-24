"""Generated CRUD use cases for DeploymentNode.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_c4.domain.models.deployment_node import DeploymentNode, NodeType
from julee_c4.domain.repositories.deployment_node import DeploymentNodeRepository


class GetDeploymentNodeRequest(BaseModel):
    """Request for getting a DeploymentNode by slug."""

    slug: str


class GetDeploymentNodeResponse(BaseModel):
    """Response for getting a DeploymentNode."""

    deployment_node: DeploymentNode


class GetDeploymentNodeUseCase(GetUseCase[DeploymentNode, DeploymentNodeRepository]):
    """Get a DeploymentNode by slug."""

    def __init__(self, repo: DeploymentNodeRepository) -> None:
        """Initialise with the deployment_node repository."""
        super().__init__(repo)

    async def execute(
        self, request: GetDeploymentNodeRequest
    ) -> GetDeploymentNodeResponse:
        """Execute the get deployment_node use case."""
        entity = await self._get_by_id(request.slug)
        return GetDeploymentNodeResponse(deployment_node=entity)


class ListDeploymentNodesRequest(BaseModel):
    """Request for listing all DeploymentNodes."""


class ListDeploymentNodesResponse(BaseModel):
    """Response for listing all DeploymentNodes."""

    deployment_nodes: list[DeploymentNode]
    total_count: int


class ListDeploymentNodesUseCase(ListUseCase[DeploymentNode, DeploymentNodeRepository]):
    """List all DeploymentNodes."""

    def __init__(self, repo: DeploymentNodeRepository) -> None:
        """Initialise with the deployment_node repository."""
        super().__init__(repo)

    async def execute(
        self, request: ListDeploymentNodesRequest
    ) -> ListDeploymentNodesResponse:
        """Execute the list deployment_nodes use case."""
        entities = await self._list_all()
        return ListDeploymentNodesResponse(
            deployment_nodes=entities, total_count=len(entities)
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

    deployment_node: DeploymentNode


class CreateDeploymentNodeUseCase(
    CreateUseCase[DeploymentNode, DeploymentNodeRepository]
):
    """Create a new DeploymentNode."""

    def __init__(self, repo: DeploymentNodeRepository) -> None:
        """Initialise with the deployment_node repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> DeploymentNode:
        """Construct a DeploymentNode from a generated ID and request fields."""
        return DeploymentNode(slug=entity_id, **kwargs)

    async def execute(
        self, request: CreateDeploymentNodeRequest
    ) -> CreateDeploymentNodeResponse:
        """Execute the create deployment_node use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            environment=request.environment,
            node_type=request.node_type,
            description=request.description,
            technology=request.technology,
            instances=request.instances,
            parent_slug=request.parent_slug,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateDeploymentNodeResponse(deployment_node=entity)


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


class UpdateDeploymentNodeResponse(BaseModel):
    """Response for updating a DeploymentNode."""

    deployment_node: DeploymentNode


class UpdateDeploymentNodeUseCase(
    UpdateUseCase[DeploymentNode, DeploymentNodeRepository]
):
    """Update a DeploymentNode."""

    def __init__(self, repo: DeploymentNodeRepository) -> None:
        """Initialise with the deployment_node repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateDeploymentNodeRequest
    ) -> UpdateDeploymentNodeResponse:
        """Execute the update deployment_node use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateDeploymentNodeResponse(deployment_node=entity)


class DeleteDeploymentNodeRequest(BaseModel):
    """Request for deleting a DeploymentNode by slug."""

    slug: str


class DeleteDeploymentNodeResponse(BaseModel):
    """Response for deleting a DeploymentNode."""

    deleted: bool


class DeleteDeploymentNodeUseCase(
    DeleteUseCase[DeploymentNode, DeploymentNodeRepository]
):
    """Delete a DeploymentNode by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: DeploymentNodeRepository) -> None:
        """Initialise with the deployment_node repository."""
        super().__init__(repo)

    async def execute(
        self, request: DeleteDeploymentNodeRequest
    ) -> DeleteDeploymentNodeResponse:
        """Execute the delete deployment_node use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteDeploymentNodeResponse(deleted=deleted)
