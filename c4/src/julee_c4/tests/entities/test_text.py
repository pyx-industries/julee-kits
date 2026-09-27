"""What Slug and Name promise.

These were nineteen field validators spread over six entities until
#70. The properties they were each asserting separately are asserted
once here, against the types that now carry them.

The last two tests are the reason the types exist: they check that two
entities naming each other end up with the same string, which is what
c4 got wrong everywhere a reference was stripped and the thing it
referred to was slugified.
"""

import pytest

from julee_c4.domain.models.component import Component
from julee_c4.domain.models.container import Container
from julee_c4.domain.models.software_system import SoftwareSystem
from julee_c4.domain.models.text import Name, Slug


class TestSlug:
    """A URL-safe identifier that normalises itself."""

    @pytest.mark.parametrize(
        ("given", "expected"),
        [
            ("Banking System", "banking-system"),
            ("  Banking System  ", "banking-system"),
            ("banking-system", "banking-system"),
            ("Banking   System", "banking-system"),
            ("Banking, System!", "banking-system"),
            ("api_app", "apiapp"),
        ],
    )
    def test_it_normalises_what_it_is_given(self, given: str, expected: str) -> None:
        """One spelling out, whatever spelling went in."""
        assert Slug(given) == expected

    def test_normalising_twice_changes_nothing(self) -> None:
        """Idempotent, so a slug can be re-made from a slug.

        Deserialisation does exactly that on every read.
        """
        once = Slug("Banking System")
        assert Slug(once) == once

    @pytest.mark.parametrize("given", ["", "   ", "!!!", "---"])
    def test_it_refuses_what_it_cannot_make_a_slug_of(self, given: str) -> None:
        """An empty identifier names everything and nothing."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Slug(given)

    def test_it_is_a_string(self) -> None:
        """Being a str is what makes it free to adopt.

        Nothing downstream unwraps it: it compares, formats and keys
        dictionaries as the string it is.
        """
        slug = Slug("Banking System")
        assert slug == "banking-system"
        assert f"{slug}/x" == "banking-system/x"
        keyed: dict[str, int] = {slug: 1}
        assert keyed["banking-system"] == 1


class TestName:
    """Text a person wrote, kept as they wrote it."""

    def test_it_keeps_what_was_written(self) -> None:
        """A name is for reading, so its spelling survives."""
        assert Name("Internet Banking System") == "Internet Banking System"

    def test_it_trims_the_edges(self) -> None:
        """Whitespace around a name is typing, not name."""
        assert Name("  Test System  ") == "Test System"

    @pytest.mark.parametrize("given", ["", "   "])
    def test_it_refuses_an_empty_name(self, given: str) -> None:
        """Something has to be displayed."""
        with pytest.raises(ValueError, match="a name cannot be empty"):
            Name(given)

    @pytest.mark.parametrize(
        "given", ["Data Steward", "data-steward", "data_steward", "DATA STEWARD"]
    )
    def test_names_that_differ_only_in_spelling_compare_equal(self, given: str) -> None:
        """How names are matched, in one place rather than sixty."""
        assert Name(given).normalized == "data steward"


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
