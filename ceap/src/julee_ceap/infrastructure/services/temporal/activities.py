"""
Temporal activity wrapper classes for the julee knowledge service
domain.

This module contains the @temporal_activity_registration decorated class
that wraps knowledge service operations as Temporal activities. This class is
imported by the worker to register activities with Temporal.

The class follows the naming pattern documented in systemPatterns.org:
- Activity names: {domain}.{service_name}.{method}
- The knowledge service gets its own activity prefix
"""

import io
import logging

from julee.core.entities.content_stream import ContentStream
from julee.integrations.temporal.decorators import temporal_activity_registration
from typing_extensions import override

from julee_ceap.domain.models.document import Document
from julee_ceap.domain.models.knowledge_service_config import (
    KnowledgeServiceConfig,
)
from julee_ceap.domain.repositories.document import DocumentRepository
from julee_ceap.infrastructure.services.knowledge_service.factory import (
    ConfigurableKnowledgeService,
)
from julee_ceap.infrastructure.services.temporal.activity_names import (
    KNOWLEDGE_SERVICE_ACTIVITY_BASE,
)

from ..knowledge_service import FileRegistrationResult


@temporal_activity_registration(KNOWLEDGE_SERVICE_ACTIVITY_BASE)
class TemporalKnowledgeService(ConfigurableKnowledgeService):
    """Temporal activity wrapper for KnowledgeService operations.

    This class handles the issue where ContentStream objects don't survive
    Temporal's serialization by re-fetching document content from the
    injected DocumentRepository before performing operations that require it.
    """

    def __init__(self, document_repo: DocumentRepository) -> None:
        super().__init__()
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.document_repo: DocumentRepository = document_repo

    @override
    async def register_file(
        self, config: KnowledgeServiceConfig, document: Document
    ) -> FileRegistrationResult:
        """Register a document file, reading its content through the port.

        A Document that has crossed an activity boundary carries no
        content stream — a live stream cannot be serialised, so the
        field is excluded from it. Content is therefore always read
        here, rather than taken from whatever arrived.

        This used to re-fetch the whole document, read its stream in
        full, and assign the result over ``ContentStream._stream``, a
        private attribute, so that the upload could seek. All three
        steps were working around content being a field of the entity
        rather than something the repository can be asked for.
        """
        content = await self.document_repo.content_of(document)

        # The upload seeks, and a response streamed off a socket cannot
        # (julee#90). Buffering it is the adapter's business, and this
        # is the adapter.
        seekable = ContentStream(io.BytesIO(content.read()))

        return await super().register_file(config, document.evolve(content=seekable))


ACTIVITY_CLASSES = (TemporalKnowledgeService,)
"""The service activities this kit offers a worker.

Services are activities on the same terms as repositories, and a worker
needs both, so this module is named in the manifest beside the
repositories one.
"""


__all__ = [
    "ACTIVITY_CLASSES",
    "TemporalKnowledgeService",
    "KNOWLEDGE_SERVICE_ACTIVITY_BASE",
]
