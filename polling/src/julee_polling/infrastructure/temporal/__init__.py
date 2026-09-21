"""
Temporal integration for the polling contrib module.

This module provides the Temporal integration layer for polling operations,
including workflow proxies for calling polling activities from workflows and
activity name constants.

This keeps all polling-temporal integration within the contrib module,
maintaining proper dependency direction (contrib imports from core, not vice versa).

No re-exports to avoid import chains that pull non-deterministic code
into Temporal workflows. Import directly from specific modules:

- from julee_polling.infrastructure.temporal.activity_names import POLLING_SERVICE_ACTIVITY_BASE
- from julee_polling.infrastructure.temporal.manager import PollingManager
- from julee_polling.infrastructure.temporal.proxies import WorkflowPollerServiceProxy
- from julee_polling.infrastructure.temporal.activities import TemporalPollerService
"""

__all__ = []
