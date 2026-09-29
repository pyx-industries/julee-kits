"""What a knowledge service answers with.

Records, not ports. Both sat in the module that declares the
KnowledgeService protocol, and when that protocol moved into
``domain/services/`` — where a driven port belongs — doctrine read these
two as ports too, because everything in that directory is one.

They are what the port hands back, so they belong here with the rest of
what this context deals in.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class QueryResult:
    """Result of a knowledge service query execution."""

    query_id: str
    """Unique identifier for this query execution."""

    query_text: str
    """The original query text that was executed."""

    result_data: Mapping[str, Any] = field(default_factory=dict)
    """The structured result data from the query."""

    execution_time_ms: int | None = None
    """Time taken to execute the query in milliseconds."""

    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class FileRegistrationResult:
    """Result of registering a file with a knowledge service."""

    document_id: str
    """The original document ID from our system."""

    knowledge_service_file_id: str
    """The file identifier assigned by the knowledge service."""

    registration_metadata: Mapping[str, Any] = field(default_factory=dict)
    """Additional metadata from the registration process."""

    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
