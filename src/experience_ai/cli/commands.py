import asyncio
import json
from pathlib import Path
import typer
from experience_ai.main import build_runtime
from experience_ai.learning.review import ExperienceReview
from experience_ai.llm.ollama import OllamaError

app = typer.Typer(
    help="Local-first adaptive reasoning with persistent verified experiences"
)


@app.command()
def chat(config: str | None = None):
    """Start an interactive local chat session."""
    rt = build_runtime(config)
    print(
        f"Experience AI Runtime | Model: {rt.settings.model.model} | Embeddings: {rt.embedder.backend} | Experiences: {len(rt.store.list())} | Skills: {len(rt.db.list_skills())}"
    )
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in {"exit", "quit"}:
            break
        if not q:
            continue
        try:
            r = asyncio.run(rt.chat(q))
            print(
                f"\nExperience: {r.experience_id or 'None'}\nSimilarity: {r.similarity:.2f}\nApplicability: {r.applicability:.2f}\nMode: {r.mode.value}\n\nAnswer:\n{r.answer}"
            )
            if r.experience_created:
                print("\nCandidate experience saved for review.")
        except OllamaError as e:
            print(f"\nError: {e}")


@app.command()
def learn(file: str = "data/problems.jsonl", config: str | None = None):
    """Solve and learn from a local JSONL file of {id, question} rows."""
    rt = build_runtime(config)

    async def run():
        for line in Path(file).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            result = await rt.chat(row["question"])
            print(
                f"{row.get('id', '?')}: {result.mode.value}; experience_created={result.experience_created}"
            )

    try:
        asyncio.run(run())
    except OllamaError as e:
        raise typer.BadParameter(str(e))


@app.command()
def benchmark(file: str = "data/problems.jsonl", config: str | None = None):
    """Compare direct Qwen calls with adaptive runtime on local questions."""
    from experience_ai.benchmark.runner import BenchmarkRunner

    rt = build_runtime(config)
    try:
        print(json.dumps(asyncio.run(BenchmarkRunner(rt).run(file)), indent=2))
    except OllamaError as e:
        raise typer.BadParameter(str(e))


@app.command()
def consolidate(config: str | None = None):
    """Build skills from multiple verified experiences."""
    from experience_ai.learning.consolidator import Consolidator

    rt = build_runtime(config)
    skills = Consolidator().consolidate(rt.store.list(eligible_only=True))
    for skill in skills:
        rt.db.save_skill(skill)
    print(f"Saved {len(skills)} skill(s).")


@app.command()
def serve(config: str | None = None, host: str = "127.0.0.1", port: int = 8000):
    """Run the local FastAPI server."""
    import uvicorn
    from experience_ai.api.server import create_app

    uvicorn.run(create_app(build_runtime(config)), host=host, port=port)


@app.command()
def health(config: str | None = None):
    """Check local runtime setup without downloading a model."""
    rt = build_runtime(config)
    ollama_ok = asyncio.run(rt.provider.health_check())
    model_ok = asyncio.run(rt.provider.model_available()) if ollama_ok else False
    print(
        json.dumps(
            {
                "database": "ok",
                "ollama": "ok" if ollama_ok else "unavailable",
                "model": rt.settings.model.model,
                "model_available": model_ok,
                "embedding_backend": rt.embedder.backend,
                "experiences": len(rt.store.list()),
            },
            indent=2,
        )
    )


@app.command()
def candidates(config: str | None = None):
    """List extracted candidate experiences waiting for review."""
    from experience_ai.models.enums import ExperienceStatus

    rt = build_runtime(config)
    items = [e for e in rt.store.list() if e.status == ExperienceStatus.CANDIDATE]
    if not items:
        print("No candidate experiences.")
        return
    for e in items:
        print(
            f"\n{e.experience_id}: {e.problem_pattern}\n  {e.problem_summary}\n  Strategy: {'; '.join(e.strategy)}\n  Verify: {'; '.join(e.verification_method) or 'add a concrete check before promotion'}"
        )


@app.command()
def verify(experience_id: str, config: str | None = None):
    """Promote a candidate after you have independently completed its verification."""
    rt = build_runtime(config)
    exp = rt.store.get(experience_id)
    if exp is None:
        raise typer.BadParameter(f"Experience not found: {experience_id}")
    print(
        f"Pattern: {exp.problem_pattern}\nStrategy: {'; '.join(exp.strategy)}\nVerification: {'; '.join(exp.verification_method) or 'No verification method recorded'}"
    )
    if not typer.confirm(
        "Have you actually completed this verification and confirmed the strategy works?",
        default=False,
    ):
        print("Left as CANDIDATE.")
        return
    try:
        ExperienceReview().promote_after_verification(exp, True)
    except ValueError as error:
        raise typer.BadParameter(str(error))
    rt.store.add(exp)
    print("Marked VERIFIED. This experience is now eligible for reuse.")
