"""Generated CRUD use cases for DeploymentNode.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_c4.domain.models.deployment_node import DeploymentNode
from julee_c4.domain.repositories.deployment_node import DeploymentNodeRepository

from ..dtos.crud_deployment_node import (
    CreateDeploymentNodeRequest,
    CreateDeploymentNodeResponse,
    DeleteDeploymentNodeRequest,
    DeleteDeploymentNodeResponse,
    GetDeploymentNodeRequest,
    GetDeploymentNodeResponse,
    ListDeploymentNodesRequest,
    ListDeploymentNodesResponse,
    UpdateDeploymentNodeRequest,
    UpdateDeploymentNodeResponse,
)


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


class CreateDeploymentNodeUseCase(
    CreateUseCase[DeploymentNode, DeploymentNodeRepository]
):
    """Create a new DeploymentNode."""

    def __init__(self, repo: DeploymentNodeRepository) -> None:
        """Initialise with the deployment_node repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> DeploymentNode:
        """Construct a DeploymentNode from a generated ID and request fields."""
        return DeploymentNode(slug=Slug(entity_id), **kwargs)

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
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateDeploymentNodeResponse(deployment_node=entity)


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
