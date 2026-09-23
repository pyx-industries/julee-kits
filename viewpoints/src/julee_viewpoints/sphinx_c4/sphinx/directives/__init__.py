"""Sphinx directives for sphinx_c4.

Thin directive adapters that use C4 domain models and the repositories on
``C4Context``.
"""

from .base import C4Directive, parse_element_ref
from .component import DefineComponentDirective
from .container import DefineContainerDirective
from .deployment_node import DefineDeploymentNodeDirective
from .diagrams import (
    ComponentDiagramDirective,
    ComponentDiagramPlaceholder,
    ContainerDiagramDirective,
    ContainerDiagramPlaceholder,
    DeploymentDiagramDirective,
    DeploymentDiagramPlaceholder,
    DynamicDiagramDirective,
    DynamicDiagramPlaceholder,
    SystemContextDiagramDirective,
    SystemContextDiagramPlaceholder,
    SystemLandscapeDiagramDirective,
    SystemLandscapeDiagramPlaceholder,
    process_c4_diagram_placeholders,
)
from .dynamic_step import DefineDynamicStepDirective
from .indexes import (
    ComponentIndexDirective,
    ComponentIndexPlaceholder,
    ContainerIndexDirective,
    ContainerIndexPlaceholder,
    DeploymentNodeIndexDirective,
    DeploymentNodeIndexPlaceholder,
    RelationshipIndexDirective,
    RelationshipIndexPlaceholder,
    SoftwareSystemIndexDirective,
    SoftwareSystemIndexPlaceholder,
    process_c4_index_placeholders,
)
from .relationship import DefineRelationshipDirective
from .software_system import DefineSoftwareSystemDirective

__all__ = [
    # Base
    "C4Directive",
    "parse_element_ref",
    # Define directives
    "DefineSoftwareSystemDirective",
    "DefineContainerDirective",
    "DefineComponentDirective",
    "DefineRelationshipDirective",
    "DefineDeploymentNodeDirective",
    "DefineDynamicStepDirective",
    # Diagram directives
    "SystemContextDiagramDirective",
    "SystemContextDiagramPlaceholder",
    "ContainerDiagramDirective",
    "ContainerDiagramPlaceholder",
    "ComponentDiagramDirective",
    "ComponentDiagramPlaceholder",
    "SystemLandscapeDiagramDirective",
    "SystemLandscapeDiagramPlaceholder",
    "DeploymentDiagramDirective",
    "DeploymentDiagramPlaceholder",
    "DynamicDiagramDirective",
    "DynamicDiagramPlaceholder",
    "process_c4_diagram_placeholders",
    # Index directives
    "SoftwareSystemIndexDirective",
    "SoftwareSystemIndexPlaceholder",
    "ContainerIndexDirective",
    "ContainerIndexPlaceholder",
    "ComponentIndexDirective",
    "ComponentIndexPlaceholder",
    "RelationshipIndexDirective",
    "RelationshipIndexPlaceholder",
    "DeploymentNodeIndexDirective",
    "DeploymentNodeIndexPlaceholder",
    "process_c4_index_placeholders",
]
