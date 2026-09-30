"""The messages validate document takes and returns.

A request is what a driving adapter hands in and a response is what it
serialises back out, so both are pydantic models. This is the one
package of the bounded context that imports pydantic (ADR 001).

The response held a DocumentPolicyValidation, for the reasons given in
the sibling module: a message built around an entity is the entity's
shape wearing another name, and ValidateDocumentWorkflow returned it
into Temporal's history.
"""

from pydantic import BaseModel

from julee_ceap.domain.models.policy.document_policy_validation import (
    DocumentPolicyValidation,
    DocumentPolicyValidationStatus,
)


class ValidateDocumentRequest(BaseModel):
    document_id: str
    policy_id: str


class ValidateDocumentResponse(BaseModel):
    """What came of validating a document against a policy.

    ``passed`` is None while the validation has not reached a verdict,
    which is not the same as failing.
    """

    validation_id: str
    status: DocumentPolicyValidationStatus
    passed: bool | None
    transformed_document_id: str | None

    @classmethod
    def of(cls, validation: DocumentPolicyValidation) -> "ValidateDocumentResponse":
        """The message for one validation.

        Args:
            validation: The entity to describe

        Returns:
            What the caller is told
        """
        return cls(
            validation_id=validation.validation_id,
            status=validation.status,
            passed=validation.passed,
            transformed_document_id=(
                str(validation.transformed_document_id)
                if validation.transformed_document_id
                else None
            ),
        )
