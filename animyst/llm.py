"""
ANIMYST LLM Integration — Provider streaming and settings management.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Generator

from animyst.storage import SettingsRepository


# ═══════════════════════════════════════════════════════════════
# Settings I/O
# ═══════════════════════════════════════════════════════════════

SETTINGS_REPOSITORY = SettingsRepository()


def load_settings() -> dict:
    """Load settings from the shared settings repository."""
    return SETTINGS_REPOSITORY.load()


def save_settings(settings: dict) -> None:
    """Save settings with restricted permissions."""
    SETTINGS_REPOSITORY.save(settings)


def get_api_key(provider: str) -> str | None:
    """Get API key for a provider. Checks settings.json first, then env vars."""
    settings = load_settings()
    keys = settings.get("api_keys", {})

    env_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
    }

    return keys.get(provider) or os.environ.get(env_map.get(provider, ""), None)


# ═══════════════════════════════════════════════════════════════
# Stream Events
# ═══════════════════════════════════════════════════════════════

@dataclass
class StreamEvent:
    """Event emitted during LLM streaming."""
    type: str  # "text", "error", "done"
    content: str = ""
    usage: dict | None = None


# ═══════════════════════════════════════════════════════════════
# Provider Streaming Functions
# ═══════════════════════════════════════════════════════════════

def stream_anthropic(
    messages: list[dict],
    model: str,
    system: str,
    temperature: float,
    max_tokens: int,
    api_key: str,
) -> Generator[StreamEvent, None, None]:
    """Stream from Anthropic's Messages API."""
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        with client.messages.stream(
            model=model,
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            for text in stream.text_stream:
                yield StreamEvent(type="text", content=text)

            response = stream.get_final_message()
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
            yield StreamEvent(type="done", usage=usage)

    except Exception as e:
        yield StreamEvent(type="error", content=str(e))


def stream_openai(
    messages: list[dict],
    model: str,
    system: str,
    temperature: float,
    max_tokens: int,
    api_key: str,
) -> Generator[StreamEvent, None, None]:
    """Stream from OpenAI's Chat Completions API."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        full_messages = [{"role": "system", "content": system}] + messages

        stream = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            stream_options={"include_usage": True},
        )

        usage = None
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield StreamEvent(type="text", content=chunk.choices[0].delta.content)
            if chunk.usage:
                usage = {
                    "input_tokens": chunk.usage.prompt_tokens,
                    "output_tokens": chunk.usage.completion_tokens,
                }

        yield StreamEvent(type="done", usage=usage)

    except Exception as e:
        yield StreamEvent(type="error", content=str(e))


def stream_google(
    messages: list[dict],
    model: str,
    system: str,
    temperature: float,
    max_tokens: int,
    api_key: str,
) -> Generator[StreamEvent, None, None]:
    """Stream from Google's Generative AI API."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])],
            ))

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        usage = None
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield StreamEvent(type="text", content=chunk.text)
            if chunk.usage_metadata:
                usage = {
                    "input_tokens": chunk.usage_metadata.prompt_token_count or 0,
                    "output_tokens": chunk.usage_metadata.candidates_token_count or 0,
                }

        yield StreamEvent(type="done", usage=usage)

    except Exception as e:
        yield StreamEvent(type="error", content=str(e))


# ═══════════════════════════════════════════════════════════════
# Dispatcher
# ═══════════════════════════════════════════════════════════════

PROVIDER_STREAMS = {
    "anthropic": stream_anthropic,
    "openai": stream_openai,
    "google": stream_google,
}


def stream_chat(
    messages: list[dict],
    model: str,
    provider: str,
    system: str = "You are a helpful assistant.",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> Generator[StreamEvent, None, None]:
    """Route streaming to the correct provider."""
    api_key = get_api_key(provider)
    if not api_key:
        yield StreamEvent(
            type="error",
            content=f"No API key for {provider}. Add one in Settings or set the environment variable.",
        )
        return

    stream_fn = PROVIDER_STREAMS.get(provider)
    if not stream_fn:
        yield StreamEvent(type="error", content=f"Unknown provider: {provider}")
        return

    yield from stream_fn(
        messages=messages,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
    )
