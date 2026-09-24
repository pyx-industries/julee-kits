"""Polling: watch an external endpoint for new data.

A julee kit. It provides the domain model for a polling schedule, the
service protocols a poller implements, an HTTP poller, and a Temporal
pipeline that runs the whole thing durably.

Install it, then adopt it::

    [tool.julee]
    kits = ["polling"]

Example usage:
    from julee_polling.domain.models.polling_config import (
        PollingConfig,
        PollingProtocol,
    )
    from julee_polling.infrastructure.services.polling.http import HttpPollerService
    # Configure polling
    config = PollingConfig(
        endpoint_identifier="api-v1",
        polling_protocol=PollingProtocol.HTTP,
        connection_params={"url": "https://api.example.com/data"},
        timeout_seconds=30
    )

    # Poll the endpoint
    service = HttpPollerService()
    result = await service.poll_endpoint(config)

Note: All imports must be explicit to avoid import chains that can pull
non-deterministic code into Temporal workflows. Import directly from
the specific modules you need rather than using this convenience module.
"""

from julee.core.entities.kit import Kit

# No re-exports to avoid import chains that pull non-deterministic code
# into Temporal workflows. Import from specific submodules instead:
#
# Domain:
# - from julee_polling.domain.models.polling_config import PollingConfig, PollingProtocol, PollingResult
# - from julee_polling.domain.services.poller import PollerService
#
# Infrastructure:
# - from julee_polling.infrastructure.services.polling.http import HttpPollerService
# - from julee_polling.infrastructure.temporal.manager import PollingManager
# - from julee_polling.infrastructure.temporal.proxies import WorkflowPollerServiceProxy
# - from julee_polling.infrastructure.temporal.activities import TemporalPollerService

kit = Kit(
    slug="polling",
    name="Polling",
    package="julee_polling",
    contributes={
        "temporal.pipelines": "julee_polling.apps.worker.pipelines",
        "temporal.activities": (
            "julee_polling.infrastructure.temporal.activities:ACTIVITY_CLASSES"
        ),
    },
)

__all__ = ["kit"]
