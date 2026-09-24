"""A documentation project that uses every directive this kit registers.

Built once and inspected by the tests beside this. One build rather than
one per directive, because the thing worth knowing about fifty-nine
directives is mostly whether they all still work at all — and a build is
the only place that answer is honest, since a directive can import, be
registered, and still raise the moment docutils calls it.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CONF = """
extensions = ["julee_viewpoints.sphinx_hcd", "julee_viewpoints.sphinx_c4"]
master_doc = "index"
exclude_patterns = ["_build"]
html_theme = "basic"
"""

# Written so that every directive has something real to render: an index
# only proves anything when something has been defined for it to find.
INDEX = """
Everything
==========

.. define-persona:: knowledge-curator
   :name: Knowledge Curator
   :goals: Find things

.. define-app:: library

.. define-accelerator:: traceability
   :status: active

.. define-integration:: catalogue-feed

.. define-contrib:: polling
   :name: Polling
   :technology: Python

.. define-epic:: finding

   .. epic-story:: Search the catalogue

.. define-journey:: first-visit
   :persona: Knowledge Curator
   :intent: Find something
   :outcome: Found it

   .. step-epic:: finding

   .. step-story:: Search the catalogue

   .. step-phase:: Afterwards

.. define-software-system:: library-system
   :name: Library System
   :type: internal

.. define-container:: api-app
   :name: API Application
   :system: library-system
   :type: api

.. define-component:: search-service
   :name: Search Service
   :container: api-app
   :system: library-system

.. define-relationship::
   :from: knowledge-curator
   :to: library-system
   :description: Looks things up

.. define-deployment-node:: eu-west
   :name: EU West
   :environment: production

.. define-dynamic-step::
   :sequence: lookup
   :step: 1
   :from: knowledge-curator
   :to: library-system
   :description: Searches

Indexes and lists
-----------------

.. persona-index::

.. app-index::

.. accelerator-index::

.. integration-index::

.. contrib-index::

.. contrib-list::

.. epic-index::

.. journey-index::

.. story-index::

.. stories::

.. software-system-index::

.. container-index::

.. component-index::

.. relationship-index::

.. deployment-node-index::

.. gherkin-stories-index::

.. gherkin-stories::

Cross references
----------------

.. apps-for-persona:: knowledge-curator

.. epics-for-persona:: knowledge-curator

.. journeys-for-persona:: knowledge-curator

.. accelerators-for-app:: library

.. dependent-accelerators:: traceability

.. accelerator-status:: traceability

.. story-list-for-app:: library

.. story-list-for-persona:: knowledge-curator

.. gherkin-stories-for-app:: library

.. gherkin-stories-for-persona:: knowledge-curator

.. gherkin-app-stories:: library

.. gherkin-story:: search-the-catalogue

.. story:: search-the-catalogue

.. story-app:: library

Diagrams
--------

.. entity-graph::
   :format: table

.. persona-diagram:: knowledge-curator

.. persona-index-diagram:: knowledge-curator

.. journey-dependency-graph::

.. accelerator-dependency-diagram::

.. system-context-diagram:: library-system

.. container-diagram:: library-system

.. component-diagram:: api-app

.. system-landscape-diagram::

.. deployment-diagram:: production

.. dynamic-diagram:: lookup

Roles
-----

A :persona:`knowledge-curator`, an :epic:`finding`, a :journey:`first-visit`,
a :story:`search-the-catalogue` and an :accelerator:`traceability`.
"""


@pytest.fixture(scope="session")
def built(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    """Build the project once, and hand back what happened.

    Returns:
        The build's return code, its stderr, and the rendered HTML
    """
    root = tmp_path_factory.mktemp("everything")
    (root / "conf.py").write_text(CONF)
    (root / "index.rst").write_text(INDEX)
    out = root / "_build"

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(root), str(out)],
        capture_output=True,
        text=True,
    )
    html = (out / "index.html").read_text() if (out / "index.html").exists() else ""
    shutil.rmtree(out, ignore_errors=True)
    return {
        "returncode": result.returncode,
        "stderr": result.stderr,
        "stdout": result.stdout,
        "html": html,
        "text": re.sub(r"<[^>]+>", " ", html),
        "source": INDEX,
    }


def registered_names(module: str, kind: str) -> set[str]:
    """What a setup() actually registers.

    Read out of the source rather than by running setup(), which would
    need a Sphinx application to register into.

    Args:
        module: "sphinx_hcd" or "sphinx_c4"
        kind: "directive" or "role"

    Returns:
        The names registered
    """
    here = Path(__file__).resolve()
    root = here.parents[3]
    package = root / module / "__init__.py"
    if not package.exists():
        package = root / f"{module}.py"
    pattern = rf"add_{kind}\(\s*[\"']([a-z0-9-]+)"
    return set(re.findall(pattern, package.read_text()))
