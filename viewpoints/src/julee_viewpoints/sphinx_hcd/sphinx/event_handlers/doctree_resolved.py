"""Doctree-resolved event handler for sphinx_hcd.

Processes placeholders that need cross-document data (all documents read).
"""

from julee_viewpoints.sphinx_hcd.sphinx.directives.accelerator import (
    process_accelerator_placeholders,
)
from julee_viewpoints.sphinx_hcd.sphinx.directives.app import process_app_placeholders
from julee_viewpoints.sphinx_hcd.sphinx.directives.contrib import (
    process_contrib_placeholders,
)
from julee_viewpoints.sphinx_hcd.sphinx.directives.epic import process_epic_placeholders
from julee_viewpoints.sphinx_hcd.sphinx.directives.integration import (
    process_integration_placeholders,
)
from julee_viewpoints.sphinx_hcd.sphinx.directives.journey import (
    process_dependency_graph_placeholder,
)
from julee_viewpoints.sphinx_hcd.sphinx.directives.persona import (
    process_persona_placeholders,
)


def on_doctree_resolved(app, doctree, docname):
    """Process doctree after all documents are read.

    This handler runs after ALL documents have been read, allowing
    cross-document references to be resolved.

    Args:
        app: Sphinx application instance
        doctree: The document tree
        docname: The document name
    """
    # Process app placeholders (need story/journey/epic registries)
    process_app_placeholders(app, doctree, docname)

    # Process epic placeholders (need story registry)
    process_epic_placeholders(app, doctree, docname)

    # Process accelerator placeholders (need many registries)
    process_accelerator_placeholders(app, doctree, docname)

    # Process integration placeholders
    process_integration_placeholders(app, doctree, docname)

    # Process persona diagram placeholders (need epic/story registries)
    process_persona_placeholders(app, doctree, docname)

    # Process contrib placeholders (need contrib registry)
    process_contrib_placeholders(app, doctree, docname)

    # Process journey dependency graph placeholder (needs all journeys)
    process_dependency_graph_placeholder(app, doctree, docname)
