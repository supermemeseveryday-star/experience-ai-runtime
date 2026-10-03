from experience_ai.memory.database import Database
from experience_ai.models.schemas import Skill


class SkillStore:
    def __init__(self, db: Database):
        self.db = db

    def add(self, skill: Skill):
        self.db.save_skill(skill)

    def list(self):
        return self.db.list_skills()
