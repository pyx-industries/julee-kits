"""Tests for Container domain model."""

import pytest
from julee.core.entities.text import Name, Slug

from julee_c4.domain.models.container import Container, ContainerType


class TestContainerCreation:
    """Test Container model creation and validation."""

    def test_create_with_required_fields(self) -> None:
        """Test creating a container with minimum required fields."""
        container = Container(
            slug=Slug("api-app"),
            name=Name("API Application"),
            system_slug=Slug("banking-system"),
        )

        assert container.slug == "api-app"
        assert container.name == "API Application"
        assert container.system_slug == "banking-system"
        assert container.container_type == ContainerType.OTHER
        assert container.tags == ()

    def test_create_with_all_fields(self) -> None:
        """Test creating a container with all fields."""
        container = Container(
            slug=Slug("api-app"),
            name=Name("API Application"),
            system_slug=Slug("banking-system"),
            description="Provides banking functionality via REST API",
            container_type=ContainerType.API,
            technology="Python 3.11, FastAPI",
            url="https://api.example.com",
            tags=("backend", "core"),
            docname="architecture/containers",
        )

        assert container.description == "Provides banking functionality via REST API"
        assert container.container_type == ContainerType.API
        assert container.technology == "Python 3.11, FastAPI"

    def test_empty_slug_raises_error(self) -> None:
        """Test that empty slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Container(slug=Slug(""), name=Name("Test"), system_slug=Slug("system"))

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError, match="a name cannot be empty"):
            Container(slug=Slug("test"), name=Name(""), system_slug=Slug("system"))

    def test_empty_system_slug_raises_error(self) -> None:
        """Test that empty system_slug raises validation error."""
        with pytest.raises(ValueError, match="nothing in it that can be a slug"):
            Container(slug=Slug("test"), name=Name("Test"), system_slug=Slug(""))

    def test_slug_is_normalized(self) -> None:
        """Test that slug is normalized (slugified)."""
        container = Container(
            slug=Slug("API App"), name=Name("Test"), system_slug=Slug("system")
        )
        assert container.slug == "api-app"


class TestContainerComputedFields:
    """Test computed fields and properties."""

    def test_name_normalized(self) -> None:
        """Test normalized name is computed."""
        container = Container(
            slug=Slug("test"), name=Name("API Application"), system_slug=Slug("system")
        )
        assert container.name_normalized == "api application"

    def test_qualified_slug(self) -> None:
        """Test qualified slug includes system."""
        container = Container(
            slug=Slug("api-app"), name=Name("Test"), system_slug=Slug("banking-system")
        )
        assert container.qualified_slug == "banking-system/api-app"

    def test_is_data_store_database(self) -> None:
        """Test is_data_store for database containers."""
        container = Container(
            slug=Slug("db"),
            name=Name("Database"),
            system_slug=Slug("system"),
            container_type=ContainerType.DATABASE,
        )
        assert container.is_data_store is True
        assert container.is_application is False

    def test_is_data_store_file_storage(self) -> None:
        """Test is_data_store for file storage containers."""
        container = Container(
            slug=Slug("storage"),
            name=Name("Storage"),
            system_slug=Slug("system"),
            container_type=ContainerType.FILE_STORAGE,
        )
        assert container.is_data_store is True

    def test_is_application_web(self) -> None:
        """Test is_application for web applications."""
        container = Container(
            slug=Slug("web"),
            name=Name("Web App"),
            system_slug=Slug("system"),
            container_type=ContainerType.WEB_APPLICATION,
        )
        assert container.is_application is True
        assert container.is_data_store is False

    def test_is_application_api(self) -> None:
        """Test is_application for API containers."""
        container = Container(
            slug=Slug("api"),
            name=Name("API"),
            system_slug=Slug("system"),
            container_type=ContainerType.API,
        )
        assert container.is_application is True

    def test_other_type_neither(self) -> None:
        """Test OTHER type is neither data store nor application."""
        container = Container(
            slug=Slug("other"),
            name=Name("Other"),
            system_slug=Slug("system"),
            container_type=ContainerType.OTHER,
        )
        assert container.is_data_store is False
        assert container.is_application is False


class TestContainerTags:
    """Test tag operations."""

    def test_has_tag_exact(self) -> None:
        """Test tag lookup with exact match."""
        container = Container(
            slug=Slug("test"),
            name=Name("Test"),
            system_slug=Slug("system"),
            tags=("backend", "core"),
        )
        assert container.has_tag("backend") is True
        assert container.has_tag("missing") is False

    def test_has_tag_case_insensitive(self) -> None:
        """Test tag lookup is case-insensitive."""
        container = Container(
            slug=Slug("test"),
            name=Name("Test"),
            system_slug=Slug("system"),
            tags=("Backend",),
        )
        assert container.has_tag("backend") is True
        assert container.has_tag("BACKEND") is True

    def test_with_tag(self) -> None:
        """Tagging returns a new entity carrying the tag."""
        container = Container(
            slug=Slug("test"),
            name=Name("Test"),
            system_slug=Slug("system"),
            tags=("existing",),
        )
        container = container.with_tag("new")
        assert "new" in container.tags


class TestContainerTypes:
    """Test all container types are valid."""

    @pytest.mark.parametrize(
        "container_type",
        [
            ContainerType.WEB_APPLICATION,
            ContainerType.MOBILE_APP,
            ContainerType.DESKTOP_APP,
            ContainerType.CONSOLE_APP,
            ContainerType.SERVERLESS_FUNCTION,
            ContainerType.DATABASE,
            ContainerType.FILE_STORAGE,
            ContainerType.MESSAGE_QUEUE,
            ContainerType.API,
            ContainerType.OTHER,
        ],
    )
    def test_container_type_valid(self, container_type: ContainerType) -> None:
        """Test all container types can be assigned."""
        container = Container(
            slug=Slug("test"),
            name=Name("Test"),
            system_slug=Slug("system"),
            container_type=container_type,
        )
        assert container.container_type == container_type
