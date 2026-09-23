"""Tests for checking documented accelerators against the code.

An accelerator is a bounded context somebody wrote up. This use case
finds the two ways that can drift: a context in the code nobody has
described, and a description of something no longer in the code.
"""

import pytest
from julee.core.entities.accelerator import Accelerator
from julee.core.entities.bounded_context_info import BoundedContextInfo

from julee_hcd.infrastructure.repositories.memory.accelerator import (
    MemoryAcceleratorRepository,
)
from julee_hcd.usecases.validate_accelerators import (
    ValidateAcceleratorsRequest,
    ValidateAcceleratorsUseCase,
)

pytestmark = pytest.mark.unit


async def _accelerators(*slugs: str) -> MemoryAcceleratorRepository:
    """A real repository holding one accelerator per slug."""
    repo = MemoryAcceleratorRepository()
    for slug in slugs:
        await repo.save(Accelerator(slug=slug, objective=f"Do {slug}"))
    return repo


class FakeCodeInfoRepository:
    """The bounded contexts found in the code."""

    def __init__(self, *slugs: str) -> None:
        """Hold one context per slug."""
        self._items = [BoundedContextInfo(slug=s) for s in slugs]

    async def list_all(self) -> list[BoundedContextInfo]:
        """Every discovered bounded context."""
        return self._items


async def test_documentation_that_matches_the_code_raises_nothing() -> None:
    """The case worth having: agreement is silent."""
    use_case = ValidateAcceleratorsUseCase(
        await _accelerators("traceability"),
        FakeCodeInfoRepository("traceability"),
    )

    response = await use_case.execute(ValidateAcceleratorsRequest())

    assert response.issues == []
    assert response.matched_slugs == ["traceability"]


async def test_code_nobody_wrote_up_is_reported_as_undocumented() -> None:
    """Someone added a bounded context and no documentation for it."""
    use_case = ValidateAcceleratorsUseCase(
        await _accelerators(),
        FakeCodeInfoRepository("traceability"),
    )

    response = await use_case.execute(ValidateAcceleratorsRequest())

    assert [i.issue_type for i in response.issues] == ["undocumented"]
    assert response.issues[0].slug == "traceability"


async def test_documentation_for_code_that_is_gone_is_reported() -> None:
    """The other direction: the write-up outlived what it described."""
    use_case = ValidateAcceleratorsUseCase(
        await _accelerators("traceability"),
        FakeCodeInfoRepository(),
    )

    response = await use_case.execute(ValidateAcceleratorsRequest())

    assert [i.issue_type for i in response.issues] == ["no_code"]
    assert response.issues[0].slug == "traceability"


async def test_both_kinds_of_drift_are_reported_together() -> None:
    """A real project drifts both ways at once."""
    use_case = ValidateAcceleratorsUseCase(
        await _accelerators("retired", "kept"),
        FakeCodeInfoRepository("kept", "brand-new"),
    )

    response = await use_case.execute(ValidateAcceleratorsRequest())

    assert {(i.slug, i.issue_type) for i in response.issues} == {
        ("brand-new", "undocumented"),
        ("retired", "no_code"),
    }
    assert response.matched_slugs == ["kept"]


async def test_an_issue_says_which_way_the_drift_goes() -> None:
    """The message is what a person reads, so it has to name the fix."""
    use_case = ValidateAcceleratorsUseCase(
        await _accelerators(),
        FakeCodeInfoRepository("traceability"),
    )

    response = await use_case.execute(ValidateAcceleratorsRequest())

    assert "define-accelerator" in response.issues[0].message
