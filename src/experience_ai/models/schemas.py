from datetime import datetime, timezone
from pydantic import BaseModel, Field
from .enums import ExperienceStatus, ReasoningMode


class Experience(BaseModel):
    experience_id: str
    problem_pattern: str
    problem_summary: str
    conditions: list[str] = Field(default_factory=list)
    strategy: list[str] = Field(default_factory=list)
    reasoning_principle: str = ""
    verification_method: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    status: ExperienceStatus = ExperienceStatus.CANDIDATE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Skill(BaseModel):
    skill_id: str
    name: str
    description: str
    general_strategy: list[str] = Field(default_factory=list)
    experience_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)


class ChatRequest(BaseModel):
    query: str
    mode: str = "adaptive"


class ChatResult(BaseModel):
    answer: str
    mode: ReasoningMode
    experience_id: str | None = None
    similarity: float = 0
    applicability: float = 0
    validation_status: str = "NOT_RUN"
    experience_created: bool = False
    latency_ms: float = 0
    input_tokens: int = 0
    output_tokens: int = 0
