"""
KnowledgeServiceQuery domain models for the Capture, Extract, Assemble,
Publish
workflow.

This module contains the KnowledgeServiceQuery domain object that represents
specific queries to knowledge services for data extraction in the CEAP
workflow system.

A KnowledgeServiceQuery defines a specific extraction operation that can be
performed against a knowledge service to extract data for a particular part
of an AssemblySpecification's JSON schema.

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from julee.core.values.text import Name, NonEmptyText

from julee_ceap.domain.values.query_metadata import QueryMetadata


@dataclass(frozen=True, kw_only=True)
class KnowledgeServiceQuery:
    """Knowledge service query configuration for extracting specific data.

    A KnowledgeServiceQuery represents a specific extraction operation that
    can be performed against a knowledge service. It defines which knowledge
    service to use and what prompt to send for data extraction.

    When executed, the relevant section of the AssemblySpecification's JSON
    schema will be
    passed along with the prompt to ensure the knowledge service response
    conforms to the expected structure and validation requirements.

    The mapping between queries and schema sections is handled by the
    AssemblySpecification's knowledge_service_queries field.

    How a query asks to be run is a QueryMetadata: a model, a token
    budget and a temperature, each optional. This was an open mapping
    whose docstring advertised top_p, endpoint, timeout and retries as
    well, none of which any adapter has ever read.
    """

    # Core query identification
    query_id: NonEmptyText
    """Unique identifier for this query."""
    name: Name
    """Human-readable name describing the query purpose."""

    # Knowledge service configuration
    knowledge_service_id: NonEmptyText
    """Identifier of the knowledge service to query."""
    prompt: NonEmptyText
    """The specific prompt to send to the knowledge service for this extraction."""

    # Service-specific configuration
    query_metadata: QueryMetadata = field(default_factory=QueryMetadata)
    """How this query asks to be run. Knobs left unset are the adapter's."""
    assistant_prompt: str | None = None
    """Optional assistant message content to constrain or prime the model's response. This is added as the final assistant message before the model generates its response, allowing control over response format and structure."""

    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
