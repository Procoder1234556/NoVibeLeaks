from __future__ import annotations

import pytest

from secmcp.api_keys import _is_cacheable_status
from secmcp.resilience import retry_transient


def test_cacheable_status_excludes_transient() -> None:
    assert _is_cacheable_status("valid")
    assert _is_cacheable_status("invalid")
    assert not _is_cacheable_status("network_error")
    assert not _is_cacheable_status("rate_limited")


@pytest.mark.asyncio
async def test_retry_transient_stops_on_success() -> None:
    calls = 0

    async def op() -> str:
        nonlocal calls
        calls += 1
        return "ok"

    out = await retry_transient(op, is_transient=lambda _: False)
    assert out == "ok"
    assert calls == 1


@pytest.mark.asyncio
async def test_retry_transient_retries_then_gives_up() -> None:
    calls = 0

    async def op() -> dict[str, str]:
        nonlocal calls
        calls += 1
        return {"status": "network_error"}

    out = await retry_transient(
        op,
        is_transient=lambda r: r["status"] == "network_error",
        max_attempts=3,
    )
    assert out["status"] == "network_error"
    assert calls == 3
