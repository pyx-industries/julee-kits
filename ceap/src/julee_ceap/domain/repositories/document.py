"""
Document repository interface defined as Protocol for the Capture, Extract,
Assemble, Publish workflow.

This module defines the core document storage and retrieval repository
protocol. The repository works with Document domain objects that use BinaryIO
streams for efficient content handling.

All repository operations follow the same principles as the sample
repositories:

- **Idempotency**: All methods are designed to be idempotent and safe for
  retry. Multiple calls with the same parameters will produce the same
  result without unintended side effects.

- **Workflow Safety**: All operations are safe to call from deterministic
  workflow contexts. Non-deterministic operations (like ID generation) are
  explicitly delegated to activities.

- **Domain Objects**: Methods accept and return domain objects or primitives,
  never framework-specific types. Content streams are handled through the
  BinaryIO interface.

- **Content Streaming**: Repository implementations should support both
  small content (via BytesIO) and large content (via file streams) through
  bytes, read in full by the adapter.

In Temporal workflow contexts, these protocols are implemented by workflow
stubs that delegate to activities for durability and proper error handling.
"""

from typing import Protocol, runtime_checkable

from julee.core.repositories.base import BaseRepository

from julee_ceap.domain.models import Document
from julee_ceap.domain.models.document.multihash import ContentMultihash


@runtime_checkable
class DocumentRepository(BaseRepository[Document], Protocol):
    """Handles document storage and retrieval operations.

    This repository manages the core document storage and metadata
    operations within the Capture, Extract, Assemble, Publish workflow.

    Inherits common CRUD operations (get, save, generate_id) from
    BaseRepository. The save method handles both content and metadata
    storage atomically.
    """

    async def store_content(self, content: bytes) -> ContentMultihash:
        """Put content in the store, and say what it turned out to be.

        Content is stored under its own hash, so it has to be read
        before it can be named — which is why this comes back with the
        multihash and the size rather than taking them. A document
        naming this content is built afterwards, from what is true.

        Storing the same bytes twice is not an error and not a second
        copy: the name is the content, so the second call finds the
        first one's object already there.

        Bytes rather than a stream. This took a ContentStream, which is
        a class with no domain meaning: not an entity, not a value
        object, and not something that survives a Temporal activity
        boundary. Every caller already had the bytes in hand and wrapped
        them only to satisfy this signature (julee-kits#89).

        Args:
            content: The content to store

        Returns:
            The multihash the content is stored under, which is the
            name a document uses for it
        """
        ...

    async def content_of(self, document: Document) -> bytes:
        """The content this document names.

        Content is stored apart from metadata and keyed by
        ``content_multihash``, so this reads an object the document
        points at rather than something it carries.

        Bytes rather than a stream, which is what two earlier bugs were
        about. julee#124 was one ContentStream handed to two readers,
        the second of which got nothing; julee#90 was a caller
        rewinding a stream that is a socket and cannot be rewound.
        Bytes can be read twice and handed to two readers, so neither
        is expressible.

        Every caller read the stream in full immediately. Whether the
        adapter buffers is the adapter's business, which the Temporal
        activity boundary settles anyway: a stream cannot cross it, and
        ``services/temporal/activities.py`` already re-reads the content
        rather than passing one (julee-kits#89).

        Args:
            document: The document whose content to read

        Returns:
            The content

        Raises:
            ValueError: If the document names content that is not there
        """
        ...
