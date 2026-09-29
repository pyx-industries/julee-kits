"""How a query asks to be run.

A value object (ADR 018): two with the same contents are the same one,
and nothing keeps one under an id.

This was ``Mapping[str, Any]``, and the ``Any`` was the last type
crossing one of ceap's driven ports that the domain could not name. The
field's docstring advertised ``top_p``, ``endpoint``, ``timeout`` and
``retries`` alongside these three, but no adapter has ever read any of
them: the Anthropic service reads ``model``, ``max_tokens`` and
``temperature`` and nothing else, and the shipped fixtures set only the
latter two. So the open mapping was buying an aspiration nothing
implements, at the price of a port signature that said nothing.

Naming the three is not the domain learning an adapter's vocabulary. A
model, a token budget and a temperature are what ceap's authors write in
an assembly specification, and they are the sentence the domain actually
speaks. A service that needs a fourth knob gets a field here, in the
open, rather than smuggling it through a bag.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryMetadata:
    """What a query says about how the knowledge service should run it.

    Every knob is optional. Leaving one unset hands the decision to the
    adapter, which holds the default — the domain has no opinion about
    what a good default model is.
    """

    model: str | None = None
    """Which model to use, or None to let the adapter choose."""

    max_tokens: int | None = None
    """The token budget for the response, or None for the adapter's."""

    temperature: float | None = None
    """How much the response may vary, or None for the adapter's."""
