from experience_ai.models.schemas import Experience
from experience_ai.llm.base import LLMProvider


async def partial_reason(
    provider: LLMProvider, query: str, exp: Experience, temperature: float
) -> str:
    prompt = f"Current problem: {query}\n\nVerified experience:\nPattern: {exp.problem_pattern}\nConditions: {exp.conditions}\nStrategy: {exp.strategy}\nPrinciple: {exp.reasoning_principle}\n\nState what differs, what remains valid, what must be adapted, then answer. Do not reveal hidden chain-of-thought; provide concise conclusions and steps."
    return await provider.generate(
        prompt,
        "You are a careful local assistant. Prefer verified applicable steps; flag uncertainty.",
        temperature,
    )
