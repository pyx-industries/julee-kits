"""Tests for PlantUMLSerializer.

The dynamic diagram is covered here because it was the one path that read
fields the model does not have, and nothing exercised it.
"""

import pytest

from julee_c4.domain.models.component import Component
from julee_c4.domain.models.container import Container, ContainerType
from julee_c4.domain.models.deployment_node import DeploymentNode
from julee_c4.domain.models.diagrams import (
    ComponentDiagram,
    ContainerDiagram,
    DeploymentDiagram,
    DynamicDiagram,
    PersonInfo,
    SystemContextDiagram,
    SystemLandscapeDiagram,
)
from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType, Relationship
from julee_c4.domain.models.software_system import SoftwareSystem, SystemType
from julee_c4.serializers.plantuml import PlantUMLSerializer

pytestmark = pytest.mark.unit


def _step(**overrides: object) -> DynamicStep:
    """A step with the fields every dynamic step needs."""
    fields: dict[str, object] = {
        "sequence_name": "checkout",
        "step_number": 1,
        "source_type": ElementType.CONTAINER,
        "source_slug": "api_app",
        "destination_type": ElementType.CONTAINER,
        "destination_slug": "database",
        "description": "Reads the basket",
    }
    fields.update(overrides)
    return DynamicStep(**fields)  # type: ignore[arg-type]


@pytest.fixture
def diagram() -> DynamicDiagram:
    """A one-step sequence between two containers."""
    return DynamicDiagram(
        sequence_name="checkout",
        steps=(_step(),),
        containers=(
            Container(
                slug="api_app",
                name="API Application",
                system_slug="shop",
                container_type=ContainerType.API,
            ),
            Container(
                slug="database",
                name="Database",
                system_slug="shop",
                container_type=ContainerType.DATABASE,
            ),
        ),
    )


def test_a_dynamic_diagram_renders_its_steps(diagram: DynamicDiagram) -> None:
    """The regression test: this path used to raise on the first step."""
    output = PlantUMLSerializer().serialize_dynamic_diagram(diagram)

    assert 'Rel(api_app, database, "1. Reads the basket")' in output


def test_a_step_with_a_return_value_renders_the_way_back(
    diagram: DynamicDiagram,
) -> None:
    """A described return is drawn as a relationship back to the source."""
    with_return = diagram.model_copy(
        update={"steps": (_step(return_value="The basket"),)}
    )

    output = PlantUMLSerializer().serialize_dynamic_diagram(with_return)

    assert 'Rel(database, api_app, "The basket")' in output


def test_a_step_without_a_return_value_draws_only_one_way(
    diagram: DynamicDiagram,
) -> None:
    """Silence about a return is not a return."""
    output = PlantUMLSerializer().serialize_dynamic_diagram(diagram)

    assert output.count("Rel(") == 1


def test_a_step_technology_is_carried_into_the_relationship(
    diagram: DynamicDiagram,
) -> None:
    """How a step happens belongs on the arrow that shows it happening."""
    with_tech = diagram.model_copy(update={"steps": (_step(technology="HTTPS"),)})

    output = PlantUMLSerializer().serialize_dynamic_diagram(with_tech)

    assert 'Rel(api_app, database, "1. Reads the basket", "HTTPS")' in output


# =============================================================================
# Identifiers
# =============================================================================


def _deployment(instance_count: int = 1) -> DeploymentDiagram:
    """A node with one container deployed on it."""
    node = DeploymentNode(slug="eu-west", name="EU West").with_container_instance(
        "api-app", instance_count=instance_count
    )
    return DeploymentDiagram(environment="production", nodes=(node,))


def test_a_deployment_diagram_renders_what_is_deployed_on_a_node() -> None:
    """The regression: this read a field ContainerInstance does not have."""
    output = PlantUMLSerializer().serialize_deployment_diagram(_deployment())

    assert "api_app" in output


def test_a_single_instance_is_not_labelled_with_its_count() -> None:
    """One of something is the usual case and says nothing worth saying."""
    output = PlantUMLSerializer().serialize_deployment_diagram(_deployment(1))

    assert '"1 instances"' not in output


def test_several_instances_say_how_many() -> None:
    """More than one is the thing a reader wants on the box."""
    output = PlantUMLSerializer().serialize_deployment_diagram(_deployment(3))

    assert "3 instances" in output


def test_hyphenated_slugs_become_valid_plantuml_identifiers(
    diagram: DynamicDiagram,
) -> None:
    """A C4 slug is hyphenated; a PlantUML identifier may not be."""
    hyphenated = diagram.model_copy(
        update={
            "steps": (_step(source_slug="api-app", destination_slug="the-database"),)
        }
    )

    output = PlantUMLSerializer().serialize_dynamic_diagram(hyphenated)

    assert "Rel(api_app, the_database," in output
    assert "Rel(api-app" not in output


# =============================================================================
# The four diagrams nothing had ever exercised
#
# Both the two that were tested had bugs in them, each found by something
# other than a test. These cover the rest.
# =============================================================================


def _system(slug: str = "shop", name: str = "Shop") -> SoftwareSystem:
    """A software system with a description worth rendering."""
    return SoftwareSystem(slug=slug, name=name, description=f"The {name.lower()}")


def _container(slug: str = "api-app", system: str = "shop") -> Container:
    """A container belonging to a system."""
    return Container(
        slug=slug,
        name="API Application",
        system_slug=system,
        container_type=ContainerType.API,
        description="Serves the shop",
    )


def _rel(source: str = "customer", destination: str = "shop") -> Relationship:
    """A relationship between two elements."""
    return Relationship(
        source_type=ElementType.PERSON,
        source_slug=source,
        destination_type=ElementType.SOFTWARE_SYSTEM,
        destination_slug=destination,
        description="Buys things",
    )


class TestSystemContext:
    """The diagram that answers "how does this fit into the world?"."""

    def test_the_system_is_drawn_with_its_description(self) -> None:
        """The one element the diagram is actually about."""
        diagram = SystemContextDiagram(system=_system())

        output = PlantUMLSerializer().serialize_system_context(diagram)

        assert 'System(shop, "Shop", "The shop")' in output

    def test_an_external_system_is_drawn_differently(self) -> None:
        """Telling ours from theirs is the point of a context diagram."""
        diagram = SystemContextDiagram(
            system=_system(),
            external_systems=(_system(slug="payments", name="Payments"),),
        )

        output = PlantUMLSerializer().serialize_system_context(diagram)

        assert "System_Ext(payments," in output
        assert "System_Ext(shop," not in output

    def test_a_person_nobody_has_described_is_drawn_by_slug(self) -> None:
        """The HCD side may be absent; a diagram should still render."""
        diagram = SystemContextDiagram(system=_system(), person_slugs=("customer",))

        output = PlantUMLSerializer().serialize_system_context(diagram)

        assert 'Person(customer, "customer")' in output

    def test_a_described_person_is_drawn_with_their_name(self) -> None:
        """What c4_bridge exists to supply."""
        diagram = SystemContextDiagram(
            system=_system(),
            person_slugs=("customer",),
            persons=(
                PersonInfo(slug="customer", name="Customer", description="Buys things"),
            ),
        )

        output = PlantUMLSerializer().serialize_system_context(diagram)

        assert 'Person(customer, "Customer", "Buys things")' in output

    def test_a_described_person_with_no_description_is_still_named(self) -> None:
        """A name alone is worth more than a slug."""
        diagram = SystemContextDiagram(
            system=_system(),
            person_slugs=("customer",),
            persons=(PersonInfo(slug="customer", name="Customer"),),
        )

        output = PlantUMLSerializer().serialize_system_context(diagram)

        assert 'Person(customer, "Customer")' in output

    def test_hyphenated_person_slugs_become_valid_identifiers(self) -> None:
        """Every identifier in every diagram, not just the ones checked."""
        diagram = SystemContextDiagram(
            system=_system(), person_slugs=("returning-customer",)
        )

        output = PlantUMLSerializer().serialize_system_context(diagram)

        assert "Person(returning_customer," in output


class TestContainerDiagram:
    """The diagram that answers "what is this built from?"."""

    def test_containers_are_drawn_inside_their_system(self) -> None:
        """The containers are the point of this one."""
        diagram = ContainerDiagram(system=_system(), containers=(_container(),))

        output = PlantUMLSerializer().serialize_container_diagram(diagram)

        assert "Container(api_app," in output

    def test_a_hyphenated_container_slug_is_a_valid_identifier(self) -> None:
        """The bug class that shipped in four diagrams at once."""
        diagram = ContainerDiagram(system=_system(), containers=(_container(),))

        output = PlantUMLSerializer().serialize_container_diagram(diagram)

        assert "Container(api-app" not in output

    def test_relationships_are_drawn_between_elements(self) -> None:
        """A diagram of boxes with no arrows says very little."""
        diagram = ContainerDiagram(
            system=_system(), containers=(_container(),), relationships=(_rel(),)
        )

        output = PlantUMLSerializer().serialize_container_diagram(diagram)

        assert "Rel(customer, shop," in output


class TestComponentDiagram:
    """The diagram that answers "what is inside this container?"."""

    def test_components_are_drawn(self) -> None:
        """The components are the point of this one."""
        diagram = ComponentDiagram(
            system=_system(),
            container=_container(),
            components=(
                Component(
                    slug="order-service",
                    name="Order Service",
                    container_slug="api-app",
                    system_slug="shop",
                ),
            ),
        )

        output = PlantUMLSerializer().serialize_component_diagram(diagram)

        assert "Component(order_service," in output

    def test_an_external_container_is_drawn_differently(self) -> None:
        """Something this container talks to but does not contain."""
        diagram = ComponentDiagram(
            system=_system(),
            container=_container(),
            external_containers=(_container(slug="billing-app"),),
        )

        output = PlantUMLSerializer().serialize_component_diagram(diagram)

        assert "billing_app" in output


class TestSystemLandscape:
    """The diagram that answers "what systems are there at all?"."""

    def test_every_system_is_drawn(self) -> None:
        """A landscape with a missing system is a wrong landscape."""
        diagram = SystemLandscapeDiagram(
            systems=(_system(), _system(slug="warehouse", name="Warehouse"))
        )

        output = PlantUMLSerializer().serialize_system_landscape(diagram)

        assert "shop" in output
        assert "warehouse" in output

    def test_an_external_system_is_distinguished(self) -> None:
        """Which of these we own is the question a landscape answers."""
        external = SoftwareSystem(
            slug="payments", name="Payments", system_type=SystemType.EXTERNAL
        )

        output = PlantUMLSerializer().serialize_system_landscape(
            SystemLandscapeDiagram(systems=(_system(), external))
        )

        assert "System_Ext(payments," in output

    def test_hyphenated_system_slugs_become_valid_identifiers(self) -> None:
        """The same bug class, in the last place it could hide."""
        diagram = SystemLandscapeDiagram(
            systems=(_system(slug="order-management", name="Orders"),)
        )

        output = PlantUMLSerializer().serialize_system_landscape(diagram)

        assert "order_management" in output
        assert "(order-management" not in output


class TestEveryDiagram:
    """What must be true of all six, and was only ever checked on some."""

    def test_every_diagram_opens_and_closes_its_plantuml_block(self) -> None:
        """An unterminated diagram renders as nothing at all."""
        serializer = PlantUMLSerializer()
        outputs = [
            serializer.serialize_system_context(SystemContextDiagram(system=_system())),
            serializer.serialize_container_diagram(
                ContainerDiagram(system=_system(), containers=(_container(),))
            ),
            serializer.serialize_component_diagram(
                ComponentDiagram(system=_system(), container=_container())
            ),
            serializer.serialize_system_landscape(
                SystemLandscapeDiagram(systems=(_system(),))
            ),
            serializer.serialize_deployment_diagram(_deployment()),
            serializer.serialize_dynamic_diagram(
                DynamicDiagram(sequence_name="checkout", steps=(_step(),))
            ),
        ]

        for output in outputs:
            assert output.startswith("@startuml")
            assert output.rstrip().endswith("@enduml")

    def test_no_diagram_emits_a_hyphen_in_an_identifier(self) -> None:
        """PlantUML will not accept one, and Sphinx will not complain."""
        import re

        serializer = PlantUMLSerializer()
        hyphenated = SoftwareSystem(
            slug="order-management", name="Orders", description="Handles orders"
        )
        outputs = [
            serializer.serialize_system_context(
                SystemContextDiagram(
                    system=hyphenated,
                    person_slugs=("returning-customer",),
                    relationships=(_rel("returning-customer", "order-management"),),
                )
            ),
            serializer.serialize_container_diagram(
                ContainerDiagram(system=hyphenated, containers=(_container(),))
            ),
            serializer.serialize_system_landscape(
                SystemLandscapeDiagram(systems=(hyphenated,))
            ),
        ]

        for output in outputs:
            offenders = re.findall(
                r"\b(?:System|System_Ext|Container|Component|Person|Rel)\([^\")]*-",
                output,
            )
            assert not offenders, f"hyphenated identifier in:\n{output}"
