"""
KnowledgeService domain models for the Capture, Extract, Assemble,
Publish workflow.

This module contains the KnowledgeService domain object that represents
knowledge services in the CEAP workflow system.

A KnowledgeService defines a service that can store documents and execute
queries against them. It acts as an interface to external AI/ML services
that can analyze and extract information from documents.

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from datetime import UTC, datetime
from enum import StrEnum

from julee.core.entities.entity import Entity
from julee.core.entities.text import Name, NonEmptyText
from pydantic import Field, field_validator


class ServiceApi(StrEnum):
    """Supported knowledge service APIs."""

    ANTHROPIC = "anthropic"


class KnowledgeServiceConfig(Entity):
    """Knowledge service configuration that defines how to interact with
    an external knowledge/AI service.

    A KnowledgeServiceConfig represents a service endpoint that can store
    documents and execute queries against them. This could be an AI service,
    vector database, search engine, or any other service that can analyze
    documents and answer questions about them.
    """

    # Core service identification
    knowledge_service_id: NonEmptyText = Field(
        description="Unique identifier for this knowledge service"
    )
    name: Name = Field(description="Human-readable name for the knowledge service")
    description: NonEmptyText = Field(
        description="Description of what this knowledge service does"
    )
    service_api: ServiceApi = Field(
        description="The external API/service this knowledge service uses"
    )

    # Timestamps
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("service_api")
    @classmethod
    def service_api_must_be_valid(cls, v: ServiceApi) -> ServiceApi:
        if v not in ServiceApi:
            raise ValueError(
                f"Invalid service API: {v}. Must be one of {list(ServiceApi)}"
            )
        return v
