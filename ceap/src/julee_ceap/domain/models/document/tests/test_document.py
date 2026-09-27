"""
Comprehensive tests for Document domain model.

This test module documents the design decisions made for the Document domain
model
using table-based tests. It covers:

- Document instantiation with various field combinations
- Content stream operations (read, seek, tell)
- Validation rules and error conditions
- JSON serialization behavior
- Stream-like interface compatibility

Design decisions documented:
- Documents must have all required fields
- Content streams are excluded from JSON serialization
- Size must be positive, filenames and content types non-empty
- Multihash is required and non-empty
- Documents act as readable streams with standard methods
"""

import hashlib
import json

import pytest
from pydantic import ValidationError

from julee_ceap.domain.models.document import Document
from julee_ceap.domain.models.document.multihash import (
    content_multihash as multihash_of,
)

from .factories import DocumentFactory

pytestmark = pytest.mark.unit


class TestDocumentInstantiation:
    """Test Document creation with various field combinations."""

    @pytest.mark.parametrize(
        "document_id,original_filename,content_type,size_bytes,multihash,expected_success",
        [
            # Valid cases
            ("doc-1", "test.txt", "text/plain", 100, multihash_of(b"hash"), True),
            (
                "doc-2",
                "document.pdf",
                "application/pdf",
                1024,
                multihash_of(b"pdf-hash"),
                True,
            ),
            (
                "doc-3",
                "data.json",
                "application/json",
                50,
                multihash_of(b"json-hash"),
                True,
            ),
            # Invalid cases - empty required fields
            (
                "",
                "test.txt",
                "text/plain",
                100,
                multihash_of(b"hash"),
                False,
            ),  # Empty document_id
            (
                "doc-4",
                "",
                "text/plain",
                100,
                multihash_of(b"hash"),
                False,
            ),  # Empty filename
            (
                "doc-5",
                "test.txt",
                "",
                100,
                multihash_of(b"hash"),
                False,
            ),  # Empty content_type
            (
                "doc-6",
                "test.txt",
                "text/plain",
                100,
                "",
                False,
            ),  # Empty multihash
            (
                "doc-6b",
                "test.txt",
                "text/plain",
                100,
                hashlib.sha256(b"hash").hexdigest(),
                False,
            ),  # A bare sha256 is not a multihash (#44)
            (
                "doc-6c",
                "test.txt",
                "text/plain",
                100,
                f"sha256-{hashlib.sha256(b'hash').hexdigest()}",
                False,
            ),  # Nor is "sha256-" and a digest (#44)
            # Invalid cases - whitespace only
            (
                "   ",
                "test.txt",
                "text/plain",
                100,
                multihash_of(b"hash"),
                False,
            ),  # Whitespace document_id
            (
                "doc-7",
                "   ",
                "text/plain",
                100,
                multihash_of(b"hash"),
                False,
            ),  # Whitespace filename
            (
                "doc-8",
                "test.txt",
                "   ",
                100,
                multihash_of(b"hash"),
                False,
            ),  # Whitespace content_type
            (
                "doc-9",
                "test.txt",
                "text/plain",
                100,
                "   ",
                False,
            ),  # Whitespace multihash
            # Invalid cases - size validation
            (
                "doc-10",
                "test.txt",
                "text/plain",
                0,
                multihash_of(b"hash"),
                False,
            ),  # Zero size
            (
                "doc-11",
                "test.txt",
                "text/plain",
                -1,
                multihash_of(b"hash"),
                False,
            ),  # Negative size
        ],
    )
    def test_document_creation_validation(
        self,
        document_id: str,
        original_filename: str,
        content_type: str,
        size_bytes: int,
        multihash: str,
        expected_success: bool,
    ) -> None:
        """Test document creation with various field validation scenarios."""

        if expected_success:
            # Should create successfully
            doc = Document(
                document_id=document_id,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=size_bytes,
                content_multihash=multihash,
            )
            assert doc.document_id == document_id
            assert doc.original_filename.strip() == original_filename.strip()
            assert doc.content_type.strip() == content_type.strip()
            assert doc.size_bytes == size_bytes
            assert doc.content_multihash.strip() == multihash.strip()
        else:
            # Should raise validation error
            with pytest.raises((ValueError, ValidationError)):
                Document(
                    document_id=document_id,
                    original_filename=original_filename,
                    content_type=content_type,
                    size_bytes=size_bytes,
                    content_multihash=multihash,
                )


class TestDocumentSerialization:
    """Test Document JSON serialization behavior."""

    def test_document_json_carries_no_content(self) -> None:
        """Content is not in the JSON because it is not in the document.

        It used to be a field marked exclude=True, kept off the wire
        because a live stream cannot go on it. The absence was a
        property of the serialiser; it is a property of the entity now,
        and a reader of the JSON sees the name of the content instead.
        """
        doc = DocumentFactory.build(size_bytes=27)

        json_str = doc.model_dump_json()
        json_data = json.loads(json_str)

        assert "content" not in json_data
        assert "content_bytes" not in json_data
        assert json_data["content_multihash"] == doc.content_multihash

        # But all other fields should be present
        assert json_data["document_id"] == doc.document_id
        assert json_data["original_filename"] == doc.original_filename
        assert json_data["content_type"] == doc.content_type
        assert json_data["size_bytes"] == doc.size_bytes
        assert json_data["content_multihash"] == doc.content_multihash
        assert json_data["status"] == doc.status.value


class TestDocumentNeedsNoContentToBeValid:
    """What a Document is now, and what it no longer claims.

    This class used to hold four tests of an invariant saying every
    document carries content — one for content, one for content_bytes,
    one for neither being an error, and one asserting that Temporal
    deserialisation was allowed to skip the whole thing by passing
    ``context={"temporal_validation": True}``.

    That last test was the defect written down as a requirement. The
    invariant was false in transit by construction, since a live stream
    cannot be serialised, and the flag existed to say so quietly. A
    document that names its content claims nothing the transport cannot
    honour, so there is nothing left to skip (#69).
    """

    def test_a_document_is_valid_with_no_content_attached(self) -> None:
        """The case that used to raise, and is now ordinary."""
        doc = Document(
            document_id="test-doc",
            original_filename="spec.json",
            content_type="application/json",
            size_bytes=100,
            content_multihash=multihash_of(b"test_hash"),
        )

        assert doc.document_id == "test-doc"

    def test_deserialising_needs_no_special_context(self) -> None:
        """What comes back from a Temporal activity is an ordinary
        Document, validated the ordinary way. It used to need a context
        flag naming Temporal, read by the entity itself."""
        document_data = {
            "document_id": "test-temporal",
            "original_filename": "temporal.json",
            "content_type": "application/json",
            "size_bytes": 100,
            "content_multihash": multihash_of(b"test_hash"),
        }

        doc = Document.model_validate(document_data)

        assert doc.document_id == "test-temporal"

    def test_a_document_does_not_carry_content(self) -> None:
        """Said directly: the fields are gone, not merely unused, so
        nothing can put a stream back on an entity and have it mean
        something."""
        doc = Document(
            document_id="test-doc",
            original_filename="spec.json",
            content_type="application/json",
            size_bytes=100,
            content_multihash=multihash_of(b"test_hash"),
        )

        assert not hasattr(doc, "content")
        assert not hasattr(doc, "content_bytes")
