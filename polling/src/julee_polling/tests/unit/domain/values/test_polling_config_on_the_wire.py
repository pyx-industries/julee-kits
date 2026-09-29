"""A PollingConfig as a Temporal schedule carries it.

The manager hands the config object itself to the schedule as the
pipeline's argument, so every schedule already created stores it as
JSON in this shape. connection_params and polling_params stopped being
open mappings and became HttpConnection and HttpPolling; the field
names did not change, and this is the test that a schedule written
before still starts the pipeline.
"""

import pytest
from pydantic import TypeAdapter

from julee_polling.domain.values.polling_config import (
    HttpConnection,
    HttpPolling,
    PollingConfig,
    PollingProtocol,
)

pytestmark = pytest.mark.unit

CONFIG = TypeAdapter(PollingConfig)
"""What the pipeline reads a schedule's argument back through."""


class TestAScheduleWrittenBefore:
    """The old dicts, under the old names."""

    def test_a_url_alone_still_loads(self) -> None:
        """What every schedule in the estate was written with."""
        found = CONFIG.validate_python(
            {
                "endpoint_identifier": "api-v1",
                "polling_protocol": "http",
                "connection_params": {"url": "https://api.example.com/data"},
                "polling_params": {},
                "timeout_seconds": 30,
                "scheduling_policy": "allow_overlap",
            }
        )

        assert found.connection_params == HttpConnection(
            url="https://api.example.com/data"
        )
        assert found.polling_params == HttpPolling()

    def test_headers_and_a_method_still_load(self) -> None:
        """The two keys the poller read besides the url."""
        found = CONFIG.validate_python(
            {
                "endpoint_identifier": "api-v1",
                "polling_protocol": "http",
                "connection_params": {
                    "url": "https://api.example.com/data",
                    "headers": {"Authorization": "Bearer t"},
                },
                "polling_params": {"method": "POST"},
            }
        )

        assert found.connection_params.headers == {"Authorization": "Bearer t"}
        assert found.polling_params.method == "POST"

    def test_an_auth_key_is_dropped_rather_than_refused(self) -> None:
        """auth was splatted into httpx and nothing in the estate set it.

        A schedule that did set it keeps loading; the key goes, and the
        request is made without it. Refusing the schedule would stop a
        poll that has been running, over a key nothing honoured.
        """
        found = CONFIG.validate_python(
            {
                "endpoint_identifier": "api-v1",
                "polling_protocol": "http",
                "connection_params": {
                    "url": "https://api.example.com/data",
                    "auth": {"token": "x"},
                },
            }
        )

        assert found.connection_params == HttpConnection(
            url="https://api.example.com/data"
        )

    def test_it_writes_the_same_shape_it_reads(self) -> None:
        """So a schedule created now looks like one created before."""
        config = PollingConfig(
            endpoint_identifier="api-v1",
            polling_protocol=PollingProtocol.HTTP,
            connection_params=HttpConnection(url="https://api.example.com/data"),
        )

        written = CONFIG.dump_python(config, mode="json")

        assert written["connection_params"] == {
            "url": "https://api.example.com/data",
            "headers": {},
        }
        assert written["polling_params"] == {"method": "GET"}
        assert CONFIG.validate_python(written) == config


class TestWhatAPollNeeds:
    """A poll without a URL is not a poll."""

    def test_a_config_without_a_url_is_refused(self) -> None:
        """It was a bag with a default of {}, and the poller raised
        KeyError on the first request. Now the config refuses."""
        with pytest.raises(ValueError):
            CONFIG.validate_python(
                {
                    "endpoint_identifier": "api-v1",
                    "polling_protocol": "http",
                    "connection_params": {},
                }
            )
