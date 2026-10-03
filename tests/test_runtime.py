import pytest
from experience_ai.models.enums import ReasoningMode, ExperienceStatus
from experience_ai.models.schemas import Experience


@pytest.mark.asyncio
async def test_deep_creates_candidate(runtime):
    result = await runtime.chat("new Python question")
    assert result.mode == ReasoningMode.DEEP_REASONING and result.experience_created
    assert runtime.store.list()[0].status == ExperienceStatus.CANDIDATE


@pytest.mark.asyncio
async def test_reuse_only_verified(runtime):
    e = Experience(
        experience_id="verified",
        problem_pattern="question",
        problem_summary="Solved",
        strategy=["Do it"],
        status=ExperienceStatus.VERIFIED,
        confidence=1,
        success_count=9,
    )
    runtime.store.add(e)
    res = await runtime.chat("question Solved Do it")
    assert res.mode == ReasoningMode.REUSE
