"""What can be worked out about a JSON Schema.

Both of these were done inline in a use case, which is how ``jsonschema``
and ``jsonpointer`` came to be imported there. Neither does I/O and
neither can answer differently on a replay, so both are calculators
rather than services (ADR 016) and workflow code may call them directly.
"""

from typing import Protocol, runtime_checkable

from julee_ceap.domain.models.schema import AssembledData, JsonSchema


@runtime_checkable
class SchemaCalculator(Protocol):
    """Reads a schema and answers questions about it."""

    def schema_for_pointer(self, schema: JsonSchema, pointer: str) -> JsonSchema:
        """The standalone schema for what a JSON Pointer names.

        An assembly specification maps a pointer into its schema to the
        query that fills that part, and a knowledge service is given the
        schema for its part alone. Root metadata a validator needs —
        ``$schema``, ``$id``, definitions — travels with it, which is
        what makes the result standalone rather than a fragment.

        Args:
            schema: The whole schema
            pointer: A JSON Pointer into it; "" is the root

        Returns:
            A schema for that part, valid on its own

        Raises:
            ValueError: If the pointer is malformed or names nothing
        """
        ...

    def schema_at_fragment(self, schema: JsonSchema, fragment: str) -> JsonSchema:
        """The sub-schema a ``$ref`` fragment names, bundled to stand alone.

        A bare ``$ref`` is ``{"$ref": "url#/fragment"}``. Once the URL is
        fetched, the fragment still has to be navigated to, and the
        parent's ``$defs`` merged in, or an internal ``$ref`` inside the
        sub-schema resolves to nothing.

        This lived in a private module, ``julee_ceap._schema_ref``, which
        a use case imported — outside the domain and outside the use
        cases both.

        Args:
            schema: The fetched document
            fragment: A JSON Pointer into it; "" means the whole thing

        Returns:
            The sub-schema, with the parent's definitions

        Raises:
            ValueError: If the fragment does not name a JSON object
        """
        ...

    def refuse_data_that_does_not_fit(
        self, data: AssembledData, schema: JsonSchema
    ) -> None:
        """Check assembled data against the schema it was assembled for.

        Raises rather than returns, because there is nothing to do with
        data that does not fit: the assembly is wrong and the caller
        cannot carry on.

        Args:
            data: The assembled data
            schema: The schema it must satisfy

        Raises:
            ValueError: If the data does not fit, or the schema is not a
                valid schema
        """
        ...
