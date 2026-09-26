"""
Use case logic for data assembly within the Capture, Extract, Assemble,
Publish workflow.

This module contains use case classes that orchestrate business logic while
remaining framework-agnostic. Dependencies are injected via repository
instances following the Clean Architecture principles.
"""

import json
import logging
from collections.abc import Mapping
from typing import Any

import jsonschema
from julee.core.usecases.decorators import try_use_case_step
from julee.core.validation import ensure_repository_protocol, validate_parameter_types
from julee.core.witnesses import ClockWitness, ExecutionWitness, SystemClockWitness
from julee.core.witnesses.execution import DefaultExecutionWitness
from pydantic import BaseModel

from julee_ceap._schema_ref import extract_schema_from_fetched
from julee_ceap.domain.models import (
    Assembly,
    AssemblySpecification,
    AssemblyStatus,
    Document,
    DocumentStatus,
    KnowledgeServiceQuery,
)
from julee_ceap.domain.models.document.multihash import content_multihash
from julee_ceap.domain.oracles import SchemaOracle
from julee_ceap.domain.repositories import (
    AssemblyRepository,
    AssemblySpecificationRepository,
    DocumentRepository,
    KnowledgeServiceConfigRepository,
    KnowledgeServiceQueryRepository,
)
from julee_ceap.infrastructure.services.knowledge_service import (
    KnowledgeService,
)

from .pointable_json_schema import PointableJSONSchema

logger = logging.getLogger(__name__)


class ExtractAssembleDataRequest(BaseModel):
    document_id: str
    assembly_specification_id: str


class ExtractAssembleDataResponse(BaseModel):
    assembly: Assembly


class ExtractAssembleDataUseCase:
    """
    Use case for extracting and assembling documents according to
    specifications.

    This class orchestrates the business logic for the "Extract, Assemble"
    phases of the Capture, Extract, Assemble, Publish workflow while remaining
    framework-agnostic. It depends only on repository protocols, not
    concrete implementations.

    In workflow contexts, this use case is called from workflow code with
    repository stubs that delegate to Temporal activities for durability.
    The use case remains completely unaware of whether it's running in a
    workflow context or a simple async context - it just calls repository
    methods and expects them to work correctly.

    Architectural Notes:

    - This class contains pure business logic with no framework dependencies
    - Repository dependencies are injected via constructor
      (dependency inversion)
    - All error handling and compensation logic is contained here
    - The use case works with domain objects exclusively
    - Deterministic execution is guaranteed by avoiding
      non-deterministic operations

    """

    def __init__(
        self,
        document_repo: DocumentRepository,
        assembly_repo: AssemblyRepository,
        assembly_specification_repo: AssemblySpecificationRepository,
        knowledge_service_query_repo: KnowledgeServiceQueryRepository,
        knowledge_service_config_repo: KnowledgeServiceConfigRepository,
        knowledge_service: KnowledgeService,
        schema_oracle: SchemaOracle,
        clock_witness: ClockWitness | None = None,
        execution_witness: ExecutionWitness | None = None,
    ) -> None:
        """Initialize extract and assemble data use case.

        Args:
            document_repo: Repository for document operations
            assembly_repo: Repository for assembly operations
            assembly_specification_repo: Repository for assembly
                specification operations
            knowledge_service_query_repo: Repository for knowledge service
                query operations
            knowledge_service_config_repo: Repository for knowledge service
                configuration operations
            knowledge_service: Knowledge service instance for external
                operations
            schema_oracle: Oracle for fetching a JSON Schema by URL
            clock_witness: Witness for the current time.
                Defaults to SystemClockWitness. Inject TemporalClockWitness
                inside Temporal workflows, where the runtime records what
                it said so a replay is told the same thing.
            execution_witness: Witness for the execution ID.
                Defaults to DefaultExecutionWitness. Inject
                TemporalExecutionWitness inside Temporal workflows.

        .. note::

            The repositories passed here may be concrete implementations
            (for testing or direct execution) or workflow stubs (for
            Temporal workflow execution). The use case doesn't know or care
            which - it just calls the methods defined in the protocols.

            Repositories are validated at construction time to catch
            configuration errors early in the application lifecycle.

        """
        # Validate at construction time for early error detection
        self.document_repo = ensure_repository_protocol(
            document_repo,
            DocumentRepository,  # type: ignore[type-abstract]
        )
        self.knowledge_service = knowledge_service
        self.schema_oracle = ensure_repository_protocol(
            schema_oracle,
            SchemaOracle,  # type: ignore[type-abstract]
        )
        self._clock_witness: ClockWitness = clock_witness or SystemClockWitness()
        self._execution_witness: ExecutionWitness = (
            execution_witness or DefaultExecutionWitness()
        )
        self.assembly_repo = ensure_repository_protocol(
            assembly_repo,
            AssemblyRepository,  # type: ignore[type-abstract]
        )
        self.assembly_specification_repo = ensure_repository_protocol(
            assembly_specification_repo,
            AssemblySpecificationRepository,  # type: ignore[type-abstract]
        )
        self.knowledge_service_query_repo = ensure_repository_protocol(
            knowledge_service_query_repo,
            KnowledgeServiceQueryRepository,  # type: ignore[type-abstract]
        )
        self.knowledge_service_config_repo = ensure_repository_protocol(
            knowledge_service_config_repo,
            KnowledgeServiceConfigRepository,  # type: ignore[type-abstract]
        )

    async def execute(
        self, request: ExtractAssembleDataRequest
    ) -> ExtractAssembleDataResponse:
        assembly = await self.assemble_data(
            request.document_id,
            request.assembly_specification_id,
        )
        return ExtractAssembleDataResponse(assembly=assembly)

    async def assemble_data(
        self,
        document_id: str,
        assembly_specification_id: str,
    ) -> Assembly:
        """
        Assemble a document according to its specification and create a new
        assembly.

        This method orchestrates the core assembly workflow:

        1. Generates a unique assembly ID
        2. Retrieves the assembly specification
        3. Stores the initial assembly in the repository
        4. Retrieves all knowledge service queries needed for the assembly
        5. Retrieves all knowledge service instances needed for the assembly
        6. Retrieves the input document and registers it with knowledge
           services
        7. Performs the assembly iteration to create the assembled document
        8. Adds the iteration to the assembly and returns it

        Args:
            document_id: ID of the document to assemble
            assembly_specification_id: ID of the specification to use

        Returns:
            New Assembly with the assembled document iteration

        Raises:
            ValueError: If required entities are not found or invalid
            RuntimeError: If assembly processing fails

        """
        execution_id = self._execution_witness.get_execution_id()
        logger.debug(
            "Starting data assembly use case",
            extra={
                "document_id": document_id,
                "assembly_specification_id": assembly_specification_id,
                "execution_id": execution_id,
            },
        )

        # Step 1: Generate unique assembly ID
        assembly_id = await self._generate_assembly_id(
            document_id, assembly_specification_id
        )

        # Step 2: Retrieve the assembly specification
        assembly_specification = await self._retrieve_assembly_specification(
            assembly_specification_id
        )

        # Step 3: Store the initial assembly
        now = self._clock_witness.now()
        assembly = Assembly(
            assembly_id=assembly_id,
            assembly_specification_id=assembly_specification_id,
            input_document_id=document_id,
            execution_id=execution_id,
            status=AssemblyStatus.IN_PROGRESS,
            assembled_document_id=None,
            created_at=now,
            updated_at=now,
        )
        await self.assembly_repo.save(assembly)

        logger.debug(
            "Initial assembly stored",
            extra={
                "assembly_id": assembly_id,
                "status": assembly.status.value,
            },
        )

        # Step 4: Retrieve all knowledge service queries once
        queries = await self._retrieve_all_queries(assembly_specification)

        # Step 5: Register the document with knowledge services
        document = await self._retrieve_document(document_id)
        document_registrations = await self._register_document_with_services(
            document, queries
        )

        # Step 7: Perform the assembly iteration
        try:
            assembled_document_id = await self._assemble_iteration(
                document,
                assembly_specification,
                document_registrations,
                queries,
            )

            # Step 8: Set the assembled document and return
            assembly = assembly.model_copy(
                update={
                    "assembled_document_id": assembled_document_id,
                    "status": AssemblyStatus.COMPLETED,
                }
            )
            await self.assembly_repo.save(assembly)

            logger.info(
                "Assembly completed successfully",
                extra={
                    "assembly_id": assembly_id,
                    "assembled_document_id": assembled_document_id,
                },
            )

            return assembly

        except Exception as e:
            # Mark assembly as failed
            assembly = assembly.model_copy(update={"status": AssemblyStatus.FAILED})
            await self.assembly_repo.save(assembly)

            logger.error(
                "Assembly failed",
                extra={
                    "assembly_id": assembly_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    @try_use_case_step("document_registration")
    @validate_parameter_types()
    async def _register_document_with_services(
        self,
        document: Document,
        queries: dict[str, KnowledgeServiceQuery],
    ) -> dict[str, str]:
        """
        Register the document with all knowledge services needed for assembly.

        This is a temporary solution - document registration will be handled
        properly in a separate process later.

        Args:
            document: The document to register
            queries: Dict of query_id to KnowledgeServiceQuery objects

        Returns:
            Dict mapping knowledge_service_id to service_file_id

        Raises:
            RuntimeError: If registration fails

        """
        registrations = {}

        required_service_ids = {
            query.knowledge_service_id for query in queries.values()
        }

        for knowledge_service_id in required_service_ids:
            # Get the config for this service
            config = await self.knowledge_service_config_repo.get(knowledge_service_id)
            if not config:
                raise ValueError(
                    f"Knowledge service config not found: {knowledge_service_id}"
                )

            registration_result = await self.knowledge_service.register_file(
                config, document
            )
            registrations[knowledge_service_id] = (
                registration_result.knowledge_service_file_id
            )

        return registrations

    @try_use_case_step("queries_retrieval")
    async def _retrieve_all_queries(
        self, assembly_specification: AssemblySpecification
    ) -> dict[str, KnowledgeServiceQuery]:
        """Retrieve all knowledge service queries needed for this assembly."""
        query_ids = list(assembly_specification.knowledge_service_queries.values())

        # TODO: TEMPORAL SERIALIZATION ISSUE - Replace with get_many when
        # fixed
        #
        # Issue: Complex return type
        # Dict[str, Optional[KnowledgeServiceQuery]] from get_many causes
        # Temporal's type system to fall back to typing.Any, resulting in
        # Pydantic models being deserialized as plain dictionaries instead of
        # model instances.
        #
        # Error: "SERIALIZATION ISSUE DETECTED: parameter
        # 'queries'['query-id'] is dict instead of KnowledgeServiceQuery!"
        #
        # Root Cause: Temporal's type resolution cannot handle the complex
        # nested generic type Dict[str, Optional[T]] and passes typing.Any to
        # the data converter, which then deserializes to plain dicts.
        #
        # Investigation: Full analysis showed:
        # - Data converter debug output confirming typing.Any fallback
        # - Repository type resolution working correctly
        # - Guard check system detecting the exact issue
        # - Evidence that simpler types (Optional[T]) work fine
        #
        # Temporary Fix: Use individual get() calls which return Optional[T]
        # that Temporal handles correctly.
        #
        # Future Solutions:
        # 1. Fix Temporal's type resolution for complex nested generics
        # 2. Create custom data converter for this specific type pattern
        # 3. Simplify repository interface to avoid Optional in batch
        #    operations
        #
        # Currently using individual get calls to avoid complex type
        # serialization issue
        queries = {}
        for query_id in query_ids:
            query = await self.knowledge_service_query_repo.get(query_id)
            if not query:
                raise ValueError(f"Knowledge service query not found: {query_id}")
            queries[query_id] = query
        return queries

    async def _resolve_jsonschema(self, schema: Mapping[str, Any]) -> dict[str, Any]:
        """Fetch and resolve a bare $ref schema; return inline schemas unchanged.

        If the schema is exactly {"$ref": "url#/fragment"}, fetches the URL via
        the injected schema_oracle (a Temporal activity in workflow context)
        and delegates fragment extraction to extract_schema_from_fetched.
        Re-fetching on every query ensures the latest published version is used.
        """
        if not (len(schema) == 1 and "$ref" in schema):
            return dict(schema)
        url, _, fragment = schema["$ref"].partition("#")
        full_schema = await self.schema_oracle.fetch(url)
        return extract_schema_from_fetched(full_schema, fragment)

    @try_use_case_step("assembly_iteration")
    async def _assemble_iteration(
        self,
        document: Document,
        assembly_specification: AssemblySpecification,
        document_registrations: dict[str, str],
        queries: dict[str, KnowledgeServiceQuery],
    ) -> str:
        """
        Perform a single assembly iteration using knowledge services.

        This method:

        1. Executes all knowledge service queries defined in the specification
        2. Stitches together the query results into a complete JSON document
        3. Creates and stores the assembled document
        4. Returns the ID of the assembled document

        Args:
            document: The input document
            assembly_specification: The specification defining how to assemble
            document_registrations: Mapping of service_id to service_file_id
            queries: Dict of query_id to KnowledgeServiceQuery objects

        Returns:
            ID of the newly created assembled document

        Raises:
            ValueError: If required entities are not found
            RuntimeError: If knowledge service operations fail

        """
        # Initialize the result data structure
        assembled_data: dict[str, Any] = {}

        # Resolve $ref schemas afresh on every query so any published patch
        # to the external schema is picked up automatically.
        resolved_jsonschema = await self._resolve_jsonschema(
            assembly_specification.jsonschema
        )

        # Process each knowledge service query
        # TODO: This is where we may want to fan-out/fan-in to do these
        # in parallel.
        for (
            schema_pointer,
            query_id,
        ) in assembly_specification.knowledge_service_queries.items():
            # Use PointableJSONSchema to generate complete schema for pointer target
            pointable_schema = PointableJSONSchema(resolved_jsonschema)
            output_schema = pointable_schema.schema_for_pointer(schema_pointer)

            # Get the query configuration
            query = queries[query_id]

            # Get the config for this service
            config = await self.knowledge_service_config_repo.get(
                query.knowledge_service_id
            )

            if not config:
                raise ValueError(
                    f"Knowledge service config not found: {query.knowledge_service_id}"
                )

            # Get the service file ID from our registrations
            service_file_id = document_registrations.get(query.knowledge_service_id)
            if not service_file_id:
                raise ValueError(
                    f"Document not registered with service {query.knowledge_service_id}"
                )

            # Execute query with complete schema
            query_result = await self.knowledge_service.execute_query(
                config,
                query.prompt,
                output_schema,
                [service_file_id],
                query.query_metadata,
                query.assistant_prompt,
            )

            # Knowledge service now returns parsed JSON directly
            result_data = query_result.result_data.get("response")
            if result_data is None:
                raise ValueError("Knowledge service returned no response data")
            self._store_result_in_assembled_data(
                assembled_data, schema_pointer, result_data
            )

        # Validate the assembled data against the JSON schema
        self._validate_assembled_data(assembled_data, resolved_jsonschema)

        # Create the assembled document
        assembled_document_id = await self._create_assembled_document(
            assembled_data, assembly_specification
        )

        return assembled_document_id

    @try_use_case_step("assembly_id_generation")
    async def _generate_assembly_id(
        self, document_id: str, assembly_specification_id: str
    ) -> str:
        """Generate a unique assembly ID with consistent error handling."""
        return await self.assembly_repo.generate_id()

    @try_use_case_step("assembly_specification_retrieval")
    async def _retrieve_assembly_specification(
        self, assembly_specification_id: str
    ) -> AssemblySpecification:
        """Retrieve assembly specification with error handling."""
        specification = await self.assembly_specification_repo.get(
            assembly_specification_id
        )
        if not specification:
            raise ValueError(
                f"Assembly specification not found: {assembly_specification_id}"
            )
        return specification

    @try_use_case_step("document_retrieval")
    async def _retrieve_document(self, document_id: str) -> Document:
        """Retrieve document with error handling."""
        document = await self.document_repo.get(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        return document

    def _store_result_in_assembled_data(
        self,
        assembled_data: dict[str, Any],
        schema_pointer: str,
        result_data: Any,
    ) -> None:
        """Store query result in appropriate location in assembled data."""
        if not schema_pointer:
            # Root level - merge the entire result if it's a dict,
            # otherwise store as-is
            if isinstance(result_data, dict):
                assembled_data.update(result_data)
            else:
                # Can't merge non-dict at root level, this would be an error
                raise ValueError("Cannot merge non-dict result data at root level")
        else:
            # Use JSON Pointer to set the data at the correct location
            try:
                # Convert pointer to path components, skipping "properties"
                # wrapper
                path_parts = (
                    schema_pointer.strip("/").split("/")
                    if schema_pointer.strip("/")
                    else []
                )

                # Remove "properties" from path if it exists (schema artifact)
                if path_parts and path_parts[0] == "properties":
                    path_parts = path_parts[1:]

                # If no path parts left, store at root level
                if not path_parts:
                    if isinstance(result_data, dict):
                        assembled_data.update(result_data)
                    else:
                        # Can't merge non-dict at root level, this would be
                        # an error
                        raise ValueError(
                            "Cannot merge non-dict result data at root level"
                        )
                    return

                # Navigate/create the nested structure
                current = assembled_data
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set the final value
                current[path_parts[-1]] = result_data

            except (KeyError, TypeError) as e:
                raise ValueError(
                    f"Cannot store result at schema pointer '{schema_pointer}': {e}"
                )

    @try_use_case_step("assembled_document_creation")
    async def _create_assembled_document(
        self,
        assembled_data: dict[str, Any],
        assembly_specification: AssemblySpecification,
    ) -> str:
        """Create and store the assembled document."""

        # Generate document ID
        document_id = await self.document_repo.generate_id()

        # Convert assembled data to JSON string
        assembled_content = json.dumps(assembled_data, indent=2)
        content_bytes = assembled_content.encode("utf-8")

        now = self._clock_witness.now()
        assembled_document = Document(
            document_id=document_id,
            original_filename=(
                f"assembled_{assembly_specification.name.replace(' ', '_')}.json"
            ),
            content_type="application/json",
            size_bytes=len(content_bytes),
            content_multihash=self._calculate_multihash_from_content(content_bytes),
            status=DocumentStatus.ASSEMBLED,
            content_bytes=content_bytes,
            created_at=now,
            updated_at=now,
        )

        # Save the document
        await self.document_repo.save(assembled_document)

        return document_id

    def _validate_assembled_data(
        self,
        assembled_data: dict[str, Any],
        resolved_jsonschema: dict[str, Any],
    ) -> None:
        """Validate that the assembled data conforms to the JSON schema."""
        try:
            jsonschema.validate(assembled_data, resolved_jsonschema)
            logger.debug("Assembled data validation passed")
        except jsonschema.ValidationError as e:
            logger.error(
                "Assembled data validation failed",
                extra={
                    "validation_error": str(e),
                    "error_path": (list(e.absolute_path) if e.absolute_path else []),
                    "schema_path": (list(e.schema_path) if e.schema_path else []),
                },
            )
            raise ValueError(
                f"Assembled data does not conform to JSON schema: {e.message}"
            )
        except jsonschema.SchemaError as e:
            logger.error(
                "JSON schema is invalid",
                extra={"schema_error": str(e)},
            )
            raise ValueError(
                f"Invalid JSON schema in assembly specification: {e.message}"
            )

    def _calculate_multihash_from_content(self, content_bytes: bytes) -> str:
        """The multihash naming this content."""
        return content_multihash(content_bytes)
