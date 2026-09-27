"""Tests for DynamicStep domain model."""

import pytest
from julee.core.entities.text import Name, Slug

from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType


class TestDynamicStepCreation:
    """Test DynamicStep model creation and validation."""

    def test_create_with_required_fields(self) -> None:
        """Test creating a step with minimum required fields."""
        step = DynamicStep(
            slug=Slug("login-step-1"),
            sequence_name=Name("user-login"),
            step_number=1,
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("web-app"),
        )

        assert step.slug == "login-step-1"
        assert step.sequence_name == "user-login"
        assert step.step_number == 1
        assert step.source_type == ElementType.PERSON
        assert step.source_slug == "customer"
        assert step.description == ""
        assert step.is_async is False

    def test_create_with_all_fields(self) -> None:
        """Test creating a step with all fields."""
        step = DynamicStep(
            slug=Slug("login-step-1"),
            sequence_name=Name("user-login"),
            step_number=1,
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("web-app"),
            description="Submits login credentials",
            technology="HTTPS",
            return_value="JWT token",
            is_async=False,
            docname="architecture/sequences",
        )

        assert step.description == "Submits login credentials"
        assert step.technology == "HTTPS"
        assert step.return_value == "JWT token"

    def test_empty_slug_is_derived_from_the_sequence(self) -> None:
        """A step's place in its sequence already identifies it."""
        step = DynamicStep(
            sequence_name=Name("test"),
            step_number=1,
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("app"),
        )

        assert step.slug == "test-step-1"

    def test_empty_sequence_name_raises_error(self) -> None:
        """Test that empty sequence_name raises validation error."""
        with pytest.raises(ValueError, match="a name cannot be empty"):
            DynamicStep(
                slug=Slug("test"),
                sequence_name=Name(""),
                step_number=1,
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("app"),
            )

    def test_zero_step_number_raises_error(self) -> None:
        """Test that step_number < 1 raises validation error."""
        with pytest.raises(ValueError, match="greater than or equal to 1"):
            DynamicStep(
                slug=Slug("test"),
                sequence_name=Name("test"),
                step_number=0,
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("app"),
            )

    def test_negative_step_number_raises_error(self) -> None:
        """Test that negative step_number raises validation error."""
        with pytest.raises(ValueError, match="greater than or equal to 1"):
            DynamicStep(
                slug=Slug("test"),
                sequence_name=Name("test"),
                step_number=-1,
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("app"),
            )

    def test_empty_source_slug_raises_error(self) -> None:
        """Test that empty source_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            DynamicStep(
                slug=Slug("test"),
                sequence_name=Name("test"),
                step_number=1,
                source_type=ElementType.PERSON,
                source_slug=Slug(""),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("app"),
            )

    def test_empty_destination_slug_raises_error(self) -> None:
        """Test that empty destination_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            DynamicStep(
                slug=Slug("test"),
                sequence_name=Name("test"),
                step_number=1,
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug(""),
            )


class TestDynamicStepProperties:
    """Test dynamic step properties."""

    @pytest.fixture
    def sample_step(self) -> DynamicStep:
        """Create a sample step for testing."""
        return DynamicStep(
            slug=Slug("login-step-1"),
            sequence_name=Name("user-login"),
            step_number=1,
            source_type=ElementType.PERSON,
            source_slug=Slug("customer"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("web-app"),
            description="Submits credentials",
            technology="HTTPS",
        )

    def test_step_label(self, sample_step: DynamicStep) -> None:
        """Test step_label format."""
        assert sample_step.step_label == "1. "

    def test_full_label_without_technology(self) -> None:
        """Test full_label without technology."""
        step = DynamicStep(
            slug=Slug("test"),
            sequence_name=Name("test"),
            step_number=2,
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
            description="Queries data",
        )
        assert step.full_label == "2. Queries data"

    def test_full_label_with_technology(self, sample_step: DynamicStep) -> None:
        """Test full_label with technology."""
        assert sample_step.full_label == "1. Submits credentials [HTTPS]"

    def test_is_person_interaction_source(self, sample_step: DynamicStep) -> None:
        """Test is_person_interaction when source is person."""
        assert sample_step.is_person_interaction is True

    def test_is_person_interaction_destination(self) -> None:
        """Test is_person_interaction when destination is person."""
        step = DynamicStep(
            slug=Slug("test"),
            sequence_name=Name("test"),
            step_number=1,
            source_type=ElementType.CONTAINER,
            source_slug=Slug("app"),
            destination_type=ElementType.PERSON,
            destination_slug=Slug("admin"),
        )
        assert step.is_person_interaction is True

    def test_is_person_interaction_false(self) -> None:
        """Test is_person_interaction when no person involved."""
        step = DynamicStep(
            slug=Slug("test"),
            sequence_name=Name("test"),
            step_number=1,
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("db"),
        )
        assert step.is_person_interaction is False


class TestDynamicStepSlugGeneration:
    """Test slug generation class method."""

    def test_generate_slug(self) -> None:
        """Test slug generation from sequence and step."""
        slug = DynamicStep.generate_slug("User Login", 1)
        assert slug == "user-login-step-1"

    def test_generate_slug_special_chars(self) -> None:
        """Test slug generation handles special characters."""
        slug = DynamicStep.generate_slug("Order Processing & Fulfillment", 5)
        assert slug == "order-processing-fulfillment-step-5"


class TestDynamicStepInvolvesElement:
    """Test involves_element method."""

    @pytest.fixture
    def sample_step(self) -> DynamicStep:
        """Create a sample step for testing."""
        return DynamicStep(
            slug=Slug("test"),
            sequence_name=Name("test"),
            step_number=1,
            source_type=ElementType.CONTAINER,
            source_slug=Slug("api-app"),
            destination_type=ElementType.CONTAINER,
            destination_slug=Slug("database"),
        )

    def test_involves_element_source(self, sample_step: DynamicStep) -> None:
        """Test involves_element for source element."""
        assert sample_step.involves_element(ElementType.CONTAINER, "api-app") is True

    def test_involves_element_destination(self, sample_step: DynamicStep) -> None:
        """Test involves_element for destination element."""
        assert sample_step.involves_element(ElementType.CONTAINER, "database") is True

    def test_involves_element_not_involved(self, sample_step: DynamicStep) -> None:
        """Test involves_element for element not in step."""
        assert sample_step.involves_element(ElementType.CONTAINER, "other") is False

    def test_involves_element_wrong_type(self, sample_step: DynamicStep) -> None:
        """Test involves_element with wrong element type."""
        assert sample_step.involves_element(ElementType.COMPONENT, "api-app") is False
