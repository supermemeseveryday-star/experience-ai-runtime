import time
import uuid
from datetime import datetime, timezone
from experience_ai.models.enums import ReasoningMode, ExperienceStatus
from experience_ai.models.schemas import ChatResult
from experience_ai.config.settings import Settings
from experience_ai.embeddings.local import LocalEmbedder, cosine_similarity
from experience_ai.llm.base import LLMProvider
from experience_ai.learning.extractor import extract_experience
from experience_ai.memory.database import Database
from experience_ai.memory.experience_store import ExperienceStore
from experience_ai.retrieval.applicability import ApplicabilityChecker
from experience_ai.retrieval.search import ExperienceSearch
from experience_ai.reasoning.router import ReasoningRouter
from experience_ai.reasoning.reuse import reuse_answer
from experience_ai.reasoning.partial import partial_reason
from experience_ai.reasoning.deep import deep_reason
from experience_ai.validation.validator import AnswerValidator


class Runtime:
    def __init__(
        self,
        settings: Settings,
        db: Database,
        embedder: LocalEmbedder,
        provider: LLMProvider,
    ):
        self.settings, self.db, self.embedder, self.provider = (
            settings,
            db,
            embedder,
            provider,
        )
        self.store = ExperienceStore(db, embedder)
        self.search = ExperienceSearch(db, embedder, self.store)
        self.checker = ApplicabilityChecker(settings.applicability)
        self.router = ReasoningRouter(settings.applicability)
        self.validator = AnswerValidator()
        # Keep stored vectors aligned when the local embedding backend changes.
        for experience, _ in self.db.list_experiences():
            self.db.update_experience(
                experience, self.embedder.embed(self.store._text(experience))
            )

    async def chat(self, query: str, mode: str = "adaptive") -> ChatResult:
        started = time.perf_counter()
        candidates = []
        candidate = None
        score = 0.0
        similarity = 0.0
        try:
            candidates = self.search.search(query, self.settings.retrieval.top_k)
            if candidates:
                candidate = candidates[0]
                similarity = candidate.similarity
                score = self.checker.score(query, candidate)
        except Exception:
            candidate = None
        decision = (
            self.router.route(score, candidate is not None)
            if mode == "adaptive"
            else ReasoningMode(mode)
        )
        if decision == ReasoningMode.REUSE:
            exp = candidate.experience
            answer = reuse_answer(exp)
            exp.usage_count += 1
            exp.success_count += 1
            exp.updated_at = datetime.now(timezone.utc)
            self.store.add(exp)
            validation = "PASSED"
            created = False
        else:
            if not await self.provider.health_check():
                from experience_ai.llm.ollama import OllamaError

                raise OllamaError(
                    "Ollama is unavailable. Start it with `ollama serve`, then ensure your configured local Qwen model is available (`ollama list`)."
                )
            answer = await (
                partial_reason(
                    self.provider,
                    query,
                    candidate.experience,
                    self.settings.model.temperature,
                )
                if decision == ReasoningMode.PARTIAL_REASONING and candidate
                else deep_reason(self.provider, query, self.settings.model.temperature)
            )
            checked = self.validator.validate(answer)
            validation = checked.status
            created = False
            if checked.valid and self.settings.memory.auto_save:
                exp = await extract_experience(
                    self.provider, query, answer, self.settings.model.temperature
                )
                if exp:
                    # Never promote without actual independent verification: candidates are not auto-reused.
                    exp.status = ExperienceStatus.CANDIDATE
                    query_embedding = self.embedder.embed(query)
                    existing = self.db.list_experiences(eligible_only=False)
                    duplicate = next(
                        (
                            old
                            for old, vector in existing
                            if cosine_similarity(query_embedding, vector)
                            >= self.settings.retrieval.deduplication_threshold
                        ),
                        None,
                    )
                    if not duplicate:
                        self.store.add(exp)
                        created = True
        latency = (time.perf_counter() - started) * 1000
        result = ChatResult(
            answer=answer,
            mode=decision,
            experience_id=candidate.experience.experience_id if candidate else None,
            similarity=similarity,
            applicability=score,
            validation_status=validation,
            experience_created=created,
            latency_ms=latency,
        )
        self.db.record_metric(
            {
                "id": uuid.uuid4().hex,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mode": decision.value,
                "experience_id": result.experience_id,
                "similarity": similarity,
                "applicability": score,
                "model": self.settings.model.model,
                "latency_ms": latency,
                "input_tokens": 0,
                "output_tokens": 0,
                "experience_created": created,
                "validation_status": validation,
            }
        )
        return result
