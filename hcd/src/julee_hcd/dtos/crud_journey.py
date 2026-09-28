"""Generated CRUD messages for Journey.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.journey import Journey, JourneyStep


class GetJourneyRequest(BaseModel):
    """Request for getting a Journey by slug."""

    slug: str


class GetJourneyResponse(BaseModel):
    """Response for getting a Journey."""

    journey: Journey


class ListJourneysRequest(BaseModel):
    """Request for listing all Journeys."""


class ListJourneysResponse(BaseModel):
    """Response for listing all Journeys."""

    journeys: list[Journey]
    total_count: int


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

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateJourneyResponse(BaseModel):
    """Response for updating a Journey."""

    journey: Journey


class DeleteJourneyRequest(BaseModel):
    """Request for deleting a Journey by slug."""

    slug: str


class DeleteJourneyResponse(BaseModel):
    """Response for deleting a Journey."""

    deleted: bool
