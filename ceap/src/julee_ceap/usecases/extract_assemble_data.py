"""
Use case logic for data assembly within the Capture, Extract, Assemble,
Publish workflow.

This module contains use case classes that orchestrate business logic while
remaining framework-agnostic. Dependencies are injected via repository
instances following the Clean Architecture principles.
"""

from dataclasses import replace
from typing import Any

from julee.core.usecases.decorators import try_use_case_step
from julee.core.validation import ensure_repository_protocol, validate_parameter_types
from julee.core.values.text import NonEmptyText
from julee.core.witnesses import ClockWitness, ExecutionWitness, SystemClockWitness
from julee.core.witnesses.execution import DefaultExecutionWitness

from julee_ceap.domain.calculators.schema import SchemaCalculator
from julee_ceap.domain.models import (
    Assembly,
    AssemblySpecification,
    AssemblyStatus,
    Document,
    DocumentStatus,
    KnowledgeServiceQuery,
)
from julee_ceap.domain.oracles import SchemaOracle
from julee_ceap.domain.repositories import (
    AssemblyRepository,
    AssemblySpecificationRepository,
    DocumentRepository,
    KnowledgeServiceConfigRepository,
    KnowledgeServiceQueryRepository,
)
from julee_ceap.domain.services.knowledge_service import (
    KnowledgeService,
)
from julee_ceap.domain.values.multihash import (
    content_multihash,
)
from julee_ceap.domain.values.schema import AssembledData, JsonSchema

from ..dtos.extract_assemble_data import (
    ExtractAssembleDataRequest,
    ExtractAssembleDataResponse,
)


class ExtractAssembleDataUseCase:
    """
    Use case for extracting and assembling documents according to
    specifications.

    This class orchestrates the business logic for the "Extract, Assemble"
    phases of the Capture, Extract, Assemble, Publish workflow while remaining
    framework-agnostic. It depends only on repository protocols, not
    concrete implementations.

    The repositories and services are whatever the composition root hands
    in. The use case does not know what stands behind them - it just calls
    the methods the ports promise, and a durable runtime or a plain async
    one is the caller's business. It just calls repository
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
        schema_calculator: SchemaCalculator,
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
            schema_calculator: Reads a schema: the part a pointer names,
                the part a $ref fragment names, and whether assembled
                data fits
            clock_witness: Witness for the current time. Defaults to
                SystemClockWitness; a composition root whose runtime
                replays injects the witness that runtime provides.
            execution_witness: Witness for the execution ID. Defaults to
                DefaultExecutionWitness; likewise the runtime's.

        .. note::

            The repositories passed here may be concrete implementations
            (for testing or direct execution) or stubs that reach a durable
            runtime. The use case doesn't know or care
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
        self.schema_calculator = schema_calculator
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
        return ExtractAssembleDataResponse.of(assembly)

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
            assembly_id=NonEmptyText(assembly_id),
            assembly_specification_id=NonEmptyText(assembly_specification_id),
            input_document_id=NonEmptyText(document_id),
            execution_id=NonEmptyText(execution_id),
            status=AssemblyStatus.IN_PROGRESS,
            assembled_document_id=None,
            created_at=now,
            updated_at=now,
        )
        await self.assembly_repo.save(assembly)

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
            assembly = replace(
                assembly,
                assembled_document_id=NonEmptyText(assembled_document_id),
                status=AssemblyStatus.COMPLETED,
            )
            await self.assembly_repo.save(assembly)

            return assembly

        except Exception:
            # Mark assembly as failed
            assembly = replace(assembly, status=AssemblyStatus.FAILED)
            await self.assembly_repo.save(assembly)

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
        registrations: dict[str, str] = {}

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
                config, document, await self.document_repo.content_of(document)
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
        # As plain strs: the port takes list[str], and to mypy a list of
        # the checked kind is not one, whatever each element is.
        query_ids = [
            str(query_id)
            for query_id in assembly_specification.knowledge_service_queries.values()
        ]
        found = await self.knowledge_service_query_repo.get_many(query_ids)
        missing = [query_id for query_id in query_ids if found.get(query_id) is None]
        if missing:
            raise ValueError(f"Knowledge service query not found: {missing[0]}")
        return {
            query_id: query
            for query_id in query_ids
            if (query := found[query_id]) is not None
        }

    async def _resolve_jsonschema(self, schema: JsonSchema) -> JsonSchema:
        """Fetch and resolve a bare $ref schema; return inline schemas unchanged.

        Re-fetching on every query ensures the latest published version is
        used. Navigating to the fragment is the calculator's, because it
        is the same reading of a schema that the rest of this use case
        asks for and it does no I/O.
        """
        if not schema.is_a_bare_ref:
            return schema
        url, _, fragment = schema.ref.partition("#")
        fetched = await self.schema_oracle.fetch(url)
        return self.schema_calculator.schema_at_fragment(fetched, fragment)

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
            output_schema = self.schema_calculator.schema_for_pointer(
                resolved_jsonschema, schema_pointer
            )

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

            if query_result.data is None:
                raise ValueError(
                    "Knowledge service answered without the structured data a "
                    "schema-directed query asks for"
                )
            self._store_result_in_assembled_data(
                assembled_data, schema_pointer, query_result.data.value
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

        # Store the content, then name it: the multihash comes back
        # from the store rather than being computed here. Writing the
        # data as JSON is the value's own business, so this does not
        # import json to ask.
        content_bytes = AssembledData(assembled_data).as_json_bytes()
        stored = await self.document_repo.store_content(content_bytes)

        now = self._clock_witness.now()
        assembled_document = Document(
            document_id=NonEmptyText(document_id),
            original_filename=(
                NonEmptyText(
                    f"assembled_{assembly_specification.name.replace(' ', '_')}.json"
                )
            ),
            content_type=NonEmptyText("application/json"),
            size_bytes=len(content_bytes),
            content_multihash=stored,
            status=DocumentStatus.ASSEMBLED,
            created_at=now,
            updated_at=now,
        )

        # Save the document
        await self.document_repo.save(assembled_document)

        return document_id

    def _validate_assembled_data(
        self,
        assembled_data: dict[str, Any],
        resolved_jsonschema: JsonSchema,
    ) -> None:
        """Refuse assembled data that does not fit the schema.

        The check, the two libraries it needs and the messages it raises
        are the calculator's. What is left here is the decision to make
        it, which is the use case's.
        """
        self.schema_calculator.refuse_data_that_does_not_fit(
            AssembledData(assembled_data), resolved_jsonschema
        )

    def _calculate_multihash_from_content(self, content_bytes: bytes) -> str:
        """The multihash naming this content."""
        return content_multihash(content_bytes)
