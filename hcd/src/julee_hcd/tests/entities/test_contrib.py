"""Tests for the ContribModule entity."""

import pytest
from pydantic import ValidationError

from julee_hcd.domain.models.contrib import ContribModule

pytestmark = pytest.mark.unit


def test_a_module_needs_a_slug_to_be_referred_to() -> None:
    """Personas and documents point at contrib modules by slug."""
    with pytest.raises(ValidationError, match="slug cannot be empty"):
        ContribModule(slug="")


def test_display_title_falls_back_to_a_readable_slug() -> None:
    """A module nobody named is still worth naming in a diagram."""
    module = ContribModule(slug="polling-workflow")

    assert module.display_title == "Polling Workflow"


def test_display_title_prefers_the_name_it_was_given() -> None:
    """A name somebody chose beats one derived from punctuation."""
    module = ContribModule(slug="polling-workflow", name="Polling")

    assert module.display_title == "Polling"


def test_c4_description_falls_back_to_saying_what_it_is() -> None:
    """An undescribed module should not leave an empty box."""
    module = ContribModule(slug="polling-workflow")

    assert module.c4_description == "Polling Workflow utility"


def test_a_module_is_python_unless_it_says_otherwise() -> None:
    """The usual answer, so most modules need not give one."""
    assert ContribModule(slug="x").technology == "Python"


def test_a_module_carries_the_document_it_was_written_in() -> None:
    """Contrib modules are authored, so they round-trip like the rest."""
    module = ContribModule(slug="x", docname="contrib/index", preamble_rst="intro")

    assert module.docname == "contrib/index"
    assert module.preamble_rst == "intro"
