"""Tests for how CEAP names a document's content.

The point of #44 was that five places computed this and three of them
disagreed. These say what the one implementation produces, so a fourth
answer cannot arrive quietly.
"""

import hashlib

import pytest

from julee_ceap.domain.models.document import Document
from julee_ceap.domain.models.document.multihash import (
    content_multihash,
    is_content_multihash,
)

from .factories import ContentStreamFactory


class TestComputingIt:
    def test_it_is_the_sha256_multihash_of_the_content(self) -> None:
        """1220 is multihash's prefix for sha2-256 at 32 bytes."""
        digest = hashlib.sha256(b"hello").hexdigest()

        assert content_multihash(b"hello") == f"1220{digest}"

    def test_the_same_content_gets_the_same_name(self) -> None:
        """Which is what lets the MinIO repository use it as the key."""
        assert content_multihash(b"hello") == content_multihash(b"hello")

    def test_different_content_gets_a_different_name(self) -> None:
        assert content_multihash(b"hello") != content_multihash(b"goodbye")

    def test_empty_content_still_has_a_name(self) -> None:
        assert is_content_multihash(content_multihash(b""))


class TestRecognisingIt:
    def test_what_it_computes_is_what_it_accepts(self) -> None:
        assert is_content_multihash(content_multihash(b"hello"))

    def test_a_bare_sha256_is_not_one(self) -> None:
        """What the memory repository used to write (#44)."""
        assert not is_content_multihash(hashlib.sha256(b"hello").hexdigest())

    def test_sha256_and_a_digest_is_not_one(self) -> None:
        """What initialize_system_data used to write (#44)."""
        digest = hashlib.sha256(b"hello").hexdigest()

        assert not is_content_multihash(f"sha256-{digest}")

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "   ",
            "test-hash-123",
            "1220",
            "1220" + "f" * 63,
            "1220" + "f" * 65,
            "1220" + "g" * 64,
            "1221" + "f" * 64,
            "1220" + "F" * 64,
        ],
    )
    def test_a_value_of_the_wrong_shape_is_not_one(self, value: str) -> None:
        """Wrong length, wrong alphabet, wrong function code, wrong case."""
        assert not is_content_multihash(value)


class TestWhatADocumentAccepts:
    def test_a_document_takes_a_real_multihash(self) -> None:
        document = Document(
            document_id="doc-1",
            original_filename="test.txt",
            content_type="text/plain",
            size_bytes=5,
            content_multihash=content_multihash(b"hello"),
            content=ContentStreamFactory.build(),
        )

        assert document.content_multihash == content_multihash(b"hello")

    @pytest.mark.parametrize(
        "value",
        ["", "   ", "test-hash-123", hashlib.sha256(b"hello").hexdigest()],
    )
    def test_a_document_refuses_anything_else(self, value: str) -> None:
        """The part that stops a fourth format arriving: every route that
        builds a Document has to go through the one implementation."""
        with pytest.raises(ValueError, match="multihash"):
            Document(
                document_id="doc-1",
                original_filename="test.txt",
                content_type="text/plain",
                size_bytes=5,
                content_multihash=value,
                content=ContentStreamFactory.build(),
            )

    def test_the_factory_names_the_content_it_builds(self) -> None:
        """It was Faker("sha256"), unrelated to the factory's own content."""
        from .factories import DocumentFactory

        document = DocumentFactory.build()

        assert is_content_multihash(document.content_multihash)
