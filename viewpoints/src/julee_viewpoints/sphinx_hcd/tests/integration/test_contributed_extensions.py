"""A solution gets its extensions from the kits it adopts.

The kit declares what it provides; until julee 0.5.10 nothing read that,
so a conf.py named this kit's modules by hand and went stale whenever
the kit gained one. This builds a project that names none of them.
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
kits = ["viewpoints"]
search_root = "src"
"""

CONF = """
from pathlib import Path

from julee.core.kits import sphinx_extensions

extensions = sphinx_extensions(Path(__file__).parent.parent)
master_doc = "index"
exclude_patterns = ["_build"]
"""

INDEX = """
Acme
====

.. define-persona:: knowledge-curator
   :name: Knowledge Curator

.. persona-index::

.. define-software-system:: library-system
   :name: Library System
   :type: internal

.. semantics-index::
"""


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    """A solution whose conf.py names no module of this kit."""
    root = tmp_path_factory.mktemp("acme")
    (root / "pyproject.toml").write_text(PYPROJECT)
    docs = root / "docs"
    docs.mkdir()
    (docs / "conf.py").write_text(CONF)
    (docs / "index.rst").write_text(INDEX)

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(docs), str(docs / "_build")],
        capture_output=True,
        text=True,
    )
    html = (
        (docs / "_build" / "index.html").read_text() if result.returncode == 0 else ""
    )
    return {
        "returncode": str(result.returncode),
        "stderr": result.stderr,
        "conf": CONF,
        "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)),
    }


def test_the_project_builds(built) -> None:
    """Asking the kits for extensions has to actually produce extensions."""
    assert built["returncode"] == "0", built["stderr"]


def test_the_conf_names_no_module_of_this_kit(built) -> None:
    """Which is the point: the manifest already says what to load."""
    assert "julee_viewpoints." not in built["conf"]


def test_the_hcd_directives_are_registered(built) -> None:
    """The first extension the kit contributes."""
    assert "Knowledge Curator" in built["text"]


def test_the_c4_directives_are_registered(built) -> None:
    """The second, which a hand-written conf.py would have had to know about."""
    assert "Library System" in built["text"]


def test_the_semantics_directives_are_registered(built) -> None:
    """And the third."""
    assert "holds nothing" in built["text"]


def test_a_solution_may_still_name_extensions_itself(tmp_path: Path) -> None:
    """Asking the kits is a convenience, not the only way in."""
    (tmp_path / "pyproject.toml").write_text(PYPROJECT)
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "conf.py").write_text(
        'extensions = ["julee_viewpoints.sphinx_hcd"]\n'
        'master_doc = "index"\nexclude_patterns = ["_build"]\n'
    )
    (docs / "index.rst").write_text(
        "Acme\n====\n\n.. define-persona:: curator\n   :name: Curator\n"
    )

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(docs), str(docs / "_build")],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
