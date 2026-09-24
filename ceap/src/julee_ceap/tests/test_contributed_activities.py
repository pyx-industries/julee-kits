"""The activities this kit hands a worker.

A class decorated @temporal_activity_registration is not registered
anywhere a solution can see. The manifest is how the kit says what there
is, and until now it named the module holding them, which a solution
cannot act on without guessing which of the module's names qualify.

The tuples are written by hand, so these check they still match the code.
The __all__ they replaced had drifted: seven entries against nine
decorated classes.
"""

import importlib

import pytest

from julee_ceap import kit
from julee_ceap.infrastructure.repositories.temporal import (
    activities as repository_activities,
)
from julee_ceap.infrastructure.services.temporal import (
    activities as service_activities,
)

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
    """The classes the manifest hands a solution at the activity point.

    A path names one thing, and here that thing is a tuple, so each is
    resolved and flattened. julee 0.5.13 grew contributed_objects() to do
    this; doing it here keeps the kit working against the julee it pins.
    """
    found: list[type] = []
    for path in kit.contributed(POINT):
        found.extend(resolve(path))  # type: ignore[arg-type]
    return tuple(found)


def decorated_in(module: object) -> set[str]:
    """Names in a module that the activity decorator has been applied to.

    The decorator returns the class it was given, so it leaves no mark on
    the class itself. What it does leave is a Temporal activity
    definition on every async method it wrapped, which is what a worker
    registers, so that is what to look for.
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


def test_the_manifest_offers_activities() -> None:
    assert kit.contributed(POINT)


def test_every_contributed_activity_is_a_class() -> None:
    """A worker is given classes and constructs them with its own clients."""
    offered = contributed_activities()

    assert offered
    assert all(isinstance(obj, type) for obj in offered)


def test_the_repository_activities_are_all_offered() -> None:
    assert set(repository_activities.ACTIVITY_CLASSES) <= set(contributed_activities())


def test_the_service_activities_are_all_offered() -> None:
    """Services are activities too, and live in a second module."""
    assert set(service_activities.ACTIVITY_CLASSES) <= set(contributed_activities())


@pytest.mark.parametrize(
    "module",
    [repository_activities, service_activities],
    ids=["repositories", "services"],
)
def test_no_decorated_class_is_left_out_of_its_tuple(module: object) -> None:
    """The check that the hand-written tuple has not drifted again."""
    in_tuple = {cls.__name__ for cls in module.ACTIVITY_CLASSES}  # type: ignore[attr-defined]

    assert decorated_in(module) - in_tuple == set()


def test_the_decorated_classes_are_found_at_all() -> None:
    """Guards the rule above against passing because it found nothing."""
    assert len(decorated_in(repository_activities)) == 8
    assert len(decorated_in(service_activities)) == 1


def test_nothing_is_offered_twice() -> None:
    offered = contributed_activities()

    assert len(set(offered)) == len(offered)
