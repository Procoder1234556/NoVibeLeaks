"""Mocked HTTP validation for all supported API key providers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from secmcp.api_keys import _CACHE, validate_api_key

# Test-shaped literals (not real credentials).
OPENAI_KEY = "sk-" + "a" * 48
ANTHROPIC_KEY = "sk-ant-api03-" + "A" * 90
STRIPE_KEY = "sk_test_" + "a" * 24
GITHUB_KEY = "ghp_" + "a" * 36
AWS_KEY = "AKIA" + "A" * 16
SUPABASE_KEY = "sbp_" + "a" * 40


@pytest.fixture(autouse=True)
def clear_validation_cache() -> None:
    _CACHE.clear()


def _mock_httpx_client(status_code: int = 200) -> MagicMock:
    mock_response = MagicMock(status_code=status_code)
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.mark.asyncio
async def test_openai_valid_mocked() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(200)):
        out = await validate_api_key("openai", OPENAI_KEY)
    assert out["status"] == "valid"
    assert "OpenAI" in out["message"]


@pytest.mark.asyncio
async def test_anthropic_invalid_mocked() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(401)):
        out = await validate_api_key("anthropic", ANTHROPIC_KEY)
    assert out["status"] == "invalid"


@pytest.mark.asyncio
async def test_stripe_valid_mocked() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(200)):
        out = await validate_api_key("stripe", STRIPE_KEY)
    assert out["status"] == "valid"


@pytest.mark.asyncio
async def test_github_valid_mocked() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(200)):
        out = await validate_api_key("github", GITHUB_KEY)
    assert out["status"] == "valid"


@pytest.mark.asyncio
async def test_supabase_requires_url() -> None:
    out = await validate_api_key("supabase", SUPABASE_KEY)
    assert out["status"] == "unknown"
    assert "supabase_url" in out["message"]


@pytest.mark.asyncio
async def test_supabase_valid_mocked() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(200)):
        out = await validate_api_key(
            "supabase",
            SUPABASE_KEY,
            supabase_url="https://example.supabase.co",
        )
    assert out["status"] == "valid"


@pytest.mark.asyncio
async def test_aws_requires_secret() -> None:
    out = await validate_api_key("aws", AWS_KEY)
    assert out["status"] == "unknown"
    assert "aws_secret" in out["message"]


@pytest.mark.asyncio
async def test_aws_valid_mocked() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(200)):
        out = await validate_api_key("aws", AWS_KEY, aws_secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    assert out["status"] == "valid"


@pytest.mark.asyncio
async def test_rate_limited_not_cached() -> None:
    with patch("secmcp.api_keys.httpx.AsyncClient", return_value=_mock_httpx_client(429)):
        first = await validate_api_key("openai", OPENAI_KEY)
        second = await validate_api_key("openai", OPENAI_KEY)
    assert first["status"] == "rate_limited"
    assert second["status"] == "rate_limited"
