import os

from dotenv import load_dotenv

from experience_ai.config.settings import load_settings
from experience_ai.embeddings.local import LocalEmbedder
from experience_ai.llm.ollama import OllamaProvider
from experience_ai.memory.database import Database
from experience_ai.runtime.orchestrator import Runtime


def build_runtime(config: str | None = None) -> Runtime:
    load_dotenv()
    settings = load_settings(config or os.getenv("EXPERIENCE_AI_CONFIG"))
    db_path = settings.database.path
    # Resolve relative database paths against the current project directory.
    return Runtime(
        settings,
        Database(db_path),
        LocalEmbedder(settings.embedding.model),
        OllamaProvider(settings.model.model, settings.model.base_url),
    )
