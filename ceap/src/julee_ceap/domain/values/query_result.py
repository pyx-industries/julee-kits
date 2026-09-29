"""What a knowledge service answers with.

Records, not ports. Both sat in the module that declares the
KnowledgeService protocol, and when that protocol moved into
``domain/services/`` — where a driven port belongs — doctrine read these
two as ports too, because everything in that directory is one.

They are what the port hands back, so they belong here with the rest of
what this context deals in.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class StructuredAnswer:
    """An answer that was asked to fit a schema, as the JSON it came as.

    Held as text and parsed on the way out. The precise type of a parsed
    JSON value is recursive, and neither Python 3.11 nor pydantic will
    carry one across a dataclass field without help from outside the
    language. The text is exact, serialises as itself, and says what it
    is; ``value`` is where the openness lives, in one place with a name.

    A query that asked for no schema has no structured answer, which is
    ``QueryResult.data`` being None. A structured answer that is JSON
    ``null`` is a StructuredAnswer whose text is ``null``. The two are
    different things and stay different.
    """

    text: str
    """The JSON, as the service wrote it."""

    def __post_init__(self) -> None:
        """Refuse text that is not JSON.

        An answer that was asked to fit a schema and does not even parse
        is not a structured answer, and the place to find that out is
        where it is built.
        """
        try:
            json.loads(self.text)
        except json.JSONDecodeError as not_json:
            raise ValueError(
                f"A structured answer must be JSON, got: {self.text[:100]}"
            ) from not_json

    @property
    def value(self) -> object:
        """The answer, parsed: a JSON value, which the caller looks at."""
        return json.loads(self.text)

    @classmethod
    def of(cls, value: object) -> "StructuredAnswer":
        """The structured answer for a value already in hand.

        For tests and doubles. A real service answers with text.

        Args:
            value: Anything json.dumps can write

        Returns:
            The answer, as the JSON that value is
        """
        return cls(json.dumps(value))


@dataclass(frozen=True)
class QueryResult:
    """Result of a knowledge service query execution."""

    query_id: str
    """Unique identifier for this query execution."""

    query_text: str
    """The original query text that was executed."""

    answer: str
    """What the service said, verbatim."""

    data: StructuredAnswer | None = None
    """The answer parsed, when a schema was asked for; None when none was.

    This and ``answer`` were one ``result_data: Mapping[str, Any]``, a
    bag the use cases read ``response`` out of and the adapters filled
    with what model was used, what it cost and why it stopped. Those are
    the adapter's own events and go to its log (ADR 017); what the domain
    is told is what was answered.
    """

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
