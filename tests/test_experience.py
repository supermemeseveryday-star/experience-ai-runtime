from experience_ai.models.schemas import Experience
from experience_ai.models.enums import ExperienceStatus


def test_sqlite_persistence(runtime):
    e = Experience(
        experience_id="exp_test",
        problem_pattern="python venv",
        problem_summary="Use a venv",
        strategy=["Create venv"],
        status=ExperienceStatus.VERIFIED,
    )
    runtime.store.add(e)
    assert runtime.store.get("exp_test").strategy == ["Create venv"]
    assert runtime.store.list(eligible_only=True)[0].experience_id == "exp_test"
