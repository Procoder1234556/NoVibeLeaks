"""Prompt J — fixture catalog reduces FP on vendor-published example literals."""

from secmcp.scanner import check_secrets_sync


def test_aws_docs_example_key_suppressed() -> None:
    code = "AWS_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n"
    assert check_secrets_sync(code=code)["count"] == 0


def test_realistic_aws_key_still_flagged() -> None:
    code = "AWS_ACCESS_KEY = 'AKIAIOSFODNN7NOTREAL'\n"
    assert check_secrets_sync(code=code)["count"] >= 1
