"""Delete use cases for the C4 entities.

Hand-written, because julee's CRUD generator emits get, list, create and
update but not delete: ADR 008's base classes have no DeleteUseCase.
Deleting is part of what a repository of documented architecture needs —
a container that no longer exists should stop appearing in diagrams — so
the kit provides it until the framework does.

Each one reports whether anything was deleted rather than raising, since
"it was already gone" is the outcome the caller asked for.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

from julee_c4.domain.repositories.component import ComponentRepository
from julee_c4.domain.repositories.container import ContainerRepository
from julee_c4.domain.repositories.deployment_node import DeploymentNodeRepository
from julee_c4.domain.repositories.dynamic_step import DynamicStepRepository
from julee_c4.domain.repositories.relationship import RelationshipRepository
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository

R = TypeVar("R")


class _DeleteBySlug(Generic[R]):
    """Shared behaviour for the delete use cases below.

    Not a use case itself, and named so as not to claim to be one: it has
    no request, no response and no execute().
    """

    def __init__(self, repo: R) -> None:
        """Initialise with the entity repository."""
        self.repo = repo

    async def _delete(self, slug: str) -> bool:
        """Delete the entity, reporting whether one was there."""
        return bool(await self.repo.delete(slug))  # type: ignore[attr-defined]


class DeleteSoftwareSystemRequest(BaseModel):
    """Request for deleting a SoftwareSystem."""

    slug: str


class DeleteSoftwareSystemResponse(BaseModel):
    """Response for deleting a SoftwareSystem."""

    deleted: bool


class DeleteSoftwareSystemUseCase(_DeleteBySlug[SoftwareSystemRepository]):
    """Delete a SoftwareSystem by slug."""

    async def execute(
        self, request: DeleteSoftwareSystemRequest
    ) -> DeleteSoftwareSystemResponse:
        """Execute the delete software system use case."""
        return DeleteSoftwareSystemResponse(deleted=await self._delete(request.slug))


class DeleteContainerRequest(BaseModel):
    """Request for deleting a Container."""

    slug: str


class DeleteContainerResponse(BaseModel):
    """Response for deleting a Container."""

    deleted: bool


class DeleteContainerUseCase(_DeleteBySlug[ContainerRepository]):
    """Delete a Container by slug."""

    async def execute(self, request: DeleteContainerRequest) -> DeleteContainerResponse:
        """Execute the delete container use case."""
        return DeleteContainerResponse(deleted=await self._delete(request.slug))


class DeleteComponentRequest(BaseModel):
    """Request for deleting a Component."""

    slug: str


class DeleteComponentResponse(BaseModel):
    """Response for deleting a Component."""

    deleted: bool


class DeleteComponentUseCase(_DeleteBySlug[ComponentRepository]):
    """Delete a Component by slug."""

    async def execute(self, request: DeleteComponentRequest) -> DeleteComponentResponse:
        """Execute the delete component use case."""
        return DeleteComponentResponse(deleted=await self._delete(request.slug))


class DeleteRelationshipRequest(BaseModel):
    """Request for deleting a Relationship."""

    slug: str


class DeleteRelationshipResponse(BaseModel):
    """Response for deleting a Relationship."""

    deleted: bool


class DeleteRelationshipUseCase(_DeleteBySlug[RelationshipRepository]):
    """Delete a Relationship by slug."""

    async def execute(
        self, request: DeleteRelationshipRequest
    ) -> DeleteRelationshipResponse:
        """Execute the delete relationship use case."""
        return DeleteRelationshipResponse(deleted=await self._delete(request.slug))


class DeleteDeploymentNodeRequest(BaseModel):
    """Request for deleting a DeploymentNode."""

    slug: str


class DeleteDeploymentNodeResponse(BaseModel):
    """Response for deleting a DeploymentNode."""

    deleted: bool


class DeleteDeploymentNodeUseCase(_DeleteBySlug[DeploymentNodeRepository]):
    """Delete a DeploymentNode by slug."""

    async def execute(
        self, request: DeleteDeploymentNodeRequest
    ) -> DeleteDeploymentNodeResponse:
        """Execute the delete deployment node use case."""
        return DeleteDeploymentNodeResponse(deleted=await self._delete(request.slug))


class DeleteDynamicStepRequest(BaseModel):
    """Request for deleting a DynamicStep."""

    slug: str


class DeleteDynamicStepResponse(BaseModel):
    """Response for deleting a DynamicStep."""

    deleted: bool


class DeleteDynamicStepUseCase(_DeleteBySlug[DynamicStepRepository]):
    """Delete a DynamicStep by slug."""

    async def execute(
        self, request: DeleteDynamicStepRequest
    ) -> DeleteDynamicStepResponse:
        """Execute the delete dynamic step use case."""
        return DeleteDynamicStepResponse(deleted=await self._delete(request.slug))
