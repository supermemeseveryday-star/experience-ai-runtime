from experience_ai.models.schemas import Experience
from experience_ai.models.enums import ExperienceStatus
from experience_ai.learning.consolidator import Consolidator


def test_consolidation_needs_multiple_verified():
    one = Experience(
        experience_id="1",
        problem_pattern="ffmpeg convert",
        problem_summary="x",
        strategy=["inspect"],
        status=ExperienceStatus.VERIFIED,
    )
    assert not Consolidator().consolidate([one])
    two = one.model_copy(update={"experience_id": "2"})
    assert len(Consolidator().consolidate([one, two])) == 1


def test_candidate_requires_explicit_verification_to_promote():
    from experience_ai.learning.review import ExperienceReview

    candidate = Experience(
        experience_id="review",
        problem_pattern="test",
        problem_summary="test",
        status=ExperienceStatus.CANDIDATE,
    )
    review = ExperienceReview()
    try:
        review.promote_after_verification(candidate, False)
        assert False, "unverified candidates must not be promoted"
    except ValueError:
        pass
    verified = review.promote_after_verification(candidate, True)
    assert verified.status == ExperienceStatus.VERIFIED and verified.success_count == 1
