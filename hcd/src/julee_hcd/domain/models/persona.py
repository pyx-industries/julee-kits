"""Persona domain model.

A persona arrives one of two ways. Someone writes one, giving it goals,
frustrations and the jobs it is trying to get done; or one is derived from
the "As a ..." of a user story, which yields little more than a name.

Both are the same entity. is_defined tells them apart, and a derived
persona can be written up later without becoming a different thing.

The deriving is at the bottom of this module. It lived in ``usecases/``,
which is how two use cases came to import each other to share it; a pure
function over entities is not a use case and does not need to be a port
either, so it lives with the entity it is about, as
``content_multihash`` lives with the multihash.
"""

from dataclasses import dataclass, replace
from typing import Any, Self, cast

from julee.core.utils import normalize_name
from julee.core.values.text import Name, Slug

from .app import App
from .base import Authored
from .epic import Epic
from .story import Story

# FIXME: this is a kludge. A field that lies about its type until
# __post_init__ runs is a hidden turd: the annotation says Slug and the
# value is a bare str for as long as it takes to construct the entity,
# and every reader has to know that to trust the annotation. It stands
# because a pydantic default_factory could read the other fields — this
# one derived the slug from the name — and a dataclass one cannot, and
# the alternative, making slug a property, would take away a caller's
# right to name one, which from_definition and the RST repository both
# exercise. The real fix is to decide whether a derived slug is derived
# or given, and stop letting it be both.
DERIVE_IT = cast("Slug", "")
"""The slug default, meaning "name it after the persona".

A persona derived from a story has only a name to be identified by, so
the name is what the slug comes from.

``Slug`` refuses an empty string, so the default cannot be a real one.
It is a plain ``str`` until ``__post_init__`` replaces it, built there
by ``Slug`` exactly as a given one is.
"""


@dataclass(frozen=True, kw_only=True)
class Persona(Authored):
    """A kind of person the solution is for.

    Personas are the "As a ..." in "As a [persona], I want to ...", and
    what the people writing the solution down know about them.
    """

    name: Name
    """Display name of the persona (e.g., "Knowledge Curator")."""

    slug: Slug = DERIVE_IT
    """Identifier; derived from the name when not given."""

    goals: tuple[str, ...] = ()
    """What this persona is trying to achieve."""

    frustrations: tuple[str, ...] = ()
    """What gets in this persona's way today."""

    jobs_to_be_done: tuple[str, ...] = ()
    """The jobs this persona hires the solution to do."""

    context: str = ""
    """The circumstances this persona works in."""

    app_slugs: tuple[Slug, ...] = ()
    """List of app slugs this persona uses."""

    epic_slugs: tuple[Slug, ...] = ()
    """List of epic slugs containing stories for this persona."""

    accelerator_slugs: tuple[Slug, ...] = ()
    """Accelerators this persona's work draws on."""

    contrib_slugs: tuple[Slug, ...] = ()
    """Contrib modules this persona's work draws on."""

    def __post_init__(self) -> None:
        """Name the persona after itself if it was not given a slug."""
        if not self.slug:
            object.__setattr__(self, "slug", Slug(self.name))

    @property
    def normalized_name(self) -> str:
        """Get normalized name for matching.

        A plain property, so it is no longer serialised. It was a
        ``computed_field``, which put it on the wire; nothing reads it
        from there, and it is derived from the name that travels beside
        it.
        """
        return self.name.normalized

    @property
    def display_name(self) -> str:
        """Get formatted name for display (same as name)."""
        return self.name

    @property
    def app_count(self) -> int:
        """Get number of apps this persona uses."""
        return len(self.app_slugs)

    @property
    def epic_count(self) -> int:
        """Get number of epics this persona participates in."""
        return len(self.epic_slugs)

    @property
    def has_apps(self) -> bool:
        """Check if persona uses any apps."""
        return len(self.app_slugs) > 0

    @property
    def has_epics(self) -> bool:
        """Check if persona participates in any epics."""
        return len(self.epic_slugs) > 0

    def uses_app(self, app_slug: str) -> bool:
        """Check if persona uses a specific app.

        Args:
            app_slug: App slug to check

        Returns:
            True if persona uses this app
        """
        return app_slug in self.app_slugs

    def participates_in_epic(self, epic_slug: str) -> bool:
        """Check if persona participates in a specific epic.

        Args:
            epic_slug: Epic slug to check

        Returns:
            True if persona has stories in this epic
        """
        return epic_slug in self.epic_slugs

    def with_app(self, app_slug: str) -> "Persona":
        """The persona with an app added; a duplicate returns this persona.

        Args:
            app_slug: App slug to add
        """
        if app_slug in self.app_slugs:
            return self
        return replace(self, app_slugs=(*self.app_slugs, Slug(app_slug)))

    def with_epic(self, epic_slug: str) -> "Persona":
        """The persona with an epic added; a duplicate returns this persona.

        Args:
            epic_slug: Epic slug to add
        """
        if epic_slug in self.epic_slugs:
            return self
        return replace(self, epic_slugs=(*self.epic_slugs, Slug(epic_slug)))

    @property
    def is_defined(self) -> bool:
        """Whether someone wrote this persona up, rather than it being derived.

        A persona derived from a story has a name and nothing else to say
        about the person behind it.
        """
        return bool(
            self.goals or self.frustrations or self.jobs_to_be_done or self.context
        )

    @classmethod
    def from_definition(
        cls,
        slug: str,
        name: str,
        goals: tuple[str, ...] = (),
        frustrations: tuple[str, ...] = (),
        jobs_to_be_done: tuple[str, ...] = (),
        context: str = "",
        docname: str = "",
    ) -> Self:
        """A persona somebody wrote up, with what they know about them.

        Args:
            slug: Identifier for the persona
            name: Display name
            goals: What the persona is trying to achieve
            frustrations: What gets in their way today
            jobs_to_be_done: The jobs they hire the solution to do
            context: The circumstances they work in
            docname: Document the persona was written in
        """
        return cls(
            slug=Slug(slug),
            name=Name(name),
            goals=goals,
            frustrations=frustrations,
            jobs_to_be_done=jobs_to_be_done,
            context=context,
            docname=docname,
        )

    @classmethod
    def from_story_reference(cls, name: str, app_slug: str = "") -> Self:
        """A persona derived from the "As a ..." of a story.

        All that is known is the name, and which app the story was about.

        Args:
            name: The persona named in the story
            app_slug: App the story belongs to, if any
        """
        return cls(
            name=Name(name),
            app_slugs=(Slug(app_slug),) if app_slug.strip() else (),
        )


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


def merge_personas(
    defined: list[Persona],
    stories: list[Story],
    epics: list[Epic],
) -> list[Persona]:
    """Every persona this context knows about, authored and derived.

    What was authored stands: a defined persona keeps what was written
    about it and gains the apps and epics its stories turn up in. A
    persona only the stories mention is included as it was found, so a
    story referring to nobody defined still has somebody to refer to.

    Args:
        defined: Personas that were authored, from a PersonaRepository
        stories: All Story entities
        epics: All Epic entities

    Returns:
        The merged personas, sorted by name
    """
    derived_data = _derive_raw(stories, epics)
    by_normalized_name = {persona.normalized_name: persona for persona in defined}

    merged_personas: list[Persona] = []
    for normalized_name, defined_persona in by_normalized_name.items():
        data = derived_data.get(normalized_name)
        if data is None:
            merged_personas.append(defined_persona)
            continue

        merged = defined_persona
        for app_slug in sorted(data["apps"]):
            merged = merged.with_app(app_slug)
        for epic_slug in sorted(data["epics"]):
            merged = merged.with_epic(epic_slug)
        merged_personas.append(merged)

    for normalized_name, data in derived_data.items():
        if normalized_name in by_normalized_name:
            continue
        merged_personas.append(
            Persona(
                name=data["name"],
                app_slugs=tuple(sorted(data["apps"])),
                epic_slugs=tuple(sorted(data["epics"])),
            )
        )

    return sorted(merged_personas, key=lambda p: p.name)


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

    # Group personas by app type. A plain dict rather than a
    # defaultdict: collections is not part of the language a use case
    # speaks, and setdefault says the same thing in it.
    personas_by_type: dict[str, list[Persona]] = {}

    for persona in all_personas:
        # Find all app types this persona uses
        persona_types: set[str] = set()
        for app_slug in persona.app_slugs:
            app_type = app_types.get(app_slug, "unknown")
            persona_types.add(app_type)

        # Add persona to each type group
        for app_type in persona_types:
            personas_by_type.setdefault(app_type, []).append(persona)

    # Sort personas within each group
    return {
        app_type: sorted(personas, key=lambda p: p.name)
        for app_type, personas in personas_by_type.items()
    }


def get_personas_for_app(
    app: App,
    stories: list[Story],
    epics: list[Epic],
) -> list[Persona]:
    """Get personas that use an app.

    Args:
        app: App to find personas for
        stories: All Story entities
        epics: All Epic entities (for persona derivation)

    Returns:
        List of Persona entities that use this app, sorted by name
    """
    # Derive all personas that show up in these stories/epics
    all_personas = derive_personas_from_stories(stories, epics)

    # Filter to those using this app
    matching = [p for p in all_personas if app.slug in p.app_slugs]
    return sorted(matching, key=lambda p: p.name)
