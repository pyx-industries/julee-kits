"""App domain model.

Represents an application in the HCD documentation system.
Apps are defined via YAML manifests in apps/*/app.yaml.
"""

from dataclasses import dataclass
from enum import StrEnum

from julee.core.entities.text import Name, Slug
from julee.core.utils import normalize_name

from .base import Authored
from .epic import Epic
from .journey import Journey
from .story import Story


class AppInterface(StrEnum):
    """How people reach an app, which decides how it is drawn in C4."""

    SPHINX = "sphinx"
    API = "api"
    MCP = "mcp"
    WEB = "web"
    CLI = "cli"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str) -> "AppInterface":
        """The interface this names, or UNKNOWN if it names none of them."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.UNKNOWN

    @property
    def user_relationship(self) -> str:
        """What a person does to the app, for the arrow into it."""
        return {
            AppInterface.SPHINX: "Writes RST",
            AppInterface.API: "HTTP",
            AppInterface.MCP: "MCP",
            AppInterface.WEB: "Uses",
            AppInterface.CLI: "Runs",
        }.get(self, "Uses")

    @property
    def accelerator_relationship(self) -> str:
        """What the app does to an accelerator, for the arrow out of it."""
        return {
            AppInterface.SPHINX: "Documents",
            AppInterface.API: "Exposes",
            AppInterface.MCP: "Provides tools for",
            AppInterface.WEB: "Presents",
            AppInterface.CLI: "Executes",
        }.get(self, "Uses")


class AppType(StrEnum):
    """Application type classification."""

    STAFF = "staff"
    EXTERNAL = "external"
    MEMBER_TOOL = "member-tool"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str) -> "AppType":
        """Convert string to AppType, defaulting to UNKNOWN."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.UNKNOWN


@dataclass(frozen=True, kw_only=True)
class App(Authored):
    """Application entity.

    Apps represent distinct applications in the system, defined via YAML
    manifests. They serve as containers for stories and provide organization
    for the documentation.
    """

    slug: Slug
    """URL-safe identifier (e.g., "staff-portal")."""

    name: Name
    """Display name (e.g., "Staff Portal")."""

    app_type: AppType = AppType.UNKNOWN
    """Classification (staff, external, member-tool)."""

    status: str | None = None
    """Optional status indicator (e.g., "in-development", "live")."""

    description: str = ""
    """Human-readable description."""

    interface: AppInterface = AppInterface.UNKNOWN
    """How people reach this app, which decides how C4 draws it."""

    technology: str = ""
    """What the app is built with; inferred from interface if blank."""

    accelerators: tuple[str, ...] = ()
    """List of accelerator slugs associated with this app."""

    manifest_path: str = ""
    """Path to the app.yaml file."""

    @property
    def name_normalized(self) -> str:
        """Lowercase name for matching, which is what Name.normalized is.

        This was a stored field, filled by a validator that returned any
        value it was given and recomputed in ``model_post_init`` in case
        the validator had not run. Three mechanisms for one derived
        value, and a caller could still write a name_normalized that
        disagreed with the name — which the repositories match on, so an
        app with a wrong one is an app that cannot be found by name.

        Persona has always done it this way. This is the other four
        catching up (#71).
        """
        return self.name.normalized

    @classmethod
    def from_manifest(
        cls,
        slug: str,
        manifest: dict,
        manifest_path: str,
    ) -> "App":
        """Create an App from a parsed YAML manifest.

        Args:
            slug: App slug (usually directory name)
            manifest: Parsed YAML content
            manifest_path: Path to the manifest file

        Returns:
            App instance
        """
        name = manifest.get("name", slug.replace("-", " ").title())
        app_type = AppType.from_string(manifest.get("type", "unknown"))

        return cls(
            slug=Slug(slug),
            name=Name(name),
            app_type=app_type,
            status=manifest.get("status"),
            description=manifest.get("description", "").strip(),
            # A manifest gives a YAML list; the field is a tuple, and
            # pydantic used to convert it. A dataclass stores what it is
            # given, so a list here would put a mutable, unhashable
            # collection inside a frozen entity (julee-kits#57).
            accelerators=tuple(manifest.get("accelerators", ())),
            manifest_path=manifest_path,
        )

    def matches_type(self, app_type: AppType | str) -> bool:
        """Check if this app matches the given type.

        Args:
            app_type: AppType enum or string to match

        Returns:
            True if app matches the type
        """
        if isinstance(app_type, str):
            app_type = AppType.from_string(app_type)
        return self.app_type == app_type

    def matches_name(self, name: str) -> bool:
        """Check if this app matches the given name (case-insensitive).

        Args:
            name: Name to match against

        Returns:
            True if normalized names match
        """
        return self.name_normalized == normalize_name(name)

    @property
    def type_label(self) -> str:
        """Get human-readable type label."""
        labels = {
            AppType.STAFF: "Staff Application",
            AppType.EXTERNAL: "External Application",
            AppType.MEMBER_TOOL: "Member Tool",
            AppType.UNKNOWN: "Unknown",
        }
        return labels.get(self.app_type, str(self.app_type))

    @property
    def interface_label(self) -> str:
        """What to call this app's interface in a diagram."""
        return {
            AppInterface.SPHINX: "Sphinx Extension",
            AppInterface.API: "REST API",
            AppInterface.MCP: "MCP Server",
            AppInterface.WEB: "Web Application",
            AppInterface.CLI: "CLI Tool",
            AppInterface.UNKNOWN: "Application",
        }.get(self.interface, str(self.interface))

    @property
    def c4_technology(self) -> str:
        """What to label this app's technology, guessing from its interface.

        An app that says what it is built with is believed; one that does
        not gets the usual answer for how it is reached.
        """
        if self.technology:
            return self.technology
        return {
            AppInterface.SPHINX: "Python/Sphinx",
            AppInterface.API: "FastAPI",
            AppInterface.MCP: "FastMCP",
            AppInterface.WEB: "Python",
            AppInterface.CLI: "Python/Click",
        }.get(self.interface, "Python")


def get_stories_for_app(
    app: App,
    stories: list[Story],
) -> list[Story]:
    """Get stories that belong to an app.

    Args:
        app: App to find stories for
        stories: All Story entities

    Returns:
        List of Story entities for this app, sorted by feature_title
    """
    matching = [s for s in stories if s.app_slug == app.slug]
    return sorted(matching, key=lambda s: s.feature_title)


def get_journeys_for_app(
    app: App,
    stories: list[Story],
    journeys: list[Journey],
) -> list[Journey]:
    """Get journeys that include stories from an app.

    Args:
        app: App to find journeys for
        stories: All Story entities
        journeys: All Journey entities

    Returns:
        List of Journey entities containing stories from this app, sorted by slug
    """
    # Get story titles for this app
    app_story_titles = {
        normalize_name(s.feature_title) for s in stories if s.app_slug == app.slug
    }

    if not app_story_titles:
        return []

    # Find journeys containing these stories
    matching = []
    for journey in journeys:
        story_refs = journey.get_story_refs()
        if any(normalize_name(ref) in app_story_titles for ref in story_refs):
            matching.append(journey)

    return sorted(matching, key=lambda j: j.slug)


def get_epics_for_app(
    app: App,
    stories: list[Story],
    epics: list[Epic],
) -> list[Epic]:
    """Get epics that contain stories from an app.

    Args:
        app: App to find epics for
        stories: All Story entities
        epics: All Epic entities

    Returns:
        List of Epic entities containing stories from this app, sorted by slug
    """
    # Get story titles for this app
    app_story_titles = {
        normalize_name(s.feature_title) for s in stories if s.app_slug == app.slug
    }

    if not app_story_titles:
        return []

    # Find epics containing these stories
    matching = []
    for epic in epics:
        if any(normalize_name(ref) in app_story_titles for ref in epic.story_refs):
            matching.append(epic)

    return sorted(matching, key=lambda e: e.slug)
