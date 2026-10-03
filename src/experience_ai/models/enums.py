from enum import Enum


class ExperienceStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    TRUSTED = "TRUSTED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class ReasoningMode(str, Enum):
    REUSE = "REUSE"
    PARTIAL_REASONING = "PARTIAL_REASONING"
    DEEP_REASONING = "DEEP_REASONING"
