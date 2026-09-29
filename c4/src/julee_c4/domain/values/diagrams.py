"""The C4 diagrams this context works out.

Values, not entities (ADR 018). A diagram is assembled on demand from
the elements and relationships that were asked for; nothing keeps one
under an id, and two diagrams of the same contents are the same
diagram. They were read as entities because of the directory they sat
in, which would have made any port returning one look bound to an
aggregate it has not got.

They are still serialized to PlantUML and Structurizr DSL by the
serializers, which is the only thing done with them.
"""

from dataclasses import dataclass, field

from ..models.component import Component
from ..models.container import Container
from ..models.deployment_node import DeploymentNode
from ..models.dynamic_step import DynamicStep
from ..models.relationship import Relationship
from ..models.software_system import SoftwareSystem


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
