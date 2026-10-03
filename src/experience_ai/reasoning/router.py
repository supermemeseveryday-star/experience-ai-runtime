from experience_ai.models.enums import ReasoningMode
from experience_ai.config.settings import ApplicabilitySettings


class ReasoningRouter:
    def __init__(self, settings: ApplicabilitySettings):
        self.settings = settings

    def route(self, score: float, has_experience: bool = True) -> ReasoningMode:
        if not has_experience:
            return ReasoningMode.DEEP_REASONING
        if score >= self.settings.reuse_threshold:
            return ReasoningMode.REUSE
        if score >= self.settings.partial_threshold:
            return ReasoningMode.PARTIAL_REASONING
        return ReasoningMode.DEEP_REASONING
