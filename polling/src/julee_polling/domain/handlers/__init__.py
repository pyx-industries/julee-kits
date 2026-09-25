"""Handler protocols for polling domain conditions.

A use case that finds new data at an endpoint hands off to a handler
rather than deciding what happens next itself: what comes after a poll
is the adopting solution's business, not this kit's (ADR 003).
"""

from .polling_result_handler import PollingResultHandler

__all__ = ["PollingResultHandler"]
