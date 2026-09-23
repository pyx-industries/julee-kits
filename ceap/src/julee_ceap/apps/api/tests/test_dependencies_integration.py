"""Dependency wiring against real infrastructure.

Separate from test_dependencies.py because these need a MinIO at
MINIO_ENDPOINT. That module marks everything unit, and a test that opens
a socket does not belong under that mark.
"""

import pytest

from julee_ceap.apps.api.dependencies import get_startup_dependencies

pytestmark = pytest.mark.integration


class TestStartupDependenciesIntegration:
    """The dependency chain built against what is actually running."""

    @pytest.mark.asyncio
    async def test_end_to_end_dependency_creation(self) -> None:
        """The dependency chain builds against real infrastructure.

        This reaches MINIO_ENDPOINT, so it is an integration test. It was
        marked unit, and swallowed any failure so long as the message
        mentioned minio or a connection — which made it a test of
        whatever happened to be listening on localhost:9000. With nothing
        there, the connection error matched and it passed; with a MinIO
        that has other credentials, InvalidAccessKeyId reached the
        assertion and failed it.
        """
        provider = await get_startup_dependencies()

        service = await provider.get_system_initialization_service()

        assert service is not None
        assert hasattr(service, "initialize")
        assert hasattr(service, "get_initialization_status")
        assert hasattr(service, "reinitialize")
