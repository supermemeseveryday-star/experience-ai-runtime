from datetime import datetime, timezone
from experience_ai.models.enums import ExperienceStatus
from experience_ai.models.schemas import Experience


class ExperienceReview:
    """Explicit human approval gate for experiences that may be reused."""

    def promote_after_verification(
        self, experience: Experience, verification_confirmed: bool
    ) -> Experience:
        if experience.status != ExperienceStatus.CANDIDATE:
            raise ValueError("Only CANDIDATE experiences can be promoted.")
        if not verification_confirmed:
            raise ValueError(
                "Promote only after you have actually completed the listed verification."
            )
        experience.status = ExperienceStatus.VERIFIED
        experience.success_count += 1
        experience.updated_at = datetime.now(timezone.utc)
        return experience
