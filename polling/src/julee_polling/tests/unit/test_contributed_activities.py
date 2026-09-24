"""The activities this kit hands a worker.

The manifest named the module holding the activity class, which a
solution cannot act on without guessing which of the module's names
qualify. It now names the class.
"""

import importlib

import pytest

from julee_polling import kit
from julee_polling.infrastructure.temporal import activities

pytestmark = pytest.mark.unit

POINT = "temporal.activities"


def resolve(path: str) -> object:
    """Import what a contribution path names.

    julee 0.5.13 has resolve_contribution() and contributed_objects() for
    this. Spelling it out here keeps the kit working against the julee it
    pins, which is the version a solution installing from PyPI will have.
    """
    module_path, _, attribute = path.partition(":")
    module = importlib.import_module(module_path)
    return getattr(module, attribute) if attribute else module


def contributed_activities() -> tuple[type, ...]:
    """The classes the manifest hands a solution at the activity point."""
    found: list[type] = []
    for path in kit.contributed(POINT):
        found.extend(resolve(path))  # type: ignore[arg-type]
    return tuple(found)


def decorated_in(module: object) -> set[str]:
    """Names in a module the activity decorator has been applied to.

    The decorator returns the class unchanged, so the mark to look for is
    the Temporal activity definition it leaves on each wrapped method.
    """
    return {
        name
        for name, obj in vars(module).items()
        if isinstance(obj, type)
        and any(
            hasattr(getattr(obj, attr, None), "__temporal_activity_definition")
            for attr in dir(obj)
            if not attr.startswith("__")
        )
    }


def test_the_poller_service_is_offered() -> None:
    assert contributed_activities() == (activities.TemporalPollerService,)


def test_every_contributed_activity_is_a_class() -> None:
    assert all(isinstance(obj, type) for obj in contributed_activities())


def test_no_decorated_class_is_left_out_of_the_tuple() -> None:
    in_tuple = {cls.__name__ for cls in activities.ACTIVITY_CLASSES}

    assert decorated_in(activities) - in_tuple == set()


def test_the_decorated_class_is_found_at_all() -> None:
    """Guards the rule above against passing because it found nothing."""
    assert decorated_in(activities) == {"TemporalPollerService"}
