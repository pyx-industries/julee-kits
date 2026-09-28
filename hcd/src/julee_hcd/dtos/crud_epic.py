"""Generated CRUD messages for Epic.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.epic import Epic


class GetEpicRequest(BaseModel):
    """Request for getting a Epic by slug."""

    slug: str


class GetEpicResponse(BaseModel):
    """Response for getting a Epic."""

    epic: Epic


class ListEpicsRequest(BaseModel):
    """Request for listing all Epics."""


class ListEpicsResponse(BaseModel):
    """Response for listing all Epics."""

    epics: list[Epic]
    total_count: int


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

    epic: Epic


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
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateEpicResponse(BaseModel):
    """Response for updating a Epic."""

    epic: Epic


class DeleteEpicRequest(BaseModel):
    """Request for deleting a Epic by slug."""

    slug: str


class DeleteEpicResponse(BaseModel):
    """Response for deleting a Epic."""

    deleted: bool
