"""Generated CRUD messages for Journey.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.journey import Journey
from julee_hcd.domain.values.journey_step import JourneyStep


class JourneyMessage(BaseModel):
    """What a Journey is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    solution_slug: str
    docname: str
    page_title: str
    preamble_rst: str
    epilogue_rst: str
    slug: str
    persona: str
    intent: str
    outcome: str
    goal: str
    depends_on: tuple[str, ...]
    steps: tuple[JourneyStep, ...]
    preconditions: tuple[str, ...]
    postconditions: tuple[str, ...]

    @classmethod
    def of(cls, entity: Journey) -> "JourneyMessage":
        """The message for one journey."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            slug=str(entity.slug),
            persona=entity.persona,
            intent=entity.intent,
            outcome=entity.outcome,
            goal=entity.goal,
            depends_on=tuple(str(item) for item in entity.depends_on),
            steps=entity.steps,
            preconditions=entity.preconditions,
            postconditions=entity.postconditions,
        )


class GetJourneyRequest(BaseModel):
    """Request for getting a Journey by slug."""

    slug: str


class GetJourneyResponse(BaseModel):
    """Response for getting a Journey."""

    journey: JourneyMessage

    @classmethod
    def of(cls, entity: Journey) -> "GetJourneyResponse":
        """The response for the journey that was found."""
        return cls(journey=JourneyMessage.of(entity))


class ListJourneysRequest(BaseModel):
    """Request for listing all Journeys."""


class ListJourneysResponse(BaseModel):
    """Response for listing all Journeys.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    journeys: list[JourneyMessage]

    @classmethod
    def of(cls, entities: list[Journey]) -> "ListJourneysResponse":
        """The response for the journeys that were found."""
        return cls(journeys=[JourneyMessage.of(entity) for entity in entities])


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

    journey: JourneyMessage

    @classmethod
    def of(cls, entity: Journey) -> "CreateJourneyResponse":
        """The response for the journey that was created."""
        return cls(journey=JourneyMessage.of(entity))


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

    journey: JourneyMessage

    @classmethod
    def of(cls, entity: Journey) -> "UpdateJourneyResponse":
        """The response for the journey as it now is."""
        return cls(journey=JourneyMessage.of(entity))


class DeleteJourneyRequest(BaseModel):
    """Request for deleting a Journey by slug."""

    slug: str


class DeleteJourneyResponse(BaseModel):
    """Response for deleting a Journey."""

    deleted: bool
