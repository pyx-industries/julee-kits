"""Tests for the fields every authored HCD entity carries.

Exercised through Epic, because the base is not an entity anyone creates
on its own and the point is that its fields arrive on the real ones.
"""

import pytest

from julee_hcd.domain.models.epic import Epic

pytestmark = pytest.mark.unit


def test_an_entity_that_was_never_written_down_has_the_fields_empty() -> None:
    """Nothing is required, so an entity built in code is still valid."""
    epic = Epic(slug="onboarding")

    assert epic.solution_slug == ""
    assert epic.docname == ""
    assert epic.page_title == ""
    assert epic.preamble_rst == ""
    assert epic.epilogue_rst == ""


def test_the_prose_around_a_directive_is_kept_verbatim() -> None:
    """The round-trip is lossless only if what is not modelled survives."""
    epic = Epic(
        slug="onboarding",
        docname="epics/onboarding",
        page_title="Getting people started",
        preamble_rst="Some words before.\n",
        epilogue_rst="Some words after.\n",
    )

    assert epic.preamble_rst == "Some words before.\n"
    assert epic.epilogue_rst == "Some words after.\n"
    assert epic.page_title == "Getting people started"


def test_an_entity_knows_which_solution_it_belongs_to() -> None:
    """One site may document more than one solution."""
    assert Epic(slug="onboarding", solution_slug="shop").solution_slug == "shop"
