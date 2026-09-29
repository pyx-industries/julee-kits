"""
Document domain models for the Capture, Extract, Assemble, Publish workflow.

This module contains the core document domain objects that represent
documents and their metadata in the CEAP workflow system.

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from julee.core.entities.text import NonEmptyText

from julee_ceap.domain.models.document.multihash import ContentMultihash


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


@dataclass(frozen=True, kw_only=True)
class Document:
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
    document_id: NonEmptyText
    original_filename: NonEmptyText
    content_type: NonEmptyText
    size_bytes: int
    """Size must be positive."""
    content_multihash: ContentMultihash
    """Multihash of document content for integrity verification."""
    """The name the content is stored under.

    The rule that this is a well-formed multihash was a validator here
    until #71. It is the type's now, so the repository's object key, a
    use case passing one along, and a port returning one all carry the
    rule instead of taking the shape on trust.

    Not merely non-empty, which is what it checked until #44: three
    formats were in circulation — a real multihash, a bare sha256 hex
    digest, and "sha256-" followed by one — so the same document was
    named differently depending on which adapter stored it.
    """

    # Document processing state
    status: DocumentStatus = DocumentStatus.CAPTURED
    knowledge_service_id: str | None = None
    assembly_types: tuple[str, ...] = ()

    # Timestamps
    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))

    additional_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Refuse a document with no content.

        This was ``Field(gt=0)``, which pydantic enforced and a
        dataclass does not. A zero-byte document has nothing to
        extract, assemble or validate, and would otherwise be stored as
        though it had.

        Raises:
            ValueError: If size_bytes is not positive
        """
        if self.size_bytes <= 0:
            raise ValueError(
                f"size_bytes must be greater than 0, got {self.size_bytes}"
            )
