"""How personas are worked out from what the stories say.

These lived in usecases/ and had no direct tests at all: they were
exercised only through DerivePersonasUseCase, and the three it does not
call were exercised only by the sphinx directives that build the docs.
Being pure is what made them easy to leave untested and is also what
makes testing them cheap.
"""

import pytest
from julee.core.entities.text import Name, NonEmptyText, Slug

from julee_hcd.domain.models.app import App, AppType
from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.models.persona import (
    Persona,
    derive_personas_by_app_type,
    derive_personas_from_stories,
    get_apps_for_persona,
    get_epics_for_persona,
    merge_personas,
)
from julee_hcd.domain.models.story import Story

pytestmark = pytest.mark.unit


def a_story(persona: str, app: str, title: str) -> Story:
    """A story told by a persona about an app.

    Args:
        persona: Who tells it
        app: The app it is about
        title: Its Feature: line

    Returns:
        The story
    """
    return Story(
        slug=NonEmptyText(f"{app}--{title.lower().replace(' ', '-')}"),
        feature_title=Name(title),
        persona=Name(persona),
        i_want="to do a thing",
        so_that="something follows",
        app_slug=Slug(app),
        file_path=f"features/{title}.feature",
    )


STORIES = [
    a_story("Knowledge Curator", "library", "Search"),
    a_story("Casual Reader", "library", "Browse"),
    a_story("Knowledge Curator", "atlas", "Chart"),
]
EPICS = [Epic(slug=Slug("finding"), story_refs=("Search",))]


class TestDerivingFromStories:
    """Personas nobody wrote up, found in the "As a..." clauses."""

    def test_it_finds_one_per_persona_a_story_names(self) -> None:
        """Not one per story: the curator tells two."""
        found = derive_personas_from_stories(STORIES, EPICS)

        assert [p.name for p in found] == ["Casual Reader", "Knowledge Curator"]

    def test_it_collects_every_app_a_persona_turns_up_in(self) -> None:
        """The curator's two stories are about two different apps."""
        curator = next(
            p
            for p in derive_personas_from_stories(STORIES, EPICS)
            if p.name == "Knowledge Curator"
        )

        assert curator.app_slugs == ("atlas", "library")

    def test_it_collects_the_epics_a_persona_s_stories_belong_to(self) -> None:
        """Reached through the epic's story_refs, not the story itself."""
        curator = next(
            p
            for p in derive_personas_from_stories(STORIES, EPICS)
            if p.name == "Knowledge Curator"
        )

        assert curator.epic_slugs == ("finding",)

    def test_a_story_telling_of_nobody_is_skipped(self) -> None:
        """Story.persona defaults to "unknown", which is not a persona."""
        found = derive_personas_from_stories(
            [*STORIES, a_story("unknown", "library", "Drift")], EPICS
        )

        assert "unknown" not in [p.name for p in found]

    def test_it_answers_the_same_thing_twice(self) -> None:
        """Deterministic is what makes it a calculator."""
        assert derive_personas_from_stories(
            STORIES, EPICS
        ) == derive_personas_from_stories(STORIES, EPICS)


class TestMerging:
    """What was authored, plus what the stories add.

    This is the calculation two use cases were reaching through each
    other to share.
    """

    def test_what_was_written_about_a_persona_stands(self) -> None:
        """The stories add to a defined persona; they do not replace it."""
        defined = Persona(
            name=Name("Knowledge Curator"), goals=("Keep the record true",)
        )

        merged = merge_personas([defined], STORIES, EPICS)

        assert [p.goals for p in merged if p.name == "Knowledge Curator"] == [
            ("Keep the record true",)
        ]

    def test_a_defined_persona_gains_what_its_stories_say(self) -> None:
        """Apps and epics come off the stories, not the definition."""
        defined = Persona(name=Name("Knowledge Curator"))

        curator = next(
            p
            for p in merge_personas([defined], STORIES, EPICS)
            if p.name == "Knowledge Curator"
        )

        assert curator.app_slugs == ("atlas", "library")
        assert curator.epic_slugs == ("finding",)

    def test_a_persona_only_a_story_mentions_is_still_there(self) -> None:
        """Most personas are never written up."""
        merged = merge_personas(
            [Persona(name=Name("Knowledge Curator"))], STORIES, EPICS
        )

        assert "Casual Reader" in [p.name for p in merged]

    def test_a_defined_persona_no_story_mentions_is_still_there(self) -> None:
        """Written up before anyone told a story about them."""
        merged = merge_personas([Persona(name=Name("Archivist"))], STORIES, EPICS)

        assert "Archivist" in [p.name for p in merged]

    def test_it_counts_a_persona_once(self) -> None:
        """Defined and derived are the same persona, not two."""
        merged = merge_personas(
            [Persona(name=Name("Knowledge Curator"))], STORIES, EPICS
        )

        assert [p.name for p in merged].count(Name("Knowledge Curator")) == 1

    def test_with_nothing_defined_it_is_the_derivation(self) -> None:
        """Which is what a solution with no PersonaRepository gets."""
        assert merge_personas([], STORIES, EPICS) == derive_personas_from_stories(
            STORIES, EPICS
        )


class TestLookingUpWhatAPersonaUses:
    """The two the sphinx directives call and nothing else did."""

    def test_it_finds_the_apps_a_persona_names(self) -> None:
        """By slug, in the order the persona holds them."""
        apps = [
            App(slug=Slug("library"), name=Name("Library")),
            App(slug=Slug("atlas"), name=Name("Atlas")),
        ]
        persona = Persona(name=Name("Curator"), app_slugs=(Slug("library"),))

        assert [a.slug for a in get_apps_for_persona(persona, apps)] == ["library"]

    def test_an_app_slug_naming_nothing_is_dropped(self) -> None:
        """A persona derived from a story about an app nobody declared."""
        persona = Persona(
            name=Name("Curator"), app_slugs=(Slug("library"), Slug("ghost"))
        )

        found = get_apps_for_persona(
            persona, [App(slug=Slug("library"), name=Name("Library"))]
        )

        assert [a.slug for a in found] == ["library"]

    def test_it_finds_the_epics_holding_a_persona_s_stories(self) -> None:
        """Matched through the epic's story_refs by normalized title."""
        persona = Persona(name=Name("Knowledge Curator"))

        found = get_epics_for_persona(persona, EPICS, STORIES)

        assert [e.slug for e in found] == ["finding"]

    def test_an_epic_holding_nobody_else_s_stories_is_not_theirs(self) -> None:
        """The reader's story is in no epic."""
        persona = Persona(name=Name("Casual Reader"))

        assert get_epics_for_persona(persona, EPICS, STORIES) == []


class TestGroupingByAppType:
    """What the persona index page is built from."""

    def test_it_groups_a_persona_under_each_type_it_uses(self) -> None:
        """The curator's two apps are of two different types."""
        apps = [
            App(slug=Slug("library"), name=Name("Library"), app_type=AppType.STAFF),
            App(slug=Slug("atlas"), name=Name("Atlas"), app_type=AppType.EXTERNAL),
        ]

        grouped = derive_personas_by_app_type(STORIES, EPICS, apps)

        assert "Knowledge Curator" in [p.name for p in grouped[AppType.STAFF.value]]
        assert "Knowledge Curator" in [p.name for p in grouped[AppType.EXTERNAL.value]]

    def test_an_app_nobody_declared_groups_as_unknown(self) -> None:
        """Rather than dropping the persona out of the index entirely."""
        grouped = derive_personas_by_app_type(STORIES, EPICS, [])

        assert "unknown" in grouped
