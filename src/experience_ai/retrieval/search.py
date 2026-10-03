from dataclasses import dataclass
from experience_ai.embeddings.local import LocalEmbedder, cosine_similarity
from experience_ai.memory.database import Database
from experience_ai.memory.experience_store import ExperienceStore


@dataclass
class Candidate:
    experience: object
    similarity: float


class ExperienceSearch:
    def __init__(self, db: Database, embedder: LocalEmbedder, store: ExperienceStore):
        self.db, self.embedder, self.store = db, embedder, store

    def search(self, query: str, top_k: int = 5) -> list[Candidate]:
        q = self.embedder.embed(query)
        found = []
        for exp, vec in self.db.list_experiences(eligible_only=True):
            found.append(Candidate(exp, cosine_similarity(q, vec)))
        return sorted(found, key=lambda x: x.similarity, reverse=True)[:top_k]
