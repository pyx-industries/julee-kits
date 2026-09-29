"""Reading a JSON Schema, with the libraries that know how.

``jsonpointer`` and ``jsonschema`` live here. They were imported by a use
case, which is how a use case came to speak two third-party packages; the
work itself was always an adapter's.

The pointer half was a class called ``PointableJSONSchema``, in
``usecases/``, that no request ever reached and that another use case
imported directly. It was never a use case: it does no I/O, takes no
ports and answers the same way every time. ADR 016 calls that a
calculator.
"""

from typing import Any

import jsonpointer
import jsonschema
from jsonpointer import JsonPointer

from julee_ceap.domain.models.schema import AssembledData, JsonSchema


class LibrarySchemaCalculator:
    """A SchemaCalculator built on jsonpointer and jsonschema."""

    def schema_for_pointer(self, schema: JsonSchema, pointer: str) -> JsonSchema:
        """The standalone schema for what a JSON Pointer names.

        Args:
            schema: The whole schema
            pointer: A JSON Pointer into it; "" is the root

        Returns:
            A schema for that part, valid on its own

        Raises:
            ValueError: If the pointer is malformed or names nothing
        """
        # A copy of the root, so every keyword a validator needs travels
        # with the part: $schema, $id, definitions.
        standalone: dict[str, Any] = dict(schema.document)
        if not pointer:
            return JsonSchema(standalone)

        try:
            target = JsonPointer(pointer).resolve(schema.document)
        except Exception as unresolvable:  # noqa: BLE001 - reported, not swallowed
            raise ValueError(
                f"Invalid JSON pointer '{pointer}': {unresolvable}"
            ) from unresolvable

        standalone["type"] = "object"
        standalone["additionalProperties"] = False
        if "title" in standalone:
            standalone["title"] = f"{standalone['title']} - {pointer}"

        named = _what_the_pointer_names(pointer)
        if named == "properties":
            standalone["properties"] = target
        else:
            standalone["properties"] = {named: target}
            standalone["required"] = [named]
        return JsonSchema(standalone)

    def schema_at_fragment(self, schema: JsonSchema, fragment: str) -> JsonSchema:
        """The sub-schema a ``$ref`` fragment names, bundled to stand alone.

        Args:
            schema: The fetched document
            fragment: A JSON Pointer into it; "" means the whole thing

        Returns:
            The sub-schema, with the parent's definitions

        Raises:
            ValueError: If the fragment does not name a JSON object
        """
        if not fragment:
            return schema

        target = jsonpointer.resolve_pointer(dict(schema.document), fragment)
        if not isinstance(target, dict):
            raise ValueError(
                f"$ref fragment '{fragment}' did not resolve to a JSON object"
            )
        bundled: dict[str, Any] = dict(target)
        parent_defs = schema.document.get("$defs", {})
        if parent_defs:
            # The sub-schema's own $defs win, so a name it redefines is
            # its own and not the parent's.
            bundled["$defs"] = {**parent_defs, **bundled.get("$defs", {})}
        return JsonSchema(bundled)

    def refuse_data_that_does_not_fit(
        self, data: AssembledData, schema: JsonSchema
    ) -> None:
        """Check assembled data against the schema it was assembled for.

        Args:
            data: The assembled data
            schema: The schema it must satisfy

        Raises:
            ValueError: If the data does not fit, or the schema is not a
                valid schema
        """
        try:
            jsonschema.validate(dict(data.document), dict(schema.document))
        except jsonschema.ValidationError as does_not_fit:
            raise ValueError(
                f"Assembled data does not conform to JSON schema: "
                f"{does_not_fit.message}"
            ) from does_not_fit
        except jsonschema.SchemaError as not_a_schema:
            raise ValueError(
                f"Invalid JSON schema in assembly specification: {not_a_schema.message}"
            ) from not_a_schema


def _what_the_pointer_names(pointer: str) -> str:
    """The property name at the end of a JSON Pointer.

    ``/properties/title`` names "title"; ``/properties/user/properties/
    name`` names "name"; ``/items`` names "items".

    Args:
        pointer: The pointer, which the caller has checked is not empty

    Returns:
        The last segment
    """
    segments = pointer.strip("/").split("/")
    return segments[-1] if segments else "result"
