"""
Memory implementation of DocumentRepository.

This module provides an in-memory implementation of the DocumentRepository
protocol that follows the Clean Architecture patterns defined in the
Fun-Police Framework. It handles document storage with content and metadata
in memory dictionaries, ensuring idempotency and proper error handling.

The implementation uses Python dictionaries to store document data, making it
ideal for testing scenarios where external dependencies should be avoided.
All operations are still async to maintain interface compatibility.
"""

import io
import logging
from typing import Any

from julee.core.entities.content_stream import (
    ContentStream,
)
from julee.repositories.memory import MemoryRepositoryMixin

from julee_ceap.domain.models.document import Document
from julee_ceap.domain.models.document.multihash import content_multihash
from julee_ceap.domain.repositories.document import DocumentRepository

logger = logging.getLogger(__name__)


class MemoryDocumentRepository(DocumentRepository, MemoryRepositoryMixin[Document]):
    """
    Memory implementation of DocumentRepository using Python dictionaries.

    This implementation stores document metadata and content in memory:
    - Documents: Dictionary keyed by document_id containing Document objects

    This provides a lightweight, dependency-free option for testing while
    maintaining the same interface as other implementations.
    """

    def __init__(self) -> None:
        """Initialize repository with empty in-memory storage."""
        self.logger = logger
        self.entity_name = "Document"
        self.storage_dict: dict[str, Document] = {}
        self.content_by_multihash: dict[str, bytes] = {}
        """Content kept apart from metadata, keyed by its own hash.

        The shape MinIO uses, for the same reason: content has a name of
        its own, so it can be read again. Bytes rather than the stored
        document's ContentStream, because a stream is spent once read —
        a double that kept one would hand the second reader an empty
        result where the real thing hands over the content (julee#124).
        """

        logger.debug("Initializing MemoryDocumentRepository")

    async def get(self, document_id: str) -> Document | None:
        """Retrieve a document's metadata.

        Metadata only: a document names its content rather than
        carrying it, and content_of() is how a caller reads it.

        Args:
            document_id: Unique document identifier

        Returns:
            Document object if found, None otherwise
        """
        return self.get_entity(document_id)

    async def store_content(self, content: ContentStream) -> str:
        """Keep these bytes under their own name, and say what it is.

        Args:
            content: The bytes to store, read once from where it is

        Returns:
            The multihash the content is stored under
        """
        raw = content.read()
        multihash = content_multihash(raw)
        self.content_by_multihash[multihash] = raw

        self.logger.debug(
            "Content stored",
            extra={"content_multihash": multihash, "content_size": len(raw)},
        )

        return multihash

    async def save(self, document: Document) -> None:
        """Save a document's metadata.

        The content it names is stored by ``store_content``, before
        there is a document to name it — a multihash cannot be known
        until the bytes have been read.

        Args:
            document: Document object to save
        """
        self.save_entity(document, "document_id")

    async def content_of(self, document: Document) -> ContentStream:
        """The content this document names, as a fresh stream.

        A new stream over the stored bytes each call, so two callers
        never share one and nobody has to rewind.

        Args:
            document: The document whose content to read

        Returns:
            A stream over the content, at its start

        Raises:
            ValueError: If the metadata names content that is not stored
        """
        content = self.content_by_multihash.get(document.content_multihash)
        if content is None:
            raise ValueError(
                f"Document {document.document_id} names content "
                f"{document.content_multihash}, which was never stored"
            )
        return ContentStream(io.BytesIO(content))

    async def generate_id(self) -> str:
        """Generate a unique document identifier.

        Returns:
            Unique document ID string
        """
        return self.generate_entity_id("doc")

    async def get_many(self, document_ids: list[str]) -> dict[str, Document | None]:
        """Retrieve multiple documents by ID.

        Args:
            document_ids: List of unique document identifiers

        Returns:
            Dict mapping document_id to Document (or None if not found)
        """
        return self.get_many_entities(document_ids)

    async def list_all(self) -> list[Document]:
        """List all documents.

        Returns:
            List of all Document entities in the repository
        """
        self.logger.debug(
            f"Memory{self.entity_name}Repository: Listing all "
            f"{self.entity_name.lower()}s"
        )

        documents = list(self.storage_dict.values())

        self.logger.info(
            f"Memory{self.entity_name}Repository: Listed all "
            f"{self.entity_name.lower()}s",
            extra={"count": len(documents)},
        )

        return documents

    def _add_entity_specific_log_data(
        self, entity: Document, log_data: dict[str, Any]
    ) -> None:
        """Add document-specific data to log entries."""
        super()._add_entity_specific_log_data(entity, log_data)
        log_data["content_length"] = entity.size_bytes
