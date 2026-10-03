from experience_ai.memory.database import Database
from experience_ai.models.schemas import Experience
from experience_ai.embeddings.local import LocalEmbedder


class ExperienceStore:
    def __init__(self, db: Database, embedder: LocalEmbedder):
        self.db, self.embedder = db, embedder

    def add(self, experience: Experience) -> None:
        self.db.save_experience(experience, self.embedder.embed(self._text(experience)))

    def get(self, exp_id: str):
        return self.db.get_experience(exp_id)

    def list(self, eligible_only=False):
        return [e for e, _ in self.db.list_experiences(eligible_only)]

    @staticmethod
    def _text(e: Experience) -> str:
        return " ".join(
            [e.problem_pattern, e.problem_summary, *e.conditions, *e.strategy]
        )
