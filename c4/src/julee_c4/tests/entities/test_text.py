"""That c4's entities agree about how they name each other.

What ``Slug`` and ``Name`` promise on their own is asserted in julee,
beside the types. What is c4's to assert is that its entities use them
at both ends of a reference — which is the defect #70 found, and which
no amount of testing the types in isolation would catch.
"""

import pytest
from julee.core.values.text import Name, Slug

from julee_c4.domain.models.component import Component
from julee_c4.domain.models.container import Container
from julee_c4.domain.models.software_system import SoftwareSystem


class TestReferencesMatchWhatTheyName:
    """The defect the types exist to make impossible (#70).

    A slug field was slugified and a field *naming* that slug was only
    stripped, so a component could name a container that could not be
    found. Nothing raised; the lookup came back empty.
    """

    def test_a_container_finds_the_system_it_names(self) -> None:
        """Both ends of the reference are written the same way."""
        system = SoftwareSystem(slug=Slug("My System"), name=Name("My System"))
        container = Container(
            slug=Slug("web"), name=Name("Web"), system_slug=Slug("My System")
        )

        assert container.system_slug == system.slug

    def test_a_component_finds_the_container_it_names(self) -> None:
        """The same, one level down, where get_by_container looks."""
        container = Container(
            slug=Slug("Web Application"), name=Name("Web"), system_slug=Slug("s")
        )
        component = Component(
            slug=Slug("api"),
            name=Name("API"),
            container_slug=Slug("Web Application"),
            system_slug=Slug("s"),
        )

        assert component.container_slug == container.slug


class TestSlugsWithUnderscoresInThem:
    """Pinned here because this is where it was found, not where it lives.

    ``slugify`` strips underscores rather than converting them, so its
    own ``[\\s_]+`` substitution is unreachable (julee#309). It matters
    to c4 because a container slugged from ``api_app`` becomes
    ``apiapp``, and the PlantUML alias derived from it has to match —
    which it did not, for months, while three tests watched one half of
    the output and never the other.

    This asserts the current behaviour so that changing it in julee
    shows up here as a decision rather than a surprise.
    """

    @pytest.mark.parametrize(
        ("given", "expected"), [("api_app", "apiapp"), ("a_b c", "ab-c")]
    )
    def test_an_underscore_is_dropped_rather_than_converted(
        self, given: str, expected: str
    ) -> None:
        """Not what the author wrote, but the same at both ends."""
        assert Slug(given) == expected
