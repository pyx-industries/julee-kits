"""C4 index directives for listing defined elements.

Provides directives for listing C4 elements recorded via the define-*
directives:

- ``software-system-index``: List all software systems
- ``container-index``: List all containers
- ``component-index``: List all components
- ``relationship-index``: List all relationships
- ``deployment-node-index``: List all deployment nodes

Every entity may have been defined by a document that Sphinx has not read
yet by the time an index directive runs, so - like the diagram directives -
these render via the placeholder pattern: the directive leaves a placeholder
node, and ``process_c4_index_placeholders`` fills it in at doctree-resolved,
once every document has been read.
"""

from docutils import nodes

from julee_c4.domain.models.component import Component
from julee_c4.domain.models.container import Container
from julee_c4.domain.models.deployment_node import DeploymentNode

from ..context import C4Context, get_c4_context
from .base import C4Directive


class SoftwareSystemIndexPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for software-system-index, resolved at doctree-resolved."""

    pass


class ContainerIndexPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for container-index, resolved at doctree-resolved."""

    pass


class ComponentIndexPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for component-index, resolved at doctree-resolved."""

    pass


class RelationshipIndexPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for relationship-index, resolved at doctree-resolved."""

    pass


class DeploymentNodeIndexPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for deployment-node-index, resolved at doctree-resolved."""

    pass


class SoftwareSystemIndexDirective(C4Directive):
    """List all defined software systems.

    Usage::

        .. software-system-index::

    Renders a bullet list of all software systems with their descriptions.
    """

    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        return [SoftwareSystemIndexPlaceholder()]


class ContainerIndexDirective(C4Directive):
    """List all defined containers.

    Usage::

        .. container-index::

    Renders a bullet list of all containers grouped by parent system.
    """

    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        return [ContainerIndexPlaceholder()]


class ComponentIndexDirective(C4Directive):
    """List all defined components.

    Usage::

        .. component-index::

    Renders a bullet list of all components grouped by parent container.
    """

    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        return [ComponentIndexPlaceholder()]


class RelationshipIndexDirective(C4Directive):
    """List all defined relationships.

    Usage::

        .. relationship-index::

    Renders a bullet list of all relationships between C4 elements.
    """

    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        return [RelationshipIndexPlaceholder()]


class DeploymentNodeIndexDirective(C4Directive):
    """List all defined deployment nodes.

    Usage::

        .. deployment-node-index::

    Renders a hierarchical list of deployment nodes.
    """

    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        return [DeploymentNodeIndexPlaceholder()]


def build_software_system_index(c4_context: C4Context) -> list[nodes.Node]:
    """Build a bullet list of every software system."""
    systems = {s.slug: s for s in c4_context.software_system_repo.list_all()}

    if not systems:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No software systems defined.")
        return [para]

    result_list = nodes.bullet_list()

    for slug in sorted(systems.keys()):
        system = systems[slug]
        item = nodes.list_item()
        para = nodes.paragraph()

        ref = nodes.reference("", "", refuri=f"#{slug}")
        ref += nodes.strong(text=system.name)
        para += ref

        para += nodes.Text(f" [{system.system_type.value}]")

        if system.description:
            para += nodes.Text(f" — {system.description[:80]}")
            if len(system.description) > 80:
                para += nodes.Text("...")

        item += para
        result_list += item

    return [result_list]


def build_container_index(c4_context: C4Context) -> list[nodes.Node]:
    """Build a bullet list of every container, grouped by parent system."""
    containers = {c.slug: c for c in c4_context.container_repo.list_all()}

    if not containers:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No containers defined.")
        return [para]

    by_system: dict[str, list[tuple[str, Container]]] = {}
    for slug, container in containers.items():
        by_system.setdefault(container.system_slug, []).append((slug, container))

    result_nodes: list[nodes.Node] = []

    for system_slug in sorted(by_system.keys()):
        heading = nodes.paragraph()
        heading += nodes.strong(text=system_slug.replace("-", " ").title())
        result_nodes.append(heading)

        container_list = nodes.bullet_list()

        for slug, container in sorted(by_system[system_slug], key=lambda x: x[0]):
            item = nodes.list_item()
            para = nodes.paragraph()

            ref = nodes.reference("", "", refuri=f"#{slug}")
            ref += nodes.Text(container.name)
            para += ref

            if container.technology:
                para += nodes.Text(f" [{container.technology}]")

            if container.description:
                para += nodes.Text(f" — {container.description[:60]}")
                if len(container.description) > 60:
                    para += nodes.Text("...")

            item += para
            container_list += item

        result_nodes.append(container_list)

    return result_nodes


def build_component_index(c4_context: C4Context) -> list[nodes.Node]:
    """Build a bullet list of every component, grouped by parent container."""
    components = {c.slug: c for c in c4_context.component_repo.list_all()}

    if not components:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No components defined.")
        return [para]

    by_container: dict[str, list[tuple[str, Component]]] = {}
    for slug, component in components.items():
        by_container.setdefault(component.container_slug, []).append((slug, component))

    result_nodes: list[nodes.Node] = []

    for container_slug in sorted(by_container.keys()):
        heading = nodes.paragraph()
        heading += nodes.strong(text=container_slug.replace("-", " ").title())
        result_nodes.append(heading)

        component_list = nodes.bullet_list()

        for slug, component in sorted(by_container[container_slug], key=lambda x: x[0]):
            item = nodes.list_item()
            para = nodes.paragraph()

            ref = nodes.reference("", "", refuri=f"#{slug}")
            ref += nodes.Text(component.name)
            para += ref

            if component.technology:
                para += nodes.Text(f" [{component.technology}]")

            if component.description:
                para += nodes.Text(f" — {component.description[:60]}")
                if len(component.description) > 60:
                    para += nodes.Text("...")

            item += para
            component_list += item

        result_nodes.append(component_list)

    return result_nodes


def build_relationship_index(c4_context: C4Context) -> list[nodes.Node]:
    """Build a bullet list of every relationship."""
    relationships = {r.slug: r for r in c4_context.relationship_repo.list_all()}

    if not relationships:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No relationships defined.")
        return [para]

    result_list = nodes.bullet_list()

    for rel_id in sorted(relationships.keys()):
        rel = relationships[rel_id]
        item = nodes.list_item()
        para = nodes.paragraph()

        para += nodes.literal(text=rel.source_slug)
        para += nodes.Text(" → ")
        para += nodes.literal(text=rel.destination_slug)

        if rel.description:
            para += nodes.Text(f" — {rel.description}")

        if rel.technology:
            para += nodes.Text(f" [{rel.technology}]")

        item += para
        result_list += item

    return [result_list]


def build_deployment_node_index(c4_context: C4Context) -> list[nodes.Node]:
    """Build a hierarchical list of every deployment node."""
    nodes_dict = {n.slug: n for n in c4_context.deployment_node_repo.list_all()}

    if not nodes_dict:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No deployment nodes defined.")
        return [para]

    by_parent: dict[str, list[tuple[str, DeploymentNode]]] = {"": []}
    for slug, node in nodes_dict.items():
        parent = node.parent_slug or ""
        by_parent.setdefault(parent, []).append((slug, node))

    def build_node_list(parent_slug: str) -> nodes.bullet_list:
        node_list = nodes.bullet_list()
        children = by_parent.get(parent_slug, [])

        for slug, deployment_node in sorted(children, key=lambda x: x[0]):
            item = nodes.list_item()
            para = nodes.paragraph()

            ref = nodes.reference("", "", refuri=f"#{slug}")
            ref += nodes.strong(text=deployment_node.name)
            para += ref

            if deployment_node.technology:
                para += nodes.Text(f" [{deployment_node.technology}]")

            if deployment_node.description:
                para += nodes.Text(f" — {deployment_node.description[:50]}")
                if len(deployment_node.description) > 50:
                    para += nodes.Text("...")

            item += para

            if slug in by_parent:
                item += build_node_list(slug)

            node_list += item

        return node_list

    return [build_node_list("")]


def process_c4_index_placeholders(app, doctree, docname):
    """Replace index placeholders with rendered content.

    Called at doctree-resolved, after every document has been read, so
    every define-* directive across the whole build has already recorded
    its element.
    """
    c4_context = get_c4_context(app)
    if c4_context is None:
        return

    for node in doctree.traverse(SoftwareSystemIndexPlaceholder):
        node.replace_self(build_software_system_index(c4_context))

    for node in doctree.traverse(ContainerIndexPlaceholder):
        node.replace_self(build_container_index(c4_context))

    for node in doctree.traverse(ComponentIndexPlaceholder):
        node.replace_self(build_component_index(c4_context))

    for node in doctree.traverse(RelationshipIndexPlaceholder):
        node.replace_self(build_relationship_index(c4_context))

    for node in doctree.traverse(DeploymentNodeIndexPlaceholder):
        node.replace_self(build_deployment_node_index(c4_context))
