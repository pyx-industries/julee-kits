"""Text that normalises itself: slugs and names.

Two value objects, together because they are the same idea twice. Each
is a ``str`` subclass whose constructor decides what the value is, so
``Slug("My System")`` is ``"my-system"`` and there is no second way to
get one.

They were field validators until #70. Nineteen of them across c4, all
but one returning a changed value rather than raising — which is not
validation, it is a constructor written in the wrong place and copied.
Copied unevenly, too: a slug field slugified and a field *naming* that
slug only stripped, so ``Component(container_slug="Web Application")``
could never match ``Container(slug="web-application")`` and the lookup
came back empty rather than wrong. A type both sides share cannot
disagree with itself.

Being ``str`` subclasses is what makes them free. They serialise as
strings, key dictionaries, format into f-strings and compare against
plain strings, so nothing downstream unwraps anything. And because the
normalising is in ``__new__`` rather than in a pydantic validator, it
still happens when the entity holding them stops being a pydantic model
(julee#307).

They belong in the kernel next to :func:`julee.core.utils.slugify`,
which is where the rules they apply already live — hcd and viewpoints
normalise the same way, by hand, in about sixty places. That move waits
on julee-kits#71, which is what measures whether the shape pays.
"""

from typing import Any

from julee.core.utils import normalize_name, slugify
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

__all__ = ["Name", "Slug"]


def _string_schema(cls: type) -> core_schema.CoreSchema:
    """A pydantic schema that builds ``cls`` from a string.

    Validation is the constructor, so there is one implementation of
    what the value is and pydantic reaches it the same way a direct
    call does. Serialisation is ``str``: what goes on the wire is a
    plain JSON string, unchanged from before these types existed.
    """
    return core_schema.no_info_after_validator_function(
        cls,
        core_schema.str_schema(),
        serialization=core_schema.plain_serializer_function_ser_schema(
            str, return_schema=core_schema.str_schema(), when_used="json"
        ),
    )


class Slug(str):
    """A URL-safe identifier, normalised on the way in.

    Entities refer to each other by slug, so the two sides of a
    reference have to agree. Declaring both sides ``Slug`` is what makes
    them agree — the alternative, remembering to call
    :func:`~julee.core.utils.slugify` at each end, is what c4 was doing
    and got wrong in eight of twelve places.

    Text with nothing slug-shaped in it is refused rather than turned
    into an empty slug, because an empty identifier names everything
    and nothing.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "Slug":
        slug = slugify(str(value).strip())
        if not slug:
            raise ValueError(
                f"{value!r} has nothing in it that can be a slug. A slug "
                f"needs at least one letter or digit"
            )
        return super().__new__(cls, slug)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return _string_schema(cls)


class Name(str):
    """Text a person wrote, kept as they wrote it.

    Unlike a :class:`Slug`, a name is for reading, so the only thing
    done to it is stripping the whitespace around it. An empty name is
    refused: something has to be displayed.

    :attr:`normalized` is how names are compared — case-insensitively,
    with hyphens and underscores read as spaces — so "Data Steward",
    "data-steward" and "data_steward" are one name. It is a property
    rather than a second field because it is not separate information.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "Name":
        text = str(value).strip()
        if not text:
            raise ValueError("a name cannot be empty")
        return super().__new__(cls, text)

    @property
    def normalized(self) -> str:
        """This name in the form names are compared in."""
        return normalize_name(self)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return _string_schema(cls)
