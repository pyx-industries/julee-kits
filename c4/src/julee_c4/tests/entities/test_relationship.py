"""Tests for Relationship domain model."""

import pytest

from julee_c4.domain.models.relationship import ElementType, Relationship
from julee_c4.domain.models.text import Slug


class TestRelationshipCreation:
    """Test Relationship model creation and validation."""

    def test_create_with_required_fields(self) -> None:
        """Test creating a relationship with minimum required fields."""
        relationship = Relationship(
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.SOFTWARE_SYSTEM,
            destination_slug=Slug("banking-system"),
        )

        assert relationship.source_type == ElementType.PERSON
        assert relationship.source_slug == "customer"
        assert relationship.destination_type == ElementType.SOFTWARE_SYSTEM
        assert relationship.destination_slug == "banking-system"
        assert relationship.description == "Uses"
        assert relationship.bidirectional is False

    def test_create_with_all_fields(self) -> None:
        """Test creating a relationship with all fields."""
        relationship = Relationship(
            slug=Slug("customer-to-banking"),
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.SOFTWARE_SYSTEM,
            destination_slug=Slug("banking-system"),
            description="Views account balances, makes payments",
            technology="HTTPS/JSON",
            tags=("external", "api"),
            bidirectional=False,
            docname="architecture/relationships",
        )

        assert relationship.slug == "customer-to-banking"
        assert relationship.description == "Views account balances, makes payments"
        assert relationship.technology == "HTTPS/JSON"
        assert relationship.tags == ("external", "api")

    def test_slug_auto_generated(self) -> None:
        """Test that slug is auto-generated from source and destination."""
        relationship = Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api-app"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("database"),
        )
        assert relationship.slug == "api-app-to-database"

    def test_empty_source_slug_raises_error(self) -> None:
        """Test that empty source_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Relationship(
                source_type=ElementType.PERSON,
                source_slug=Slug(""),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("system"),
            )

    def test_empty_destination_slug_raises_error(self) -> None:
        """Test that empty destination_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Relationship(
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug(""),
            )


class TestRelationshipProperties:
    """Test relationship properties."""

    def test_is_person_relationship_source(self) -> None:
        """Test is_person_relationship when source is person."""
        relationship = Relationship(
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.SOFTWARE_SYSTEM,
            destination_slug=Slug("system"),
        )
        assert relationship.is_person_relationship is True

    def test_is_person_relationship_destination(self) -> None:
        """Test is_person_relationship when destination is person."""
        relationship = Relationship(
            source_type=ElementType.SOFTWARE_SYSTEM,
            source_slug=Slug("system"),
            destination_type=ElementType.PERSON,
            destination_slug=Slug("admin"),
        )
        assert relationship.is_person_relationship is True

    def test_is_person_relationship_false(self) -> None:
        """Test is_person_relationship when no person involved."""
        relationship = Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
        )
        assert relationship.is_person_relationship is False

    def test_is_cross_system(self) -> None:
        """Test is_cross_system when system involved."""
        relationship = Relationship(
            source_type=ElementType.SOFTWARE_SYSTEM,
            source_slug=Slug("system-a"),
            destination_type=ElementType.SOFTWARE_SYSTEM,
            destination_slug=Slug("system-b"),
        )
        assert relationship.is_cross_system is True

    def test_is_internal(self) -> None:
        """Test is_internal for container-to-container relationships."""
        relationship = Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
        )
        assert relationship.is_internal is True

    def test_is_internal_component(self) -> None:
        """Test is_internal for component relationships."""
        relationship = Relationship(
            source_type=ElementType.COMPONENT,
            source_slug=Slug("controller"),
            destination_type=ElementType.COMPONENT,
            destination_slug=Slug("service"),
        )
        assert relationship.is_internal is True

    def test_label_without_technology(self) -> None:
        """Test label generation without technology."""
        relationship = Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
            description="Reads from",
        )
        assert relationship.label == "Reads from"

    def test_label_with_technology(self) -> None:
        """Test label generation with technology."""
        relationship = Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
            description="Reads from",
            technology="SQL/TCP",
        )
        assert relationship.label == "Reads from\\n[SQL/TCP]"


class TestRelationshipInvolvesElement:
    """Test involves_* methods."""

    @pytest.fixture
    def relationship(self) -> Relationship:
        """Create a sample relationship."""
        return Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api-app"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("database"),
            description="Reads/writes data",
        )

    def test_involves_element_source(self, relationship: Relationship) -> None:
        """Test involves_element for source element."""
        assert relationship.involves_element(ElementType.CONTAINER, "api-app") is True

    def test_involves_element_destination(self, relationship: Relationship) -> None:
        """Test involves_element for destination element."""
        assert relationship.involves_element(ElementType.CONTAINER, "database") is True

    def test_involves_element_not_involved(self, relationship: Relationship) -> None:
        """Test involves_element for element not in relationship."""
        assert relationship.involves_element(ElementType.CONTAINER, "other") is False

    def test_involves_container(self, relationship: Relationship) -> None:
        """Test involves_container method."""
        assert relationship.involves_container("api-app") is True
        assert relationship.involves_container("database") is True
        assert relationship.involves_container("other") is False

    def test_involves_system(self) -> None:
        """Test involves_system method."""
        relationship = Relationship(
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.SOFTWARE_SYSTEM,
            destination_slug=Slug("banking"),
        )
        assert relationship.involves_system("banking") is True
        assert relationship.involves_system("other") is False

    def test_involves_person(self) -> None:
        """Test involves_person method."""
        relationship = Relationship(
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.SOFTWARE_SYSTEM,
            destination_slug=Slug("banking"),
        )
        assert relationship.involves_person("customer") is True
        assert relationship.involves_person("admin") is False


class TestRelationshipTags:
    """Test tag operations."""

    def test_has_tag(self) -> None:
        """Test tag lookup."""
        relationship = Relationship(
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
            tags=("async", "internal"),
        )
        assert relationship.has_tag("async") is True
        assert relationship.has_tag("ASYNC") is True  # Case-insensitive
        assert relationship.has_tag("missing") is False


class TestElementType:
    """Test ElementType enum."""

    def test_all_element_types(self) -> None:
        """Test all element types exist."""
        assert ElementType.PERSON.value == "person"
        assert ElementType.SOFTWARE_SYSTEM.value == "software_system"
        assert ElementType.CONTAINER.value == "container"
        assert ElementType.COMPONENT.value == "component"
