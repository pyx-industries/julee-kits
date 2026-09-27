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
        """Retrieve a document with metadata and content.

        The content is a fresh stream over the stored bytes, as MinIO's
        is a fresh response: what is kept is the content, not a stream
        over it, so asking twice gives two readable streams rather than
        one spent one.

        Args:
            document_id: Unique document identifier

        Returns:
            Document object if found, None otherwise
        """
        document = self.get_entity(document_id)
        if document is None:
            return None

        content = self.content_by_multihash.get(document.content_multihash)
        if content is None:
            return document

        return document.evolve(content=ContentStream(io.BytesIO(content)))

    async def save(self, document: Document) -> None:
        """Save a document with its content and metadata.

        If the document has content_bytes, it will be normalized to bytes
        (encoding str as UTF-8), converted to a ContentStream and the
        content hash will be calculated automatically.

        Args:
            document: Document object to save

        Raises:
            ValueError: If document has no content or content_bytes
            TypeError: If content_bytes is not bytes or str
        """
        # Handle content_string conversion (only if no content provided)
        if document.content_bytes is not None:
            if isinstance(document.content_bytes, str):
                raw_bytes = document.content_bytes.encode("utf-8")
            elif isinstance(document.content_bytes, bytes):
                raw_bytes = document.content_bytes
            else:
                raise TypeError("content_bytes must be of type 'bytes' or 'str'.")

            content_stream = ContentStream(io.BytesIO(raw_bytes))

            # Create new document with ContentStream and calculated hash
            multihash_of_content = content_multihash(raw_bytes)
            document = document.evolve(
                content=content_stream,
                content_multihash=multihash_of_content,
                size_bytes=len(raw_bytes),
            )

            self.logger.debug(
                "Converted content_bytes to ContentStream for document save",
                extra={
                    "document_id": document.document_id,
                    "content_multihash": multihash_of_content,
                    "content_length": len(raw_bytes),
                },
            )

        # Keep the content where it can be read again, under the name
        # the document uses for it. Whatever arrived as a stream is read
        # here rather than kept, because keeping it would mean the next
        # reader gets what is left of it.
        if document.content is not None:
            self.content_by_multihash[document.content_multihash] = (
                document.content.read()
            )

        # Create a copy without content_string (content saved
        # in separate content-addressable storage)
        document_for_storage = document.evolve(content_bytes=None)
        self.save_entity(document_for_storage, "document_id")

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
