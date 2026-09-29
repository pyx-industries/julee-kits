"""Tests for the resolve_app_references use case.

The four functions it calls are tested next to the entities they
are about, in tests/models/test_app_references.py.
"""

import pytest
from julee.core.entities.text import Name, NonEmptyText, Slug

from julee_hcd.domain.models.app import App, AppType
from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.models.journey import Journey, JourneyStep
from julee_hcd.domain.models.story import Story
from julee_hcd.usecases.resolve_app_references import (
    ResolveAppReferencesRequest,
    ResolveAppReferencesUseCase,
)


def create_app(slug: str, name: str = "") -> App:
    """Helper to create test apps."""
    return App(
        slug=Slug(slug),
        name=Name(name or slug.replace("-", " ").title()),
        app_type=AppType.STAFF,
        manifest_path=f"apps/{slug}/app.yaml",
    )


def create_story(
    feature_title: str,
    app_slug: str,
    persona: str = "Test User",
) -> Story:
    """Helper to create test stories."""
    return Story(
        slug=NonEmptyText(feature_title.lower().replace(" ", "-")),
        feature_title=Name(feature_title),
        persona=Name(persona),
        i_want="test",
        so_that="verify",
        app_slug=Slug(app_slug),
        file_path="test.feature",
    )


def create_epic(slug: str, story_refs: list[str]) -> Epic:
    """Helper to create test epics."""
    return Epic(slug=Slug(slug), story_refs=tuple(story_refs))


def create_journey(slug: str, story_refs: list[str]) -> Journey:
    """Helper to create test journeys."""
    steps = [JourneyStep.story(ref) for ref in story_refs]
    return Journey(slug=Slug(slug), persona="User", steps=tuple(steps))


class TestResolveAppReferencesUseCase:
    """Test the use case that resolves everything an app connects to."""

    @pytest.mark.asyncio
    async def test_cross_references(self) -> None:
        """An app's stories, personas, journeys and epics come back together."""
        app = create_app("vocabulary-tool")
        stories = [
            create_story("Upload Document", "vocabulary-tool", "Curator"),
            create_story("Review Document", "vocabulary-tool", "Reviewer"),
        ]
        epics = [
            create_epic(
                "vocabulary-management", ["Upload Document", "Review Document"]
            ),
        ]
        journeys = [
            create_journey("build-vocabulary", ["Upload Document"]),
        ]

        response = await ResolveAppReferencesUseCase().execute(
            ResolveAppReferencesRequest(
                app=app,
                stories=tuple(stories),
                epics=tuple(epics),
                journeys=tuple(journeys),
            )
        )

        assert len(response.stories) == 2
        assert len(response.personas) == 2
        assert len(response.journeys) == 1
        assert len(response.epics) == 1
