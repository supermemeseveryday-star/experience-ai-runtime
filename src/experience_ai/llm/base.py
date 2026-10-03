from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, prompt: str, system: str = "", temperature: float = 0.2
    ) -> str: ...
    @abstractmethod
    async def health_check(self) -> bool: ...
