"""
Test factories for AssemblySpecification domain objects using factory_boy.

This module provides factory_boy factories for creating test instances of
AssemblySpecification domain objects with sensible defaults.
"""

import uuid
from datetime import UTC, datetime

from factory.base import Factory
from factory.declarations import LazyAttribute, LazyFunction
from julee.core.values.text import Name, NonEmptyText

from julee_ceap.domain.models.assembly_specification import (
    AssemblySpecification,
    AssemblySpecificationStatus,
    KnowledgeServiceQuery,
)
from julee_ceap.domain.values.schema import JsonSchema


class AssemblyFactory(Factory):
    """Factory for creating AssemblySpecification instances with sensible
    test defaults."""

    class Meta:
        model = AssemblySpecification

    # Core assembly identification
    assembly_specification_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))
    name = Name("Test Assembly")
    applicability = NonEmptyText("Test documents for automated testing purposes")

    # Valid JSON Schema for testing
    @LazyAttribute
    def jsonschema(self) -> JsonSchema:
        return JsonSchema(
            {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "author": {"type": "string"},
                            "created_date": {"type": "string", "format": "date"},
                        },
                    },
                },
                "required": ["title"],
            }
        )

    # Assembly configuration
    status = AssemblySpecificationStatus.ACTIVE
    version = NonEmptyText("0.1.0")

    # Timestamps
    created_at = LazyFunction(lambda: datetime.now(UTC))
    updated_at = LazyFunction(lambda: datetime.now(UTC))


class KnowledgeServiceQueryFactory(Factory):
    """Factory for creating KnowledgeServiceQuery instances with sensible
    test defaults."""

    class Meta:
        model = KnowledgeServiceQuery

    # Core query identification
    query_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))
    name = Name("Test Knowledge Service Query")

    # Knowledge service configuration
    knowledge_service_id = NonEmptyText("test-knowledge-service")
    prompt = NonEmptyText("Extract test data from the document")

    # Timestamps
    created_at = LazyFunction(lambda: datetime.now(UTC))
    updated_at = LazyFunction(lambda: datetime.now(UTC))
