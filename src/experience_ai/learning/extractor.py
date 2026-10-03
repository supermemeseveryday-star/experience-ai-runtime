import json
import uuid
from experience_ai.models.schemas import Experience
from experience_ai.models.enums import ExperienceStatus
from experience_ai.llm.base import LLMProvider


async def extract_experience(
    provider: LLMProvider, query: str, answer: str, temperature: float = 0.2
) -> Experience | None:
    prompt = (
        "Convert the solved problem and answer into a compact reusable experience JSON. "
        "Fields: problem_pattern, problem_summary, conditions (array), strategy (array), reasoning_principle, "
        "verification_method (array), failure_conditions (array), alternatives (array), confidence (0..1). "
        "Do not include hidden chain-of-thought. Return JSON only.\n\n"
        f"Problem: {query}\nAnswer: {answer}"
    )
    raw = await provider.generate(
        prompt,
        "Extract only reusable conclusions and steps. Never invent verification results.",
        temperature,
    )
    try:
        raw = raw[raw.index("{") : raw.rindex("}") + 1]
        data = json.loads(raw)
        data.update(
            experience_id="exp_" + uuid.uuid4().hex[:12],
            status=ExperienceStatus.CANDIDATE,
            usage_count=0,
            success_count=0,
            failure_count=0,
        )
        return Experience.model_validate(data)
    except (ValueError, KeyError, TypeError):
        return None
