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
  the unified ContentStream interface wrapping io.IOBase.

In Temporal workflow contexts, these protocols are implemented by workflow
stubs that delegate to activities for durability and proper error handling.
"""

from typing import Protocol, runtime_checkable

from julee.core.entities.content_stream import ContentStream
from julee.repositories.base import BaseRepository

from julee_ceap.domain.models import Document


@runtime_checkable
class DocumentRepository(BaseRepository[Document], Protocol):
    """Handles document storage and retrieval operations.

    This repository manages the core document storage and metadata
    operations within the Capture, Extract, Assemble, Publish workflow.

    Inherits common CRUD operations (get, save, generate_id) from
    BaseRepository. The save method handles both content and metadata
    storage atomically.
    """

    async def content_of(self, document: Document) -> ContentStream:
        """The content this document names, as a stream to read once.

        A fresh stream each call. Content is stored apart from metadata
        and keyed by ``content_multihash``, so this reads an object the
        document points at rather than something it carries — which is
        why every caller gets its own stream and none of them has
        anything to rewind.

        That matters twice over. julee#124 was one ContentStream handed
        to two readers, the second of which got nothing; julee#90 was a
        caller rewinding a stream that is a socket and cannot be
        rewound. Asking again answers both, and asking is only possible
        because the content has a name of its own.

        Args:
            document: The document whose content to read

        Returns:
            A stream over the content, at its start

        Raises:
            ValueError: If the document names content that is not there
        """
        ...
