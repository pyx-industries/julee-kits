"""
Test factories for Document domain objects using factory_boy.

This module provides factory_boy factories for creating test instances of
Document domain objects with sensible defaults.
"""

import io
from datetime import UTC, datetime
from typing import Any

from factory.base import Factory
from factory.declarations import LazyAttribute, LazyFunction
from factory.faker import Faker
from julee.core.entities.content_stream import (
    ContentStream,
)

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.models.document.multihash import content_multihash


# Helper functions to generate content bytes consistently
def _get_default_content_bytes() -> bytes:
    """Generate the default content bytes for documents."""
    return b"Test document content for testing purposes"


class ContentStreamFactory(Factory):
    class Meta:
        model = ContentStream

    # Create ContentStream with BytesIO containing test content
    @classmethod
    def _create(cls, model_class: type[ContentStream], **kwargs: Any) -> ContentStream:
        content = kwargs.get("content", b"Test stream content")
        return model_class(io.BytesIO(content))

    @classmethod
    def _build(cls, model_class: type[ContentStream], **kwargs: Any) -> ContentStream:
        content = kwargs.get("content", b"Test stream content")
        return model_class(io.BytesIO(content))


class DocumentFactory(Factory):
    """Factory for creating Document instances with sensible test defaults."""

    class Meta:
        model = Document

    # Core document identification
    document_id = Faker("uuid4")
    original_filename = "test_document.txt"
    content_type = "text/plain"

    # Document processing state
    status = DocumentStatus.CAPTURED
    knowledge_service_id = None
    assembly_types: list[str] = []

    # Timestamps
    created_at = LazyFunction(lambda: datetime.now(UTC))
    updated_at = LazyFunction(lambda: datetime.now(UTC))

    # Additional data
    additional_metadata: dict[str, Any] = {}

    # Content - using LazyAttribute to create fresh BytesIO for each instance
    @LazyAttribute
    def content_multihash(self) -> str:
        # The name of the content this factory actually builds. It was
        # Faker("sha256") — a bare digest of nothing in particular, so a
        # factory-built document was never internally consistent and no
        # test running off it ever saw the format production writes (#44).
        return content_multihash(_get_default_content_bytes())

    @LazyAttribute
    def size_bytes(self) -> int:
        # Calculate size from the default content
        return len(_get_default_content_bytes())

    @LazyAttribute
    def content(self) -> ContentStream:
        # Create ContentStream with default content
        return ContentStream(io.BytesIO(_get_default_content_bytes()))
