"""Generated CRUD messages for Story.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.story import Story


class GetStoryRequest(BaseModel):
    """Request for getting a Story by slug."""

    slug: str


class GetStoryResponse(BaseModel):
    """Response for getting a Story."""

    story: Story


class ListStoriesRequest(BaseModel):
    """Request for listing all Stories."""


class ListStoriesResponse(BaseModel):
    """Response for listing all Stories."""

    stories: list[Story]
    total_count: int


class CreateStoryRequest(BaseModel):
    """Request for creating a Story."""

    slug: str
    feature_title: str
    persona: str
    i_want: str
    so_that: str
    app_slug: str
    file_path: str
    abs_path: str = ""
    gherkin_snippet: str = ""
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateStoryResponse(BaseModel):
    """Response for creating a Story."""

    story: Story


class UpdateStoryRequest(BaseModel):
    """Request for updating a Story.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    feature_title: str | None = None
    persona: str | None = None
    i_want: str | None = None
    so_that: str | None = None
    app_slug: str | None = None
    file_path: str | None = None
    abs_path: str | None = None
    gherkin_snippet: str | None = None
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


class UpdateStoryResponse(BaseModel):
    """Response for updating a Story."""

    story: Story


class DeleteStoryRequest(BaseModel):
    """Request for deleting a Story by slug."""

    slug: str


class DeleteStoryResponse(BaseModel):
    """Response for deleting a Story."""

    deleted: bool
