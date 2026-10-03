from datetime import datetime, timezone
from experience_ai.config.settings import ApplicabilitySettings
from experience_ai.retrieval.search import Candidate


class ApplicabilityChecker:
    def __init__(self, settings: ApplicabilitySettings):
        self.settings = settings

    def score(
        self, query: str, candidate: Candidate, conditions: list[str] | None = None
    ) -> float:
        e = candidate.experience
        q = set(query.lower().split())
        conds = e.conditions
        compat = (
            1.0
            if not conds
            else sum(1 for c in conds if any(w in q for w in c.lower().split()))
            / len(conds)
        )
        success = (
            e.success_count / (e.success_count + e.failure_count)
            if e.success_count + e.failure_count
            else 0.75
        )
        age = max(0, (datetime.now(timezone.utc) - e.updated_at).days)
        freshness = max(0.5, 1 - age / 730)
        w = self.settings
        return max(
            0,
            min(
                1,
                candidate.similarity * w.similarity_weight
                + compat * w.condition_weight
                + e.confidence * w.confidence_weight
                + success * w.success_weight
                + freshness * w.freshness_weight,
            ),
        )
