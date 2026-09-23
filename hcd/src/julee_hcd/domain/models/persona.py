"""Persona domain model.

A persona arrives one of two ways. Someone writes one, giving it goals,
frustrations and the jobs it is trying to get done; or one is derived from
the "As a ..." of a user story, which yields little more than a name.

Both are the same entity. is_defined tells them apart, and a derived
persona can be written up later without becoming a different thing.
"""

from typing import Self

from julee.core.utils import normalize_name, slugify
from pydantic import Field, computed_field, field_validator

from .base import Authored


class Persona(Authored):
    """A kind of person the solution is for.

    Personas are the "As a ..." in "As a [persona], I want to ...", and
    what the people writing the solution down know about them.
    """

    name: str = Field(
        description='Display name of the persona (e.g., "Knowledge Curator")'
    )
    slug: str = Field(
        default="",
        description="Identifier; derived from the name when not given",
    )
    goals: tuple[str, ...] = Field(
        default_factory=tuple,
        description="What this persona is trying to achieve",
    )
    frustrations: tuple[str, ...] = Field(
        default_factory=tuple,
        description="What gets in this persona's way today",
    )
    jobs_to_be_done: tuple[str, ...] = Field(
        default_factory=tuple,
        description="The jobs this persona hires the solution to do",
    )
    context: str = Field(
        default="",
        description="The circumstances this persona works in",
    )
    app_slugs: tuple[str, ...] = Field(
        default_factory=tuple, description="List of app slugs this persona uses"
    )
    epic_slugs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="List of epic slugs containing stories for this persona",
    )
    accelerator_slugs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Accelerators this persona's work draws on",
    )
    contrib_slugs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Contrib modules this persona's work draws on",
    )

    def model_post_init(self, __context: object) -> None:
        """Derive the slug from the name when none was given.

        A persona derived from a story has only a name to be identified
        by, so the name is what the slug comes from.
        """
        if not self.slug:
            object.__setattr__(self, "slug", slugify(self.name))

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def normalized_name(self) -> str:
        """Get normalized name for matching."""
        return normalize_name(self.name)

    @property
    def display_name(self) -> str:
        """Get formatted name for display (same as name)."""
        return self.name

    @property
    def app_count(self) -> int:
        """Get number of apps this persona uses."""
        return len(self.app_slugs)

    @property
    def epic_count(self) -> int:
        """Get number of epics this persona participates in."""
        return len(self.epic_slugs)

    @property
    def has_apps(self) -> bool:
        """Check if persona uses any apps."""
        return len(self.app_slugs) > 0

    @property
    def has_epics(self) -> bool:
        """Check if persona participates in any epics."""
        return len(self.epic_slugs) > 0

    def uses_app(self, app_slug: str) -> bool:
        """Check if persona uses a specific app.

        Args:
            app_slug: App slug to check

        Returns:
            True if persona uses this app
        """
        return app_slug in self.app_slugs

    def participates_in_epic(self, epic_slug: str) -> bool:
        """Check if persona participates in a specific epic.

        Args:
            epic_slug: Epic slug to check

        Returns:
            True if persona has stories in this epic
        """
        return epic_slug in self.epic_slugs

    def with_app(self, app_slug: str) -> "Persona":
        """The persona with an app added; a duplicate returns this persona.

        Args:
            app_slug: App slug to add
        """
        if app_slug in self.app_slugs:
            return self
        return self.model_copy(update={"app_slugs": (*self.app_slugs, app_slug)})

    def with_epic(self, epic_slug: str) -> "Persona":
        """The persona with an epic added; a duplicate returns this persona.

        Args:
            epic_slug: Epic slug to add
        """
        if epic_slug in self.epic_slugs:
            return self
        return self.model_copy(update={"epic_slugs": (*self.epic_slugs, epic_slug)})

    @property
    def is_defined(self) -> bool:
        """Whether someone wrote this persona up, rather than it being derived.

        A persona derived from a story has a name and nothing else to say
        about the person behind it.
        """
        return bool(
            self.goals or self.frustrations or self.jobs_to_be_done or self.context
        )

    @classmethod
    def from_definition(
        cls,
        slug: str,
        name: str,
        goals: tuple[str, ...] = (),
        frustrations: tuple[str, ...] = (),
        jobs_to_be_done: tuple[str, ...] = (),
        context: str = "",
        docname: str = "",
    ) -> Self:
        """A persona somebody wrote up, with what they know about them.

        Args:
            slug: Identifier for the persona
            name: Display name
            goals: What the persona is trying to achieve
            frustrations: What gets in their way today
            jobs_to_be_done: The jobs they hire the solution to do
            context: The circumstances they work in
            docname: Document the persona was written in
        """
        return cls(
            slug=slug,
            name=name,
            goals=goals,
            frustrations=frustrations,
            jobs_to_be_done=jobs_to_be_done,
            context=context,
            docname=docname,
        )

    @classmethod
    def from_story_reference(cls, name: str, app_slug: str = "") -> Self:
        """A persona derived from the "As a ..." of a story.

        All that is known is the name, and which app the story was about.

        Args:
            name: The persona named in the story
            app_slug: App the story belongs to, if any
        """
        return cls(name=name, app_slugs=(app_slug,) if app_slug else ())
