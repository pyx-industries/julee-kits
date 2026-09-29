"""
Test factories for Document domain objects using factory_boy.

This module provides factory_boy factories for creating test instances of
Document domain objects with sensible defaults.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from factory.base import Factory
from factory.declarations import LazyAttribute, LazyFunction
from julee.core.values.text import NonEmptyText

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.values.multihash import (
    ContentMultihash,
    content_multihash,
)


# Helper functions to generate content bytes consistently
def _get_default_content_bytes() -> bytes:
    """Generate the default content bytes for documents."""
    return b"Test document content for testing purposes"


class DocumentFactory(Factory):
    """Factory for creating Document instances with sensible test defaults."""

    class Meta:
        model = Document

    # Core document identification
    document_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))
    original_filename = NonEmptyText("test_document.txt")
    content_type = NonEmptyText("text/plain")

    # Document processing state
    status = DocumentStatus.CAPTURED
    knowledge_service_id = None
    assembly_types: tuple[str, ...] = ()

    # Timestamps
    created_at = LazyFunction(lambda: datetime.now(UTC))
    updated_at = LazyFunction(lambda: datetime.now(UTC))

    # Additional data
    additional_metadata: dict[str, Any] = {}

    # Content - using LazyAttribute to create fresh BytesIO for each instance
    @LazyAttribute
    def content_multihash(self) -> ContentMultihash:
        # The name of the content this factory actually builds. It was
        # Faker("sha256") — a bare digest of nothing in particular, so a
        # factory-built document was never internally consistent and no
        # test running off it ever saw the format production writes (#44).
        return ContentMultihash(content_multihash(_get_default_content_bytes()))

    @LazyAttribute
    def size_bytes(self) -> int:
        # Calculate size from the default content
        return len(_get_default_content_bytes())

    # A `content` attribute used to sit here, building a ContentStream.
    # Document has had no content field since #69; pydantic ignores an
    # unknown keyword by default, so factory_boy passed it and it went
    # nowhere. A dataclass refuses it, which is how it was found.
