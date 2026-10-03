from fastapi.testclient import TestClient
from experience_ai.api.server import create_app


def test_api_health_and_openai_shape(runtime):
    c = TestClient(create_app(runtime))
    assert c.get("/health").status_code == 200
    assert (
        c.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "fresh question"}]},
        ).json()["object"]
        == "chat.completion"
    )
