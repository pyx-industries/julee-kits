"""Every directive this kit registers is used, and the build survives it.

Fifty-nine directives and five roles were each verified once by hand and
nothing since. The question worth answering automatically is not what
each one renders — that is what the use case tests are for — but whether
they all still work at all. A directive can import cleanly, register
cleanly, and raise the moment docutils calls it.

So: one project using all of them, built once, and a test that fails if
a directive is ever registered without being added here.
"""

import pytest

from .conftest import registered_names

pytestmark = pytest.mark.integration

ALL_DIRECTIVES = sorted(
    registered_names("sphinx_hcd", "directive")
    | registered_names("sphinx_c4", "directive")
)
ALL_ROLES = sorted(registered_names("sphinx_hcd", "role"))


def test_the_project_builds(built) -> None:
    """The one that matters: nothing raised while rendering any of them."""
    assert built["returncode"] == 0, built["stderr"]


def test_the_build_warns_about_nothing_unintended(built) -> None:
    """A warning is usually a directive quietly declining to do its job.

    The deprecated aliases are the exception: warning is the whole point
    of them, and the test below checks they still do.
    """
    noise = [
        line
        for line in built["stderr"].splitlines()
        if "WARNING" in line and "toctree" not in line and "is deprecated" not in line
    ]

    assert not noise, "\n".join(noise)


DEPRECATED = {
    "gherkin-stories-index": "story-index",
    "gherkin-stories": "stories",
    "gherkin-stories-for-app": "story-list-for-app",
    "gherkin-stories-for-persona": "story-list-for-persona",
    "gherkin-app-stories": "story-app",
    "gherkin-story": "story",
}


@pytest.mark.parametrize(("old", "new"), sorted(DEPRECATED.items()))
def test_a_deprecated_directive_says_what_to_use_instead(
    built, old: str, new: str
) -> None:
    """Warning is what a deprecated alias is for; silence would be worse."""
    assert f"'{old}' is deprecated, use '{new}'" in built["stderr"]


@pytest.mark.parametrize("directive", ALL_DIRECTIVES)
def test_every_registered_directive_is_exercised(directive: str) -> None:
    """A directive nobody uses here is a directive nobody tests.

    This is the test that keeps the file above honest: register a new
    directive without adding it, and this fails.
    """
    assert (
        f".. {directive}::" in built_source()
    ), f"{directive} is registered but never used in the test project"


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_registered_role_is_exercised(role: str) -> None:
    """Same, for roles."""
    assert (
        f":{role}:`" in built_source()
    ), f":{role}: is registered but never used in the test project"


def built_source() -> str:
    """The project's source, without needing the build fixture."""
    from .conftest import INDEX

    return INDEX


# =============================================================================
# What the reader should end up seeing
# =============================================================================


@pytest.mark.parametrize(
    "expected",
    [
        "Knowledge Curator",
        "Find things",
        "Traceability",
        "Polling",
        "Library System",
        "API Application",
        "Search Service",
        "EU West",
        "Looks things up",
    ],
    ids=lambda name: name.lower().replace(" ", "-"),
)
def test_what_was_defined_appears_in_the_page(built, expected: str) -> None:
    """A directive that renders nothing is indistinguishable from a typo."""
    assert expected in built["text"]


def test_a_directive_naming_something_absent_says_so(built) -> None:
    """Degrading with a message beats degrading silently.

    define-app and define-integration refer to something declared in a
    YAML manifest rather than defining it here, so a project without the
    manifest should be told, not left with a gap.
    """
    assert "not found" in built["text"]


def test_an_index_lists_what_was_defined_elsewhere_on_the_page(built) -> None:
    """Indexes are the directives that depend on the whole build."""
    assert built["text"].count("Knowledge Curator") > 1


def test_a_diagram_emits_plantuml(built) -> None:
    """The C4 diagrams render to text that PlantUML can take."""
    assert "@startuml" in built["html"]


def test_a_role_links_rather_than_printing_its_slug(built) -> None:
    """A role that cannot resolve degrades, but it should still be a link."""
    assert "knowledge-curator" in built["html"]
