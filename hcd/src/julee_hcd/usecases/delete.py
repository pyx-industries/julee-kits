"""Delete use cases for the HCD entities.

Hand-written, because julee's CRUD generator emits get, list, create and
update but not delete (julee#198). Documentation that cannot forget is
documentation that goes stale: a persona nobody kept should stop
appearing in the index.

Each reports whether anything was deleted rather than raising, since
"it was already gone" is the outcome the caller asked for.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from julee_hcd.domain.repositories.app import AppRepository
from julee_hcd.domain.repositories.base import HcdRepository
from julee_hcd.domain.repositories.contrib import ContribRepository
from julee_hcd.domain.repositories.epic import EpicRepository
from julee_hcd.domain.repositories.integration import IntegrationRepository
from julee_hcd.domain.repositories.journey import JourneyRepository
from julee_hcd.domain.repositories.persona import PersonaRepository
from julee_hcd.domain.repositories.story import StoryRepository

# Bound to the protocol that declares delete, so these use cases can call
# it without reaching past the type system for it.
R = TypeVar("R", bound=HcdRepository[Any])


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
        return bool(await self.repo.delete(slug))


class DeleteAppRequest(BaseModel):
    """Request for deleting a App."""

    slug: str


class DeleteAppResponse(BaseModel):
    """Response for deleting a App."""

    deleted: bool


class DeleteAppUseCase(_DeleteBySlug[AppRepository]):
    """Delete a App by slug."""

    async def execute(self, request: DeleteAppRequest) -> DeleteAppResponse:
        """Execute the delete app use case."""
        return DeleteAppResponse(deleted=await self._delete(request.slug))


class DeleteContribModuleRequest(BaseModel):
    """Request for deleting a ContribModule."""

    slug: str


class DeleteContribModuleResponse(BaseModel):
    """Response for deleting a ContribModule."""

    deleted: bool


class DeleteContribModuleUseCase(_DeleteBySlug[ContribRepository]):
    """Delete a ContribModule by slug."""

    async def execute(
        self, request: DeleteContribModuleRequest
    ) -> DeleteContribModuleResponse:
        """Execute the delete contrib_module use case."""
        return DeleteContribModuleResponse(deleted=await self._delete(request.slug))


class DeleteEpicRequest(BaseModel):
    """Request for deleting a Epic."""

    slug: str


class DeleteEpicResponse(BaseModel):
    """Response for deleting a Epic."""

    deleted: bool


class DeleteEpicUseCase(_DeleteBySlug[EpicRepository]):
    """Delete a Epic by slug."""

    async def execute(self, request: DeleteEpicRequest) -> DeleteEpicResponse:
        """Execute the delete epic use case."""
        return DeleteEpicResponse(deleted=await self._delete(request.slug))


class DeleteIntegrationRequest(BaseModel):
    """Request for deleting a Integration."""

    slug: str


class DeleteIntegrationResponse(BaseModel):
    """Response for deleting a Integration."""

    deleted: bool


class DeleteIntegrationUseCase(_DeleteBySlug[IntegrationRepository]):
    """Delete a Integration by slug."""

    async def execute(
        self, request: DeleteIntegrationRequest
    ) -> DeleteIntegrationResponse:
        """Execute the delete integration use case."""
        return DeleteIntegrationResponse(deleted=await self._delete(request.slug))


class DeleteJourneyRequest(BaseModel):
    """Request for deleting a Journey."""

    slug: str


class DeleteJourneyResponse(BaseModel):
    """Response for deleting a Journey."""

    deleted: bool


class DeleteJourneyUseCase(_DeleteBySlug[JourneyRepository]):
    """Delete a Journey by slug."""

    async def execute(self, request: DeleteJourneyRequest) -> DeleteJourneyResponse:
        """Execute the delete journey use case."""
        return DeleteJourneyResponse(deleted=await self._delete(request.slug))


class DeletePersonaRequest(BaseModel):
    """Request for deleting a Persona."""

    slug: str


class DeletePersonaResponse(BaseModel):
    """Response for deleting a Persona."""

    deleted: bool


class DeletePersonaUseCase(_DeleteBySlug[PersonaRepository]):
    """Delete a Persona by slug."""

    async def execute(self, request: DeletePersonaRequest) -> DeletePersonaResponse:
        """Execute the delete persona use case."""
        return DeletePersonaResponse(deleted=await self._delete(request.slug))


class DeleteStoryRequest(BaseModel):
    """Request for deleting a Story."""

    slug: str


class DeleteStoryResponse(BaseModel):
    """Response for deleting a Story."""

    deleted: bool


class DeleteStoryUseCase(_DeleteBySlug[StoryRepository]):
    """Delete a Story by slug."""

    async def execute(self, request: DeleteStoryRequest) -> DeleteStoryResponse:
        """Execute the delete story use case."""
        return DeleteStoryResponse(deleted=await self._delete(request.slug))
