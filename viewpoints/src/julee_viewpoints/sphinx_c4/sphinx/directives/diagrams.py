"""Diagram directives for sphinx_c4.

Provides directives for generating C4 diagrams as PlantUML: system context,
container, component, system landscape, deployment, and dynamic (sequence)
diagrams.

A diagram draws on elements that may have been defined by documents Sphinx
has not read yet, so every directive here leaves a placeholder node and the
diagram is actually computed and serialized by
``process_c4_diagram_placeholders`` at doctree-resolved, once every
document has been read.
"""

import os

from docutils import nodes
from docutils.parsers.rst import directives

from julee_c4.domain.repositories.component import ComponentRepository
from julee_c4.domain.repositories.container import ContainerRepository
from julee_c4.domain.repositories.deployment_node import DeploymentNodeRepository
from julee_c4.domain.repositories.dynamic_step import DynamicStepRepository
from julee_c4.domain.repositories.relationship import RelationshipRepository
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository
from julee_c4.serializers.plantuml import PlantUMLSerializer
from julee_c4.usecases.diagrams.component_diagram import (
    GetComponentDiagramRequest,
    GetComponentDiagramUseCase,
)
from julee_c4.usecases.diagrams.container_diagram import (
    GetContainerDiagramRequest,
    GetContainerDiagramUseCase,
)
from julee_c4.usecases.diagrams.deployment_diagram import (
    GetDeploymentDiagramRequest,
    GetDeploymentDiagramUseCase,
)
from julee_c4.usecases.diagrams.dynamic_diagram import (
    GetDynamicDiagramRequest,
    GetDynamicDiagramUseCase,
)
from julee_c4.usecases.diagrams.system_context import (
    GetSystemContextDiagramRequest,
    GetSystemContextDiagramUseCase,
)
from julee_c4.usecases.diagrams.system_landscape import (
    GetSystemLandscapeDiagramRequest,
    GetSystemLandscapeDiagramUseCase,
)

from ..context import C4Context, get_c4_context
from .base import C4Directive


def _make_plantuml_node(puml_source: str, docname: str) -> nodes.Node:
    """Create a PlantUML node, or a literal block if the extension is absent.

    Args:
        puml_source: PlantUML source code
        docname: Document name, for path resolution

    Returns:
        A plantuml node if ``sphinxcontrib.plantuml`` is installed,
        otherwise a literal block showing the raw source.
    """
    try:
        from sphinxcontrib.plantuml import plantuml
    except ImportError:
        return nodes.literal_block(puml_source, puml_source)

    node: nodes.Element = plantuml(puml_source)
    node["uml"] = puml_source
    node["incdir"] = os.path.dirname(docname)
    node["filename"] = os.path.basename(docname)
    return node


class DiagramDirective(C4Directive):
    """Base class for diagram directives."""

    option_spec = {
        "title": directives.unchanged,
        "format": directives.unchanged,
    }


class SystemContextDiagramPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for system-context-diagram, resolved at doctree-resolved."""

    pass


class ContainerDiagramPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for container-diagram, resolved at doctree-resolved."""

    pass


class ComponentDiagramPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for component-diagram, resolved at doctree-resolved."""

    pass


class SystemLandscapeDiagramPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for system-landscape-diagram, resolved at doctree-resolved."""

    pass


class DeploymentDiagramPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for deployment-diagram, resolved at doctree-resolved."""

    pass


class DynamicDiagramPlaceholder(nodes.General, nodes.Element):
    """Placeholder node for dynamic-diagram, resolved at doctree-resolved."""

    pass


class SystemContextDiagramDirective(DiagramDirective):
    """Generate a system context diagram.

    Usage::

        .. system-context-diagram:: banking-system
           :title: Banking System Context

    Shows the software system in its environment, with the persons and
    external systems it relates to.
    """

    required_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        system_slug = self.arguments[0]
        title = self.options.get("title", f"System Context: {system_slug}")

        node = SystemContextDiagramPlaceholder()
        node["system_slug"] = system_slug
        node["title"] = title
        return [node]


class ContainerDiagramDirective(DiagramDirective):
    """Generate a container diagram.

    Usage::

        .. container-diagram:: banking-system
           :title: Banking System Containers

    Shows the containers within a software system.
    """

    required_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        system_slug = self.arguments[0]
        title = self.options.get("title", f"Containers: {system_slug}")

        node = ContainerDiagramPlaceholder()
        node["system_slug"] = system_slug
        node["title"] = title
        return [node]


class ComponentDiagramDirective(DiagramDirective):
    """Generate a component diagram.

    Usage::

        .. component-diagram:: api-app
           :title: API Application Components

    Shows the components within a container.
    """

    required_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        container_slug = self.arguments[0]
        title = self.options.get("title", f"Components: {container_slug}")

        node = ComponentDiagramPlaceholder()
        node["container_slug"] = container_slug
        node["title"] = title
        return [node]


class SystemLandscapeDiagramDirective(DiagramDirective):
    """Generate a system landscape diagram.

    Usage::

        .. system-landscape-diagram::
           :title: Enterprise System Landscape

    Shows every software system and the relationships between them.
    """

    has_content = False

    def run(self) -> list[nodes.Node]:
        title = self.options.get("title", "System Landscape")

        node = SystemLandscapeDiagramPlaceholder()
        node["title"] = title
        return [node]


class DeploymentDiagramDirective(DiagramDirective):
    """Generate a deployment diagram.

    Usage::

        .. deployment-diagram:: production
           :title: Production Deployment

    Shows how containers are deployed to infrastructure nodes in an
    environment.
    """

    required_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        environment = self.arguments[0]
        title = self.options.get("title", f"Deployment: {environment}")

        node = DeploymentDiagramPlaceholder()
        node["environment"] = environment
        node["title"] = title
        return [node]


class DynamicDiagramDirective(DiagramDirective):
    """Generate a dynamic (sequence) diagram.

    Usage::

        .. dynamic-diagram:: user-login
           :title: User Login Flow

    Shows a sequence of interactions for a specific scenario.
    """

    required_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        sequence_name = self.arguments[0]
        title = self.options.get("title", f"Dynamic: {sequence_name}")

        node = DynamicDiagramPlaceholder()
        node["sequence_name"] = sequence_name
        node["title"] = title
        return [node]


def build_system_context_diagram(
    c4_context: C4Context, system_slug: str, title: str, docname: str
) -> list[nodes.Node]:
    """Compute and serialize a system context diagram."""
    # SyncRepositoryAdapter.async_repo is typed as the narrow structural
    # protocol the adapter itself depends on. The concrete Memory*
    # repository behind it satisfies the fuller domain protocol a diagram
    # use case wants (get_by_system, get_for_element, ...) - assert it.
    software_system_async = c4_context.software_system_repo.async_repo
    assert isinstance(software_system_async, SoftwareSystemRepository)
    relationship_async = c4_context.relationship_repo.async_repo
    assert isinstance(relationship_async, RelationshipRepository)

    use_case = GetSystemContextDiagramUseCase(software_system_async, relationship_async)
    response = c4_context.software_system_repo.run_async(
        use_case.execute(GetSystemContextDiagramRequest(system_slug=system_slug))
    )

    if not response.diagram:
        para = nodes.paragraph()
        para += nodes.emphasis(text=f"Software system '{system_slug}' not found")
        return [para]

    serializer = PlantUMLSerializer()
    puml = serializer.serialize_system_context(response.diagram, title)
    return [_make_plantuml_node(puml, docname)]


def build_container_diagram(
    c4_context: C4Context, system_slug: str, title: str, docname: str
) -> list[nodes.Node]:
    """Compute and serialize a container diagram."""
    software_system_async = c4_context.software_system_repo.async_repo
    assert isinstance(software_system_async, SoftwareSystemRepository)
    container_async = c4_context.container_repo.async_repo
    assert isinstance(container_async, ContainerRepository)
    relationship_async = c4_context.relationship_repo.async_repo
    assert isinstance(relationship_async, RelationshipRepository)

    use_case = GetContainerDiagramUseCase(
        software_system_async, container_async, relationship_async
    )
    response = c4_context.software_system_repo.run_async(
        use_case.execute(GetContainerDiagramRequest(system_slug=system_slug))
    )

    if not response.diagram:
        para = nodes.paragraph()
        para += nodes.emphasis(text=f"Software system '{system_slug}' not found")
        return [para]

    serializer = PlantUMLSerializer()
    puml = serializer.serialize_container_diagram(response.diagram, title)
    return [_make_plantuml_node(puml, docname)]


def build_component_diagram(
    c4_context: C4Context, container_slug: str, title: str, docname: str
) -> list[nodes.Node]:
    """Compute and serialize a component diagram."""
    software_system_async = c4_context.software_system_repo.async_repo
    assert isinstance(software_system_async, SoftwareSystemRepository)
    container_async = c4_context.container_repo.async_repo
    assert isinstance(container_async, ContainerRepository)
    component_async = c4_context.component_repo.async_repo
    assert isinstance(component_async, ComponentRepository)
    relationship_async = c4_context.relationship_repo.async_repo
    assert isinstance(relationship_async, RelationshipRepository)

    use_case = GetComponentDiagramUseCase(
        software_system_async, container_async, component_async, relationship_async
    )
    response = c4_context.container_repo.run_async(
        use_case.execute(GetComponentDiagramRequest(container_slug=container_slug))
    )

    if not response.diagram:
        para = nodes.paragraph()
        para += nodes.emphasis(text=f"Container '{container_slug}' not found")
        return [para]

    serializer = PlantUMLSerializer()
    puml = serializer.serialize_component_diagram(response.diagram, title)
    return [_make_plantuml_node(puml, docname)]


def build_system_landscape_diagram(
    c4_context: C4Context, title: str, docname: str
) -> list[nodes.Node]:
    """Compute and serialize a system landscape diagram."""
    software_system_async = c4_context.software_system_repo.async_repo
    assert isinstance(software_system_async, SoftwareSystemRepository)
    relationship_async = c4_context.relationship_repo.async_repo
    assert isinstance(relationship_async, RelationshipRepository)

    use_case = GetSystemLandscapeDiagramUseCase(
        software_system_async, relationship_async
    )
    response = c4_context.software_system_repo.run_async(
        use_case.execute(GetSystemLandscapeDiagramRequest())
    )

    if not response.diagram.systems:
        para = nodes.paragraph()
        para += nodes.emphasis(text="No software systems defined")
        return [para]

    serializer = PlantUMLSerializer()
    puml = serializer.serialize_system_landscape(response.diagram, title)
    return [_make_plantuml_node(puml, docname)]


def build_deployment_diagram(
    c4_context: C4Context, environment: str, title: str, docname: str
) -> list[nodes.Node]:
    """Compute and serialize a deployment diagram."""
    deployment_node_async = c4_context.deployment_node_repo.async_repo
    assert isinstance(deployment_node_async, DeploymentNodeRepository)
    container_async = c4_context.container_repo.async_repo
    assert isinstance(container_async, ContainerRepository)
    relationship_async = c4_context.relationship_repo.async_repo
    assert isinstance(relationship_async, RelationshipRepository)

    use_case = GetDeploymentDiagramUseCase(
        deployment_node_async, container_async, relationship_async
    )
    response = c4_context.deployment_node_repo.run_async(
        use_case.execute(GetDeploymentDiagramRequest(environment=environment))
    )

    if not response.diagram.nodes:
        para = nodes.paragraph()
        para += nodes.emphasis(
            text=f"No deployment nodes for environment '{environment}'"
        )
        return [para]

    serializer = PlantUMLSerializer()
    puml = serializer.serialize_deployment_diagram(response.diagram, title)
    return [_make_plantuml_node(puml, docname)]


def build_dynamic_diagram(
    c4_context: C4Context, sequence_name: str, title: str, docname: str
) -> list[nodes.Node]:
    """Compute and serialize a dynamic (sequence) diagram."""
    dynamic_step_async = c4_context.dynamic_step_repo.async_repo
    assert isinstance(dynamic_step_async, DynamicStepRepository)
    software_system_async = c4_context.software_system_repo.async_repo
    assert isinstance(software_system_async, SoftwareSystemRepository)
    container_async = c4_context.container_repo.async_repo
    assert isinstance(container_async, ContainerRepository)
    component_async = c4_context.component_repo.async_repo
    assert isinstance(component_async, ComponentRepository)

    use_case = GetDynamicDiagramUseCase(
        dynamic_step_async, software_system_async, container_async, component_async
    )
    response = c4_context.dynamic_step_repo.run_async(
        use_case.execute(GetDynamicDiagramRequest(sequence_name=sequence_name))
    )

    if not response.diagram or not response.diagram.steps:
        para = nodes.paragraph()
        para += nodes.emphasis(text=f"No dynamic steps for sequence '{sequence_name}'")
        return [para]

    serializer = PlantUMLSerializer()
    puml = serializer.serialize_dynamic_diagram(response.diagram, title)
    return [_make_plantuml_node(puml, docname)]


def process_c4_diagram_placeholders(app, doctree, docname):
    """Replace diagram placeholders with rendered content.

    Called at doctree-resolved, after every document has been read, so
    every define-* directive across the whole build has already recorded
    its element.
    """
    c4_context = get_c4_context(app)
    if c4_context is None:
        return

    for node in doctree.traverse(SystemContextDiagramPlaceholder):
        content = build_system_context_diagram(
            c4_context, node["system_slug"], node["title"], docname
        )
        node.replace_self(content)

    for node in doctree.traverse(ContainerDiagramPlaceholder):
        content = build_container_diagram(
            c4_context, node["system_slug"], node["title"], docname
        )
        node.replace_self(content)

    for node in doctree.traverse(ComponentDiagramPlaceholder):
        content = build_component_diagram(
            c4_context, node["container_slug"], node["title"], docname
        )
        node.replace_self(content)

    for node in doctree.traverse(SystemLandscapeDiagramPlaceholder):
        content = build_system_landscape_diagram(c4_context, node["title"], docname)
        node.replace_self(content)

    for node in doctree.traverse(DeploymentDiagramPlaceholder):
        content = build_deployment_diagram(
            c4_context, node["environment"], node["title"], docname
        )
        node.replace_self(content)

    for node in doctree.traverse(DynamicDiagramPlaceholder):
        content = build_dynamic_diagram(
            c4_context, node["sequence_name"], node["title"], docname
        )
        node.replace_self(content)
