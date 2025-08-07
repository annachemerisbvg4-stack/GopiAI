from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest

from gopiai.llm import ToolSpec, build_payload
from gopiai.llm.mock_provider import MockProvider


def test_openai_tools_serialization():
    tools = [
        ToolSpec(
            name="search_docs",
            description="Search in docs",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )
    ]
    payload = build_payload(
        provider="openrouter",
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "hi"}],
        tools=tools,
        temperature=0.2,
        top_p=0.95,
    )
    assert "tools" in payload
    assert isinstance(payload["tools"], list)
    assert payload["tools"][0]["type"] == "function"
    assert payload.get("tool_choice", "auto") == "auto"


def test_gemini_function_declarations():
    tools = [
        ToolSpec(
            name="search_docs",
            description="Search in docs",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )
    ]
    payload = build_payload(
        provider="google",
        model="gemini-1.5-pro",
        messages=[{"role": "user", "content": "hi"}],
        tools=tools,
        temperature=0.2,
        top_p=0.95,
    )
    assert "tools" in payload
    assert "function_declarations" in payload["tools"]
    assert payload["tools"]["function_declarations"][0]["name"] == "search_docs"


def test_mock_provider_openai_style_tool_call():
    tools = [
        ToolSpec(
            name="get_profile",
            description="Get user profile",
            parameters={
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"],
            },
        )
    ]
    provider = MockProvider(provider="openrouter", model="openai/gpt-4o")
    resp = provider.chat(
        messages=[{"role": "user", "content": "who am i?"}],
        tools=tools,
        temperature=0.2,
        top_p=0.9,
        tool_choice="auto",
    )
    assert "choices" in resp
    assert resp["choices"][0]["finish_reason"] in ("tool_calls", "stop")
    tool_calls = resp["choices"][0]["message"].get("tool_calls", [])
    assert tool_calls and tool_calls[0]["type"] == "function"


def test_mock_provider_gemini_style_function_call():
    tools = [
        ToolSpec(
            name="search_docs",
            description="Search in docs",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )
    ]
    provider = MockProvider(provider="google", model="gemini-1.5-pro")
    resp = provider.chat(
        messages=[{"role": "user", "content": "find"}],
        tools=tools,
        temperature=0.4,
    )
    assert "candidates" in resp
    parts = resp["candidates"][0]["content"].get("parts", [])
    assert parts and "functionCall" in parts[0]
