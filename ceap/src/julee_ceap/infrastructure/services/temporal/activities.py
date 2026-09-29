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

import logging

from julee.integrations.temporal.decorators import temporal_activity_registration

from julee_ceap.domain.repositories.document import DocumentRepository
from julee_ceap.infrastructure.services.knowledge_service.factory import (
    ConfigurableKnowledgeService,
)
from julee_ceap.infrastructure.services.temporal.activity_names import (
    KNOWLEDGE_SERVICE_ACTIVITY_BASE,
)


@temporal_activity_registration(KNOWLEDGE_SERVICE_ACTIVITY_BASE)
class TemporalKnowledgeService(ConfigurableKnowledgeService):
    """Temporal activity wrapper for KnowledgeService operations.

    This class existed to work around ContentStream not surviving
    Temporal's serialization by re-fetching document content from the
    injected DocumentRepository before performing operations that require it.
    """

    def __init__(self, document_repo: DocumentRepository) -> None:
        super().__init__()
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.document_repo: DocumentRepository = document_repo

    # register_file was overridden here, and the override existed for one
    # reason: a ContentStream could not cross an activity boundary, so
    # what arrived was not the caller's stream and the content had to be
    # fetched again through the repository. The port takes bytes now
    # (julee-kits#89), and bytes serialise, so there is nothing left to
    # work around.
    #
    # The class remains because it is the registered activity class the
    # worker and the entry point name. Whether it should still exist,
    # now that it adds nothing to ConfigurableKnowledgeService, is worth
    # asking separately: removing it changes what a worker registers.


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
