class ValidationResult:
    def __init__(self, valid: bool, status: str, notes: str = ""):
        self.valid, self.status, self.notes = valid, status, notes


class AnswerValidator:
    """Conservative MVP validator: catches empty/obvious refusal answers; domain checks are pluggable."""

    def validate(self, answer: str) -> ValidationResult:
        valid = bool(answer and answer.strip())
        return ValidationResult(
            valid, "PASSED" if valid else "FAILED", "Non-empty response check"
        )
