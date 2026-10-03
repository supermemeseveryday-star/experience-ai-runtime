from experience_ai.llm.base import LLMProvider


async def deep_reason(provider: LLMProvider, query: str, temperature: float) -> str:
    return await provider.generate(
        query,
        "You are a careful technical assistant. Solve the user's request and give a concise, verifiable answer. Before answering, check that the steps match the request, distinguish assumptions from facts, and never claim you ran a command unless you actually did. Do not provide hidden chain-of-thought.",
        temperature,
    )
