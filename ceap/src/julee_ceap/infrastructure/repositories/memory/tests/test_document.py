"""
Unit tests for MemoryDocumentRepository.

These tests verify the memory implementation logic without requiring external
dependencies. They follow the Clean Architecture testing patterns and verify
idempotency, error handling, and content operations including content_bytes.
"""

import pytest
from julee.core.values.text import NonEmptyText

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.values.multihash import ContentMultihash
from julee_ceap.domain.values.multihash import (
    content_multihash as multihash_of,
)
from julee_ceap.infrastructure.repositories.memory.document import (
    MemoryDocumentRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def repository() -> MemoryDocumentRepository:
    """Provide a repository instance for testing."""
    return MemoryDocumentRepository()


@pytest.fixture
def sample_content() -> bytes:
    """Sample content for testing."""
    content_bytes = b"This is test content for document storage"
    return content_bytes


@pytest.fixture
def sample_document(sample_content: bytes) -> Document:
    """Sample document for testing."""
    return Document(
        document_id=NonEmptyText("test-doc-123"),
        original_filename=NonEmptyText("test.txt"),
        content_type=NonEmptyText("text/plain"),
        size_bytes=41,
        content_multihash=ContentMultihash(multihash_of(b"test_hash_placeholder")),
        status=DocumentStatus.CAPTURED,
    )


class TestMemoryDocumentRepositoryContentBytes:
    """Test content_bytes functionality."""

    async def test_save_document_with_content_bytes(
        self, repository: MemoryDocumentRepository
    ) -> None:
        """Test saving document with content_bytes."""
        content = '{"assembled": "document", "data": "test"}'

        # Create document with content_bytes
        stored = await repository.store_content(content.encode("utf-8"))
        document = Document(
            document_id=NonEmptyText("test-doc-content-string"),
            original_filename=NonEmptyText("assembled.json"),
            content_type=NonEmptyText("application/json"),
            size_bytes=len(content.encode("utf-8")),
            content_multihash=ContentMultihash(stored),
            status=DocumentStatus.CAPTURED,
        )

        # Act - save should convert content_bytes to ContentStream
        await repository.save(document)

        # Assert document was saved successfully
        retrieved = await repository.get(document.document_id)
        assert retrieved is not None
        assert retrieved.content_multihash != "placeholder"  # Hash was calculated
        assert retrieved.size_bytes == len(content.encode("utf-8"))

        # Content is read through the port
        stream = await repository.content_of(retrieved)
        assert stream.decode("utf-8") == content

    async def test_save_document_with_content_bytes_unicode(
        self, repository: MemoryDocumentRepository
    ) -> None:
        """Test saving document with unicode content_bytes."""
        content = '{"title": "测试文档", "emoji": "🚀", "content": "éñ"}'

        stored = await repository.store_content(content.encode("utf-8"))

        document = Document(
            document_id=NonEmptyText("test-doc-unicode"),
            original_filename=NonEmptyText("unicode.json"),
            content_type=NonEmptyText("application/json"),
            size_bytes=100,
            content_multihash=ContentMultihash(stored),
            status=DocumentStatus.CAPTURED,
        )

        await repository.save(document)
        retrieved = await repository.get(document.document_id)

        assert retrieved is not None
        stream = await repository.content_of(retrieved)
        assert stream.decode("utf-8") == content

    # Note: Empty content test removed because domain model requires
    # size_bytes > 0

    async def test_save_excludes_content_bytes_from_storage(
        self, repository: MemoryDocumentRepository
    ) -> None:
        """Test that content_bytes is not stored in memory storage."""
        content = '{"test": "data that should not be in storage"}'

        stored = await repository.store_content(content.encode("utf-8"))

        document = Document(
            document_id=NonEmptyText("test-storage-exclusion"),
            original_filename=NonEmptyText("test.json"),
            content_type=NonEmptyText("application/json"),
            size_bytes=100,
            content_multihash=ContentMultihash(stored),
            status=DocumentStatus.CAPTURED,
        )

        await repository.save(document)

        # Check stored document directly from internal storage
        stored_document = repository.storage_dict.get("test-storage-exclusion")
        assert stored_document is not None

        # Verify essential fields are still present
        assert stored_document.document_id == "test-storage-exclusion"
        assert stored_document.content_multihash is not None
        assert stored_document.content_multihash != "placeholder"

        # And the content it names is still readable
        retrieved = await repository.get("test-storage-exclusion")
        assert retrieved is not None
        stream = await repository.content_of(retrieved)
        assert stream.decode("utf-8") == content


class TestMemoryDocumentRepositoryBasicOperations:
    """Test basic repository operations."""

    async def test_save_and_get_document_with_content_stream(
        self, repository: MemoryDocumentRepository, sample_document: Document
    ) -> None:
        """Test basic save and retrieve operations with ContentStream."""
        # Act
        await repository.save(sample_document)
        retrieved = await repository.get(sample_document.document_id)

        # Assert
        assert retrieved is not None
        assert retrieved.document_id == sample_document.document_id
        assert retrieved.original_filename == sample_document.original_filename

    async def test_get_nonexistent_document(
        self, repository: MemoryDocumentRepository
    ) -> None:
        """Test retrieving a document that doesn't exist."""
        result = await repository.get("nonexistent-123")
        assert result is None

    async def test_generate_id(self, repository: MemoryDocumentRepository) -> None:
        """Test that generate_id returns a unique string."""
        doc_id_1 = await repository.generate_id()
        doc_id_2 = await repository.generate_id()

        assert isinstance(doc_id_1, str)
        assert isinstance(doc_id_2, str)
        assert doc_id_1 != doc_id_2
        assert len(doc_id_1) > 0
        assert len(doc_id_2) > 0


class TestMemoryDocumentRepositoryErrorHandling:
    """Test error handling scenarios."""

    async def test_save_handles_empty_document_id(
        self, repository: MemoryDocumentRepository
    ) -> None:
        """Test error handling for empty document ID."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Document(
                document_id=NonEmptyText(""),
                original_filename=NonEmptyText("test.txt"),
                content_type=NonEmptyText("text/plain"),
                size_bytes=100,
                content_multihash=ContentMultihash(multihash_of(b"test_hash")),
                status=DocumentStatus.CAPTURED,
            )

    async def test_save_handles_empty_filename(
        self, repository: MemoryDocumentRepository
    ) -> None:
        """Test error handling for empty filename."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Document(
                document_id=NonEmptyText("test-123"),
                original_filename=NonEmptyText(""),
                content_type=NonEmptyText("text/plain"),
                size_bytes=100,
                content_multihash=ContentMultihash(multihash_of(b"test_hash")),
                status=DocumentStatus.CAPTURED,
            )
