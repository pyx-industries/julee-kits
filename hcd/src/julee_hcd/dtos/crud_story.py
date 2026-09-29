"""Generated CRUD messages for Story.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.story import Story


class StoryMessage(BaseModel):
    """What a Story is, as a use case reports it.

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
    feature_title: str
    file_path: str
    persona: str
    i_want: str
    so_that: str
    app_slug: str
    abs_path: str
    gherkin_snippet: str

    @classmethod
    def of(cls, entity: Story) -> "StoryMessage":
        """The message for one story."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            slug=str(entity.slug),
            feature_title=str(entity.feature_title),
            file_path=entity.file_path,
            persona=str(entity.persona),
            i_want=entity.i_want,
            so_that=entity.so_that,
            app_slug=str(entity.app_slug),
            abs_path=entity.abs_path,
            gherkin_snippet=entity.gherkin_snippet,
        )


class GetStoryRequest(BaseModel):
    """Request for getting a Story by slug."""

    slug: str


class GetStoryResponse(BaseModel):
    """Response for getting a Story."""

    story: StoryMessage

    @classmethod
    def of(cls, entity: Story) -> "GetStoryResponse":
        """The response for the story that was found."""
        return cls(story=StoryMessage.of(entity))


class ListStoriesRequest(BaseModel):
    """Request for listing all Stories."""


class ListStoriesResponse(BaseModel):
    """Response for listing all Stories.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    stories: list[StoryMessage]

    @classmethod
    def of(cls, entities: list[Story]) -> "ListStoriesResponse":
        """The response for the stories that were found."""
        return cls(stories=[StoryMessage.of(entity) for entity in entities])


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

    story: StoryMessage

    @classmethod
    def of(cls, entity: Story) -> "CreateStoryResponse":
        """The response for the story that was created."""
        return cls(story=StoryMessage.of(entity))


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

    story: StoryMessage

    @classmethod
    def of(cls, entity: Story) -> "UpdateStoryResponse":
        """The response for the story as it now is."""
        return cls(story=StoryMessage.of(entity))


class DeleteStoryRequest(BaseModel):
    """Request for deleting a Story by slug."""

    slug: str


class DeleteStoryResponse(BaseModel):
    """Response for deleting a Story."""

    deleted: bool
