"""The messages validate accelerators takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from julee.core.entities.accelerator import AcceleratorValidationIssue
from pydantic import BaseModel


class ValidateAcceleratorsRequest(BaseModel):
    """Request for validating accelerators against code structure.

    Compares documented accelerators (from RST) with discovered bounded
    contexts (from src/ directory scanning).
    """


class ValidateAcceleratorsResponse(BaseModel):
    """Response from validating accelerators against code structure.

    Contains lists of matched accelerators and any issues found.
    """

    documented_slugs: list[str]
    discovered_slugs: list[str]
    matched_slugs: list[str]
    issues: list[AcceleratorValidationIssue]

    @property
    def is_valid(self) -> bool:
        """Check if validation passed with no issues."""
        return len(self.issues) == 0
