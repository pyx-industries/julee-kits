"""Generated CRUD use cases for Journey.

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

from julee_hcd.domain.models.journey import Journey
from julee_hcd.domain.repositories.journey import JourneyRepository

from ..dtos.crud_journey import (
    CreateJourneyRequest,
    CreateJourneyResponse,
    DeleteJourneyRequest,
    DeleteJourneyResponse,
    GetJourneyRequest,
    GetJourneyResponse,
    ListJourneysRequest,
    ListJourneysResponse,
    UpdateJourneyRequest,
    UpdateJourneyResponse,
)


class GetJourneyUseCase(GetUseCase[Journey, JourneyRepository]):
    """Get a Journey by slug."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: GetJourneyRequest) -> GetJourneyResponse:
        """Execute the get journey use case."""
        entity = await self._get_by_id(request.slug)
        return GetJourneyResponse.of(entity)


class ListJourneysUseCase(ListUseCase[Journey, JourneyRepository]):
    """List all Journeys."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: ListJourneysRequest) -> ListJourneysResponse:
        """Execute the list journeys use case."""
        entities = await self._list_all()
        return ListJourneysResponse.of(entities)


class CreateJourneyUseCase(CreateUseCase[Journey, JourneyRepository]):
    """Create a new Journey."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Journey:
        """Construct a Journey from a generated ID and request fields."""
        return Journey(slug=Slug(entity_id), **kwargs)

    async def execute(self, request: CreateJourneyRequest) -> CreateJourneyResponse:
        """Execute the create journey use case."""
        entity = await self._create(
            entity_id=request.slug,
            persona=request.persona,
            intent=request.intent,
            outcome=request.outcome,
            goal=request.goal,
            depends_on=request.depends_on,
            steps=request.steps,
            preconditions=request.preconditions,
            postconditions=request.postconditions,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateJourneyResponse.of(entity)


class UpdateJourneyUseCase(UpdateUseCase[Journey, JourneyRepository]):
    """Update a Journey."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateJourneyRequest) -> UpdateJourneyResponse:
        """Execute the update journey use case."""
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateJourneyResponse.of(entity)


class DeleteJourneyUseCase(DeleteUseCase[Journey, JourneyRepository]):
    """Delete a Journey by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: DeleteJourneyRequest) -> DeleteJourneyResponse:
        """Execute the delete journey use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteJourneyResponse(deleted=deleted)
