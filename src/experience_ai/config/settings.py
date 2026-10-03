from pathlib import Path
from pydantic import BaseModel, Field
import yaml


class ModelSettings(BaseModel):
    provider: str = "ollama"
    model: str = "qwen"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.2


class EmbeddingSettings(BaseModel):
    model: str = "sentence-transformers/all-MiniLM-L6-v2"


class RetrievalSettings(BaseModel):
    top_k: int = 5
    deduplication_threshold: float = 0.92


class ApplicabilitySettings(BaseModel):
    reuse_threshold: float = 0.90
    partial_threshold: float = 0.65
    similarity_weight: float = 0.35
    condition_weight: float = 0.25
    confidence_weight: float = 0.20
    success_weight: float = 0.15
    freshness_weight: float = 0.05


class RuntimeSettings(BaseModel):
    default_mode: str = "adaptive"


class MemorySettings(BaseModel):
    auto_save: bool = True
    auto_consolidate: bool = False


class DatabaseSettings(BaseModel):
    path: str = "data/experience.db"


class Settings(BaseModel):
    model: ModelSettings = Field(default_factory=ModelSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    applicability: ApplicabilitySettings = Field(default_factory=ApplicabilitySettings)
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


def load_settings(path: str | Path | None = None) -> Settings:
    candidate = Path(path or "config/settings.yaml")
    if not candidate.exists():
        return Settings()
    with candidate.open(encoding="utf-8") as f:
        return Settings.model_validate(yaml.safe_load(f) or {})
