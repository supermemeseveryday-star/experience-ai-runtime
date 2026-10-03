import json
import time
from pathlib import Path


class BenchmarkRunner:
    def __init__(self, runtime):
        self.runtime = runtime

    async def run(self, path: str) -> dict:
        rows = [
            json.loads(line)
            for line in Path(path).read_text().splitlines()
            if line.strip()
        ]
        baseline = []
        adaptive = []
        for row in rows:
            t = time.perf_counter()
            answer = await self.runtime.provider.generate(
                row["question"],
                "Answer accurately and concisely.",
                self.runtime.settings.model.temperature,
            )
            baseline.append(
                {"latency_ms": (time.perf_counter() - t) * 1000, "answer": answer}
            )
            adaptive.append(await self.runtime.chat(row["question"]))
        return {
            "count": len(rows),
            "baseline": {
                "average_latency_ms": sum(x["latency_ms"] for x in baseline)
                / max(len(baseline), 1),
                "average_tokens": 0,
            },
            "runtime": {
                "average_latency_ms": sum(x.latency_ms for x in adaptive)
                / max(len(adaptive), 1),
                "reuse_rate": sum(x.mode.value == "REUSE" for x in adaptive)
                / max(len(adaptive), 1),
                "deep_reasoning_rate": sum(
                    x.mode.value == "DEEP_REASONING" for x in adaptive
                )
                / max(len(adaptive), 1),
                "experience_hit_rate": sum(
                    x.experience_id is not None for x in adaptive
                )
                / max(len(adaptive), 1),
                "average_tokens": 0,
            },
            "note": "Accuracy requires a labeled dataset; the synthetic starter data is unlabeled, so this run reports no accuracy score.",
        }
