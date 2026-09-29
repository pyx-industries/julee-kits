"""
AssemblySpecification domain models for the Capture, Extract, Assemble,
Publish workflow.

This module contains the AssemblySpecification domain object that represents
assembly configurations in the CEAP workflow system.

An AssemblySpecification defines a type of document output (like "meeting
minutes"), includes information about its applicability and and specifies
which extractors are needed to collect the data for that output.

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import jsonpointer
import jsonschema
from julee.core.values.text import Name, NonEmptyText

from julee_ceap.domain.values.schema import JsonSchema


class AssemblySpecificationStatus(StrEnum):
    """Status of an assembly specification configuration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


@dataclass(frozen=True, kw_only=True)
class AssemblySpecification:
    """Assembly specification configuration that defines how to assemble
    documents of a specific type.

    An AssemblySpecification represents a type of document output (like
    "meeting minutes", "project report", etc.) and defines which extractors
    should be used to collect the necessary data from source documents.

    The AssemblySpecification does not contain the template itself - templates
    will be handled separately during the assembly rendering (or publishing?)
    phase. This separation allows the same AssemblySpecification definition to
    be used with different templates over time.
    """

    # Core assembly identification
    assembly_specification_id: NonEmptyText
    """Unique identifier for this assembly specification."""
    name: Name
    """Human-readable name like 'meeting minutes'."""
    applicability: NonEmptyText
    """Text description identifying to what type of information this assembly applies, such as an online transcript of a video meeting. This information may be used by knowledge service for document-assembly matching."""

    jsonschema: JsonSchema
    """JSON Schema defining the structure of data to be extracted for this assembly."""

    # AssemblySpecification configuration
    status: AssemblySpecificationStatus = AssemblySpecificationStatus.ACTIVE
    knowledge_service_queries: Mapping[str, NonEmptyText] = field(default_factory=dict)
    """Mapping from JSON Pointer paths to KnowledgeServiceQuery IDs. Keys are JSON Pointer strings (e.g., '/properties/attendees', '') and values are query IDs for extracting data for that schema section."""

    # AssemblySpecification metadata
    version: NonEmptyText = NonEmptyText("0.1.0")
    """Assembly definition version."""
    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    # May later add a detailed description, change log, additional metadata
    # Timestamps

    def __post_init__(self) -> None:
        """Check the schema, then the pointers into it.

        These were two field_validator methods. Order matters and used
        to be implicit in the field order: the pointer check reads the
        schema beside it, which pydantic supplied through info.data. It
        says so directly now.

        Raises:
            ValueError: If the schema or any pointer into it is bad
        """
        refuse_a_bad_schema(self.jsonschema.document)
        refuse_a_bad_pointer(self.knowledge_service_queries, self.jsonschema.document)


def refuse_a_bad_schema(v: Mapping[str, Any]) -> None:
    """The schema is a JSON Schema, or a bare $ref to one.

    Args:
        v: The schema as given

    Raises:
        ValueError: If it is neither
    """
    if not isinstance(v, dict):
        raise ValueError("JSON Schema must be a dictionary")

    if len(v) == 1 and "$ref" in v:
        # Bare $ref — accept as-is. Resolution and schema validation
        # happen at assembly time via SchemaOracle, not here.
        if not isinstance(v["$ref"], str) or not v["$ref"].strip():
            raise ValueError("$ref value must be a non-empty string")
        return

    if "type" not in v:
        raise ValueError("JSON Schema must have a 'type' field")

    try:
        jsonschema.Draft7Validator.check_schema(v)
    except jsonschema.SchemaError as e:
        raise ValueError(f"Invalid JSON Schema: {e.message}")


def refuse_a_bad_pointer(
    v: Mapping[str, NonEmptyText], jsonschema_value: Mapping[str, Any]
) -> None:
    """Every key must be a JSON Pointer into this spec's schema.

    A rule, and one no type can carry: whether a pointer resolves
    depends on the jsonschema field beside it. The part that was a
    normalisation — stripping each query id, and rebuilding the
    mapping to hold the stripped ones — is NonEmptyText's now
    (#306).

    The keys stay plain str. An empty pointer is the root of the
    schema and legitimate, so NonEmptyText would refuse a valid one.
    """
    if not isinstance(v, dict):
        raise ValueError("Knowledge service queries must be a dictionary")

    if not jsonschema_value:
        raise ValueError("Cannot validate schema pointers without jsonschema field")

    is_ref_schema = (
        isinstance(jsonschema_value, dict)
        and len(jsonschema_value) == 1
        and "$ref" in jsonschema_value
    )

    for schema_pointer in v:
        # Validate JSON Pointer format; existence against the resolved
        # schema is only possible for inline schemas (not bare $refs —
        # those are resolved at assembly time via SchemaOracle).
        try:
            if schema_pointer == "":
                # Empty string is valid - refers to root of schema
                pass
            elif is_ref_schema:
                # Format validation only — can't check existence without
                # fetching the remote schema
                jsonpointer.JsonPointer(schema_pointer)
            else:
                ptr = jsonpointer.JsonPointer(schema_pointer)
                ptr.resolve(jsonschema_value)
        except jsonpointer.JsonPointerException as e:
            raise ValueError(f"Invalid JSON Pointer '{schema_pointer}': {e}")
        except (KeyError, IndexError, TypeError):
            raise ValueError(
                f"JSON Pointer '{schema_pointer}' does not exist in schema"
            )
