"""DerivePersonasUseCase with co-located request/response.

Use case for deriving personas from stories and epics.

Supports two persona sources:
1. Defined personas: Explicitly created via define-persona directive
2. Derived personas: Extracted from user story "As a..." clauses

Defined personas are authoritative and get enriched with story data.
Derived personas fill gaps when stories reference undefined personas.
"""

from collections import defaultdict
from typing import Any

from julee.core.utils import normalize_name
from pydantic import BaseModel

from julee_hcd.domain.models.app import App
from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.models.story import Story
from julee_hcd.domain.repositories.epic import EpicRepository
from julee_hcd.domain.repositories.persona import PersonaRepository
from julee_hcd.domain.repositories.story import StoryRepository


def _derive_raw(stories: list[Story], epics: list[Epic]) -> dict[str, dict[str, Any]]:
    """Persona data collected from stories and epics, keyed by normalized name.

    Args:
        stories: All Story entities
        epics: All Epic entities

    Returns:
        Mapping of normalized persona name to its display name and the
        apps and epics it was seen in
    """
    derived_data: dict[str, dict[str, Any]] = {}

    for story in stories:
        normalized = story.persona_normalized
        if not normalized or normalized == "unknown":
            continue

        entry = derived_data.setdefault(
            normalized,
            {"name": story.persona, "apps": set(), "epics": set()},
        )
        entry["apps"].add(story.app_slug)

    story_to_persona: dict[str, str] = {
        normalize_name(story.feature_title): story.persona_normalized
        for story in stories
    }

    for epic in epics:
        for story_ref in epic.story_refs:
            persona_normalized = story_to_persona.get(normalize_name(story_ref))
            if persona_normalized and persona_normalized in derived_data:
                derived_data[persona_normalized]["epics"].add(epic.slug)

    return derived_data


def derive_personas_from_stories(
    stories: list[Story], epics: list[Epic]
) -> list[Persona]:
    """Derive personas from stories and epics alone, with no authored data.

    Used where there is no PersonaRepository to consult — the personas
    that come back are always derived-only.

    Args:
        stories: All Story entities
        epics: All Epic entities

    Returns:
        List of Persona entities, sorted by name
    """
    personas = [
        Persona(
            name=data["name"],
            app_slugs=tuple(sorted(data["apps"])),
            epic_slugs=tuple(sorted(data["epics"])),
        )
        for data in _derive_raw(stories, epics).values()
    ]
    return sorted(personas, key=lambda p: p.name)


class DerivePersonasRequest(BaseModel):
    """Request for deriving personas from stories and epics."""


class DerivePersonasResponse(BaseModel):
    """Response from deriving personas."""

    personas: list[Persona]


class DerivePersonasUseCase:
    """Derive and merge personas.

    Combines defined personas (from PersonaRepository) with derived
    personas (from stories). Defined personas are authoritative and
    get enriched with app_slugs/epic_slugs from their stories.
    """

    def __init__(
        self,
        story_repo: StoryRepository,
        epic_repo: EpicRepository,
        persona_repo: PersonaRepository | None = None,
    ) -> None:
        """Initialize with repository dependencies.

        Args:
            story_repo: Story repository instance
            epic_repo: Epic repository instance
            persona_repo: Optional persona repository for defined personas
        """
        self.story_repo = story_repo
        self.epic_repo = epic_repo
        self.persona_repo = persona_repo

    async def execute(self, request: DerivePersonasRequest) -> DerivePersonasResponse:
        """Derive and merge personas from all sources.

        Process:
        1. Fetch defined personas from PersonaRepository (if available)
        2. Derive personas from stories (extract from "As a..." clauses)
        3. Merge: defined personas get enriched with app_slugs/epic_slugs
        4. Derived personas without definitions are included as fallback

        Args:
            request: Derive personas request (extensible for filtering)

        Returns:
            Response containing merged list of personas
        """
        stories = await self.story_repo.list_all()
        epics = await self.epic_repo.list_all()

        defined_personas: dict[str, Persona] = {}
        if self.persona_repo:
            for persona in await self.persona_repo.list_all():
                defined_personas[persona.normalized_name] = persona

        derived_data = _derive_raw(stories, epics)

        result_personas: list[Persona] = []
        seen_normalized: set[str] = set()

        # Defined personas take priority; enrich them with what stories say
        # about the apps and epics they turn up in, without losing what
        # was written about them.
        for normalized_name, defined_persona in defined_personas.items():
            seen_normalized.add(normalized_name)

            data = derived_data.get(normalized_name)
            if data is None:
                result_personas.append(defined_persona)
                continue

            merged = defined_persona
            for app_slug in sorted(data["apps"]):
                merged = merged.with_app(app_slug)
            for epic_slug in sorted(data["epics"]):
                merged = merged.with_epic(epic_slug)
            result_personas.append(merged)

        # Then, add derived personas that have no definition
        for normalized_name, data in derived_data.items():
            if normalized_name in seen_normalized:
                continue

            result_personas.append(
                Persona(
                    name=data["name"],
                    app_slugs=tuple(sorted(data["apps"])),
                    epic_slugs=tuple(sorted(data["epics"])),
                )
            )

        sorted_personas = sorted(result_personas, key=lambda p: p.name)
        return DerivePersonasResponse(personas=sorted_personas)


def get_apps_for_persona(
    persona: Persona,
    apps: list[App],
) -> list[App]:
    """Get App entities for a persona.

    Args:
        persona: Persona to get apps for
        apps: All App entities

    Returns:
        List of App entities this persona uses
    """
    app_lookup = {app.slug: app for app in apps}
    return [app_lookup[slug] for slug in persona.app_slugs if slug in app_lookup]


def get_epics_for_persona(
    persona: Persona,
    epics: list[Epic],
    stories: list[Story],
) -> list[Epic]:
    """Get Epic entities for a persona.

    Args:
        persona: Persona to get epics for
        epics: All Epic entities
        stories: All Story entities

    Returns:
        List of Epic entities containing stories for this persona
    """
    # Build lookup of normalized story title -> normalized persona
    story_to_persona: dict[str, str] = {}
    for story in stories:
        story_to_persona[normalize_name(story.feature_title)] = story.persona_normalized

    matching_epics = []
    for epic in epics:
        for story_ref in epic.story_refs:
            story_normalized = normalize_name(story_ref)
            if story_to_persona.get(story_normalized) == persona.normalized_name:
                matching_epics.append(epic)
                break

    return sorted(matching_epics, key=lambda e: e.slug)


def derive_personas_by_app_type(
    stories: list[Story],
    epics: list[Epic],
    apps: list[App],
) -> dict[str, list[Persona]]:
    """Derive personas grouped by the type of apps they use.

    Args:
        stories: List of Story entities
        epics: List of Epic entities
        apps: List of App entities

    Returns:
        Dict mapping app type strings to lists of Persona entities
    """
    # First derive all personas
    all_personas = derive_personas_from_stories(stories, epics)

    # Build app slug -> app type lookup
    app_types: dict[str, str] = {}
    for app in apps:
        app_types[app.slug] = app.app_type.value if app.app_type else "unknown"

    # Group personas by app type
    personas_by_type: dict[str, list[Persona]] = defaultdict(list)

    for persona in all_personas:
        # Find all app types this persona uses
        persona_types: set[str] = set()
        for app_slug in persona.app_slugs:
            app_type = app_types.get(app_slug, "unknown")
            persona_types.add(app_type)

        # Add persona to each type group
        for app_type in persona_types:
            personas_by_type[app_type].append(persona)

    # Sort personas within each group
    return {
        app_type: sorted(personas, key=lambda p: p.name)
        for app_type, personas in personas_by_type.items()
    }
