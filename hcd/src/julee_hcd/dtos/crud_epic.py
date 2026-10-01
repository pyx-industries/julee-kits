"""Generated CRUD messages for Epic.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.epic import Epic


class EpicMessage(BaseModel):
    """What a Epic is, as a use case reports it.

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
    description: str
    story_refs: tuple[str, ...]

    @classmethod
    def of(cls, entity: Epic) -> "EpicMessage":
        """The message for one epic."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            slug=str(entity.slug),
            description=entity.description,
            story_refs=entity.story_refs,
        )


class GetEpicRequest(BaseModel):
    """Request for getting a Epic by slug."""

    slug: str


class GetEpicResponse(BaseModel):
    """Response for getting a Epic."""

    epic: EpicMessage

    @classmethod
    def of(cls, entity: Epic) -> "GetEpicResponse":
        """The response for the epic that was found."""
        return cls(epic=EpicMessage.of(entity))


class ListEpicsRequest(BaseModel):
    """Request for listing all Epics."""


class ListEpicsResponse(BaseModel):
    """Response for listing all Epics.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    epics: list[EpicMessage]

    @classmethod
    def of(cls, entities: list[Epic]) -> "ListEpicsResponse":
        """The response for the epics that were found."""
        return cls(epics=[EpicMessage.of(entity) for entity in entities])


class CreateEpicRequest(BaseModel):
    """Request for creating a Epic."""

    slug: str
    description: str = ""
    story_refs: tuple[str, ...] = ()
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateEpicResponse(BaseModel):
    """Response for creating a Epic."""

    epic: EpicMessage

    @classmethod
    def of(cls, entity: Epic) -> "CreateEpicResponse":
        """The response for the epic that was created."""
        return cls(epic=EpicMessage.of(entity))


class UpdateEpicRequest(BaseModel):
    """Request for updating a Epic.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    description: str | None = None
    story_refs: tuple[str, ...] | None = None
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
        return {
            name: getattr(self, name)
            for name in self.model_fields_set
            if name != "slug"
        }


class UpdateEpicResponse(BaseModel):
    """Response for updating a Epic."""

    epic: EpicMessage

    @classmethod
    def of(cls, entity: Epic) -> "UpdateEpicResponse":
        """The response for the epic as it now is."""
        return cls(epic=EpicMessage.of(entity))


class DeleteEpicRequest(BaseModel):
    """Request for deleting a Epic by slug."""

    slug: str


class DeleteEpicResponse(BaseModel):
    """Response for deleting a Epic."""

    deleted: bool
