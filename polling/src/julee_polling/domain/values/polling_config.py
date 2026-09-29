"""What a poll is configured with, and what it comes back with.

Both are frozen dataclasses: the domain ring holds no pydantic, and both
cross a driven port, which speaks nothing else.

Both are values. Nothing keeps a PollingResult — it is what one poll came
back with, and a second poll of the same endpoint is a different result
rather than an update to this one (ADR 018).
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class PollingProtocol(StrEnum):
    """Supported polling protocols."""

    HTTP = "http"


class SchedulingPolicy(StrEnum):
    """Scheduling policy for polling operations."""

    ALLOW_OVERLAP = "allow_overlap"
    SKIP_IF_RUNNING = "skip_if_running"


@dataclass(frozen=True)
class PollingConfig:
    """Configuration for a polling operation."""

    endpoint_identifier: str
    """Unique identifier for this endpoint."""

    polling_protocol: PollingProtocol
    connection_params: Mapping[str, Any] = field(default_factory=dict)
    polling_params: Mapping[str, Any] = field(default_factory=dict)
    timeout_seconds: int | None = 30

    scheduling_policy: SchedulingPolicy = SchedulingPolicy.ALLOW_OVERLAP
    """Policy for handling overlapping polling operations."""


@dataclass(frozen=True)
class PollingResult:
    """Result of a polling operation.

    ``content_hash`` is set by whoever fetched the content, which is
    the only party that saw the bytes before anything else touched
    them. It is None when the poll did not succeed.
    """

    success: bool
    content: bytes
    metadata: Mapping[str, Any] = field(default_factory=dict)
    polled_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    content_hash: str | None = None
    error_message: str | None = None
