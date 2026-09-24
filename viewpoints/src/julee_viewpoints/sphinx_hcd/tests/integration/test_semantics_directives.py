"""The semantics directives, built against a solution that has some.

These need a real project — a pyproject.toml declaring adopted kits, and
a semantics/ directory saying what the solution holds — so they get a
project of their own rather than joining the every-directive one.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PYPROJECT = """
[project]
name = "acme"
version = "0"

[tool.julee]
kits = ["hcd", "c4"]
search_root = "src"
"""

OURS = """
[adopt]
hcd = "all"
c4 = "all"

[[claim]]
id = "ours"
source = "julee_hcd.domain.models.app.App"
kind = "references"
target = "julee_hcd.domain.models.contrib.ContribModule"
note = "An app may be built on a contrib module."
"""

CONF = """
extensions = ["julee_viewpoints.semantics"]
master_doc = "index"
exclude_patterns = ["_build"]
"""

INDEX = """
Semantics
=========

.. semantics-index::

.. kit-claims::
"""


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    """A solution that adopts two kits and holds claims of its own."""
    root = tmp_path_factory.mktemp("acme")
    (root / "pyproject.toml").write_text(PYPROJECT)
    (root / "semantics").mkdir()
    (root / "semantics" / "ours.toml").write_text(OURS)
    docs = root / "docs"
    docs.mkdir()
    (docs / "conf.py").write_text(CONF)
    (docs / "index.rst").write_text(INDEX)

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(docs), str(docs / "_build")],
        capture_output=True,
        text=True,
    )
    html = (docs / "_build" / "index.html").read_text()
    return {
        "stderr": result.stderr,
        "returncode": str(result.returncode),
        "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)),
    }


def test_the_project_builds(built) -> None:
    """Reading semantics must not be able to fail a documentation build."""
    assert built["returncode"] == "0", built["stderr"]


def test_a_claim_the_solution_accepted_from_a_kit_is_shown(built) -> None:
    """Accepting is the common case and should be visible as such."""
    assert "Integration" in built["text"]
    assert "part of" in built["text"]


def test_a_claim_the_solution_made_itself_is_shown(built) -> None:
    """A solution knows things about its own words that no kit does."""
    assert "An app may be built on a contrib module." in built["text"]


def test_the_note_is_rendered_because_it_is_the_documentation(built) -> None:
    """Without the note this is configuration, not documentation."""
    assert "the accelerator is the work" in built["text"]


def test_what_a_kit_claims_is_shown_separately_from_what_is_held(
    built,
) -> None:
    """A reader should be able to see what was on offer, not only taken."""
    assert built["text"].count("part of") > 1


def test_a_kit_claim_is_attributed_to_the_kit(built) -> None:
    """Provenance is the point: a kit asserts, a solution decides."""
    assert "hcd" in built["text"]
    assert "c4" in built["text"]


def test_a_project_without_semantics_says_so_rather_than_failing(
    tmp_path: Path,
) -> None:
    """Most solutions hold nothing, and should still build."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0"\n')
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "conf.py").write_text(CONF)
    (docs / "index.rst").write_text(INDEX)

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(docs), str(docs / "_build")],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = re.sub(r"<[^>]+>", " ", (docs / "_build" / "index.html").read_text())
    assert "holds nothing" in re.sub(r"\s+", " ", text)
