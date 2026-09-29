"""PollDataUseCase — poll an endpoint and report what was found.

Polls, compares what came back against what was seen last time, and
tells the handler when there is something new. It knows nothing of
Temporal, workflows or where the previous run was stored.

It also decides nothing. Whether a poll counts as done is the caller's
call; this reports what happened and lets the caller make it.
"""

from julee_polling.domain.calculators.new_data import NewDataCalculator
from julee_polling.domain.handlers.polling_result_handler import (
    PollingResultHandler,
)
from julee_polling.domain.oracles.poller import PollerOracle
from julee_polling.domain.values.handoff import Handoff
from julee_polling.domain.values.polling_config import PollingResult
from julee_polling.dtos.poll_data import PollDataRequest, PollDataResponse


class PollDataUseCase:
    """Poll an endpoint, detect new data, and notify the handler.

    The handler is the role that must be told when there is new data.
    Which thing fills that role — an ingester, a router that fans out
    to several, nothing at all — is the composition root's business.
    """

    def __init__(
        self,
        poller: PollerOracle,
        handler: PollingResultHandler,
        calculator: NewDataCalculator,
    ) -> None:
        self._poller = poller
        self._handler = handler
        self._calculator = calculator

    async def execute(self, request: PollDataRequest) -> PollDataResponse:
        """Poll once and report what was found.

        Args:
            request: The endpoint to poll and what was seen last time

        Returns:
            What came back, and whether the handler was told
        """
        result = await self._poller.poll_endpoint(request.config)

        if not result.success or result.content_hash is None:
            return self._report(request, result, Handoff.NOT_NEEDED)

        if result.content_hash == request.previous_hash:
            return self._report(request, result, Handoff.NOT_NEEDED)

        try:
            item_ids = await self._calculator.identify_new_items(
                request.previous_content, result.content
            )
            acknowledgement = await self._handler.handle_new_data(
                request.config.endpoint_identifier,
                item_ids,
                result.content_hash,
            )
        except Exception as refusal:
            # Nobody was told, so the obligation stands. Saying so is
            # the whole of what this use case owes its caller.
            return self._report(
                request,
                result,
                Handoff.FAILED,
                found=True,
                info=(f"{type(refusal).__name__}: {refusal}",),
            )

        return self._report(
            request,
            result,
            Handoff.DISCHARGED,
            found=True,
            notified=len(item_ids),
            info=tuple(acknowledgement.info),
        )

    @staticmethod
    def _report(
        request: PollDataRequest,
        result: PollingResult,
        handoff: Handoff,
        *,
        found: bool = False,
        notified: int = 0,
        info: tuple[str, ...] = (),
    ) -> PollDataResponse:
        """One place the response is built, so every path reports alike."""
        return PollDataResponse(
            endpoint_id=request.config.endpoint_identifier,
            content_hash=result.content_hash,
            content=result.content.decode("utf-8", errors="ignore"),
            polled_at=result.polled_at.isoformat(),
            polled_successfully=result.success,
            new_items_found=found,
            items_notified=notified,
            handoff=handoff,
            handoff_info=info,
        )
