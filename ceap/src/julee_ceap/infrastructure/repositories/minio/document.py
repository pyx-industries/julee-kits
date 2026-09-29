"""
Minio implementation of DocumentRepository.

This module provides a Minio-based implementation of the DocumentRepository
protocol that follows the Clean Architecture patterns defined in the
Fun-Police Framework. It handles document storage with both metadata and
content streams, ensuring idempotency and proper error handling.

The implementation separates document metadata (stored as JSON) from content
(stored as content-addressable binary objects) in Minio, following the large
payload handling pattern from the architectural guidelines.
"""

import io
import json
import logging
from datetime import UTC, datetime

from julee.integrations.minio.client import MinioClient, MinioRepositoryMixin
from minio.error import S3Error
from pydantic import BaseModel, ConfigDict, TypeAdapter

from julee_ceap.domain.models.document import Document
from julee_ceap.domain.models.document.multihash import (
    ContentMultihash,
    content_multihash,
)
from julee_ceap.domain.repositories.document import DocumentRepository


class RawMetadata(BaseModel):
    """Simple wrapper for raw document metadata JSON."""

    model_config = ConfigDict(extra="allow")  # Allow arbitrary fields

    # Only include fields we actually use for type safety
    content_multihash: str | None = None


class MinioDocumentRepository(DocumentRepository, MinioRepositoryMixin):
    """
    Minio implementation of DocumentRepository using Minio for persistence.

    This implementation stores document metadata and content separately:
    - Metadata: JSON objects in the "documents" bucket
    - Content: Binary objects in the "documents-content" bucket

    This separation allows for efficient metadata queries while supporting
    large content files without hitting Temporal's 2MB payload limits.
    """

    def __init__(self, client: MinioClient) -> None:
        """Initialize repository with Minio client.

        Args:
            client: MinioClient protocol implementation (real or fake)
        """
        self.client = client
        self.logger = logging.getLogger("MinioDocumentRepository")
        self.metadata_bucket = "documents"
        self.content_bucket = "documents-content"
        self.ensure_buckets_exist([self.metadata_bucket, self.content_bucket])

    async def get(self, document_id: str) -> Document | None:
        """Retrieve a document with metadata and content."""
        try:
            # First, get the metadata
            metadata_response = self.client.get_object(
                bucket_name=self.metadata_bucket, object_name=document_id
            )
            metadata_data = metadata_response.read()
            metadata_response.close()
            metadata_response.release_conn()

            metadata_json = metadata_data.decode("utf-8")

            # Parse metadata JSON directly to dict (content field excluded)
            document_dict = json.loads(metadata_json)

            # Now get the content stream using the content multihash as key
            content_multihash = document_dict.get("content_multihash")
            if not content_multihash:
                self.logger.error(
                    "Document metadata missing content_multihash",
                    extra={"document_id": document_id},
                )
                return None

            self.logger.info(
                "Document retrieved successfully",
                extra={
                    "document_id": document_id,
                    "content_multihash": content_multihash,
                    "retrieved_at": datetime.now(UTC).isoformat(),
                },
            )

            # Metadata only. This used to open the content object too,
            # just to hang a stream off the document — so every caller
            # that wanted a name and a status paid for a second request
            # and got a stream it never read. content_of() is for the
            # callers that want the bytes.
            # Through a TypeAdapter, so every field is rebuilt as what
            # the entity declares. Document(**document_dict) handed each
            # one the raw JSON: a str where the multihash belongs, with
            # its format never checked (#44).
            return TypeAdapter(Document).validate_python(document_dict)

        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                self.logger.debug(
                    "Document not found",
                    extra={"document_id": document_id},
                )
                return None
            else:
                self.logger.error(
                    "Error retrieving document metadata",
                    extra={"document_id": document_id, "error": str(e)},
                )
                raise
        except Exception as e:
            self.logger.error(
                "Unexpected error during document retrieval",
                extra={
                    "document_id": document_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            return None

    async def content_of(self, document: Document) -> bytes:
        """The content this document names.

        Read in full here rather than handed back as the live response.
        Whether the adapter buffers is the adapter's business, and every
        caller read it in full immediately anyway. Bytes also cannot be
        spent by one reader or need rewinding, which is what julee#124
        and julee#90 were (julee-kits#89).

        Args:
            document: The document whose content to read

        Returns:
            The content

        Raises:
            ValueError: If the metadata names content that is not stored
        """
        try:
            response = self.client.get_object(
                bucket_name=self.content_bucket,
                object_name=document.content_multihash,
            )
        except S3Error as error:
            if getattr(error, "code", None) == "NoSuchKey":
                self.logger.error(
                    "Data integrity error: document names content that is not stored",
                    extra={
                        "document_id": document.document_id,
                        "content_multihash": document.content_multihash,
                    },
                )
                raise ValueError(
                    f"Document {document.document_id} names content "
                    f"{document.content_multihash}, which is not in "
                    f"{self.content_bucket}"
                ) from error
            raise

        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def store_content(self, content: bytes) -> ContentMultihash:
        """Keep these bytes under their own name, and say what it is.

        The name is the content, so storing the same bytes twice finds
        the first object already there and adds nothing — which is why
        this can be called without checking first.

        Args:
            content: The bytes to store

        Returns:
            The multihash the content is stored under
        """
        multihash = ContentMultihash(content_multihash(content))

        try:
            self.client.stat_object(
                bucket_name=self.content_bucket, object_name=multihash
            )
            self.logger.debug(
                "Content already stored under this name, adding nothing",
                extra={"content_multihash": multihash},
            )
            return multihash
        except S3Error as error:
            if getattr(error, "code", None) not in ("NoSuchKey", "NoSuchObject"):
                raise

        self.client.put_object(
            bucket_name=self.content_bucket,
            object_name=multihash,
            data=io.BytesIO(content),
            length=len(content),
        )

        self.logger.debug(
            "Content stored",
            extra={"content_multihash": multihash, "content_size": len(content)},
        )

        return multihash

    async def save(self, document: Document) -> None:
        """Save a document's metadata.

        The content it names is stored by ``store_content``, before
        there is a document to name it: a multihash cannot be known
        until the bytes have been read, so the content goes first and
        the document is built from what came back.

        This used to do both, taking content off the document, hashing
        it, and correcting the document's own multihash afterwards if
        the caller had guessed wrong. There is nothing to correct now.
        """
        self.logger.info(
            "Saving document",
            extra={
                "document_id": document.document_id,
                "original_filename": document.original_filename,
                "content_type": document.content_type,
                "size_bytes": document.size_bytes,
                "status": document.status.value,
            },
        )

        document = self.update_timestamps(document)

        try:
            await self._store_metadata(document)

            self.logger.info(
                "Document saved successfully",
                extra={
                    "document_id": document.document_id,
                    "content_multihash": document.content_multihash,
                },
            )

        except Exception as e:
            self.logger.error(
                "Failed to save document",
                extra={"document_id": document.document_id, "error": str(e)},
                exc_info=True,
            )
            raise

    async def get_many(self, document_ids: list[str]) -> dict[str, Document | None]:
        """Retrieve multiple documents by ID using batch operations.

        Args:
            document_ids: List of unique document identifiers

        Returns:
            Dict mapping document_id to Document (or None if not found)

        Note:
            This implementation optimizes by batch-fetching metadata first,
            then batch-fetching unique content streams, then splicing them
            together.
        """
        if not document_ids:
            return {}

        self.logger.debug(
            "MinioDocumentRepository: Attempting to retrieve multiple docs",
            extra={
                "document_ids": document_ids,
                "count": len(document_ids),
                "metadata_bucket": self.metadata_bucket,
            },
        )

        # Step 1: Batch retrieve metadata for all documents
        raw_metadata_results = self.get_many_json_objects(
            bucket_name=self.metadata_bucket,
            object_names=document_ids,  # Direct mapping for metadata
            model_class=RawMetadata,
            not_found_log_message="Document metadata not found",
            error_log_message="Error retrieving document metadata",
            extra_log_data={"document_ids": document_ids},
        )

        # Use RawMetadata objects directly
        metadata_results: dict[str, RawMetadata | None] = raw_metadata_results

        # Step 2: Extract unique content multihashes from found metadata
        content_hashes = set()
        for metadata in metadata_results.values():
            if metadata and metadata.content_multihash:
                content_hashes.add(metadata.content_multihash)

        # Step 3: Read each unique object's content once.
        #
        # No content is fetched here. This used to read every
        # document's bytes in order to hang a stream off each one, so a
        # caller listing fifty documents paid for fifty content reads
        # and used none of them. content_of() is for the callers that
        # want the bytes, one at a time, freshly.

        result: dict[str, Document | None] = {}
        for document_id in document_ids:
            metadata = metadata_results.get(document_id)
            if not metadata:
                result[document_id] = None
                continue

            try:
                result[document_id] = TypeAdapter(Document).validate_python(
                    metadata.model_dump()
                )
            except Exception as e:
                self.logger.error(
                    "Failed to create Document from metadata",
                    extra={
                        "document_id": document_id,
                        "error": str(e),
                    },
                )
                result[document_id] = None

        found_count = sum(1 for doc in result.values() if doc is not None)
        self.logger.info(
            f"Retrieved {found_count}/{len(document_ids)} documents",
            extra={
                "requested_count": len(document_ids),
                "found_count": found_count,
                "missing_count": len(document_ids) - found_count,
                "unique_content_fetched": len(content_hashes),
            },
        )

        return result

    async def list_all(self) -> list[Document]:
        """List all documents.

        Returns:
            List of all documents, sorted by document_id
        """
        try:
            # Extract document IDs from objects in the metadata bucket
            document_ids = self.list_objects_with_prefix_extract_ids(
                bucket_name=self.metadata_bucket,
                prefix="",
                entity_type_name="documents",
            )

            if not document_ids:
                return []

            # Get all documents using the existing get_many method
            document_results = await self.get_many(document_ids)

            # Filter out None results and sort by document_id
            documents = [doc for doc in document_results.values() if doc is not None]
            documents.sort(key=lambda x: x.document_id)

            self.logger.debug(
                "Retrieved documents",
                extra={"count": len(documents)},
            )

            return documents

        except Exception as e:
            self.logger.error(
                "Failed to list documents",
                exc_info=True,
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            raise

    async def generate_id(self) -> str:
        """Generate a unique document identifier."""
        return self.generate_id_with_prefix("doc")

    async def _store_metadata(self, document: Document) -> None:
        """Store document metadata to Minio with idempotency check."""
        object_name = document.document_id

        # Serialize metadata (content stream and content_string excluded)
        metadata_json = TypeAdapter(Document).dump_json(document)

        try:
            # Check if metadata already exists and is identical (idempotency)
            try:
                existing_response = self.client.get_object(
                    bucket_name=self.metadata_bucket, object_name=object_name
                )
                existing_data = existing_response.read()
                existing_response.close()
                existing_response.release_conn()

                if existing_data == metadata_json:
                    self.logger.debug(
                        "Metadata unchanged, skipping storage",
                        extra={"document_id": document.document_id},
                    )
                    return

            except S3Error as e:
                if getattr(e, "code", None) == "NoSuchKey":
                    # Metadata doesn't exist, continue to store it
                    pass
                else:
                    raise

            # Store the metadata
            self.client.put_object(
                bucket_name=self.metadata_bucket,
                object_name=object_name,
                data=io.BytesIO(metadata_json),
                length=len(metadata_json),
                content_type="application/json",
                metadata={
                    "content_multihash": document.content_multihash or "",
                    "original_filename": document.original_filename or "",
                },
            )

            self.logger.debug(
                "Metadata stored successfully",
                extra={
                    "document_id": document.document_id,
                    "metadata_size": len(metadata_json),
                },
            )

        except Exception as e:
            self.logger.error(
                "Failed to store metadata",
                extra={
                    "document_id": document.document_id,
                    "error": str(e),
                },
            )
            raise
