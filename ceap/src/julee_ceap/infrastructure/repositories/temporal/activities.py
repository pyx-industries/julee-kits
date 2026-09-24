"""
Temporal activity wrapper classes for the julee domain.

This module contains all @temporal_activity_registration decorated classes
that wrap pure backend repositories as Temporal activities. These classes are
imported by the worker to register activities with Temporal.

The classes follow the naming pattern documented in systemPatterns.org:
- Activity names: {domain}.{repo_name}.{method}
- Each repository type gets its own activity prefix
"""

from julee.integrations.temporal.decorators import temporal_activity_registration

from julee_ceap.infrastructure.repositories.http.schema import (
    HttpRemoteSchemaRepository,
)
from julee_ceap.infrastructure.repositories.minio.assembly import (
    MinioAssemblyRepository,
)
from julee_ceap.infrastructure.repositories.minio.assembly_specification import (
    MinioAssemblySpecificationRepository,
)
from julee_ceap.infrastructure.repositories.minio.document import (
    MinioDocumentRepository,
)
from julee_ceap.infrastructure.repositories.minio.document_policy_validation import (
    MinioDocumentPolicyValidationRepository,
)
from julee_ceap.infrastructure.repositories.minio.knowledge_service_config import (
    MinioKnowledgeServiceConfigRepository,
)
from julee_ceap.infrastructure.repositories.minio.knowledge_service_query import (
    MinioKnowledgeServiceQueryRepository,
)
from julee_ceap.infrastructure.repositories.minio.policy import (
    MinioPolicyRepository,
)

# Import activity name bases from shared module
from julee_ceap.infrastructure.repositories.temporal.activity_names import (
    ASSEMBLY_ACTIVITY_BASE,
    ASSEMBLY_SPECIFICATION_ACTIVITY_BASE,
    DOCUMENT_ACTIVITY_BASE,
    DOCUMENT_POLICY_VALIDATION_ACTIVITY_BASE,
    KNOWLEDGE_SERVICE_CONFIG_ACTIVITY_BASE,
    KNOWLEDGE_SERVICE_QUERY_ACTIVITY_BASE,
    POLICY_ACTIVITY_BASE,
    REMOTE_SCHEMA_ACTIVITY_BASE,
)


@temporal_activity_registration(ASSEMBLY_ACTIVITY_BASE)
class TemporalMinioAssemblyRepository(MinioAssemblyRepository):
    """Temporal activity wrapper for MinioAssemblyRepository."""

    pass


@temporal_activity_registration(ASSEMBLY_SPECIFICATION_ACTIVITY_BASE)
class TemporalMinioAssemblySpecificationRepository(
    MinioAssemblySpecificationRepository
):
    """Temporal activity wrapper for MinioAssemblySpecificationRepository."""

    pass


@temporal_activity_registration(DOCUMENT_ACTIVITY_BASE)
class TemporalMinioDocumentRepository(MinioDocumentRepository):
    """Temporal activity wrapper for MinioDocumentRepository."""

    pass


@temporal_activity_registration(KNOWLEDGE_SERVICE_CONFIG_ACTIVITY_BASE)
class TemporalMinioKnowledgeServiceConfigRepository(
    MinioKnowledgeServiceConfigRepository
):
    """Temporal activity wrapper for MinioKnowledgeServiceConfigRepository."""

    pass


@temporal_activity_registration(KNOWLEDGE_SERVICE_QUERY_ACTIVITY_BASE)
class TemporalMinioKnowledgeServiceQueryRepository(
    MinioKnowledgeServiceQueryRepository
):
    """Temporal activity wrapper for MinioKnowledgeServiceQueryRepository."""

    pass


@temporal_activity_registration(POLICY_ACTIVITY_BASE)
class TemporalMinioPolicyRepository(MinioPolicyRepository):
    """Temporal activity wrapper for MinioPolicyRepository."""

    pass


@temporal_activity_registration(DOCUMENT_POLICY_VALIDATION_ACTIVITY_BASE)
class TemporalMinioDocumentPolicyValidationRepository(
    MinioDocumentPolicyValidationRepository
):
    """Temporal activity wrapper for DocumentPolicyValidationRepository."""

    pass


@temporal_activity_registration(REMOTE_SCHEMA_ACTIVITY_BASE)
class TemporalHttpRemoteSchemaRepository(HttpRemoteSchemaRepository):
    """Temporal activity wrapper for HttpRemoteSchemaRepository."""

    pass


ACTIVITY_CLASSES = (
    TemporalMinioAssemblyRepository,
    TemporalMinioAssemblySpecificationRepository,
    TemporalMinioDocumentRepository,
    TemporalMinioKnowledgeServiceConfigRepository,
    TemporalMinioKnowledgeServiceQueryRepository,
    TemporalMinioPolicyRepository,
    TemporalMinioDocumentPolicyValidationRepository,
    TemporalHttpRemoteSchemaRepository,
)
"""The repository activities this kit offers a worker.

Named in the manifest under "temporal.activities", so a solution is told
what there is rather than reading this module to find out. A class
decorated here and missing from this tuple is doctrine's to report.

Classes, not instances: each takes its dependencies at construction, and
which client to hand it is the composition root's decision.
"""


__all__ = [
    "ACTIVITY_CLASSES",
    "TemporalMinioAssemblyRepository",
    "TemporalMinioAssemblySpecificationRepository",
    "TemporalMinioDocumentRepository",
    "TemporalMinioKnowledgeServiceConfigRepository",
    "TemporalMinioKnowledgeServiceQueryRepository",
    "TemporalMinioPolicyRepository",
    "TemporalMinioDocumentPolicyValidationRepository",
    "TemporalHttpRemoteSchemaRepository",
    # Export constants for proxy consistency
    "ASSEMBLY_ACTIVITY_BASE",
    "ASSEMBLY_SPECIFICATION_ACTIVITY_BASE",
    "DOCUMENT_ACTIVITY_BASE",
    "KNOWLEDGE_SERVICE_CONFIG_ACTIVITY_BASE",
    "KNOWLEDGE_SERVICE_QUERY_ACTIVITY_BASE",
]
