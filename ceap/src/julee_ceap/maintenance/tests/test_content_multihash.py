"""Tests for classifying a stored content name.

The decisions the migration rests on, tested without a store.
"""

import pytest

from julee_ceap.domain.models.document.multihash import content_multihash
from julee_ceap.maintenance.content_multihash import (
    Naming,
    classify,
    legacy_content_multihash,
    metadata_rewrites,
    unresolved_content_names,
)

pytestmark = pytest.mark.unit

CONTENT = b"This is test content for document storage"


class TestTellingThemApart:
    def test_the_current_name_is_the_multihash_of_the_content(self) -> None:
        assert classify(content_multihash(CONTENT), CONTENT) is Naming.CURRENT

    def test_the_legacy_name_is_recognised(self) -> None:
        assert classify(legacy_content_multihash(CONTENT), CONTENT) is Naming.LEGACY

    def test_anything_else_is_left_alone(self) -> None:
        """Something else wrote it, or the bytes are not the bytes that
        named it. Either way the migration does not guess."""
        assert classify("1220" + "f" * 64, CONTENT) is Naming.UNKNOWN

    def test_the_two_namings_never_coincide(self) -> None:
        """Which is what makes the classification decidable: a match of
        both would need sha256(c) == sha256(sha256(c))."""
        for content in [b"", b"a", CONTENT, b"x" * 10_000]:
            assert content_multihash(content) != legacy_content_multihash(content)

    def test_they_are_the_same_shape(self) -> None:
        """So a stored value cannot be classified by looking at it. This
        is the reason the migration has to read the content."""
        current = content_multihash(CONTENT)
        legacy = legacy_content_multihash(CONTENT)

        assert len(current) == len(legacy)
        assert current[:4] == legacy[:4] == "1220"

    def test_classifying_is_stable_under_repetition(self) -> None:
        """An already-migrated object reads as CURRENT, which is what
        makes a second run a no-op."""
        name = content_multihash(CONTENT)

        assert classify(name, CONTENT) is classify(name, CONTENT) is Naming.CURRENT


class TestWhichDocumentsMove:
    def test_a_document_naming_a_renamed_object_is_rewritten(self) -> None:
        legacy = legacy_content_multihash(CONTENT)
        current = content_multihash(CONTENT)

        rewrites = metadata_rewrites([("doc-1", legacy)], {legacy: current})

        assert rewrites == [("doc-1", legacy, current)]

    def test_a_document_already_naming_the_current_object_is_left(self) -> None:
        current = content_multihash(CONTENT)

        assert metadata_rewrites([("doc-1", current)], {}) == []

    def test_every_document_sharing_content_moves_together(self) -> None:
        """Two documents with the same content share one object, before
        and after, so the mapping stays one to one."""
        legacy = legacy_content_multihash(CONTENT)
        current = content_multihash(CONTENT)

        rewrites = metadata_rewrites(
            [("doc-1", legacy), ("doc-2", legacy)], {legacy: current}
        )

        assert [wanted for _, _, wanted in rewrites] == [current, current]


class TestAskingTheStore:
    def test_content_that_is_present_raises_nothing(self) -> None:
        current = content_multihash(CONTENT)

        assert unresolved_content_names([("doc-1", current)], [current]) == []

    def test_content_that_is_absent_is_named(self) -> None:
        current = content_multihash(CONTENT)

        (objection,) = unresolved_content_names([("doc-1", current)], [])

        assert "doc-1" in objection
        assert current in objection

    def test_a_store_with_nothing_in_it_and_nothing_expected_is_fine(self) -> None:
        assert unresolved_content_names([], []) == []
