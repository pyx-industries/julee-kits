"""Knowledge service adapters, and the factory that chooses one.

The protocol itself is domain — a driven port is what a use case depends
on — and lives in ``domain/services/``. It sat here, so two use cases
imported infrastructure to get it, and the driven port rule never read
it: that rule scans ``domain/``, so being in the wrong directory was
what exempted its two pydantic result types from ever being checked.
"""

import logging

from julee_ceap.domain.services.knowledge_service import (
    FileRegistrationResult,
    KnowledgeService,
    QueryResult,
)

logger = logging.getLogger(__name__)


def ensure_knowledge_service(service: object) -> KnowledgeService:
    """Ensure an object satisfies the KnowledgeService protocol.

    Args:
        service: The service implementation to validate

    Returns:
        The validated service (type checker knows it satisfies
        KnowledgeService)

    Raises:
        TypeError: If the service doesn't satisfy the protocol
    """
    if not isinstance(service, KnowledgeService):
        raise TypeError(
            f"Service {type(service).__name__} does not satisfy "
            f"KnowledgeService protocol"
        )

    return service


__all__ = [
    "KnowledgeService",
    "ensure_knowledge_service",
    "QueryResult",
    "FileRegistrationResult",
]
