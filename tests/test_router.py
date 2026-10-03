from experience_ai.models.enums import ReasoningMode


def test_thresholds(runtime):
    r = runtime.router
    assert r.route(0.95) == ReasoningMode.REUSE
    assert r.route(0.75) == ReasoningMode.PARTIAL_REASONING
    assert r.route(0.2) == ReasoningMode.DEEP_REASONING
    assert r.route(1, False) == ReasoningMode.DEEP_REASONING
