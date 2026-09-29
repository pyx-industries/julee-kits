"""What PollDataUseCase promises, asked directly.

Every other test of this use case runs it inside a Temporal workflow,
which exercises it but can only see what the pipeline chooses to put in
its completion dict. Its own contract is asked here, with the three
ports stood in for, so what it reports can be read whole.
"""

from datetime import UTC, datetime

import pytest
from julee.core.entities.acknowledgement import Acknowledgement

from julee_polling.domain.values.handoff import Handoff
from julee_polling.domain.values.polling_config import (
    HttpConnection,
    PollingConfig,
    PollingProtocol,
    PollingResult,
)
from julee_polling.dtos.poll_data import PollDataRequest
from julee_polling.usecases.poll_data import PollDataUseCase

pytestmark = pytest.mark.unit

CONTENT = b"what the endpoint said"
HASH = "a-hash"


def a_config() -> PollingConfig:
    """The endpoint under test."""
    return PollingConfig(
        endpoint_identifier="test-api",
        polling_protocol=PollingProtocol.HTTP,
        connection_params=HttpConnection(url="https://api.example.com/data"),
    )


def a_result(
    *,
    success: bool = True,
    content: bytes = CONTENT,
    content_hash: str | None = HASH,
) -> PollingResult:
    """What the poller came back with."""
    return PollingResult(
        success=success,
        content=content,
        content_hash=content_hash,
        polled_at=datetime.now(UTC),
    )


class FakePoller:
    """A PollerOracle returning whatever it was built with."""

    def __init__(self, result: PollingResult) -> None:
        self._result = result

    async def poll_endpoint(self, config: PollingConfig) -> PollingResult:
        return self._result


class FakeCalculator:
    """A NewDataCalculator returning a fixed set of items, or raising."""

    def __init__(self, item_ids: list[str], raises: Exception | None = None) -> None:
        self._item_ids = item_ids
        self._raises = raises

    async def identify_new_items(
        self, previous_data: bytes | None, new_data: bytes
    ) -> list[str]:
        if self._raises:
            raise self._raises
        return self._item_ids


class FakeHandler:
    """A PollingResultHandler that records, answers, or refuses."""

    def __init__(
        self,
        acknowledgement: Acknowledgement | None = None,
        raises: Exception | None = None,
    ) -> None:
        self.calls: list[tuple[str, list[str], str]] = []
        self._acknowledgement = acknowledgement or Acknowledgement.wilco()
        self._raises = raises

    async def handle_new_data(
        self, endpoint_id: str, new_item_ids: list[str], content_hash: str
    ) -> Acknowledgement:
        self.calls.append((endpoint_id, new_item_ids, content_hash))
        if self._raises:
            raise self._raises
        return self._acknowledgement


def a_use_case(
    result: PollingResult,
    handler: FakeHandler | None = None,
    calculator: FakeCalculator | None = None,
) -> tuple[PollDataUseCase, FakeHandler]:
    """The use case with its three ports stood in for."""
    handler = handler or FakeHandler()
    # No casts: the ports are Protocols and these satisfy them
    # structurally, which is the whole reason a port is a Protocol.
    return (
        PollDataUseCase(
            poller=FakePoller(result),
            handler=handler,
            calculator=calculator or FakeCalculator(["one"]),
        ),
        handler,
    )


class TestNothingToHandOver:
    """The cases where nobody is put under an obligation."""

    async def test_a_failed_poll_tells_nobody(self) -> None:
        """A poll that failed saw nothing, whatever else it came back with.

        The hash is deliberately set here: an adapter that leaves a
        stale one behind must not be read as having seen something.
        Without this the success check is indistinguishable from the
        hash check, and either could be deleted unnoticed.
        """
        use_case, handler = a_use_case(a_result(success=False, content_hash=HASH))

        response = await use_case.execute(PollDataRequest(config=a_config()))

        assert response.handoff is Handoff.NOT_NEEDED
        assert response.polled_successfully is False
        assert handler.calls == []

    async def test_a_poll_with_no_hash_tells_nobody(self) -> None:
        """Nothing to compare with is nothing to report.

        A previous hash is given deliberately. Without one the
        comparison below would find None equal to None and stop there
        anyway, so the guard could be deleted and this would not
        notice.
        """
        use_case, handler = a_use_case(a_result(content_hash=None))

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.handoff is Handoff.NOT_NEEDED
        assert handler.calls == []

    async def test_unchanged_content_tells_nobody(self) -> None:
        """The same content is not new."""
        use_case, handler = a_use_case(a_result())

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash=HASH)
        )

        assert response.handoff is Handoff.NOT_NEEDED
        assert response.new_items_found is False
        assert handler.calls == []


class TestHandingOver:
    """What is reported when the handler was told."""

    async def test_new_content_is_handed_over(self) -> None:
        """Changed content puts the poller under an obligation."""
        use_case, handler = a_use_case(
            a_result(), calculator=FakeCalculator(["one", "two"])
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.handoff is Handoff.DISCHARGED
        assert handler.calls == [("test-api", ["one", "two"], HASH)]

    async def test_it_reports_how_many_it_handed_over(self) -> None:
        """What was notified, which is all the use case can know.

        Not how many were processed: that is the handler's business and
        the acknowledgement deliberately does not say.
        """
        use_case, _ = a_use_case(
            a_result(), calculator=FakeCalculator(["one", "two", "three"])
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.items_notified == 3

    async def test_what_the_handler_said_comes_back(self) -> None:
        """The acknowledgement's only payload."""
        use_case, _ = a_use_case(
            a_result(),
            handler=FakeHandler(Acknowledgement.wilco(info=["queued for ingest"])),
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.handoff_info == ("queued for ingest",)

    async def test_a_refusal_still_discharged_the_obligation(self) -> None:
        """Unable is an answer from someone who was told.

        What they do about it is theirs; the poller notified them, which
        is the whole of what it owed.
        """
        use_case, _ = a_use_case(
            a_result(), handler=FakeHandler(Acknowledgement.unable(info=["full"]))
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.handoff is Handoff.DISCHARGED
        assert response.handoff_info == ("full",)


class TestTheHandoffFailing:
    """Nobody was told, so the obligation stands."""

    async def test_a_handler_that_raises_did_not_discharge_it(self) -> None:
        """Raising is not an answer."""
        use_case, _ = a_use_case(
            a_result(), handler=FakeHandler(raises=RuntimeError("queue is down"))
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.handoff is Handoff.FAILED

    async def test_the_reason_travels_with_it(self) -> None:
        """So whoever writes it down has something to write."""
        use_case, _ = a_use_case(
            a_result(), handler=FakeHandler(raises=RuntimeError("queue is down"))
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert "queue is down" in response.handoff_info[0]

    async def test_a_calculator_that_raises_fails_the_handoff_too(self) -> None:
        """Nothing was worked out, so nothing was handed over."""
        use_case, handler = a_use_case(
            a_result(), calculator=FakeCalculator([], raises=ValueError("bad payload"))
        )

        response = await use_case.execute(
            PollDataRequest(config=a_config(), previous_hash="something-else")
        )

        assert response.handoff is Handoff.FAILED
        assert handler.calls == []
