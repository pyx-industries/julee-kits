"""
PollerOracle protocol for external endpoint polling operations.

This module defines the PollerOracle protocol that handles interactions
with various types of external endpoints for data polling and change detection.

Concrete implementations of this protocol are provided for different polling
mechanisms and are created via factory functions.
"""

from typing import Protocol, runtime_checkable

from ..values.polling_config import PollingConfig, PollingResult


@runtime_checkable
class PollerOracle(Protocol):
    """Polls an external endpoint and says what came back.

    An oracle, not a service. It was a PollerService, and ADR 016 asks a
    service to be bound to two or more of this context's entities — this
    one is bound to none: a PollingConfig and a PollingResult are both
    values (ADR 018), and polling keeps no entities at all.

    Bound to no entity and reached through an activity is what an oracle
    is. It performs I/O and its answer can differ between replays, so
    workflow code must not call it inline.
    """

    async def poll_endpoint(self, config: PollingConfig) -> PollingResult:
        """
        Poll an endpoint according to the provided configuration.

        Args:
            config: PollingConfig containing endpoint details and parameters

        Returns:
            PollingResult with success status, content, and metadata

        Raises:
            PollingError: When polling operation fails
        """
        ...
