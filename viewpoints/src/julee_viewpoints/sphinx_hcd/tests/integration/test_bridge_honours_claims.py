"""A C4 diagram borrows an HCD persona only when the solution says so.

c4 claims that the people on its diagrams are the personas HCD
describes. A claim is an assertion its author is not entitled to act on,
so the bridge asks the solution first. A solution that has said nothing
gets bare slugs — the same as if the HCD viewpoint were not loaded.
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

ACCEPTING = """
[adopt]
c4 = ["person-is-a-persona"]
"""

DECLINING = """
[adopt]
c4 = "none"
"""

CONF = """
extensions = [
    "julee_viewpoints.sphinx_hcd",
    "julee_viewpoints.sphinx_c4",
    "julee_viewpoints.c4_bridge",
]
master_doc = "index"
exclude_patterns = ["_build"]
"""

INDEX = """
Diagram
=======

.. define-persona:: knowledge-curator
   :name: Knowledge Curator

.. define-software-system:: library-system
   :name: Library System
   :type: internal

.. define-relationship::
   :from: person:knowledge-curator
   :to: library-system
   :description: Looks things up

.. system-context-diagram:: library-system
"""


def build(root: Path, semantics: str | None) -> str:
    """Build a solution, optionally declaring what it holds.

    Args:
        root: Where to write the solution
        semantics: What to put in semantics/ours.toml, or None for none

    Returns:
        The rendered page's text
    """
    (root / "pyproject.toml").write_text(PYPROJECT)
    if semantics is not None:
        (root / "semantics").mkdir()
        (root / "semantics" / "ours.toml").write_text(semantics)
    docs = root / "docs"
    docs.mkdir()
    (docs / "conf.py").write_text(CONF)
    (docs / "index.rst").write_text(INDEX)

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(docs), str(docs / "_build")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return (docs / "_build" / "index.html").read_text()


def test_a_solution_that_accepts_the_claim_gets_the_persona_s_name(
    tmp_path: Path,
) -> None:
    """The claim is what lets the diagram borrow rather than repeat."""
    html = build(tmp_path, ACCEPTING)

    assert 'Person(knowledge_curator, "Knowledge Curator"' in html


def test_a_solution_that_has_said_nothing_gets_the_bare_slug(
    tmp_path: Path,
) -> None:
    """Silence is not consent: adopting c4 is not accepting its opinions."""
    html = build(tmp_path, semantics=None)

    assert 'Person(knowledge_curator, "knowledge-curator")' in html
    assert "Knowledge Curator" not in re.sub(r"<[^>]+>", " ", html).replace(
        "knowledge-curator", ""
    )


def test_a_solution_that_declines_the_claim_gets_the_bare_slug(
    tmp_path: Path,
) -> None:
    """Declining is how a solution disagrees, and it must be honoured."""
    html = build(tmp_path, DECLINING)

    assert 'Person(knowledge_curator, "knowledge-curator")' in html


def test_the_diagram_is_drawn_either_way(tmp_path: Path) -> None:
    """Declining a claim costs a description, not a diagram."""
    html = build(tmp_path, semantics=None)

    assert "@startuml" in html
    assert "library_system" in html
