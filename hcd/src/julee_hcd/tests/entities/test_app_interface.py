"""Tests for AppInterface and the C4 labels an App derives from it."""

import pytest

from julee_hcd.domain.models.app import App, AppInterface

pytestmark = pytest.mark.unit


def test_an_app_with_no_stated_interface_is_unknown() -> None:
    """Most apps are described before anyone says how they are reached."""
    assert App(slug="x", name="X").interface is AppInterface.UNKNOWN


def test_an_unrecognised_interface_name_is_unknown_rather_than_an_error() -> None:
    """Documentation should render, not fail, when a word is misspelt."""
    assert AppInterface.from_string("nonsense") is AppInterface.UNKNOWN


def test_from_string_ignores_case() -> None:
    """RST authors do not think about case."""
    assert AppInterface.from_string("MCP") is AppInterface.MCP


@pytest.mark.parametrize(
    ("interface", "label", "technology"),
    [
        (AppInterface.SPHINX, "Sphinx Extension", "Python/Sphinx"),
        (AppInterface.API, "REST API", "FastAPI"),
        (AppInterface.MCP, "MCP Server", "FastMCP"),
        (AppInterface.WEB, "Web Application", "Python"),
        (AppInterface.CLI, "CLI Tool", "Python/Click"),
        (AppInterface.UNKNOWN, "Application", "Python"),
    ],
)
def test_each_interface_labels_itself_for_a_diagram(
    interface: AppInterface, label: str, technology: str
) -> None:
    """How an app is reached is what a reader wants on the box."""
    app = App(slug="x", name="X", interface=interface)

    assert app.interface_label == label
    assert app.c4_technology == technology


def test_an_app_that_states_its_technology_is_believed() -> None:
    """The guess is a fallback, not an override."""
    app = App(slug="x", name="X", interface=AppInterface.API, technology="Go")

    assert app.c4_technology == "Go"


@pytest.mark.parametrize(
    ("interface", "from_user", "to_accelerator"),
    [
        (AppInterface.SPHINX, "Writes RST", "Documents"),
        (AppInterface.API, "HTTP", "Exposes"),
        (AppInterface.MCP, "MCP", "Provides tools for"),
        (AppInterface.WEB, "Uses", "Presents"),
        (AppInterface.CLI, "Runs", "Executes"),
        (AppInterface.UNKNOWN, "Uses", "Uses"),
    ],
)
def test_an_interface_names_the_arrows_either_side_of_it(
    interface: AppInterface, from_user: str, to_accelerator: str
) -> None:
    """A C4 arrow says how, and how depends on the interface."""
    assert interface.user_relationship == from_user
    assert interface.accelerator_relationship == to_accelerator
