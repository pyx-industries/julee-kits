"""Something outside that an integration depends on.

A value, not an entity (ADR 018). Two dependencies of the same contents
are the same dependency, and nothing keeps one under an id.
"""

from dataclasses import dataclass

from julee.core.values.text import Name


@dataclass(frozen=True, kw_only=True)
class ExternalDependency:
    """External system that an integration depends on."""

    name: Name
    """Display name of the external system."""

    url: str | None = None
    """Optional URL for documentation or reference."""

    description: str = ""
    """Optional brief description."""

    @classmethod
    def from_dict(cls, data: dict) -> "ExternalDependency":
        """Create from dictionary (YAML parsed data).

        Args:
            data: Dictionary with name, url, description keys

        Returns:
            ExternalDependency instance
        """
        # Name is built here rather than left to the field. Pydantic
        # used to make one out of whatever arrived, which is what
        # refused the "" default below; a dataclass would have stored
        # the empty string and given the dependency no name at all.
        return cls(
            name=Name(data.get("name", "")),
            url=data.get("url"),
            description=data.get("description", ""),
        )
