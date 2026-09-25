"""
Repository protocols for the CEAP (Capture, Extract, Assemble, Publish) domain.

This module exports all repository protocol interfaces for the CEAP workflow,
following the Clean Architecture patterns established in the Julee framework.

Each is bound to exactly one entity. The schema fetcher that used to sit
here is bound to none and is an oracle: see :mod:`julee_ceap.domain.oracles`.
"""

from .assembly import AssemblyRepository
from .assembly_specification import AssemblySpecificationRepository
from .document import DocumentRepository
from .document_policy_validation import DocumentPolicyValidationRepository
from .knowledge_service_config import KnowledgeServiceConfigRepository
from .knowledge_service_query import KnowledgeServiceQueryRepository
from .policy import PolicyRepository

__all__ = [
    "DocumentRepository",
    "AssemblyRepository",
    "AssemblySpecificationRepository",
    "KnowledgeServiceConfigRepository",
    "KnowledgeServiceQueryRepository",
    "PolicyRepository",
    "DocumentPolicyValidationRepository",
]
