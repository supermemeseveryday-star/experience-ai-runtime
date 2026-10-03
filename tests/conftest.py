import pytest
from experience_ai.config.settings import Settings
from experience_ai.embeddings.local import LocalEmbedder
from experience_ai.memory.database import Database
from experience_ai.runtime.orchestrator import Runtime


class FakeProvider:
    async def health_check(self):
        return True

    async def model_available(self):
        return True

    async def generate(self, prompt, system="", temperature=0.2):
        if "Convert the solved problem" in prompt:
            return '{"problem_pattern":"python setup","problem_summary":"Set up Python project","conditions":["Python"],"strategy":["Use a virtual environment"],"reasoning_principle":"Isolate dependencies","verification_method":["python --version"],"failure_conditions":[],"alternatives":[],"confidence":0.8}'
        return "Use a virtual environment and verify with python --version."


@pytest.fixture
def runtime(tmp_path):
    settings = Settings()
    settings.database.path = str(tmp_path / "test.db")
    return Runtime(
        settings, Database(settings.database.path), LocalEmbedder(), FakeProvider()
    )
