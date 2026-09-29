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

from julee.integrations.temporal.decorators import temporal_activity_registration

from julee_ceap.infrastructure.services.knowledge_service.factory import (
    ConfigurableKnowledgeService,
)
from julee_ceap.infrastructure.services.temporal.activity_names import (
    KNOWLEDGE_SERVICE_ACTIVITY_BASE,
)


@temporal_activity_registration(KNOWLEDGE_SERVICE_ACTIVITY_BASE)
class TemporalKnowledgeService(ConfigurableKnowledgeService):
    """The knowledge service's activity twin, as every repository has one.

    Nothing but the decorator: the activity names the worker registers
    and the proxy calls come from the prefix, and the behaviour is
    ConfigurableKnowledgeService's. It used to take a DocumentRepository
    to re-fetch content a ContentStream could not carry across an
    activity; the port takes bytes now (julee-kits#89).
    """


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
