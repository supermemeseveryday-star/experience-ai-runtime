import uuid
from experience_ai.models.schemas import Experience, Skill


class Consolidator:
    def consolidate(self, experiences: list[Experience]) -> list[Skill]:
        # Group only repeated verified experience families; conservative token overlap.
        groups: dict[str, list[Experience]] = {}
        for e in experiences:
            if e.status.value not in {"VERIFIED", "TRUSTED"}:
                continue
            key = (
                e.problem_pattern.lower().split()[0]
                if e.problem_pattern.split()
                else ""
            )
            if key:
                groups.setdefault(key, []).append(e)
        skills = []
        for key, items in groups.items():
            if len(items) < 2:
                continue
            common = []
            for e in items:
                for step in e.strategy:
                    if step not in common:
                        common.append(step)
            skills.append(
                Skill(
                    skill_id="skill_" + uuid.uuid4().hex[:12],
                    name=key.title() + " Problem Solving",
                    description=f"General capability derived from {len(items)} verified experiences.",
                    general_strategy=common,
                    experience_ids=[e.experience_id for e in items],
                    confidence=sum(e.confidence for e in items) / len(items),
                )
            )
        return skills
