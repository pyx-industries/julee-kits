"""Generated CRUD use cases for Journey.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_hcd.domain.models.journey import Journey, JourneyStep
from julee_hcd.domain.repositories.journey import JourneyRepository


class GetJourneyRequest(BaseModel):
    """Request for getting a Journey by slug."""

    slug: str


class GetJourneyResponse(BaseModel):
    """Response for getting a Journey."""

    journey: Journey


class GetJourneyUseCase(GetUseCase[Journey, JourneyRepository]):
    """Get a Journey by slug."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: GetJourneyRequest) -> GetJourneyResponse:
        """Execute the get journey use case."""
        entity = await self._get_by_id(request.slug)
        return GetJourneyResponse(journey=entity)


class ListJourneysRequest(BaseModel):
    """Request for listing all Journeys."""


class ListJourneysResponse(BaseModel):
    """Response for listing all Journeys."""

    journeys: list[Journey]
    total_count: int


class ListJourneysUseCase(ListUseCase[Journey, JourneyRepository]):
    """List all Journeys."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: ListJourneysRequest) -> ListJourneysResponse:
        """Execute the list journeys use case."""
        entities = await self._list_all()
        return ListJourneysResponse(journeys=entities, total_count=len(entities))


class CreateJourneyRequest(BaseModel):
    """Request for creating a Journey."""

    slug: str
    persona: str = ""
    intent: str = ""
    outcome: str = ""
    goal: str = ""
    depends_on: tuple[str, ...] = ()
    steps: tuple[JourneyStep, ...] = ()
    preconditions: tuple[str, ...] = ()
    postconditions: tuple[str, ...] = ()
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateJourneyResponse(BaseModel):
    """Response for creating a Journey."""

    journey: Journey


class CreateJourneyUseCase(CreateUseCase[Journey, JourneyRepository]):
    """Create a new Journey."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> Journey:
        """Construct a Journey from a generated ID and request fields."""
        return Journey(slug=entity_id, **kwargs)

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
        return CreateJourneyResponse(journey=entity)


class UpdateJourneyRequest(BaseModel):
    """Request for updating a Journey.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    persona: str | None = None
    intent: str | None = None
    outcome: str | None = None
    goal: str | None = None
    depends_on: tuple[str, ...] | None = None
    steps: tuple[JourneyStep, ...] | None = None
    preconditions: tuple[str, ...] | None = None
    postconditions: tuple[str, ...] | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdateJourneyResponse(BaseModel):
    """Response for updating a Journey."""

    journey: Journey


class UpdateJourneyUseCase(UpdateUseCase[Journey, JourneyRepository]):
    """Update a Journey."""

    def __init__(self, repo: JourneyRepository) -> None:
        """Initialise with the journey repository."""
        super().__init__(repo)

    async def execute(self, request: UpdateJourneyRequest) -> UpdateJourneyResponse:
        """Execute the update journey use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateJourneyResponse(journey=entity)
