"""The messages this API answers with.

These define the contract between the API and external clients.

Most endpoints still answer with a domain entity, and the docstring here
used to call that a clean architecture principle. It is the opposite of
one: an entity is a record this context keeps, a response is a message it
sends, and making them the same thing means a client depends on the
domain's shape and the domain cannot change without breaking it.

AssemblySpecificationResponse was the first to be separated, because
adding a value object to the entity changed the JSON a client sees —
which is the coupling, demonstrating itself. It happened again when
query_metadata stopped being an open mapping and the query endpoints'
JSON changed with it. The remaining six endpoints are separated here,
so the next change to an entity is a change to this file or to nothing.
No endpoint answers with an entity now, and tests/test_responses.py
writes down what each message names, so it stays that way.

An id, a name and a filename go out as ``str``. NonEmptyText and Name
are how this context tells itself a string has been checked; a client
reading one has no use for that, and a client is not the one doing the
checking.
"""

from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from julee_ceap.domain.models.assembly_specification import (
    AssemblySpecification,
    AssemblySpecificationStatus,
)
from julee_ceap.domain.models.assembly_specification.knowledge_service_query import (
    KnowledgeServiceQuery,
)
from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.models.knowledge_service_config import (
    KnowledgeServiceConfig,
    ServiceApi,
)
from julee_ceap.domain.values.query_metadata import QueryMetadata


class ServiceStatus(StrEnum):
    """Service status enumeration."""

    UP = "up"
    DOWN = "down"


class SystemStatus(StrEnum):
    """Overall system status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceHealthStatus(BaseModel):
    """Health status for individual services."""

    api: ServiceStatus
    temporal: ServiceStatus
    storage: ServiceStatus


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint."""

    status: SystemStatus
    timestamp: str
    services: ServiceHealthStatus


class AssemblySpecificationResponse(BaseModel):
    """What the API says an assembly specification is.

    The schema goes out as the JSON document a client sent, not as the
    domain's ``JsonSchema`` wrapper around it. That wrapper is how this
    context says "this mapping is a schema" to itself; a client sending
    and reading a schema has no use for it.
    """

    assembly_specification_id: str
    name: str
    applicability: str
    jsonschema: Mapping[str, Any]
    status: AssemblySpecificationStatus
    knowledge_service_queries: Mapping[str, str]
    version: str
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def of(
        cls, specification: AssemblySpecification
    ) -> "AssemblySpecificationResponse":
        """The message for one specification.

        Args:
            specification: The entity to describe

        Returns:
            What a client is told
        """
        return cls(
            assembly_specification_id=str(specification.assembly_specification_id),
            name=str(specification.name),
            applicability=str(specification.applicability),
            jsonschema=specification.jsonschema.document,
            status=specification.status,
            knowledge_service_queries={
                pointer: str(query)
                for pointer, query in specification.knowledge_service_queries.items()
            },
            version=str(specification.version),
            created_at=specification.created_at,
            updated_at=specification.updated_at,
        )


class DocumentResponse(BaseModel):
    """What the API says a document is.

    The content multihash goes out as a plain string. It is a
    ContentMultihash in the domain, which is how this context says "this
    string is a multihash of some content" to itself.
    """

    document_id: str
    original_filename: str
    content_type: str
    size_bytes: int
    content_multihash: str
    status: DocumentStatus
    knowledge_service_id: str | None
    assembly_types: tuple[str, ...]
    additional_metadata: Mapping[str, Any]
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def of(cls, document: Document) -> "DocumentResponse":
        """The message for one document.

        Args:
            document: The entity to describe

        Returns:
            What a client is told
        """
        return cls(
            document_id=str(document.document_id),
            original_filename=str(document.original_filename),
            content_type=str(document.content_type),
            size_bytes=document.size_bytes,
            content_multihash=str(document.content_multihash),
            status=document.status,
            knowledge_service_id=document.knowledge_service_id,
            assembly_types=document.assembly_types,
            additional_metadata=document.additional_metadata,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class KnowledgeServiceConfigResponse(BaseModel):
    """What the API says a knowledge service is."""

    knowledge_service_id: str
    name: str
    description: str
    service_api: ServiceApi
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def of(cls, config: KnowledgeServiceConfig) -> "KnowledgeServiceConfigResponse":
        """The message for one knowledge service.

        Args:
            config: The entity to describe

        Returns:
            What a client is told
        """
        return cls(
            knowledge_service_id=str(config.knowledge_service_id),
            name=str(config.name),
            description=str(config.description),
            service_api=config.service_api,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )


class QueryMetadataResponse(BaseModel):
    """How a query asked to be run, on the way out.

    Written here rather than shared with QueryMetadataRequest: a request
    and a response are two messages, and they are free to differ. A
    client may omit a knob when asking; a response names all three, so a
    reader does not have to guess whether a missing one means unset.
    """

    model: str | None
    max_tokens: int | None
    temperature: float | None

    @classmethod
    def of(cls, metadata: QueryMetadata) -> "QueryMetadataResponse":
        """The message for one query's tuning.

        Args:
            metadata: The value to describe

        Returns:
            What a client is told
        """
        return cls(
            model=metadata.model,
            max_tokens=metadata.max_tokens,
            temperature=metadata.temperature,
        )


class KnowledgeServiceQueryResponse(BaseModel):
    """What the API says a knowledge service query is."""

    query_id: str
    name: str
    knowledge_service_id: str
    prompt: str
    query_metadata: QueryMetadataResponse
    assistant_prompt: str | None
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def of(cls, query: KnowledgeServiceQuery) -> "KnowledgeServiceQueryResponse":
        """The message for one query.

        Args:
            query: The entity to describe

        Returns:
            What a client is told
        """
        return cls(
            query_id=str(query.query_id),
            name=str(query.name),
            knowledge_service_id=str(query.knowledge_service_id),
            prompt=str(query.prompt),
            query_metadata=QueryMetadataResponse.of(query.query_metadata),
            assistant_prompt=query.assistant_prompt,
            created_at=query.created_at,
            updated_at=query.updated_at,
        )
