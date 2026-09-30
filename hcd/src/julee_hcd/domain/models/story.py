"""Story domain model.

Represents a user story extracted from a Gherkin .feature file.
"""

from dataclasses import dataclass

from julee.core.utils import normalize_name, slugify
from julee.core.values.text import Name, NonEmptyText, Slug

from .base import Authored
from .epic import Epic
from .journey import Journey


@dataclass(frozen=True, kw_only=True)
class Story(Authored):
    """A user story extracted from a Gherkin feature file.

    Stories are the primary unit of user-facing functionality in HCD.
    They capture who wants to do what and why.
    """

    slug: NonEmptyText
    """Identifier, app slug and feature title joined by --."""

    feature_title: Name
    """The Feature: line from the Gherkin file."""

    file_path: str
    """Relative path to the .feature file."""

    persona: Name = Name("unknown")
    """The actor from "As a <persona>"."""

    i_want: str = "do something"
    """The action from "I want to <action>"."""

    so_that: str = "achieve a goal"
    """The benefit from "So that <benefit>"."""

    app_slug: Slug = Slug("unknown")
    """The application this story belongs to."""

    abs_path: str = ""
    """Absolute path to the .feature file."""

    gherkin_snippet: str = ""
    """The story header portion of the feature file."""

    @property
    def persona_normalized(self) -> str:
        """Lowercase persona for matching, which is Name.normalized."""
        return self.persona.normalized

    @property
    def app_normalized(self) -> str:
        """The app slug in the form names are compared in.

        Both of these were stored fields filled by a before-validator
        until #71, so a caller could write one that disagreed with the
        field it is derived from — and matching reads the stored one.

        This one normalises a *slug*, not a name, which is a separate
        problem: :meth:`matches_app` takes an app's display name and
        compares it with this, so the two agree only when the app's
        slug happens to be the slugified form of its name. Resolving a
        name to a slug needs the App repository, so it is not the
        entity's to do. Recorded on #71 and #72 rather than changed
        here.
        """
        return normalize_name(self.app_slug)

    @classmethod
    def from_feature_file(
        cls,
        feature_title: str,
        persona: str,
        i_want: str,
        so_that: str,
        app_slug: str,
        file_path: str,
        abs_path: str = "",
        gherkin_snippet: str = "",
    ) -> "Story":
        """Create a Story from parsed feature file data.

        Args:
            feature_title: The Feature: line content
            persona: The "As a" actor
            i_want: The "I want to" action
            so_that: The "So that" benefit
            app_slug: Application slug (from directory structure)
            file_path: Relative path to .feature file
            abs_path: Absolute path to .feature file
            gherkin_snippet: The story header text

        Returns:
            A new Story instance
        """
        # Include app_slug in slug to avoid collisions between apps
        return cls(
            # Not a Slug: slugify collapses the -- that keeps two
            # apps' identically titled stories apart.
            slug=NonEmptyText(f"{app_slug}--{slugify(feature_title)}"),
            feature_title=Name(feature_title),
            persona=Name(persona) if persona.strip() else Name("unknown"),
            i_want=i_want,
            so_that=so_that,
            app_slug=Slug(app_slug) if app_slug.strip() else Slug("unknown"),
            file_path=file_path,
            abs_path=abs_path,
            gherkin_snippet=gherkin_snippet,
        )

    def matches_persona(self, persona_name: str) -> bool:
        """Check if this story belongs to a persona (case-insensitive)."""
        return self.persona_normalized == normalize_name(persona_name)

    def matches_app(self, app_name: str) -> bool:
        """Check if this story belongs to an app (case-insensitive)."""
        return self.app_normalized == normalize_name(app_name)


def get_epics_for_story(
    story: Story,
    epics: list[Epic],
) -> list[Epic]:
    """Get epics that contain a specific story.

    Args:
        story: Story to find epics for
        epics: All Epic entities to search

    Returns:
        List of Epic entities containing this story, sorted by slug
    """
    story_normalized = normalize_name(story.feature_title)
    matching = []

    for epic in epics:
        if any(normalize_name(ref) == story_normalized for ref in epic.story_refs):
            matching.append(epic)

    return sorted(matching, key=lambda e: e.slug)


def get_journeys_for_story(
    story: Story,
    journeys: list[Journey],
) -> list[Journey]:
    """Get journeys that reference a specific story.

    Args:
        story: Story to find journeys for
        journeys: All Journey entities to search

    Returns:
        List of Journey entities containing this story, sorted by slug
    """
    story_normalized = normalize_name(story.feature_title)
    matching = []

    for journey in journeys:
        story_refs = journey.get_story_refs()
        if any(normalize_name(ref) == story_normalized for ref in story_refs):
            matching.append(journey)

    return sorted(matching, key=lambda j: j.slug)


def get_related_stories(
    story: Story,
    stories: list[Story],
    epics: list[Epic],
) -> list[Story]:
    """Get stories related to a story via shared epics.

    Finds other stories that are in the same epic(s) as the given story.

    Args:
        story: Story to find related stories for
        stories: All Story entities
        epics: All Epic entities

    Returns:
        List of related Story entities (excluding the input story), sorted by feature_title
    """
    # Find epics containing this story
    story_epics = get_epics_for_story(story, epics)

    # Collect all story refs from those epics
    related_refs: set[str] = set()
    for epic in story_epics:
        for ref in epic.story_refs:
            related_refs.add(normalize_name(ref))

    # Remove the original story
    story_normalized = normalize_name(story.feature_title)
    related_refs.discard(story_normalized)

    # Find matching stories
    related = []
    for s in stories:
        if normalize_name(s.feature_title) in related_refs:
            related.append(s)

    return sorted(related, key=lambda s: s.feature_title)
