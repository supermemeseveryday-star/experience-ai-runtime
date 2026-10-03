import httpx
from .base import LLMProvider


class OllamaError(RuntimeError):
    pass


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "qwen", base_url: str = "http://localhost:11434"):
        self.model, self.base_url = model, base_url.rstrip("/")

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2) as c:
                r = await c.get(f"{self.base_url}/api/tags")
                return r.is_success
        except httpx.HTTPError:
            return False

    async def model_available(self) -> bool:
        """Return whether the configured model is already installed locally."""
        try:
            async with httpx.AsyncClient(timeout=2) as c:
                r = await c.get(f"{self.base_url}/api/tags")
                r.raise_for_status()
                names = {item.get("name", "") for item in r.json().get("models", [])}
                return self.model in names or f"{self.model}:latest" in names
        except (httpx.HTTPError, ValueError):
            return False

    async def generate(
        self, prompt: str, system: str = "", temperature: float = 0.2
    ) -> str:
        try:
            async with httpx.AsyncClient(timeout=180) as c:
                r = await c.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": system,
                        "stream": False,
                        "options": {"temperature": temperature},
                    },
                )
                r.raise_for_status()
                return r.json().get("response", "").strip()
        except httpx.ConnectError as e:
            raise OllamaError(
                "Ollama is unavailable. Start it with `ollama serve`, then ensure your configured local Qwen model is available (`ollama list`)."
            ) from e
        except httpx.HTTPError as e:
            raise OllamaError(
                f"Ollama request failed for model '{self.model}': {e}"
            ) from e
