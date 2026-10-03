import pytest
from experience_ai.llm.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_ollama_health_failure_is_clear():
    provider = OllamaProvider("qwen", "http://127.0.0.1:1")
    assert await provider.health_check() is False
