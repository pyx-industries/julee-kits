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
class HttpConnection:
    """Where an HTTP poll goes, and what it sends with the request.

    This was ``connection_params: Mapping[str, Any]``, a bag the HTTP
    poller read ``url``, ``headers`` and ``auth`` out of. The first two
    are named here. ``auth`` was splatted into the httpx call as
    arbitrary keyword arguments and nothing in the estate ever set it;
    a bag inside a bag, and it goes.
    """

    url: str
    """The endpoint to poll."""

    headers: Mapping[str, str] = field(default_factory=dict)
    """Sent with every request, before the header factory adds its own."""


@dataclass(frozen=True)
class HttpPolling:
    """How an HTTP poll asks.

    This was ``polling_params: Mapping[str, Any]``, of which the poller
    read ``method`` and nothing else.
    """

    method: str = "GET"
    """The HTTP method."""


@dataclass(frozen=True)
class PollingConfig:
    """Configuration for a polling operation.

    The two nested values keep the field names the bags had. A config
    is the argument a Temporal schedule starts the pipeline with, so
    every schedule already created carries this shape, and a rename
    would orphan them. The names are the wire; the types are new.
    """

    endpoint_identifier: str
    """Unique identifier for this endpoint."""

    polling_protocol: PollingProtocol
    connection_params: HttpConnection
    """Where to poll and what to send. Required: a poll needs a URL."""
    polling_params: HttpPolling = field(default_factory=HttpPolling)
    """How to ask. Defaults to a GET."""
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
    # FIXME: probably cruft. The HTTP poller fills this with status_code,
    # response_headers, url and method, or error_type on failure, and
    # nothing reads it but the poller's own tests: the use case reads
    # success, content, content_hash and polled_at, and a failure has
    # error_message. It crosses the PollerOracle activity, so the full
    # response headers of every poll are written into Temporal history
    # for no reader. The likely fix is to log them in the adapter (ADR 017)
    # and drop the field; a status code becomes a named field on the day
    # the domain acts on one. Left until a third-party solution is being
    # refactored and can be checked for a reader.
    metadata: Mapping[str, Any] = field(default_factory=dict)
    polled_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    content_hash: str | None = None
    error_message: str | None = None
