"""Tests for personas somebody wrote up, as against ones derived.

The published viewpoints copy of this entity had only derived personas.
These cover what authoring one means, which is what the archived version
knew and the copy had lost.
"""

from typing import Any

import pytest

from julee_hcd.domain.models.persona import Persona

pytestmark = pytest.mark.unit


def test_a_persona_derives_its_slug_from_its_name() -> None:
    """A persona out of a story has a name and nothing else to be keyed by."""
    assert Persona(name="Knowledge Curator").slug == "knowledge-curator"


def test_a_persona_keeps_a_slug_it_was_given() -> None:
    """Derivation is a fallback, not a rule about what slugs may be."""
    assert Persona(name="Knowledge Curator", slug="curator").slug == "curator"


def test_a_persona_with_only_a_name_is_not_defined() -> None:
    """Being mentioned in a story is not the same as being described."""
    assert Persona(name="Knowledge Curator").is_defined is False


@pytest.mark.parametrize(
    "written",
    [
        {"goals": ("Find things",)},
        {"frustrations": ("Search is slow",)},
        {"jobs_to_be_done": ("Answer a question",)},
        {"context": "Works in a reading room"},
    ],
)
def test_any_one_thing_written_about_a_persona_makes_it_defined(
    written: dict[str, Any],
) -> None:
    """Whichever part somebody filled in, the persona has been described."""
    assert Persona(name="Knowledge Curator", **written).is_defined is True


def test_from_definition_keeps_everything_it_was_told() -> None:
    """Authoring a persona is the point of the richer fields."""
    persona = Persona.from_definition(
        slug="curator",
        name="Knowledge Curator",
        goals=("Find things",),
        frustrations=("Search is slow",),
        jobs_to_be_done=("Answer a question",),
        context="Works in a reading room",
        docname="personas/curator",
    )

    assert persona.slug == "curator"
    assert persona.goals == ("Find things",)
    assert persona.frustrations == ("Search is slow",)
    assert persona.jobs_to_be_done == ("Answer a question",)
    assert persona.context == "Works in a reading room"
    assert persona.docname == "personas/curator"
    assert persona.is_defined is True


def test_from_story_reference_knows_only_the_name_and_the_app() -> None:
    """All a story says is "As a [persona]", and which app it was about."""
    persona = Persona.from_story_reference("Knowledge Curator", app_slug="library")

    assert persona.name == "Knowledge Curator"
    assert persona.app_slugs == ("library",)
    assert persona.goals == ()
    assert persona.is_defined is False


def test_from_story_reference_without_an_app_lists_none() -> None:
    """An empty app slug is not an app."""
    assert Persona.from_story_reference("Knowledge Curator").app_slugs == ()


def test_a_persona_can_name_the_accelerators_and_contribs_it_draws_on() -> None:
    """These are the links to the rest of a solution's documentation."""
    persona = Persona(
        name="Knowledge Curator",
        accelerator_slugs=("traceability",),
        contrib_slugs=("polling-workflow",),
    )

    assert persona.accelerator_slugs == ("traceability",)
    assert persona.contrib_slugs == ("polling-workflow",)


def test_a_derived_persona_can_be_written_up_without_changing_identity() -> None:
    """Both kinds are the same entity; describing one does not replace it."""
    derived = Persona.from_story_reference("Knowledge Curator")

    written = derived.model_copy(update={"goals": ("Find things",)})

    assert written.slug == derived.slug
    assert derived.is_defined is False
    assert written.is_defined is True
