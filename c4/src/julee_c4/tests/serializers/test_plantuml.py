"""Tests for PlantUMLSerializer.

The dynamic diagram is covered here because it was the one path that read
fields the model does not have, and nothing exercised it.
"""

import pytest

from julee_c4.domain.models.container import Container, ContainerType
from julee_c4.domain.models.diagrams import DynamicDiagram
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
