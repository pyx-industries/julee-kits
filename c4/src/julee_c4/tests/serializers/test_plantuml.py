"""Tests for PlantUMLSerializer.

The dynamic diagram is covered here because it was the one path that read
fields the model does not have, and nothing exercised it.
"""

import pytest

from julee_c4.domain.models.container import Container, ContainerType
from julee_c4.domain.models.deployment_node import DeploymentNode
from julee_c4.domain.models.diagrams import DeploymentDiagram, DynamicDiagram
from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType
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
