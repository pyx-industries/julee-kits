"""Tests for SoftwareSystem domain model."""

import pytest
from julee.core.entities.text import Name, Slug
from pydantic import TypeAdapter

from julee_c4.domain.models.software_system import (
    SoftwareSystem,
    SystemType,
)


class TestSoftwareSystemCreation:
    """Test SoftwareSystem model creation and validation."""

    def test_create_with_required_fields(self) -> None:
        """Test creating a system with minimum required fields."""
        system = SoftwareSystem(
            slug=Slug("banking-system"),
            name=Name("Internet Banking System"),
        )

        assert system.slug == "banking-system"
        assert system.name == "Internet Banking System"
        assert system.description == ""
        assert system.system_type == SystemType.INTERNAL
        assert system.tags == ()

    def test_create_with_all_fields(self) -> None:
        """Test creating a system with all fields."""
        system = SoftwareSystem(
            slug=Slug("banking-system"),
            name=Name("Internet Banking System"),
            description="Allows customers to view account balances",
            system_type=SystemType.INTERNAL,
            owner="Digital Team",
            technology="Java, Spring Boot",
            url="https://docs.example.com/banking",
            tags=("core", "finance"),
            docname="architecture/systems",
        )

        assert system.slug == "banking-system"
        assert system.description == "Allows customers to view account balances"
        assert system.owner == "Digital Team"
        assert system.technology == "Java, Spring Boot"
        assert system.tags == ("core", "finance")

    def test_empty_slug_raises_error(self) -> None:
        """Test that empty slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            SoftwareSystem(slug=Slug(""), name=Name("Test System"))

    def test_whitespace_slug_raises_error(self) -> None:
        """Test that whitespace-only slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            SoftwareSystem(slug=Slug("   "), name=Name("Test System"))

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError, match="a name cannot be empty"):
            SoftwareSystem(slug=Slug("test"), name=Name(""))

    def test_slug_is_normalized(self) -> None:
        """Test that slug is normalized (slugified)."""
        system = SoftwareSystem(slug=Slug("Banking System"), name=Name("Test"))
        assert system.slug == "banking-system"

    def test_name_is_trimmed(self) -> None:
        """Test that name is trimmed of whitespace."""
        system = SoftwareSystem(slug=Slug("test"), name=Name("  Test System  "))
        assert system.name == "Test System"


class TestSoftwareSystemComputedFields:
    """Test computed fields and properties."""

    def test_name_normalized(self) -> None:
        """Test normalized name is computed."""
        system = SoftwareSystem(slug=Slug("test"), name=Name("Internet Banking System"))
        assert system.name_normalized == "internet banking system"

    def test_display_title(self) -> None:
        """Test display_title returns name."""
        system = SoftwareSystem(slug=Slug("test"), name=Name("Banking System"))
        assert system.display_title == "Banking System"

    def test_is_external_true(self) -> None:
        """Test is_external for external systems."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), system_type=SystemType.EXTERNAL
        )
        assert system.is_external is True
        assert system.is_internal is False

    def test_is_internal_true(self) -> None:
        """Test is_internal for internal systems."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), system_type=SystemType.INTERNAL
        )
        assert system.is_internal is True
        assert system.is_external is False

    def test_is_existing_neither(self) -> None:
        """Test existing systems are neither internal nor external."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), system_type=SystemType.EXISTING
        )
        assert system.is_internal is False
        assert system.is_external is False


class TestSoftwareSystemTags:
    """Test tag operations."""

    def test_has_tag_exact(self) -> None:
        """Test tag lookup with exact match."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), tags=("core", "finance")
        )
        assert system.has_tag("core") is True
        assert system.has_tag("missing") is False

    def test_has_tag_case_insensitive(self) -> None:
        """Test tag lookup is case-insensitive."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), tags=("Core", "Finance")
        )
        assert system.has_tag("core") is True
        assert system.has_tag("FINANCE") is True

    def test_with_tag_new(self) -> None:
        """Tagging returns a new entity carrying the tag."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), tags=("existing",)
        )

        tagged = system.with_tag("new")

        assert tagged.tags == ("existing", "new")

    def test_with_tag_leaves_the_original_alone(self) -> None:
        """The entity is frozen: tagging makes one, it does not edit one."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), tags=("existing",)
        )

        system.with_tag("new")

        assert system.tags == ("existing",)

    def test_with_tag_duplicate(self) -> None:
        """A tag already present is not added twice."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), tags=("existing",)
        )
        system = system.with_tag("existing")
        assert len(system.tags) == 1

    def test_with_tag_case_insensitive_duplicate(self) -> None:
        """Tags differing only in case are the same tag."""
        system = SoftwareSystem(
            slug=Slug("test"), name=Name("Test"), tags=("Existing",)
        )
        system = system.with_tag("existing")
        assert len(system.tags) == 1


class TestSoftwareSystemSerialization:
    """How an adapter turns one into something to store or send.

    The entity does not serialise itself. It is a frozen dataclass
    holding domain values, and turning that into JSON is the business
    of whatever is writing the JSON — a repository, an API, a data
    converter. TypeAdapter is what those use.
    """

    def test_to_dict(self) -> None:
        """Test model can be serialized to dict."""
        system = SoftwareSystem(
            slug=Slug("test"),
            name=Name("Test System"),
            system_type=SystemType.EXTERNAL,
        )
        data = TypeAdapter(SoftwareSystem).dump_python(system, mode="json")
        assert data["slug"] == "test"
        assert data["name"] == "Test System"
        assert data["system_type"] == "external"

    def test_to_json(self) -> None:
        """Test model can be serialized to JSON."""
        system = SoftwareSystem(slug=Slug("test"), name=Name("Test System"))
        json_str = TypeAdapter(SoftwareSystem).dump_json(system).decode()
        assert '"slug":"test"' in json_str
        assert '"name":"Test System"' in json_str
