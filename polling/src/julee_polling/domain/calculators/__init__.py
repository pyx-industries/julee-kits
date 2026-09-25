"""
Calculator protocols for the polling domain.

A calculator works out an answer from what it was handed: same arguments,
same answer, every time (ADR 016). That is why a workflow may call one
inline rather than paying a round trip to an activity for it.

It is also the seam this kit uses to require something of its adopter —
ADR 012's contribution contract running the other way. Polling knows how
to fetch bytes and compare them; only the adopting solution knows what
counts as a new item in them.
"""

from .new_data import NewDataCalculator

__all__ = [
    "NewDataCalculator",
]
