"""Validate third-party API keys without exposing full values."""

from __future__ import annotations

import hashlib
import re
import time
from typing import Any, Literal

import httpx

from secmcp.resilience import retry_transient, with_validation_bulkhead

Provider = Literal["openai", "anthropic", "stripe", "supabase", "github", "aws"]

Status = Literal["valid", "invalid", "rate_limited", "network_error", "unknown"]

# ponytail: in-process TTL cache keyed by hash, not raw key
_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_CACHE_TTL_SEC = 120.0

_PROVIDER_PATTERNS: dict[Provider, re.Pattern[str]] = {
    "openai": re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    "anthropic": re.compile(r"sk-ant-api[0-9]{2}-[a-zA-Z0-9_-]{80,}"),
    "stripe": re.compile(r"sk_(live|test)_[a-zA-Z0-9]{24,}"),
    "github": re.compile(r"(ghp_|github_pat_)[a-zA-Z0-9_]{20,}"),
    "aws": re.compile(r"AKIA[0-9A-Z]{16}"),
    "supabase": re.compile(r"sbp_[a-zA-Z0-9]{40,}|eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]+\."),
}


def mask_key(key: str) -> str:
    key = key.strip()
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}…{key[-4:]}"


def detect_provider(key: str) -> Provider | None:
    for name, pat in _PROVIDER_PATTERNS.items():
        if pat.search(key):
            return name
    return None


def extract_key_from_code(code: str, provider: Provider | None) -> str | None:
    if provider:
        pat = _PROVIDER_PATTERNS.get(provider)
        if pat:
            m = pat.search(code)
            if m:
                return m.group(0)
    for pat in _PROVIDER_PATTERNS.values():
        m = pat.search(code)
        if m:
            return m.group(0)
    return None


def _cache_key(provider: str, key: str) -> str:
    digest = hashlib.sha256(f"{provider}:{key}".encode()).hexdigest()
    return digest


def _cached(provider: str, key: str) -> dict[str, Any] | None:
    ck = _cache_key(provider, key)
    entry = _CACHE.get(ck)
    if not entry:
        return None
    ts, payload = entry
    if time.monotonic() - ts > _CACHE_TTL_SEC:
        _CACHE.pop(ck, None)
        return None
    return payload


def _store_cache(provider: str, key: str, payload: dict[str, Any]) -> None:
    _CACHE[_cache_key(provider, key)] = (time.monotonic(), payload)


def _is_cacheable_status(status: str) -> bool:
    """Do not cache transient provider outcomes (invalidation / retry semantics)."""
    return status in ("valid", "invalid", "unknown")


async def validate_api_key(
    provider: str,
    key: str,
    *,
    supabase_url: str | None = None,
    aws_secret: str | None = None,
) -> dict[str, Any]:
    """Return status + message; never includes full key."""
    provider_norm = provider.lower().strip()
    if provider_norm not in _PROVIDER_PATTERNS:
        return {
            "provider": provider,
            "status": "unknown",
            "masked_key": mask_key(key),
            "message": f"Unsupported provider '{provider}'. Supported: openai, anthropic, stripe, supabase, github, aws.",
        }

    key = key.strip()
    if not key:
        return {
            "provider": provider_norm,
            "status": "invalid",
            "masked_key": "****",
            "message": "No API key provided.",
        }

    cached = _cached(provider_norm, key)
    if cached:
        return cached

    async def _attempt() -> dict[str, Any]:
        try:
            return await _validate(
                provider_norm,
                key,
                supabase_url=supabase_url,
                aws_secret=aws_secret,
            )
        except httpx.TimeoutException:
            return {
                "provider": provider_norm,
                "status": "network_error",
                "masked_key": mask_key(key),
                "message": "Request timed out while validating the key.",
            }
        except httpx.HTTPError:
            return {
                "provider": provider_norm,
                "status": "network_error",
                "masked_key": mask_key(key),
                "message": "Network error while validating the key.",
            }

    async def _run() -> dict[str, Any]:
        return await retry_transient(
            _attempt,
            is_transient=lambda r: r.get("status") in ("network_error", "rate_limited"),
        )

    result = await with_validation_bulkhead(_run())

    if _is_cacheable_status(str(result.get("status", ""))):
        _store_cache(provider_norm, key, result)
    return result


async def _validate(
    provider: str,
    key: str,
    *,
    supabase_url: str | None,
    aws_secret: str | None,
) -> dict[str, Any]:
    masked = mask_key(key)
    base = {"provider": provider, "masked_key": masked}

    async with httpx.AsyncClient(timeout=6.0) as client:
        if provider == "openai":
            r = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {key}"},
            )
            return _http_to_status(
                r,
                base,
                valid_msg="OpenAI key is valid.",
                invalid_msg="OpenAI key is invalid or revoked.",
            )

        if provider == "anthropic":
            r = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                },
            )
            return _http_to_status(
                r,
                base,
                valid_msg="Anthropic key is valid.",
                invalid_msg="Anthropic key is invalid or revoked.",
            )

        if provider == "stripe":
            r = await client.get(
                "https://api.stripe.com/v1/balance",
                auth=(key, ""),
            )
            return _http_to_status(
                r,
                base,
                valid_msg="Stripe secret key is valid.",
                invalid_msg="Stripe secret key is invalid.",
            )

        if provider == "github":
            r = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Accept": "application/vnd.github+json",
                },
            )
            return _http_to_status(
                r,
                base,
                valid_msg="GitHub token is valid.",
                invalid_msg="GitHub token is invalid or expired.",
            )

        if provider == "supabase":
            if not supabase_url:
                return {
                    **base,
                    "status": "unknown",
                    "message": "Supabase validation needs supabase_url (project REST URL).",
                }
            url = supabase_url.rstrip("/") + "/rest/v1/"
            r = await client.get(
                url,
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}",
                },
            )
            return _http_to_status(
                r,
                base,
                valid_msg="Supabase key accepted by project API.",
                invalid_msg="Supabase key rejected by project API.",
            )

        if provider == "aws":
            if not aws_secret:
                return {
                    **base,
                    "status": "unknown",
                    "message": "AWS validation needs aws_secret (secret access key) with the access key id.",
                }
            # STS GetCallerIdentity — minimal auth check
            import hmac
            import datetime as dt

            host = "sts.amazonaws.com"
            amz_date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            date_stamp = amz_date[:8]
            region = "us-east-1"
            service = "sts"
            params = "Action=GetCallerIdentity&Version=2011-06-15"
            canonical_headers = f"host:{host}\nx-amz-date:{amz_date}\n"
            signed_headers = "host;x-amz-date"
            payload_hash = hashlib.sha256(b"").hexdigest()
            canonical_request = (
                f"GET\n/\n{params}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
            )
            credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
            string_to_sign = (
                "AWS4-HMAC-SHA256\n"
                f"{amz_date}\n"
                f"{credential_scope}\n"
                f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
            )

            def sign(key_b: bytes, msg: str) -> bytes:
                return hmac.new(key_b, msg.encode(), hashlib.sha256).digest()

            k_date = sign(("AWS4" + aws_secret).encode(), date_stamp)
            k_region = sign(k_date, region)
            k_service = sign(k_region, service)
            k_signing = sign(k_service, "aws4_request")
            signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
            auth_header = (
                f"AWS4-HMAC-SHA256 Credential={key}/{credential_scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}"
            )
            r = await client.get(
                f"https://{host}/?{params}",
                headers={
                    "Authorization": auth_header,
                    "x-amz-date": amz_date,
                },
            )
            return _http_to_status(
                r,
                base,
                valid_msg="AWS access key pair is valid.",
                invalid_msg="AWS access key id or secret is invalid.",
            )

    return {**base, "status": "unknown", "message": "Validation not implemented."}


def _http_to_status(
    response: httpx.Response,
    base: dict[str, Any],
    *,
    valid_msg: str,
    invalid_msg: str,
) -> dict[str, Any]:
    if response.status_code == 429:
        return {**base, "status": "rate_limited", "message": "Provider rate-limited validation; try again shortly."}
    if response.status_code in (200, 201, 204):
        return {**base, "status": "valid", "message": valid_msg}
    if response.status_code in (401, 403):
        return {**base, "status": "invalid", "message": invalid_msg}
    if response.status_code >= 500:
        return {
            **base,
            "status": "network_error",
            "message": f"Provider returned server error ({response.status_code}).",
        }
    return {**base, "status": "invalid", "message": invalid_msg}
