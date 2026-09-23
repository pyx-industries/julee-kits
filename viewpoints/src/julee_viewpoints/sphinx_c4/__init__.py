"""Sphinx C4 Architecture Model Extension.

Provides Sphinx directives for documenting julee solutions through the
C4 Architecture viewpoint - projecting solution content in terms of
software systems, containers, components, and deployment nodes.

C4 as a Viewpoint
------------------
The C4 extension is one of the viewpoint projections in julee_viewpoints:

- ``julee_viewpoints.sphinx_hcd`` -> Human-Centered Design viewpoint
- ``julee_viewpoints.sphinx_c4`` -> Architecture viewpoint (this extension)

Both project the SAME solution content through a different lens.

C4 Model Levels
----------------
The C4 model provides four levels of abstraction:

1. **Context** - How the system fits into the world (people and other systems)
2. **Container** - High-level technology choices (APIs, databases, etc.)
3. **Component** - Logical components within containers
4. **Code** - Implementation details (typically via autodoc, not C4 directives)

Directives Provided
--------------------
Define directives: ``define-software-system``, ``define-container``,
``define-component``, ``define-relationship``, ``define-deployment-node``,
``define-dynamic-step``.

Index directives: ``software-system-index``, ``container-index``,
``component-index``, ``relationship-index``, ``deployment-node-index``.

Diagram directives: ``system-context-diagram``, ``container-diagram``,
``component-diagram``, ``system-landscape-diagram``, ``deployment-diagram``,
``dynamic-diagram``.

Usage in conf.py::

    extensions = ["julee_viewpoints.sphinx_c4"]
"""

from sphinx.util import logging

from .sphinx.context import ensure_c4_context
from .sphinx.directives import (
    ComponentDiagramDirective,
    ComponentDiagramPlaceholder,
    ComponentIndexDirective,
    ComponentIndexPlaceholder,
    ContainerDiagramDirective,
    ContainerDiagramPlaceholder,
    ContainerIndexDirective,
    ContainerIndexPlaceholder,
    DefineComponentDirective,
    DefineContainerDirective,
    DefineDeploymentNodeDirective,
    DefineDynamicStepDirective,
    DefineRelationshipDirective,
    DefineSoftwareSystemDirective,
    DeploymentDiagramDirective,
    DeploymentDiagramPlaceholder,
    DeploymentNodeIndexDirective,
    DeploymentNodeIndexPlaceholder,
    DynamicDiagramDirective,
    DynamicDiagramPlaceholder,
    RelationshipIndexDirective,
    RelationshipIndexPlaceholder,
    SoftwareSystemIndexDirective,
    SoftwareSystemIndexPlaceholder,
    SystemContextDiagramDirective,
    SystemContextDiagramPlaceholder,
    SystemLandscapeDiagramDirective,
    SystemLandscapeDiagramPlaceholder,
    process_c4_diagram_placeholders,
    process_c4_index_placeholders,
)

logger = logging.getLogger(__name__)


def setup(app):
    """Set up the C4 extension for Sphinx.

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata
    """
    # Create the C4Context when the builder starts, so every directive can
    # rely on it being there.
    app.connect("builder-inited", _init_context_handler, priority=0)

    # Register define-* directives
    app.add_directive("define-software-system", DefineSoftwareSystemDirective)
    app.add_directive("define-container", DefineContainerDirective)
    app.add_directive("define-component", DefineComponentDirective)
    app.add_directive("define-relationship", DefineRelationshipDirective)
    app.add_directive("define-deployment-node", DefineDeploymentNodeDirective)
    app.add_directive("define-dynamic-step", DefineDynamicStepDirective)

    # Register diagram directives
    app.add_directive("system-context-diagram", SystemContextDiagramDirective)
    app.add_directive("container-diagram", ContainerDiagramDirective)
    app.add_directive("component-diagram", ComponentDiagramDirective)
    app.add_directive("system-landscape-diagram", SystemLandscapeDiagramDirective)
    app.add_directive("deployment-diagram", DeploymentDiagramDirective)
    app.add_directive("dynamic-diagram", DynamicDiagramDirective)
    app.add_node(SystemContextDiagramPlaceholder)
    app.add_node(ContainerDiagramPlaceholder)
    app.add_node(ComponentDiagramPlaceholder)
    app.add_node(SystemLandscapeDiagramPlaceholder)
    app.add_node(DeploymentDiagramPlaceholder)
    app.add_node(DynamicDiagramPlaceholder)

    # Register index directives
    app.add_directive("software-system-index", SoftwareSystemIndexDirective)
    app.add_directive("container-index", ContainerIndexDirective)
    app.add_directive("component-index", ComponentIndexDirective)
    app.add_directive("relationship-index", RelationshipIndexDirective)
    app.add_directive("deployment-node-index", DeploymentNodeIndexDirective)
    app.add_node(SoftwareSystemIndexPlaceholder)
    app.add_node(ContainerIndexPlaceholder)
    app.add_node(ComponentIndexPlaceholder)
    app.add_node(RelationshipIndexPlaceholder)
    app.add_node(DeploymentNodeIndexPlaceholder)

    # Resolve placeholders once every document has been read
    app.connect("doctree-resolved", process_c4_diagram_placeholders)
    app.connect("doctree-resolved", process_c4_index_placeholders)

    logger.info("Loaded julee_viewpoints.sphinx_c4 extension")

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _init_context_handler(app):
    """Create the C4 context when the builder starts."""
    ensure_c4_context(app)
