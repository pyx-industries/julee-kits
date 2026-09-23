"""AcceleratorRepository protocol."""

from typing import Protocol, runtime_checkable

from julee.core.entities.accelerator import Accelerator


@runtime_checkable
class AcceleratorRepository(Protocol):
    """Where documented accelerators are read from.

    Accelerator lives in the kernel rather than in this kit, so that HCD
    and the private supply-chain work — which cannot see each other —
    agree on what an accelerator is. The repository over it is still a
    kit concern, which is why the protocol is here.

    Narrower than the other protocols in this package: an accelerator is
    written up elsewhere and only read here, so there is nothing to save.
    """

    async def list_all(self) -> list[Accelerator]:
        """Every documented accelerator."""
        ...
