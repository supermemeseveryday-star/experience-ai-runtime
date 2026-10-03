import json
from pathlib import Path
from sqlalchemy import create_engine, String, Text, Float, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from experience_ai.models.schemas import Experience, Skill
from experience_ai.models.enums import ExperienceStatus


class Base(DeclarativeBase):
    pass


class ExperienceRow(Base):
    __tablename__ = "experiences"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    data: Mapped[str] = mapped_column(Text)
    embedding: Mapped[str] = mapped_column(Text)


class SkillRow(Base):
    __tablename__ = "skills"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    data: Mapped[str] = mapped_column(Text)


class MetricRow(Base):
    __tablename__ = "request_metrics"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    experience_id: Mapped[str | None] = mapped_column(String, nullable=True)
    similarity: Mapped[float] = mapped_column(Float, default=0)
    applicability: Mapped[float] = mapped_column(Float, default=0)
    model: Mapped[str] = mapped_column(String)
    latency_ms: Mapped[float] = mapped_column(Float, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    experience_created: Mapped[bool] = mapped_column(Integer, default=0)
    validation_status: Mapped[str] = mapped_column(String)


class Database:
    def __init__(self, path: str):
        p = Path(path)
        if path != ":memory:":
            p.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            "sqlite://" if path == ":memory:" else f"sqlite:///{p.resolve()}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(self.engine, expire_on_commit=False)

    def save_experience(self, exp: Experience, embedding: list[float]) -> None:
        with self.Session.begin() as s:
            s.merge(
                ExperienceRow(
                    id=exp.experience_id,
                    data=exp.model_dump_json(),
                    embedding=json.dumps(embedding),
                )
            )

    def get_experience(self, exp_id: str) -> Experience | None:
        with self.Session() as s:
            row = s.get(ExperienceRow, exp_id)
            return Experience.model_validate_json(row.data) if row else None

    def list_experiences(
        self, eligible_only: bool = False
    ) -> list[tuple[Experience, list[float]]]:
        with self.Session() as s:
            rows = s.scalars(select(ExperienceRow)).all()
            vals = [
                (Experience.model_validate_json(r.data), json.loads(r.embedding))
                for r in rows
            ]
            return (
                [
                    (e, v)
                    for e, v in vals
                    if e.status in (ExperienceStatus.VERIFIED, ExperienceStatus.TRUSTED)
                ]
                if eligible_only
                else vals
            )

    def save_skill(self, skill: Skill) -> None:
        with self.Session.begin() as s:
            s.merge(SkillRow(id=skill.skill_id, data=skill.model_dump_json()))

    def list_skills(self) -> list[Skill]:
        with self.Session() as s:
            return [
                Skill.model_validate_json(r.data)
                for r in s.scalars(select(SkillRow)).all()
            ]

    def update_experience(self, exp: Experience, embedding: list[float]) -> None:
        self.save_experience(exp, embedding)

    def record_metric(self, row: dict) -> None:
        with self.Session.begin() as s:
            s.add(MetricRow(**row))

    def metrics(self) -> list[dict]:
        with self.Session() as s:
            return [
                {
                    "mode": r.mode,
                    "experience_id": r.experience_id,
                    "similarity": r.similarity,
                    "applicability": r.applicability,
                    "model": r.model,
                    "latency_ms": r.latency_ms,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "experience_created": bool(r.experience_created),
                    "validation_status": r.validation_status,
                }
                for r in s.scalars(select(MetricRow)).all()
            ]
