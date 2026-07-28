import json
import os
from typing import Optional

import httpx


GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqLLM:
    """Free-tier-friendly Groq text generation with a reliable local fallback."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: int = 120,
        fallback: Optional[str] = None,
    ) -> str:
        if not self.api_key:
            if fallback is not None:
                return fallback
            raise RuntimeError("GROQ_API_KEY is not configured and no local fallback was supplied.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.75,
            "max_completion_tokens": 2200,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(GROQ_CHAT_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            text = data["choices"][0]["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Groq returned an empty response.")
            return text.strip()
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            if fallback is not None:
                print(f"Groq request failed; using local fallback: {exc}")
                return fallback
            raise RuntimeError(f"Groq generation failed: {exc}") from exc
