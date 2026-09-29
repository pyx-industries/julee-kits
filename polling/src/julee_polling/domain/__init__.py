"""
Domain layer for the polling contrib module.

This module contains the core domain values, services, and business rules
for the polling contrib module. It defines the fundamental concepts and
protocols that govern polling operations.

No re-exports to avoid import chains that pull non-deterministic code
into Temporal workflows. Import directly from specific modules:

- from julee_polling.domain.values.polling_config import PollingConfig, PollingProtocol, PollingResult
- from julee_polling.domain.oracles.poller import PollerOracle
"""

__all__ = []
