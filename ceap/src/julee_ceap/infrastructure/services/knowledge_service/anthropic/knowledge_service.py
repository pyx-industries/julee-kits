"""
Anthropic implementation of KnowledgeService for the Capture, Extract,
Assemble, Publish workflow.

This module provides the Anthropic-specific implementation of the
KnowledgeService protocol. It handles interactions with Anthropic's API
for document registration and query execution.

Requirements:
    - ANTHROPIC_API_KEY environment variable must be set
"""

import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from anthropic import AsyncAnthropic
from julee.core.observability import log_extra

from julee_ceap.domain.models.document.document import Document
from julee_ceap.domain.models.knowledge_service_config import (
    KnowledgeServiceConfig,
)
from julee_ceap.domain.services.knowledge_service import (
    FileRegistrationResult,
    KnowledgeService,
    QueryResult,
)
from julee_ceap.domain.values.query_metadata import QueryMetadata
from julee_ceap.domain.values.query_result import StructuredAnswer
from julee_ceap.domain.values.schema import JsonSchema

logger = logging.getLogger(__name__)

# Default configuration constants
DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_MAX_TOKENS = 4000


class AnthropicKnowledgeService(KnowledgeService):
    """
    Anthropic implementation of the KnowledgeService protocol.

    This class handles interactions with Anthropic's API for document
    registration and query execution. It implements the KnowledgeService
    protocol with Anthropic-specific logic.
    """

    def __init__(self) -> None:
        """Initialize Anthropic knowledge service without configuration.

        Configuration will be provided per method call to maintain
        stateless operation compatible with Temporal workflows.
        """
        # No initialization needed - everything happens per method call
        pass

    def _get_client(self, config: KnowledgeServiceConfig) -> AsyncAnthropic:
        """Get an initialized Anthropic client.

        Args:
            config: KnowledgeServiceConfig (for future extensibility)

        Returns:
            Configured AsyncAnthropic client instance

        Raises:
            ValueError: If ANTHROPIC_API_KEY environment variable is not set
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for "
                "AnthropicKnowledgeService"
            )

        return AsyncAnthropic(
            api_key=api_key,
            default_headers={"anthropic-beta": "files-api-2025-04-14"},
        )

    async def register_file(
        self,
        config: KnowledgeServiceConfig,
        document: Document,
        content: bytes,
    ) -> FileRegistrationResult:
        """Register a document file with Anthropic.

        Args:
            config: KnowledgeServiceConfig for this operation
            document: Document domain object to register

        Returns:
            FileRegistrationResult with Anthropic-specific details
        """
        logger.debug(
            "Registering file with Anthropic",
            extra={
                "knowledge_service_id": config.knowledge_service_id,
                "document_id": document.document_id,
            },
        )

        try:
            # Get Anthropic client for this operation
            client = self._get_client(config)

            # No seek(0) here. The content arrives as a fresh stream
            # at its start, because it was asked for rather than taken
            # off the document, and a response off a socket cannot be
            # rewound anyway (julee#90).

            # Anthropic only supports PDF and plaintext files
            # Convert JSON content type to text/plain for compatibility
            # Plain str from here: what goes to the API is a header
            # value, not the document's own content type.
            content_type = str(document.content_type)
            if content_type == "application/json":
                content_type = "text/plain"

            file_response = await client.beta.files.upload(
                file=(
                    document.original_filename,
                    content,
                    content_type,
                )
            )

            anthropic_file_id = file_response.id

            result = FileRegistrationResult(
                document_id=document.document_id,
                knowledge_service_file_id=anthropic_file_id,
                registration_metadata={
                    "service": "anthropic",
                    "registered_via": "beta_files_api",
                    "filename": document.original_filename,
                    "content_type": document.content_type,
                    "size_bytes": document.size_bytes,
                    "content_multihash": document.content_multihash,
                    "anthropic_file_id": anthropic_file_id,
                },
                created_at=datetime.now(UTC),
            )

            logger.info(
                "File registered with Anthropic beta Files API",
                extra={
                    "knowledge_service_id": config.knowledge_service_id,
                    "document_id": document.document_id,
                    "anthropic_file_id": anthropic_file_id,
                    "original_filename": document.original_filename,
                    "size_bytes": document.size_bytes,
                },
            )

            return result

        except Exception as e:
            logger.error(
                "Failed to register file with Anthropic",
                extra={
                    "knowledge_service_id": config.knowledge_service_id,
                    "document_id": document.document_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def execute_query(
        self,
        config: KnowledgeServiceConfig,
        query_text: str,
        output_schema: JsonSchema | None = None,
        service_file_ids: list[str] | None = None,
        query_metadata: QueryMetadata = QueryMetadata(),
        assistant_prompt: str | None = None,
    ) -> QueryResult:
        """Execute a query against Anthropic.

        Args:
            config: KnowledgeServiceConfig for this operation
            query_text: The query to execute
            output_schema: Optional JSON schema for inclusion in prompt (not used for structured outputs)
            service_file_ids: Optional list of Anthropic file IDs to provide
                             as context for the query
            query_metadata: Optional Anthropic-specific configuration such as
                           model, temperature, max_tokens, etc.
            assistant_prompt: Optional assistant message content to constrain
                             or prime the model's response.

        Returns:
            QueryResult with Anthropic query results
        """
        logger.debug(
            "Executing query with Anthropic",
            extra={
                "knowledge_service_id": config.knowledge_service_id,
                "query_text": query_text,
                "document_count": (len(service_file_ids) if service_file_ids else 0),
                "file_count": (len(service_file_ids) if service_file_ids else 0),
            },
        )

        start_time = time.time()
        query_id = f"anthropic_{uuid.uuid4().hex[:12]}"

        # A knob the query left unset is this adapter's to choose
        model = query_metadata.model or DEFAULT_MODEL
        max_tokens = query_metadata.max_tokens or DEFAULT_MAX_TOKENS
        temperature = query_metadata.temperature

        try:
            # Get Anthropic client for this operation
            client = self._get_client(config)

            # Prepare the message content with file attachments if provided
            content_parts = []

            # Add file attachments if service_file_ids are provided
            if service_file_ids:
                for file_id in service_file_ids:
                    content_parts.append(
                        {
                            "type": "document",
                            "source": {"type": "file", "file_id": file_id},
                        }
                    )

            # Handle schema embedding if provided
            if output_schema:
                # Build query with embedded schema
                schema_json = json.dumps(dict(output_schema.document), indent=2)
                enhanced_query_text = f"""{query_text}

Please structure your response according to this JSON schema:
{schema_json}

Return only valid JSON that conforms to this schema, without any surrounding
text or markdown formatting."""
            else:
                enhanced_query_text = query_text

            # Add the text query
            content_parts.append({"type": "text", "text": enhanced_query_text})

            # Prepare messages for the API
            messages = [{"role": "user", "content": content_parts}]

            # Add assistant message if provided to constrain response
            if assistant_prompt:
                messages.append({"role": "assistant", "content": assistant_prompt})

            # Any is this adapter's own business: what the SDK wants is
            # the SDK's shape, not the domain's. It was inferred before,
            # because the knobs came out of an untyped mapping.
            create_params: dict[str, Any] = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
            }

            # Add temperature if specified
            if temperature is not None:
                create_params["temperature"] = temperature

            response = await client.messages.create(**create_params)

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Validate response has exactly one content block of type 'text'
            if len(response.content) != 1:
                raise ValueError(
                    f"Expected exactly 1 content block, got {len(response.content)}"
                )

            content_block = response.content[0]

            if not hasattr(content_block, "type") or content_block.type != "text":
                block_type = getattr(content_block, "type", "unknown")
                raise ValueError(
                    f"Expected content block type 'text', got '{block_type}'"
                )

            if not hasattr(content_block, "text"):
                raise ValueError("Text content block missing 'text' attribute")

            response_text = str(content_block.text)

            logger.debug(
                "Single text content block validated and extracted",
                extra={
                    "knowledge_service_id": config.knowledge_service_id,
                    "query_id": query_id,
                    "response_length": len(response_text),
                },
            )

            # An answer that was asked to fit a schema is JSON, and its
            # structured form is built from the text that parses: the
            # prompt prefix and the response together, when the prompt
            # opened the object for the model.
            structured: StructuredAnswer | None = None
            if output_schema:
                if assistant_prompt and assistant_prompt.strip().startswith("{"):
                    json_text_to_parse = assistant_prompt + response_text
                else:
                    json_text_to_parse = response_text
                try:
                    structured = StructuredAnswer(json_text_to_parse.strip())
                except ValueError as not_json:
                    logger.error(
                        "Anthropic was asked for JSON and did not answer with it",
                        extra={
                            "knowledge_service_id": config.knowledge_service_id,
                            "query_id": query_id,
                            "assistant_prompt": assistant_prompt,
                            "response_text_preview": response_text[:100],
                        },
                    )
                    raise ValueError(
                        f"Expected valid JSON response when output schema provided, "
                        f"but failed to parse: {not_json}"
                    ) from not_json

            # What the service said, verbatim, and its structured form
            # when a schema asked for one. What the model was, what it
            # cost and why it stopped are this adapter's to log, not the
            # domain's to carry (ADR 017).
            logger.info(
                "Anthropic answered",
                extra=log_extra(
                    query_id=query_id,
                    model=model,
                    stop_reason=response.stop_reason,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    sources=list(service_file_ids or []),
                ),
            )
            result = QueryResult(
                query_id=query_id,
                query_text=query_text,
                answer=response_text,
                data=structured,
                execution_time_ms=execution_time_ms,
                created_at=datetime.now(UTC),
            )

            logger.info(
                "Query executed with Anthropic successfully",
                extra={
                    "knowledge_service_id": config.knowledge_service_id,
                    "query_id": query_id,
                    "execution_time_ms": execution_time_ms,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "file_count": (len(service_file_ids) if service_file_ids else 0),
                },
            )

            return result

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "Failed to execute query with Anthropic",
                extra={
                    "knowledge_service_id": config.knowledge_service_id,
                    "query_id": query_id,
                    "query_text": query_text,
                    "execution_time_ms": execution_time_ms,
                    "file_count": (len(service_file_ids) if service_file_ids else 0),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise
