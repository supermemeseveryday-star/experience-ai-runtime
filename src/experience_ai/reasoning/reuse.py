from experience_ai.models.schemas import Experience


def reuse_answer(exp: Experience) -> str:
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(exp.strategy, 1))
    answer = f"{exp.problem_summary}\n\nRecommended approach:\n{steps}"
    if exp.reasoning_principle:
        answer += f"\n\nPrinciple: {exp.reasoning_principle}"
    answer += f"\n\nVerify with: {', '.join(exp.verification_method) or 'confirm the expected result'}"
    if exp.failure_conditions:
        answer += f"\n\nWatch for: {', '.join(exp.failure_conditions)}"
    if exp.alternatives:
        answer += f"\n\nAlternatives: {', '.join(exp.alternatives)}"
    return answer
