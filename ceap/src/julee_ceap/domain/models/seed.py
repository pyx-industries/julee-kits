"""What a system should start with, before anyone uses it.

A seed is not an entity. Nothing keeps one and nothing has an id for it:
it is a description of an entity that ought to exist, handed over by
whoever knows where such descriptions are kept.
"""

from dataclasses import dataclass

from julee.core.entities.text import NonEmptyText


@dataclass(frozen=True)
class DocumentSeed:
    """A document the system should start with, and its content.

    The content travels as bytes rather than the document being built
    already, because a document names its content by hash and the hash
    is only known once the content is stored. Storing and then naming is
    the use case's decision, not the adapter's, so the adapter hands
    over what it read and the use case does the rest.
    """

    document_id: NonEmptyText
    original_filename: NonEmptyText
    content_type: NonEmptyText
    content: bytes
