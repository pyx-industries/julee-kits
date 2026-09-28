"""C4 Diagram domain models.

These models represent the computed data for various C4 diagram types.
They are domain objects that can be serialized to different output formats
(PlantUML, Structurizr DSL, etc.) by serializers.
"""

from dataclasses import dataclass, field

from .component import Component
from .container import Container
from .deployment_node import DeploymentNode
from .dynamic_step import DynamicStep
from .relationship import Relationship
from .software_system import SoftwareSystem


@dataclass(frozen=True)
class PersonInfo:
    """Minimal person info for diagrams.

    Represents a user/actor in C4 diagrams. This is a lightweight
    representation used when full Person entities aren't needed.
    """

    slug: str
    name: str
    description: str = ""


@dataclass(frozen=True)
class SystemLandscapeDiagram:
    """Domain model for a C4 System Landscape diagram.

    Shows all software systems and their relationships at the highest level.
    """

    systems: tuple[SoftwareSystem, ...] = field(default_factory=tuple)
    person_slugs: tuple[str, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemContextDiagram:
    """Domain model for a C4 System Context diagram.

    Shows a single system in context with its users and external systems.
    """

    system: SoftwareSystem
    external_systems: tuple[SoftwareSystem, ...] = field(default_factory=tuple)
    person_slugs: tuple[str, ...] = field(default_factory=tuple)
    persons: tuple[PersonInfo, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ContainerDiagram:
    """Domain model for a C4 Container diagram.

    Shows the containers within a software system.
    """

    system: SoftwareSystem
    containers: tuple[Container, ...] = field(default_factory=tuple)
    external_systems: tuple[SoftwareSystem, ...] = field(default_factory=tuple)
    person_slugs: tuple[str, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ComponentDiagram:
    """Domain model for a C4 Component diagram.

    Shows the components within a container.
    """

    system: SoftwareSystem
    container: Container
    components: tuple[Component, ...] = field(default_factory=tuple)
    external_containers: tuple[Container, ...] = field(default_factory=tuple)
    external_systems: tuple[SoftwareSystem, ...] = field(default_factory=tuple)
    person_slugs: tuple[str, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DeploymentDiagram:
    """Domain model for a C4 Deployment diagram.

    Shows the deployment infrastructure for an environment.
    """

    environment: str
    nodes: tuple[DeploymentNode, ...] = field(default_factory=tuple)
    containers: tuple[Container, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DynamicDiagram:
    """Domain model for a C4 Dynamic diagram.

    Shows a sequence of interactions for a specific scenario.
    """

    sequence_name: str
    steps: tuple[DynamicStep, ...] = field(default_factory=tuple)
    systems: tuple[SoftwareSystem, ...] = field(default_factory=tuple)
    containers: tuple[Container, ...] = field(default_factory=tuple)
    components: tuple[Component, ...] = field(default_factory=tuple)
    person_slugs: tuple[str, ...] = field(default_factory=tuple)
