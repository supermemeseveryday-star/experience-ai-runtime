from fastapi import FastAPI, HTTPException
from experience_ai.models.schemas import ChatRequest, Experience
from experience_ai.llm.ollama import OllamaError


def create_app(runtime):
    app = FastAPI(title="Experience AI Runtime", version="0.1.0")

    @app.get("/health")
    async def health():
        ollama_ok = await runtime.provider.health_check()
        model_ok = await runtime.provider.model_available() if ollama_ok else False
        return {
            "status": "ok" if ollama_ok and model_ok else "degraded",
            "ollama": ollama_ok,
            "model": runtime.settings.model.model,
            "model_available": model_ok,
        }

    @app.post("/chat")
    async def chat(body: ChatRequest):
        try:
            return (await runtime.chat(body.query, body.mode)).model_dump(mode="json")
        except OllamaError as e:
            raise HTTPException(503, str(e))

    @app.get("/experiences")
    async def experiences():
        return [e.model_dump(mode="json") for e in runtime.store.list()]

    @app.get("/experiences/{exp_id}")
    async def experience(exp_id: str):
        e = runtime.store.get(exp_id)
        if not e:
            raise HTTPException(404, "Experience not found")
        return e.model_dump(mode="json")

    @app.post("/experiences")
    async def add_experience(e: Experience):
        runtime.store.add(e)
        return e.model_dump(mode="json")

    @app.get("/skills")
    async def skills():
        return [s.model_dump() for s in runtime.db.list_skills()]

    @app.get("/metrics")
    async def metrics():
        rows = runtime.db.metrics()
        n = max(len(rows), 1)
        return {
            "requests": len(rows),
            "experience_hit_rate": sum(bool(r["experience_id"]) for r in rows) / n,
            "reuse_rate": sum(r["mode"] == "REUSE" for r in rows) / n,
            "partial_reasoning_rate": sum(
                r["mode"] == "PARTIAL_REASONING" for r in rows
            )
            / n,
            "deep_reasoning_rate": sum(r["mode"] == "DEEP_REASONING" for r in rows) / n,
            "average_latency_ms": sum(r["latency_ms"] for r in rows) / n,
            "average_tokens": sum(r["input_tokens"] + r["output_tokens"] for r in rows)
            / n,
            "experience_creation_rate": sum(r["experience_created"] for r in rows) / n,
            "validation_failure_rate": sum(
                r["validation_status"] == "FAILED" for r in rows
            )
            / n,
        }

    @app.get("/settings")
    async def settings():
        return runtime.settings.model_dump()

    @app.post("/benchmark")
    async def benchmark(body: dict):
        from experience_ai.benchmark.runner import BenchmarkRunner

        try:
            return await BenchmarkRunner(runtime).run(
                body.get("file", "data/problems.jsonl")
            )
        except OllamaError as e:
            raise HTTPException(503, str(e))

    @app.post("/v1/chat/completions")
    async def completions(body: dict):
        msgs = body.get("messages", [])
        query = "\n".join(m.get("content", "") for m in msgs if m.get("role") == "user")
        try:
            result = await runtime.chat(query)
        except OllamaError as e:
            raise HTTPException(503, str(e))
        return {
            "id": "chatcmpl-experience-ai",
            "object": "chat.completion",
            "created": 0,
            "model": body.get("model", "experience-ai"),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": result.answer},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": result.input_tokens,
                "completion_tokens": result.output_tokens,
                "total_tokens": result.input_tokens + result.output_tokens,
            },
        }

    return app
