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

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from julee.core.entities.text import Name, NonEmptyText


class ServiceApi(StrEnum):
    """Supported knowledge service APIs."""

    ANTHROPIC = "anthropic"


@dataclass(frozen=True, kw_only=True)
class KnowledgeServiceConfig:
    """Knowledge service configuration that defines how to interact with
    an external knowledge/AI service.

    A KnowledgeServiceConfig represents a service endpoint that can store
    documents and execute queries against them. This could be an AI service,
    vector database, search engine, or any other service that can analyze
    documents and answer questions about them.
    """

    # Core service identification
    knowledge_service_id: NonEmptyText
    """Unique identifier for this knowledge service."""
    name: Name
    """Human-readable name for the knowledge service."""
    description: NonEmptyText
    """Description of what this knowledge service does."""
    service_api: ServiceApi
    """The external API/service this knowledge service uses."""

    # Timestamps
    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))

    # service_api carried a validator refusing a value outside ServiceApi.
    # It could never fire: pydantic had already coerced the value to a
    # member before it ran, so "not in ServiceApi" was never true. The
    # annotation is the whole of the rule.
