from abc import ABC, abstractmethod

import httpx

from backend.app.config import get_settings


class ProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict[str, str]]) -> str:
        ...


class OpenAICompatibleProvider(AIProvider):
    def __init__(self, endpoint: str, key_name: str, model: str):
        self.endpoint = endpoint
        self.key_name = key_name
        self.model = model

    async def complete(self, messages):
        s = get_settings()
        key = getattr(s, self.key_name)
        if not key:
            raise ProviderError(f"{self.key_name.upper()} is not configured.")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.endpoint,
                    json={"model": self.model, "messages": messages, "temperature": 0.2},
                    headers={"Authorization": "Bearer " + key},
                )
            if response.status_code >= 400:
                raise ProviderError(f"AI provider returned HTTP {response.status_code}.")
            return response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("AI provider request failed; check the key, model and network.") from exc


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self):
        s = get_settings()
        super().__init__("https://api.openai.com/v1/chat/completions", "openai_api_key", s.ai_model)


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self):
        s = get_settings()
        model = s.ai_model if s.ai_model and s.ai_model != "gpt-4.1-mini" else "llama-3.3-70b-versatile"
        super().__init__("https://api.groq.com/openai/v1/chat/completions", "groq_api_key", model)


class GeminiProvider(AIProvider):
    async def complete(self, messages):
        s = get_settings()
        if not s.gemini_api_key:
            raise ProviderError("GEMINI_API_KEY is not configured.")
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in messages if m["role"] != "system"
        ]
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Please help."}]}]
        system_text = "\n".join(m["content"] for m in messages if m["role"] == "system")
        payload = {"contents": contents}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/" + s.ai_model + ":generateContent",
                    headers={"x-goog-api-key": s.gemini_api_key},
                    json=payload,
                )
            if response.status_code >= 400:
                raise ProviderError(f"Gemini returned HTTP {response.status_code}.")
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("Gemini request failed; check the key, model and network.") from exc


def get_provider():
    provider = get_settings().ai_provider.lower()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "groq":
        return GroqProvider()
    return OpenAIProvider()
