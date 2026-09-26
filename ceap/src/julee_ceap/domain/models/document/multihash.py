"""How CEAP names a document's content.

``Document.content_multihash`` is a `multihash
<https://multiformats.io/multihash/>`_: a self-describing digest that
says which function produced it before it says what the digest is. A
sha256 multihash is ``1220`` — function 0x12, length 0x20 — followed by
the 32-byte digest, hex encoded.

It is not only an integrity check. The MinIO repository uses it as the
object key, so two documents with identical content share one object,
and a document's content is found by asking for its multihash.

Five places computed it independently and three of them disagreed
(#44): the MinIO repository and two use cases produced a well-formed
multihash, the memory repository produced a bare sha256 hex digest, and
``initialize_system_data`` produced ``sha256-`` followed by the hex
digest. The same document therefore got a different name depending on
which adapter stored it, and tests running against the memory adapter
never saw the format production uses.

The three that agreed were also wrong. They called
``multihash.encode(sha256(content).digest(), SHA2_256)``, and that
library's ``encode`` hashes its argument rather than taking a digest —
and writes the length of *its input* as the length byte, not the length
of the digest it produces. So they stored ``1220`` followed by
sha256(sha256(content)): a double hash, labelled as a single one. It
passed for well-formed only because a sha256 digest is 32 bytes, which
is the length the prefix claims. Give that library 40 bytes and it
writes ``1228`` in front of a 32-byte digest.

A multihash is two bytes and a digest. Writing those two bytes here is
less code than calling a library that gets them wrong.

There is one implementation now, and a document will not accept a value
that is not one.
"""

import hashlib
import re

__all__ = [
    "SHA2_256_PREFIX",
    "content_multihash",
    "is_content_multihash",
]

SHA2_256_PREFIX = "1220"
"""The two bytes in front of a sha256 multihash, hex encoded.

``0x12`` is multihash's code for sha2-256 and ``0x20`` is the digest
length in bytes. Both are fixed for this function, so the prefix is a
constant rather than something to encode.
"""


_WELL_FORMED = re.compile(rf"^{SHA2_256_PREFIX}[0-9a-f]{{64}}$")
"""The shape :func:`content_multihash` produces.

Matched rather than decoded, so the check is cheap enough to run in a
validator on every document.
"""


def content_multihash(content: bytes) -> str:
    """The multihash naming this content.

    Args:
        content: The document's bytes

    Returns:
        A hex-encoded sha256 multihash: "1220" and 64 hex characters
    """
    return SHA2_256_PREFIX + hashlib.sha256(content).hexdigest()


def is_content_multihash(value: str) -> bool:
    """Whether a string is a sha256 multihash this kit would have written.

    Args:
        value: The candidate, as stored on a document

    Returns:
        True if it has the shape :func:`content_multihash` produces
    """
    return bool(_WELL_FORMED.match(value))
