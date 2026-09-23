"""File-backed implementation of AppRepository."""

import logging
from pathlib import Path

from julee.core.utils import normalize_name
from julee.repositories.file import FileRepositoryMixin

from julee_hcd.domain.models.app import App, AppType
from julee_hcd.domain.repositories.app import AppRepository
from julee_hcd.parsers.yaml import scan_app_manifests
from julee_hcd.serializers.yaml import serialize_app

logger = logging.getLogger(__name__)


class FileAppRepository(FileRepositoryMixin[App], AppRepository):
    """File-backed implementation of AppRepository.

    Apps are stored as YAML manifests in the directory structure:
    {base_path}/{app_slug}/app.yaml
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize with base path for app manifests.

        Args:
            base_path: Root directory for app manifests (e.g., docs/apps/)
        """
        self.base_path = Path(base_path)
        self.storage_dict: dict[str, App] = {}
        self.entity_name = "App"
        self.id_field = "slug"

        # Load existing apps from disk
        self._load_all()

    def _get_file_path(self, entity: App) -> Path:
        """Get file path for an app manifest."""
        return self.base_path / entity.slug / "app.yaml"

    def _serialize(self, entity: App) -> str:
        """Serialize app to YAML format."""
        return serialize_app(entity)

    def _load_all(self) -> None:
        """Load all apps from YAML manifests."""
        if not self.base_path.exists():
            logger.info(f"Apps directory not found: {self.base_path}")
            return

        apps = scan_app_manifests(self.base_path)
        for app in apps:
            self.storage_dict[app.slug] = app

        logger.info(f"Loaded {len(self.storage_dict)} apps from {self.base_path}")

    async def get_by_type(self, app_type: AppType) -> list[App]:
        """Get all apps of a specific type."""
        return [app for app in self.storage_dict.values() if app.app_type == app_type]

    async def get_by_name(self, name: str) -> App | None:
        """Get an app by its display name (case-insensitive)."""
        name_normalized = normalize_name(name)
        for app in self.storage_dict.values():
            if app.name_normalized == name_normalized:
                return app
        return None

    async def get_with_accelerator(self, accelerator_slug: str) -> list[App]:
        """Get apps that expose a specific accelerator."""
        return [
            app
            for app in self.storage_dict.values()
            if accelerator_slug in (app.accelerators or [])
        ]

    async def get_all_types(self) -> set[AppType]:
        """Get all unique app types that have apps."""
        return {app.app_type for app in self.storage_dict.values()}

    async def get_apps_with_accelerators(self) -> list[App]:
        """Get all apps that have accelerators defined."""
        return [app for app in self.storage_dict.values() if app.accelerators]

    async def get_by_accelerator(self, accelerator_slug: str) -> list[App]:
        """Get all apps that reference a specific accelerator."""
        return [
            app
            for app in self.storage_dict.values()
            if accelerator_slug in app.accelerators
        ]

    async def list_filtered(
        self,
        app_type: str | None = None,
        has_accelerator: str | None = None,
    ) -> list[App]:
        """List apps matching filters.

        Uses AND logic when multiple filters are provided.
        """
        apps = list(self.storage_dict.values())

        # Filter by app type
        if app_type is not None:
            target_type = AppType.from_string(app_type)
            apps = [a for a in apps if a.app_type == target_type]

        # Filter by accelerator
        if has_accelerator is not None:
            apps = [a for a in apps if has_accelerator in a.accelerators]

        return apps
