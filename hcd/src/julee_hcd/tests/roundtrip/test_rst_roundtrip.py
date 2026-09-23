"""The RST round-trip: a document read and written back is the document.

This is the thing the rst repositories exist for, and the reason the
entities carry page_title, preamble_rst and epilogue_rst. A round-trip
that reformats would put noise into the diff of every documentation
repository that saves an entity, so byte equality is the bar, not
equality of the parts this kit happens to model.
"""

from pathlib import Path

import pytest

from julee_hcd.infrastructure.repositories.rst.epic import RstEpicRepository

pytestmark = pytest.mark.unit

EPIC_RST = """Getting people started
======================

Some words before.

.. define-epic:: onboarding

   How a new person gets going.

   .. epic-story:: Sign up

Some words after.
"""


@pytest.fixture
def epic_dir(tmp_path: Path) -> Path:
    """A directory holding one epic document."""
    (tmp_path / "onboarding.rst").write_text(EPIC_RST)
    return tmp_path


async def test_everything_the_document_said_is_read_back(epic_dir: Path) -> None:
    """Including the parts that are not the entity's own fields."""
    epic = await RstEpicRepository(epic_dir).get("onboarding")

    assert epic is not None
    assert epic.slug == "onboarding"
    assert epic.description == "How a new person gets going."
    assert epic.story_refs == ("Sign up",)
    assert epic.page_title == "Getting people started"
    assert epic.preamble_rst == "Some words before."
    assert epic.epilogue_rst == "Some words after."


async def test_writing_back_gives_the_same_bytes(epic_dir: Path) -> None:
    """The round-trip, stated as plainly as it can be."""
    repo = RstEpicRepository(epic_dir)
    epic = await repo.get("onboarding")
    assert epic is not None

    await repo.save(epic)

    assert (epic_dir / "onboarding.rst").read_text() == EPIC_RST


async def test_saving_twice_changes_nothing_the_second_time(
    epic_dir: Path,
) -> None:
    """Saving is idempotent, so a build does not churn the repository."""
    first = RstEpicRepository(epic_dir)
    epic = await first.get("onboarding")
    assert epic is not None
    await first.save(epic)
    after_one = (epic_dir / "onboarding.rst").read_text()

    second = RstEpicRepository(epic_dir)
    reread = await second.get("onboarding")
    assert reread is not None
    await second.save(reread)

    assert (epic_dir / "onboarding.rst").read_text() == after_one


async def test_an_edit_keeps_the_prose_around_it(epic_dir: Path) -> None:
    """Changing a field must not discard what the author wrote around it."""
    repo = RstEpicRepository(epic_dir)
    epic = await repo.get("onboarding")
    assert epic is not None

    await repo.save(epic.model_copy(update={"description": "Rewritten."}))
    written = (epic_dir / "onboarding.rst").read_text()

    assert "Rewritten." in written
    assert "Some words before." in written
    assert "Some words after." in written
    assert "Getting people started" in written


async def test_deleting_removes_the_document(epic_dir: Path) -> None:
    """An epic nobody kept should not leave its file behind."""
    repo = RstEpicRepository(epic_dir)

    assert await repo.delete("onboarding") is True

    assert not (epic_dir / "onboarding.rst").exists()
