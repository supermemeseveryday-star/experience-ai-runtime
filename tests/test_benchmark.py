import json
import pytest
from experience_ai.benchmark.runner import BenchmarkRunner


@pytest.mark.asyncio
async def test_benchmark_runs_fake_provider(runtime, tmp_path):
    path = tmp_path / "problems.jsonl"
    path.write_text(json.dumps({"id": "1", "question": "a new question"}) + "\n")
    result = await BenchmarkRunner(runtime).run(str(path))
    assert result["count"] == 1
    assert "reuse_rate" in result["runtime"]
    assert "accuracy" not in result or result["note"]
