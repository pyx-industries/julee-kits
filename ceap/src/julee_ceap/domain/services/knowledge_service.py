"""
KnowledgeService protocol for external service operations in the Capture,
Extract, Assemble, Publish workflow.

This module defines the KnowledgeService protocol that handles interactions
with external knowledge services, including document registration and query
execution. This protocol is separate from the repository layer which only
handles local metadata persistence.

Concrete implementations of this protocol are provided for different external
services (Anthropic, OpenAI, etc.) and are created via factory functions.
"""

from typing import (
    Protocol,
    runtime_checkable,
)

from julee_ceap.domain.models.document.document import Document
from julee_ceap.domain.models.knowledge_service_config.knowledge_service_config import (
    KnowledgeServiceConfig,
)
from julee_ceap.domain.values.query_metadata import QueryMetadata
from julee_ceap.domain.values.query_result import (
    FileRegistrationResult,
    QueryResult,
)
from julee_ceap.domain.values.schema import JsonSchema


@runtime_checkable
class KnowledgeService(Protocol):
    """
    Protocol for interacting with external knowledge services.

    This protocol defines the interface for external operations that were
    moved out of the repository layer. Implementations handle the specifics
    of different knowledge service APIs (Anthropic, OpenAI, etc.).
    """

    async def register_file(
        self,
        config: KnowledgeServiceConfig,
        document: Document,
        content: bytes,
    ) -> FileRegistrationResult:
        """Register a document file with the external knowledge service.

        This method registers a document with the external knowledge service,
        allowing that service to analyze and index the document content for
        future queries.

        The content is handed over rather than taken off the document. A
        Document names its content and does not carry it, so whoever
        calls this has already asked the repository for it and knows
        whether the stream it got can be read where it is going (#69).

        Args:
            config: KnowledgeServiceConfig for the service to use
            document: Document domain object to register

        Returns:
            FileRegistrationResult containing registration details and the
            service's internal file identifier

        .. rubric:: Implementation Notes

        - Must be idempotent: re-registering same document returns same result
        - Should handle service unavailability gracefully
        - Must return the service's internal file ID for future queries
        - Document content is accessed directly from the Document object
        - Should handle various document formats and sizes

        """
        ...

    async def execute_query(
        self,
        config: KnowledgeServiceConfig,
        query_text: str,
        output_schema: JsonSchema | None = None,
        service_file_ids: list[str] | None = None,
        query_metadata: QueryMetadata = QueryMetadata(),
        assistant_prompt: str | None = None,
    ) -> QueryResult:
        """Execute a query against the external knowledge service.

        This method executes a text query against the knowledge service,
        optionally scoping the query to specific documents that have been
        previously registered with the service.

        Args:
            config: KnowledgeServiceConfig for the service to use
            query_text: The query to execute (natural language or structured)
            output_schema: Optional JSON schema for structured response.
                          When provided, the service will attempt to return
                          results conforming to this schema using structured
                          outputs or schema-guided prompting.
            service_file_ids: Optional list of service file IDs to provide as
                             context for the query. These are the IDs returned
                             by the knowledge service from register_file
                             operations, and are included in the query to give
                             the service access to specific documents.
            query_metadata: Optional service-specific metadata and
                           configuration options such as model selection,
                           temperature, max_tokens, etc. The structure depends
                           on the specific knowledge service being used.
            assistant_prompt: Optional assistant message content to constrain
                             or prime the model's response. This is added as
                             the final assistant message before the model
                             generates its response, allowing control over
                             response format and structure.

        Returns:
            QueryResult containing query results and execution metadata

        .. rubric:: Implementation Notes

        - Must be idempotent: same query returns consistent results
        - Service file IDs are provided as context to enhance query responses
        - Should handle service unavailability gracefully
        - Query results should be structured as domain objects
        - Should track execution time and metadata
        - Must handle various query formats (natural language, structured,
          etc.)
        - Should validate that service_file_ids exist in the service before
          including them in the query context

        """
        ...
