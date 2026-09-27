"""
Document domain models for the Capture, Extract, Assemble, Publish workflow.

This module contains the core document domain objects that represent
documents and their metadata in the CEAP workflow system.

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from collections.abc import Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from julee.core.entities.entity import Entity
from pydantic import Field, field_validator

from julee_ceap.domain.models.document.multihash import is_content_multihash


class DocumentStatus(StrEnum):
    """Status of a document through the Capture, Extract, Assemble, Publish
    pipeline."""

    CAPTURED = "captured"
    REGISTERED = "registered"  # Registered with knowledge service
    # Assembly specification types determined
    ASSEMBLY_SPECIFICATION_IDENTIFIED = "assembly_specification_identified"
    EXTRACTED = "extracted"  # Extractions completed
    ASSEMBLED = "assembled"  # Template rendered and policies applied
    PUBLISHED = "published"
    FAILED = "failed"


class Document(Entity):
    """A document's metadata, and the name of its content.

    The content is not here. It is stored under its own hash and read
    with ``DocumentRepository.content_of``, which is how the storage
    layer has always kept it: metadata in one bucket, content in
    another, keyed by ``content_multihash``.

    It used to be a field, ``content: ContentStream | None``, excluded
    from serialisation because a live stream cannot be serialised. So a
    Document that had crossed a Temporal boundary never carried it, and
    an invariant saying every document has content was false in transit
    by construction. What that produced was a validator containing

        if info.context.get("temporal_validation"): return self

    in a domain entity: a dependency on the name of an infrastructure
    technology, in the innermost ring, written as a string literal that
    no import linter or type checker would catch. A Document whose
    invariant had been skipped was also indistinguishable from one whose
    invariant held, so nothing downstream could rely on it (#69).

    A document that names its content claims nothing the transport
    cannot honour, so there is nothing left for a flag to silence.
    """

    # Core document identification
    document_id: str
    original_filename: str
    content_type: str
    size_bytes: int = Field(gt=0, description="Size must be positive")
    content_multihash: str = Field(
        description="Multihash of document content for integrity verification"
    )

    # Document processing state
    status: DocumentStatus = DocumentStatus.CAPTURED
    knowledge_service_id: str | None = None
    assembly_types: tuple[str, ...] = Field(default_factory=tuple)

    # Timestamps
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))

    additional_metadata: Mapping[str, Any] = Field(default_factory=dict)

    @field_validator("document_id")
    @classmethod
    def document_id_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Document ID cannot be empty")
        return v.strip()

    @field_validator("original_filename")
    @classmethod
    def filename_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Original filename cannot be empty")
        return v.strip()

    @field_validator("content_type")
    @classmethod
    def content_type_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content type cannot be empty")
        return v.strip()

    @field_validator("content_multihash")
    @classmethod
    def content_multihash_must_be_a_multihash(cls, v: str) -> str:
        """The content name MUST be one :func:`content_multihash` would write.

        Not merely non-empty, which is what this checked until #44. Three
        formats were in circulation — a real multihash, a bare sha256 hex
        digest, and "sha256-" followed by one — so the same document was
        named differently depending on which adapter stored it, and the
        MinIO repository uses that name as the object key.

        Checking the shape here is what stops a fourth appearing: any
        route that builds a Document, test factories included, has to go
        through the one implementation.
        """
        candidate = v.strip() if v else ""
        if not candidate:
            raise ValueError("Content multihash cannot be empty")
        if not is_content_multihash(candidate):
            raise ValueError(
                f"Content multihash must be a hex-encoded sha256 multihash "
                f"('1220' and 64 hex characters), not {candidate!r}. Use "
                f"julee_ceap.domain.models.document.multihash."
                f"content_multihash() to compute one."
            )
        return candidate
