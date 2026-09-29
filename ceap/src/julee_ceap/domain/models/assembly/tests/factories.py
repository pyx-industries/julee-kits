"""
Test factories for Assembly domain objects using factory_boy.

This module provides factory_boy factories for creating test instances of
Assembly domain objects with sensible defaults.
"""

import uuid
from datetime import UTC, datetime

from factory.base import Factory
from factory.declarations import LazyFunction
from julee.core.values.text import NonEmptyText

from julee_ceap.domain.models.assembly import (
    Assembly,
    AssemblyStatus,
)


class AssemblyFactory(Factory):
    """Factory for creating Assembly instances with sensible test defaults."""

    class Meta:
        model = Assembly

    # Core assembly identification
    assembly_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))
    assembly_specification_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))
    input_document_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))
    execution_id = LazyFunction(lambda: NonEmptyText(str(uuid.uuid4())))

    # Assembly process tracking
    status = AssemblyStatus.PENDING
    assembled_document_id = None

    # Timestamps
    created_at = LazyFunction(lambda: datetime.now(UTC))
    updated_at = LazyFunction(lambda: datetime.now(UTC))
