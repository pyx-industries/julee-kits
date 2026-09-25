"""
Oracle protocols for the CEAP domain.

An oracle asks something the solution does not control and gets the answer
back in that thing's own currency rather than ours (ADR 016). It names no
entity because nothing it deals in has been modelled: a JSON Schema fetched
from a URL is the schema author's, not this context's.

Oracles are reached from workflow code through an activity, never called
directly, because their answer can differ between replays.
"""

from .schema import SchemaOracle

__all__ = [
    "SchemaOracle",
]
