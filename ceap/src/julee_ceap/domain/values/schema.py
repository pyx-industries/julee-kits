"""A JSON Schema, as something this context has modelled.

CEAP assembles data to fit a schema and refuses data that does not, so a
schema is not foreign JSON that happens to pass through: it is what an
assembly specification is written against.

It was ``Mapping[str, Any]``, and ``SchemaOracle.fetch`` returned that.
Doctrine objected to the ``Any`` and the oracle's docstring answered
that "what comes back is the schema author's JSON and not something CEAP
has modelled" — which describes the gap rather than closing it. This
closes it.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JsonSchema:
    """A JSON Schema document.

    The document stays a ``Mapping`` rather than being modelled field by
    field. A JSON Schema is an open format — an author may write keywords
    this kit has never heard of, and dropping them would change what the
    schema means. What is modelled is that this mapping *is a schema*,
    which is what a port needs to say.
    """

    document: Mapping[str, Any]
    """The schema as written, keywords and all."""

    def __bool__(self) -> bool:
        """Whether there is anything here.

        An empty schema is not one, and several callers ask before
        using it.
        """
        return bool(self.document)

    @property
    def is_a_bare_ref(self) -> bool:
        """Whether this is exactly ``{"$ref": url}`` and nothing else.

        Such a schema names another document and carries no rules of its
        own, so it has to be fetched before anything can be checked
        against it.
        """
        return len(self.document) == 1 and "$ref" in self.document

    @property
    def ref(self) -> str:
        """The ``$ref`` value, for a schema that has one.

        Returns:
            The reference as written, or "" if there is none
        """
        found = self.document.get("$ref", "")
        return found if isinstance(found, str) else ""


@dataclass(frozen=True)
class AssembledData:
    """The JSON a document was assembled into, ready to be checked.

    The sibling of :class:`JsonSchema`, and for the same reason: a port
    saying ``Mapping[str, Any]`` says nothing about what it is handling,
    and this context handles exactly two kinds of open JSON — a schema,
    and data that has to fit one.

    Kept apart from the schema rather than folded in, because they are
    checked against each other and a type that was both would make that
    sentence impossible to write.
    """

    document: Mapping[str, Any]
    """The assembled data, as the queries filled it in."""

    @classmethod
    def of_json_text(cls, text: str) -> "AssembledData":
        """The data some JSON text describes.

        A knowledge service answers with text, and the answer has to be
        JSON or there is nothing to assemble. Parsing is how that is
        found out, which is why it happens here rather than being
        checked some other way.

        Args:
            text: What the service answered

        Returns:
            The data it describes

        Raises:
            ValueError: If the text is empty or is not JSON
        """
        if not text.strip():
            raise ValueError("Empty response from transformation query")
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as not_json:
            raise ValueError(
                f"Transformation result must be valid JSON, got: "
                f"{text[:100]}... Parse error: {not_json}"
            ) from not_json
        if not isinstance(parsed, dict):
            raise ValueError(
                f"Transformation result must be a JSON object, got "
                f"{type(parsed).__name__}"
            )
        return cls(parsed)

    def as_json_bytes(self) -> bytes:
        """This data, written as the JSON it is.

        Assembled data is stored as a document, and a document is bytes.
        Writing itself is the value's own business: it is JSON, so it
        knows how, and a use case does not have to import json to ask.

        Returns:
            The data as indented JSON, UTF-8 encoded
        """
        return json.dumps(dict(self.document), indent=2).encode("utf-8")
