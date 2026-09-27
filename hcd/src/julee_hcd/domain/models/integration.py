"""Integration domain model.

Represents an integration module in the HCD documentation system.
Integrations are defined via YAML manifests in integrations/*/integration.yaml.
"""

from enum import StrEnum

from julee.core.entities.entity import Entity
from julee.core.entities.text import Name, NonEmptyText, Slug
from julee.core.utils import normalize_name
from pydantic import Field, computed_field

from .base import Authored


class Direction(StrEnum):
    """Integration data flow direction."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

    @classmethod
    def from_string(cls, value: str) -> "Direction":
        """Convert string to Direction, defaulting to BIDIRECTIONAL."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.BIDIRECTIONAL

    @property
    def label(self) -> str:
        """Get human-readable label."""
        labels = {
            Direction.INBOUND: "Inbound (data source)",
            Direction.OUTBOUND: "Outbound (data sink)",
            Direction.BIDIRECTIONAL: "Bidirectional",
        }
        return labels.get(self, str(self.value))


class ExternalDependency(Entity):
    """External system that an integration depends on."""

    name: Name = Field(description="Display name of the external system")
    url: str | None = Field(
        default=None, description="Optional URL for documentation or reference"
    )
    description: str = Field(default="", description="Optional brief description")

    @classmethod
    def from_dict(cls, data: dict) -> "ExternalDependency":
        """Create from dictionary (YAML parsed data).

        Args:
            data: Dictionary with name, url, description keys

        Returns:
            ExternalDependency instance
        """
        return cls(
            name=data.get("name", ""),
            url=data.get("url"),
            description=data.get("description", ""),
        )


class Integration(Authored):
    """Integration module entity.

    Integrations represent connections to external systems, defining
    data flow direction and external dependencies.
    """

    slug: Slug = Field(
        description='URL-safe identifier (e.g., "pilot-data-collection")'
    )
    module: NonEmptyText = Field(
        description='Python module name (e.g., "pilot_data_collection")'
    )
    name: Name = Field(description="Display name")
    description: str = Field(default="", description="Human-readable description")
    direction: Direction = Field(
        default=Direction.BIDIRECTIONAL, description="Data flow direction"
    )
    depends_on: tuple[ExternalDependency, ...] = Field(
        default_factory=tuple, description="List of external dependencies"
    )
    manifest_path: str = Field(
        default="", description="Path to the integration.yaml file"
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name_normalized(self) -> str:
        """Lowercase name for matching, which is what Name.normalized is.

        A stored field until #71, filled by a validator that returned
        any value it was given and recomputed in ``model_post_init`` in
        case the validator had not run. A caller could write one that
        disagreed with the name, and the repositories match on it.

        ``module`` is NonEmptyText rather than Slug deliberately: it is
        a Python import path, and slugifying one would take the dots
        out.
        """
        return self.name.normalized

    @classmethod
    def from_manifest(
        cls,
        module_name: str,
        manifest: dict,
        manifest_path: str,
    ) -> "Integration":
        """Create an Integration from a parsed YAML manifest.

        Args:
            module_name: Module directory name
            manifest: Parsed YAML content
            manifest_path: Path to the manifest file

        Returns:
            Integration instance
        """
        slug = manifest.get("slug", module_name.replace("_", "-"))
        name = manifest.get("name", slug.replace("-", " ").title())
        direction = Direction.from_string(manifest.get("direction", "bidirectional"))

        # Parse depends_on list
        depends_on_raw = manifest.get("depends_on", [])
        depends_on = [
            (
                ExternalDependency.from_dict(dep)
                if isinstance(dep, dict)
                else ExternalDependency(name=Name(str(dep)))
            )
            for dep in depends_on_raw
        ]

        return cls(
            slug=Slug(slug),
            module=NonEmptyText(module_name),
            name=Name(name),
            description=manifest.get("description", "").strip(),
            direction=direction,
            depends_on=tuple(depends_on),
            manifest_path=manifest_path,
        )

    def matches_direction(self, direction: Direction | str) -> bool:
        """Check if this integration matches the given direction.

        Args:
            direction: Direction enum or string to match

        Returns:
            True if integration matches the direction
        """
        if isinstance(direction, str):
            direction = Direction.from_string(direction)
        return self.direction == direction

    def matches_name(self, name: str) -> bool:
        """Check if this integration matches the given name (case-insensitive).

        Args:
            name: Name to match against

        Returns:
            True if normalized names match
        """
        return self.name_normalized == normalize_name(name)

    def has_dependency(self, dep_name: str) -> bool:
        """Check if this integration has a specific dependency.

        Args:
            dep_name: Dependency name to check (case-insensitive)

        Returns:
            True if dependency exists
        """
        dep_normalized = normalize_name(dep_name)
        return any(
            normalize_name(dep.name) == dep_normalized for dep in self.depends_on
        )

    @property
    def direction_label(self) -> str:
        """Get human-readable direction label."""
        return self.direction.label

    @property
    def module_path(self) -> str:
        """Get full module path for display."""
        return f"integrations.{self.module}"
