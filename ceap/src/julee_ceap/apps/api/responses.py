"""The messages this API answers with.

These define the contract between the API and external clients.

Most endpoints still answer with a domain entity, and the docstring here
used to call that a clean architecture principle. It is the opposite of
one: an entity is a record this context keeps, a response is a message it
sends, and making them the same thing means a client depends on the
domain's shape and the domain cannot change without breaking it.

AssemblySpecificationResponse is the first to be separated, because
adding a value object to the entity changed the JSON a client sees —
which is the coupling, demonstrating itself. The other eight endpoints
are still to do.
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
