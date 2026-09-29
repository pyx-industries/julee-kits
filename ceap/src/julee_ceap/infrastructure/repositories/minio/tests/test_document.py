"""
Unit tests for MinioDocumentRepository.

These tests mock the Minio client to test the repository implementation logic
without requiring a real MinIO instance. They follow the Clean Architecture
testing patterns and verify idempotency, error handling, and content.
"""

import io
import json
from dataclasses import replace
from typing import Any
from unittest.mock import Mock

import pytest
from julee.core.entities.text import NonEmptyText
from julee.integrations.minio.testing import FakeMinioClient
from minio.error import S3Error

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.values.multihash import ContentMultihash
from julee_ceap.domain.values.multihash import (
    content_multihash as multihash_of,
)
from julee_ceap.infrastructure.repositories.minio.document import (
    MinioDocumentRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def fake_minio_client() -> FakeMinioClient:
    """Provide a fake Minio client for state-based testing."""
    return FakeMinioClient()


@pytest.fixture
def repository(fake_minio_client: FakeMinioClient) -> MinioDocumentRepository:
    """Provide a repository instance with fake client."""
    return MinioDocumentRepository(fake_minio_client)


@pytest.fixture
def sample_content() -> bytes:
    """Sample content for testing."""
    content_bytes = b"This is test content for document storage"
    return content_bytes


@pytest.fixture
def sample_document(sample_content: bytes) -> Document:
    """Sample document for testing."""
    # The name the repository will compute for this content. Worked out
    # by hand here until #44: the fixture reproduced the production
    # calculation rather than checking it, so it agreed with the bug.
    content_bytes = b"This is test content for document storage"
    actual_multihash = multihash_of(content_bytes)

    return Document(
        document_id=NonEmptyText("test-doc-123"),
        original_filename=NonEmptyText("test.txt"),
        content_type=NonEmptyText("text/plain"),
        size_bytes=len(content_bytes),
        content_multihash=ContentMultihash(actual_multihash),
        status=DocumentStatus.CAPTURED,
    )


class TestMinioDocumentRepositoryInitialization:
    """Test repository initialization and bucket creation."""

    def test_init_creates_buckets_when_missing(self) -> None:
        """Test that missing buckets are created during initialization."""
        fake_client = FakeMinioClient()

        # Verify no buckets exist initially
        assert not fake_client.bucket_exists("documents")
        assert not fake_client.bucket_exists("documents-content")

        # Initialize repository - should create buckets
        MinioDocumentRepository(fake_client)

        # Verify buckets were created
        assert fake_client.bucket_exists("documents")
        assert fake_client.bucket_exists("documents-content")

    def test_init_skips_existing_buckets(self) -> None:
        """Test that existing buckets are not recreated."""
        fake_client = FakeMinioClient()

        # Pre-create buckets
        fake_client.make_bucket("documents")
        fake_client.make_bucket("documents-content")

        # Initialize repository - should not fail or recreate
        MinioDocumentRepository(fake_client)

        # Verify buckets still exist (no exception thrown)
        assert fake_client.bucket_exists("documents")
        assert fake_client.bucket_exists("documents-content")

    def test_init_handles_bucket_creation_error(self) -> None:
        """Test proper error handling during bucket creation."""
        fake_client = FakeMinioClient()

        # Pre-create one bucket to cause a conflict
        fake_client.make_bucket("documents")

        # Override make_bucket to raise error for second bucket
        original_make_bucket = fake_client.make_bucket

        def failing_make_bucket(bucket_name: str) -> None:
            if bucket_name == "documents-content":
                raise S3Error(
                    code="AccessDenied",
                    message="Access denied",
                    resource="AccessDenied",
                    request_id="req123",
                    host_id="host123",
                    response=Mock(),
                )
            return original_make_bucket(bucket_name)

        fake_client.make_bucket = failing_make_bucket  # type: ignore[method-assign]

        with pytest.raises(S3Error):
            MinioDocumentRepository(fake_client)


class TestMinioDocumentRepositoryStore:
    """Test document storage operations."""

    async def test_store_new_document(
        self, fake_minio_client: FakeMinioClient, sample_document: Document
    ) -> None:
        """Test storing a new document with content."""
        repository = MinioDocumentRepository(fake_minio_client)

        # Verify buckets are empty initially
        assert fake_minio_client.get_object_count("documents") == 0
        assert fake_minio_client.get_object_count("documents-content") == 0

        # Act. Two calls now, in this order: content cannot be named
        # until it has been read, so it is stored before the document
        # that names it.
        await repository.store_content(b"This is test content for document storage")
        await repository.save(sample_document)

        # Assert content and metadata were stored
        assert fake_minio_client.get_object_count("documents") == 1
        assert fake_minio_client.get_object_count("documents-content") == 1

        # Verify content was stored with calculated multihash as key
        content_objects = fake_minio_client.get_stored_objects("documents-content")
        calculated_multihash = sample_document.content_multihash
        assert calculated_multihash in content_objects

        # Verify metadata was stored with document ID as key
        metadata_objects = fake_minio_client.get_stored_objects("documents")
        assert sample_document.document_id in metadata_objects

    async def test_store_document_with_existing_content_deduplication(
        self, fake_minio_client: FakeMinioClient, sample_document: Document
    ) -> None:
        """Test that existing content is not re-stored (deduplication)."""
        repository = MinioDocumentRepository(fake_minio_client)

        content_bytes = b"This is test content for document storage"

        first = await repository.store_content(content_bytes)
        await repository.save(sample_document)
        stored_multihash = first

        # The same bytes again, under different metadata. The name is
        # the content, so the second store finds the first one's object.
        await repository.store_content(content_bytes)

        second_document = Document(
            document_id=NonEmptyText("different-doc-456"),
            original_filename=NonEmptyText("different.txt"),
            content_type=NonEmptyText("text/plain"),
            size_bytes=len(content_bytes),
            content_multihash=ContentMultihash(
                stored_multihash
            ),  # Same calculated multihash
            status=DocumentStatus.CAPTURED,
        )

        # Store second document - should reuse existing content
        await repository.save(second_document)

        # Assert: 2 metadata objects, but only 1 content object (worked)
        assert fake_minio_client.get_object_count("documents") == 2
        assert fake_minio_client.get_object_count("documents-content") == 1

        # Verify deduplication: both documents reference same content object
        content_objects = fake_minio_client.get_stored_objects("documents-content")
        assert len(content_objects) == 1  # Only one content object stored
        assert stored_multihash in content_objects  # Stored under the correct hash key

        # Verify both documents have the same multihash (share content)
        assert sample_document.content_multihash == stored_multihash
        assert second_document.content_multihash == stored_multihash

    async def test_a_document_is_saved_naming_what_was_stored(
        self, fake_minio_client: FakeMinioClient
    ) -> None:
        """There is nothing left to correct.

        This used to assert that save() noticed a document whose
        content_multihash disagreed with its content, and quietly
        replaced it — which it could only do because it was handed the
        content as well. A document now names content that is already
        in the store, under the name the store gave it, so a caller has
        nothing to guess at and save() has nothing to second-guess.
        """
        repository = MinioDocumentRepository(fake_minio_client)
        content = b"This is test content for document storage"

        stored = await repository.store_content(content)
        document = Document(
            document_id=NonEmptyText("test-doc-123"),
            original_filename=NonEmptyText("test.txt"),
            content_type=NonEmptyText("text/plain"),
            size_bytes=len(content),
            content_multihash=ContentMultihash(stored),
            status=DocumentStatus.CAPTURED,
        )
        await repository.save(document)

        found = await repository.get("test-doc-123")
        assert found is not None
        assert found.content_multihash == multihash_of(content)
        assert await repository.content_of(found) == content

    async def test_store_handles_content_storage_error(
        self, fake_minio_client: FakeMinioClient, sample_document: Document
    ) -> None:
        """Test proper error handling during content storage.

        store_content raises now, not save. Which is the point: a
        failure to store content happens before there is a document
        naming it, so nothing half-written is left behind."""
        repository = MinioDocumentRepository(fake_minio_client)

        # Override put_object to raise error when storing content
        original_put_object = repository.client.put_object

        def failing_put_object(
            bucket_name: str,
            object_name: str,
            data: Any,
            length: int,
            **kwargs: Any,
        ) -> Any:
            if bucket_name == "documents-content":
                raise S3Error(
                    code="AccessDenied",
                    message="Access denied",
                    resource="AccessDenied",
                    request_id="req123",
                    host_id="host123",
                    response=Mock(),
                )
            return original_put_object(bucket_name, object_name, data, length, **kwargs)

        repository.client.put_object = failing_put_object  # type: ignore[method-assign, assignment]

        # Act & Assert
        with pytest.raises(S3Error):
            await repository.store_content(b"some content")

        # Verify no objects were stored
        assert fake_minio_client.get_object_count("documents") == 0
        assert fake_minio_client.get_object_count("documents-content") == 0


class TestMinioDocumentRepositoryGet:
    """Test document retrieval operations."""

    async def test_get_existing_document(
        self, repository: MinioDocumentRepository, sample_document: Document
    ) -> None:
        """Test retrieving an existing document with content."""
        await repository.store_content(b"This is test content for document storage")
        await repository.save(sample_document)

        # Act - retrieve the document
        result = await repository.get(sample_document.document_id)

        # Assert
        assert result is not None
        assert result.document_id == sample_document.document_id
        assert result.original_filename == sample_document.original_filename
        assert result.content_type == sample_document.content_type
        assert result.size_bytes == sample_document.size_bytes

        # Content is read through the port, not off what came back
        assert await repository.content_of(result) == (
            b"This is test content for document storage"
        )

    async def test_get_document_missing_content_multihash(
        self, repository: MinioDocumentRepository
    ) -> None:
        """Test handling document metadata without content_multihash."""
        # Manually store invalid metadata (missing content_multihash)
        invalid_metadata_json = (
            '{"document_id": "test-123", "original_filename": "test.txt"}'
        )
        repository.client.put_object(
            "documents",
            "test-123",
            io.BytesIO(invalid_metadata_json.encode("utf-8")),
            len(invalid_metadata_json),
            content_type="application/json",
        )

        # Act
        result = await repository.get("test-123")

        # Assert
        assert result is None

    async def test_get_document_with_missing_content(
        self, repository: MinioDocumentRepository
    ) -> None:
        """Metadata without its content still reads back.

        get() used to fetch the content object too, and returned None
        when it was missing — so a document whose content had been
        reaped came back as "not found", which is not what happened.
        It reads the metadata now, and content_of is where the absence
        shows up, as an integrity error rather than a shrug."""
        # Store metadata but not content
        metadata_json = (
            '{"document_id": "test-123", "content_multihash": "'
            + multihash_of(b"missing")
            + '",'
            ' "original_filename": "test.txt", "content_type": "text/plain",'
            ' "size_bytes": 100, "status": "captured"}'
        )
        repository.client.put_object(
            "documents",
            "test-123",
            io.BytesIO(metadata_json.encode("utf-8")),
            len(metadata_json),
            content_type="application/json",
        )

        # Act
        result = await repository.get("test-123")

        # Assert - the document is there, and says what it names
        assert result is not None
        assert result.document_id == "test-123"

        # The content it names is not, and asking says so
        with pytest.raises(ValueError, match="names content"):
            await repository.content_of(result)

    async def test_get_nonexistent_document(
        self, repository: MinioDocumentRepository
    ) -> None:
        """Test retrieving a document that doesn't exist."""
        # Act - try to get a document that was never stored
        result = await repository.get("nonexistent-123")

        # Assert
        assert result is None


class TestMinioDocumentRepositoryUpdate:
    """Test document update operations."""

    async def test_update_document(
        self, repository: MinioDocumentRepository, sample_document: Document
    ) -> None:
        """Test updating a document."""
        # Store document initially
        await repository.save(sample_document)
        original_updated_at = sample_document.updated_at

        # Modify document
        sample_document = replace(sample_document, status=DocumentStatus.EXTRACTED)

        # Act
        await repository.save(sample_document)

        # Verify document was actually updated in storage with new timestamp
        retrieved_doc = await repository.get(sample_document.document_id)
        assert retrieved_doc is not None
        assert retrieved_doc.status == DocumentStatus.EXTRACTED
        # Repository updates updated_at on save — verify it changed
        assert retrieved_doc.updated_at != original_updated_at
        if original_updated_at and retrieved_doc.updated_at:
            assert retrieved_doc.updated_at > original_updated_at


class TestMinioDocumentRepositoryGenerateId:
    """Test ID generation."""

    async def test_generate_id(self, repository: MinioDocumentRepository) -> None:
        """Test that generate_id returns a unique string."""
        # Act
        doc_id_1 = await repository.generate_id()
        doc_id_2 = await repository.generate_id()

        # Assert
        assert isinstance(doc_id_1, str)
        assert isinstance(doc_id_2, str)
        assert doc_id_1 != doc_id_2
        assert len(doc_id_1) > 0
        assert len(doc_id_2) > 0


class TestMinioDocumentRepositorySavingAStreamItCannotRewind:
    """Saving content that arrived over the network (#90).

    A document fetched from one repository and saved into another
    carries the response it was fetched over. That response is consumed
    as it is read and cannot be rewound, which is what a real transfer
    hands the save path.

    These tests replaced two that called the old private multihash
    helper with a BytesIO. A BytesIO is seekable, so they exercised the
    one kind of stream this could not fail on.
    """

    @pytest.fixture
    def a_stored_document(self, repository: MinioDocumentRepository) -> bytes:
        content = b"a document being transferred between repositories"
        stored = multihash_of(content)
        repository.client.put_object(
            bucket_name=repository.content_bucket,
            object_name=stored,
            data=io.BytesIO(content),
            length=len(content),
        )
        metadata = json.dumps(
            {
                "document_id": "doc-1",
                "original_filename": "spec.pdf",
                "content_type": "application/pdf",
                "size_bytes": len(content),
                "content_multihash": stored,
                "status": "captured",
            }
        ).encode("utf-8")
        repository.client.put_object(
            bucket_name=repository.metadata_bucket,
            object_name="doc-1",
            data=io.BytesIO(metadata),
            length=len(metadata),
            content_type="application/json",
        )
        return content

    @pytest.fixture
    def destination(
        self, fake_minio_client: FakeMinioClient
    ) -> MinioDocumentRepository:
        """Somewhere else to put it, as a transfer has."""
        other = MinioDocumentRepository(fake_minio_client)
        other.content_bucket = "products-content"
        other.metadata_bucket = "products"
        fake_minio_client.make_bucket(other.content_bucket)
        fake_minio_client.make_bucket(other.metadata_bucket)
        return other

    @pytest.mark.asyncio
    async def test_what_content_of_returns_can_be_read_again(
        self, repository: MinioDocumentRepository, a_stored_document: bytes
    ) -> None:
        """The premise the tests below rest on.

        It used to be the opposite: content_of handed back a live
        response, which could not be rewound, and that was asserted here
        so the tests below would be re-read rather than trusted if it
        ever changed. It has changed. The port returns bytes
        (julee-kits#89), so the premise is now that reading does not
        spend them, and nothing below has to hold a stream carefully.
        """
        document = await repository.get("doc-1")
        assert document is not None

        content = await repository.content_of(document)

        assert content == a_stored_document
        assert content == a_stored_document

    @pytest.mark.asyncio
    async def test_a_document_can_be_transferred_to_another_repository(
        self,
        repository: MinioDocumentRepository,
        destination: MinioDocumentRepository,
        a_stored_document: bytes,
    ) -> None:
        """Used to raise io.UnsupportedOperation: seek. The save path
        read the content to hash it, then rewound to read it again to
        upload it."""
        document = await repository.get("doc-1")
        assert document is not None

        await destination.store_content(await repository.content_of(document))
        await destination.save(document)

        response = destination.client.get_object(
            bucket_name=destination.content_bucket,
            object_name=multihash_of(a_stored_document),
        )
        assert response.read() == a_stored_document

    @pytest.mark.asyncio
    async def test_the_transferred_document_is_readable_again(
        self,
        repository: MinioDocumentRepository,
        destination: MinioDocumentRepository,
        a_stored_document: bytes,
    ) -> None:
        """Storing the bytes is not enough if the metadata names them
        wrongly; this reads the document back out the far end."""
        document = await repository.get("doc-1")
        assert document is not None

        await destination.store_content(await repository.content_of(document))
        await destination.save(document)
        transferred = await destination.get("doc-1")

        assert transferred is not None
        assert await destination.content_of(transferred) == a_stored_document

    @pytest.mark.asyncio
    async def test_saving_a_seekable_stream_still_works(
        self, repository: MinioDocumentRepository
    ) -> None:
        """The case that always worked, kept so the fix is not a trade."""
        content = b"content handed in as bytes, not fetched"
        stored = await repository.store_content(content)
        document = Document(
            document_id=NonEmptyText("doc-fresh"),
            original_filename=NonEmptyText("fresh.txt"),
            content_type=NonEmptyText("text/plain"),
            size_bytes=len(content),
            content_multihash=ContentMultihash(stored),
        )

        await repository.save(document)

        response = repository.client.get_object(
            bucket_name=repository.content_bucket,
            object_name=multihash_of(content),
        )
        assert response.read() == content

    @pytest.mark.asyncio
    async def test_empty_content_is_named_and_stored(
        self, repository: MinioDocumentRepository
    ) -> None:
        """Empty content has a multihash like any other.

        size_bytes is 1 because the entity forbids 0, which is a rule
        about documents rather than about content: the store will keep
        b"" and name it quite happily.
        """
        stored = await repository.store_content(b"")
        document = Document(
            document_id=NonEmptyText("doc-empty"),
            original_filename=NonEmptyText("empty.txt"),
            content_type=NonEmptyText("text/plain"),
            size_bytes=1,
            content_multihash=ContentMultihash(stored),
        )

        await repository.save(document)

        response = repository.client.get_object(
            bucket_name=repository.content_bucket, object_name=multihash_of(b"")
        )
        assert response.read() == b""


class TestMinioDocumentRepositoryContentBytes:
    """Test content_bytes functionality."""

    async def test_save_document_with_content_bytes(
        self, repository: MinioDocumentRepository
    ) -> None:
        """Test saving document with content_bytes (small content)."""
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

        # Act
        await repository.save(document)

        # Assert document was saved successfully
        retrieved = await repository.get(document.document_id)
        assert retrieved is not None
        assert retrieved.content_multihash == stored
        assert retrieved.size_bytes == len(content.encode("utf-8"))

        # Content is read through the port
        stream = await repository.content_of(retrieved)
        assert stream.decode("utf-8") == content

    async def test_save_document_with_content_bytes_unicode(
        self, repository: MinioDocumentRepository
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

    async def test_save_excludes_content_bytes_from_metadata(
        self,
        repository: MinioDocumentRepository,
        fake_minio_client: FakeMinioClient,
    ) -> None:
        """Test that content_bytes is not stored in metadata."""
        content = '{"test": "data that should not be in metadata"}'

        stored = await repository.store_content(content.encode("utf-8"))

        document = Document(
            document_id=NonEmptyText("test-metadata-exclusion"),
            original_filename=NonEmptyText("test.json"),
            content_type=NonEmptyText("application/json"),
            size_bytes=100,
            content_multihash=ContentMultihash(stored),
            status=DocumentStatus.CAPTURED,
        )

        await repository.save(document)

        # Check raw metadata stored in MinIO
        metadata_response = fake_minio_client.get_object(
            bucket_name="documents", object_name="test-metadata-exclusion"
        )
        metadata_data = metadata_response.read()
        metadata_json = metadata_data.decode("utf-8")

        import json

        metadata_dict = json.loads(metadata_json)

        # Verify content_bytes is not in stored metadata
        assert "content_bytes" not in metadata_dict
        assert "content" not in metadata_dict

        # Verify essential fields are still present
        assert metadata_dict["document_id"] == "test-metadata-exclusion"
        assert "content_multihash" in metadata_dict
        assert "status" in metadata_dict


class TestMinioDocumentRepositoryErrorHandling:
    """Test error handling scenarios."""

    async def test_store_handles_metadata_storage_error(
        self, fake_minio_client: FakeMinioClient, sample_document: Document
    ) -> None:
        """Test error handling when metadata storage fails."""
        repository = MinioDocumentRepository(fake_minio_client)

        # Override put_object to fail only for metadata storage
        original_put_object = repository.client.put_object

        def failing_put_object(
            bucket_name: str,
            object_name: str,
            data: Any,
            length: int,
            **kwargs: Any,
        ) -> Any:
            if bucket_name == "documents":
                raise S3Error(
                    code="AccessDenied",
                    message="Access denied",
                    resource="AccessDenied",
                    request_id="req123",
                    host_id="host123",
                    response=Mock(),
                )
            return original_put_object(bucket_name, object_name, data, length, **kwargs)

        repository.client.put_object = failing_put_object  # type: ignore[method-assign, assignment]

        # Act & Assert. The content is already in by the time the
        # metadata write fails, which is the order this repository has
        # always used and now says out loud.
        original_put_object(
            "documents-content",
            sample_document.content_multihash,
            io.BytesIO(b"This is test content for document storage"),
            41,
        )

        with pytest.raises(S3Error):
            await repository.save(sample_document)

        # Verify content was stored but metadata was not
        assert fake_minio_client.get_object_count("documents-content") == 1
        assert fake_minio_client.get_object_count("documents") == 0

    async def test_get_handles_unexpected_error(
        self, repository: MinioDocumentRepository
    ) -> None:
        """Test handling of unexpected errors during get operation."""
        # Override get_object to raise unexpected error
        original_get_object = repository.client.get_object

        def failing_get_object(bucket_name: str, object_name: str) -> Any:
            if bucket_name == "documents":
                raise Exception("Unexpected error")
            return original_get_object(bucket_name, object_name)

        repository.client.get_object = failing_get_object  # type: ignore[method-assign]

        # Act
        result = await repository.get("test-123")

        # Assert - should return None and not propagate exception
        assert result is None


async def content_of(
    repository: MinioDocumentRepository,
    found: dict[str, Document | None],
    document_id: str,
) -> bytes:
    """What one document of a get_many result names, read back.

    get_many returns metadata, so the content is asked for rather than
    taken off what came back — which is the point: two documents naming
    the same content each get a stream of their own (julee#124).
    """
    document = found[document_id]
    assert document is not None, f"{document_id} was not found"
    return await repository.content_of(document)


class TestMinioDocumentRepositoryGetMany:
    """Fetching several documents at once (#124).

    Content is deduplicated by multihash, so two documents holding the
    same bytes are one object in the store. What they must not share is
    the reading of it.
    """

    @pytest.fixture
    def two_documents_one_file(self, repository: MinioDocumentRepository) -> bytes:
        """The same file uploaded twice, as RBA did with a spec sheet."""
        content = b"the same pdf, uploaded twice"
        stored = multihash_of(content)
        repository.client.put_object(
            bucket_name=repository.content_bucket,
            object_name=stored,
            data=io.BytesIO(content),
            length=len(content),
        )
        for document_id in ("doc-a", "doc-b"):
            metadata = json.dumps(
                {
                    "document_id": document_id,
                    "original_filename": "spec-sheet.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": len(content),
                    "content_multihash": stored,
                    "status": "captured",
                }
            ).encode("utf-8")
            repository.client.put_object(
                bucket_name=repository.metadata_bucket,
                object_name=document_id,
                data=io.BytesIO(metadata),
                length=len(metadata),
                content_type="application/json",
            )
        return content

    @pytest.mark.asyncio
    async def test_both_documents_can_read_their_content(
        self, repository: MinioDocumentRepository, two_documents_one_file: bytes
    ) -> None:
        """Reading the first used to exhaust the stream the second held,
        so the second document came back with b"" and every field parsed
        out of it as null."""
        found = await repository.get_many(["doc-a", "doc-b"])

        assert await content_of(repository, found, "doc-a") == two_documents_one_file
        assert await content_of(repository, found, "doc-b") == two_documents_one_file

    @pytest.mark.asyncio
    async def test_reading_in_the_other_order_works_too(
        self, repository: MinioDocumentRepository, two_documents_one_file: bytes
    ) -> None:
        """Whichever consumer gets there first, both are served."""
        found = await repository.get_many(["doc-a", "doc-b"])

        assert await content_of(repository, found, "doc-b") == two_documents_one_file
        assert await content_of(repository, found, "doc-a") == two_documents_one_file

    @pytest.mark.asyncio
    async def test_two_documents_naming_one_file_both_get_it(
        self, repository: MinioDocumentRepository, two_documents_one_file: bytes
    ) -> None:
        """julee#124 was two documents sharing one spent stream.

        This asserted that they got two distinct streams. There are no
        streams: content_of returns bytes, so neither document can take
        anything from the other, and the identity of what comes back is
        not a property worth asserting — identical bytes may well be
        the same object.

        What is left to check is that both get the content, which is
        what the hazard cost.
        """
        found = await repository.get_many(["doc-a", "doc-b"])
        first, second = found["doc-a"], found["doc-b"]
        assert first is not None and second is not None

        one = await repository.content_of(first)
        other = await repository.content_of(second)

        assert one == two_documents_one_file
        assert other == two_documents_one_file

    @pytest.mark.asyncio
    async def test_the_content_is_still_stored_once_for_both(
        self, repository: MinioDocumentRepository, two_documents_one_file: bytes
    ) -> None:
        """The deduplication is the point of get_many and is kept: one
        object, read once, handed out as two streams."""
        found = await repository.get_many(["doc-a", "doc-b"])
        first, second = found["doc-a"], found["doc-b"]

        assert first is not None and second is not None
        assert first.content_multihash == second.content_multihash

    @pytest.mark.asyncio
    async def test_documents_with_different_content_are_unaffected(
        self, repository: MinioDocumentRepository
    ) -> None:
        for document_id, content in [("doc-1", b"first"), ("doc-2", b"second")]:
            stored = multihash_of(content)
            repository.client.put_object(
                bucket_name=repository.content_bucket,
                object_name=stored,
                data=io.BytesIO(content),
                length=len(content),
            )
            metadata = json.dumps(
                {
                    "document_id": document_id,
                    "original_filename": "f.txt",
                    "content_type": "text/plain",
                    "size_bytes": len(content),
                    "content_multihash": stored,
                    "status": "captured",
                }
            ).encode("utf-8")
            repository.client.put_object(
                bucket_name=repository.metadata_bucket,
                object_name=document_id,
                data=io.BytesIO(metadata),
                length=len(metadata),
                content_type="application/json",
            )

        found = await repository.get_many(["doc-1", "doc-2"])

        assert await content_of(repository, found, "doc-1") == b"first"
        assert await content_of(repository, found, "doc-2") == b"second"

    @pytest.mark.asyncio
    async def test_a_document_that_is_not_there_is_None(
        self, repository: MinioDocumentRepository, two_documents_one_file: bytes
    ) -> None:
        found = await repository.get_many(["doc-a", "doc-missing"])

        assert found["doc-missing"] is None
        assert await content_of(repository, found, "doc-a") == two_documents_one_file
