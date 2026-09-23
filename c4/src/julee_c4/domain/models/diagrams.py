"""C4 Diagram domain models.

These models represent the computed data for various C4 diagram types.
They are domain objects that can be serialized to different output formats
(PlantUML, Structurizr DSL, etc.) by serializers.
"""

from julee.core.entities.entity import Entity
from pydantic import Field

from .component import Component
from .container import Container
from .deployment_node import DeploymentNode
from .dynamic_step import DynamicStep
from .relationship import Relationship
from .software_system import SoftwareSystem


class PersonInfo(Entity):
    """Minimal person info for diagrams.

    Represents a user/actor in C4 diagrams. This is a lightweight
    representation used when full Person entities aren't needed.
    """

    slug: str
    name: str
    description: str = ""


class SystemLandscapeDiagram(Entity):
    """Domain model for a C4 System Landscape diagram.

    Shows all software systems and their relationships at the highest level.
    """

    systems: tuple[SoftwareSystem, ...] = Field(default_factory=tuple)
    person_slugs: tuple[str, ...] = Field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = Field(default_factory=tuple)


class SystemContextDiagram(Entity):
    """Domain model for a C4 System Context diagram.

    Shows a single system in context with its users and external systems.
    """

    system: SoftwareSystem
    external_systems: tuple[SoftwareSystem, ...] = Field(default_factory=tuple)
    person_slugs: tuple[str, ...] = Field(default_factory=tuple)
    persons: tuple[PersonInfo, ...] = Field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = Field(default_factory=tuple)


class ContainerDiagram(Entity):
    """Domain model for a C4 Container diagram.

    Shows the containers within a software system.
    """

    system: SoftwareSystem
    containers: tuple[Container, ...] = Field(default_factory=tuple)
    external_systems: tuple[SoftwareSystem, ...] = Field(default_factory=tuple)
    person_slugs: tuple[str, ...] = Field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = Field(default_factory=tuple)


class ComponentDiagram(Entity):
    """Domain model for a C4 Component diagram.

    Shows the components within a container.
    """

    system: SoftwareSystem
    container: Container
    components: tuple[Component, ...] = Field(default_factory=tuple)
    external_containers: tuple[Container, ...] = Field(default_factory=tuple)
    external_systems: tuple[SoftwareSystem, ...] = Field(default_factory=tuple)
    person_slugs: tuple[str, ...] = Field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = Field(default_factory=tuple)


class DeploymentDiagram(Entity):
    """Domain model for a C4 Deployment diagram.

    Shows the deployment infrastructure for an environment.
    """

    environment: str
    nodes: tuple[DeploymentNode, ...] = Field(default_factory=tuple)
    containers: tuple[Container, ...] = Field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = Field(default_factory=tuple)


class DynamicDiagram(Entity):
    """Domain model for a C4 Dynamic diagram.

    Shows a sequence of interactions for a specific scenario.
    """

    sequence_name: str
    steps: tuple[DynamicStep, ...] = Field(default_factory=tuple)
    systems: tuple[SoftwareSystem, ...] = Field(default_factory=tuple)
    containers: tuple[Container, ...] = Field(default_factory=tuple)
    components: tuple[Component, ...] = Field(default_factory=tuple)
    person_slugs: tuple[str, ...] = Field(default_factory=tuple)
