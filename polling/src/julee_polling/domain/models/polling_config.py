"""
Polling domain models.

This module contains the core domain models for polling operations,
including configuration and result models.
"""

from collections.abc import Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from julee.core.entities.entity import Entity
from pydantic import Field


class PollingProtocol(StrEnum):
    """Supported polling protocols."""

    HTTP = "http"


class SchedulingPolicy(StrEnum):
    """Scheduling policy for polling operations."""

    ALLOW_OVERLAP = "allow_overlap"
    SKIP_IF_RUNNING = "skip_if_running"


class PollingConfig(Entity):
    """Configuration for a polling operation."""

    endpoint_identifier: str = Field(description="Unique identifier for this endpoint")
    polling_protocol: PollingProtocol
    connection_params: Mapping[str, Any] = Field(default_factory=dict)
    polling_params: Mapping[str, Any] = Field(default_factory=dict)
    timeout_seconds: int | None = Field(default=30)
    scheduling_policy: SchedulingPolicy = Field(
        default=SchedulingPolicy.ALLOW_OVERLAP,
        description="Policy for handling overlapping polling operations",
    )


class PollingResult(Entity):
    """Result of a polling operation."""

    success: bool
    content: bytes
    metadata: Mapping[str, Any] = Field(default_factory=dict)
    polled_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    content_hash: str | None = None
    error_message: str | None = None
