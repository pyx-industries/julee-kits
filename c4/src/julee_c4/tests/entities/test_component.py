"""Tests for Component domain model."""

import pytest

from julee_c4.domain.models.component import Component
from julee_c4.domain.models.text import Name, Slug


class TestComponentCreation:
    """Test Component model creation and validation."""

    def test_create_with_required_fields(self) -> None:
        """Test creating a component with minimum required fields."""
        component = Component(
            slug=Slug("auth-controller"),
            name=Name("Authentication Controller"),
            container_slug=Slug("api-app"),
            system_slug=Slug("banking-system"),
        )

        assert component.slug == "auth-controller"
        assert component.name == "Authentication Controller"
        assert component.container_slug == "api-app"
        assert component.system_slug == "banking-system"
        assert component.description == ""
        assert component.tags == ()

    def test_create_with_all_fields(self) -> None:
        """Test creating a component with all fields."""
        component = Component(
            slug=Slug("auth-controller"),
            name=Name("Authentication Controller"),
            container_slug=Slug("api-app"),
            system_slug=Slug("banking-system"),
            description="Handles user authentication and authorization",
            technology="Python, FastAPI",
            interface="REST API",
            code_path="src/controllers/auth.py",
            tags=("security", "core"),
            docname="architecture/components",
        )

        assert component.description == "Handles user authentication and authorization"
        assert component.technology == "Python, FastAPI"
        assert component.interface == "REST API"
        assert component.code_path == "src/controllers/auth.py"

    def test_empty_slug_raises_error(self) -> None:
        """Test that empty slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Component(
                slug=Slug(""),
                name=Name("Test"),
                container_slug=Slug("container"),
                system_slug=Slug("system"),
            )

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError, match="a name cannot be empty"):
            Component(
                slug=Slug("test"),
                name=Name(""),
                container_slug=Slug("container"),
                system_slug=Slug("system"),
            )

    def test_empty_container_slug_raises_error(self) -> None:
        """Test that empty container_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Component(
                slug=Slug("test"),
                name=Name("Test"),
                container_slug=Slug(""),
                system_slug=Slug("system"),
            )

    def test_empty_system_slug_raises_error(self) -> None:
        """Test that empty system_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Component(
                slug=Slug("test"),
                name=Name("Test"),
                container_slug=Slug("container"),
                system_slug=Slug(""),
            )

    def test_slug_is_normalized(self) -> None:
        """Test that slug is normalized (slugified)."""
        component = Component(
            slug=Slug("Auth Controller"),
            name=Name("Test"),
            container_slug=Slug("container"),
            system_slug=Slug("system"),
        )
        assert component.slug == "auth-controller"


class TestComponentComputedFields:
    """Test computed fields and properties."""

    def test_name_normalized(self) -> None:
        """Test normalized name is computed."""
        component = Component(
            slug=Slug("test"),
            name=Name("Authentication Controller"),
            container_slug=Slug("container"),
            system_slug=Slug("system"),
        )
        assert component.name_normalized == "authentication controller"

    def test_qualified_slug(self) -> None:
        """Test qualified slug includes container and system."""
        component = Component(
            slug=Slug("auth-controller"),
            name=Name("Test"),
            container_slug=Slug("api-app"),
            system_slug=Slug("banking-system"),
        )
        assert component.qualified_slug == "banking-system/api-app/auth-controller"


class TestComponentTags:
    """Test tag operations."""

    def test_has_tag_exact(self) -> None:
        """Test tag lookup with exact match."""
        component = Component(
            slug=Slug("test"),
            name=Name("Test"),
            container_slug=Slug("container"),
            system_slug=Slug("system"),
            tags=("security", "core"),
        )
        assert component.has_tag("security") is True
        assert component.has_tag("missing") is False

    def test_has_tag_case_insensitive(self) -> None:
        """Test tag lookup is case-insensitive."""
        component = Component(
            slug=Slug("test"),
            name=Name("Test"),
            container_slug=Slug("container"),
            system_slug=Slug("system"),
            tags=("Security",),
        )
        assert component.has_tag("security") is True
        assert component.has_tag("SECURITY") is True

    def test_with_tag(self) -> None:
        """Tagging returns a new entity carrying the tag."""
        component = Component(
            slug=Slug("test"),
            name=Name("Test"),
            container_slug=Slug("container"),
            system_slug=Slug("system"),
            tags=("existing",),
        )
        component = component.with_tag("new")
        assert "new" in component.tags
        assert len(component.tags) == 2


class TestComponentSerialization:
    """Test serialization."""

    def test_to_dict(self) -> None:
        """Test model can be serialized to dict."""
        component = Component(
            slug=Slug("test"),
            name=Name("Test Component"),
            container_slug=Slug("container"),
            system_slug=Slug("system"),
            technology="Python",
        )
        data = component.model_dump()
        assert data["slug"] == "test"
        assert data["name"] == "Test Component"
        assert data["container_slug"] == "container"
        assert data["technology"] == "Python"
