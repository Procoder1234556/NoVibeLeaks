"""SecMCP — security layer MCP server (stdio)."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from secmcp.scanner import (
    check_secrets_sync,
    list_rules_summary,
    scan_vibe_bugs_sync,
    security_score_async,
    validate_key_for_tool,
)

mcp = MCPServer(
    "NoVibeLeaks",
    instructions=(
        "Real-time security checks for vibe-coded apps: secrets, API key validation, "
        "and common LLM anti-patterns. Pass code snippets or file paths. "
        "Every scan returns detailed_report, interactive_graph (Mermaid flowchart for "
        "in-chat rendering), and vibe_stage (1–15). For a full repo walk, pass a "
        "directory path to get_security_score and set write_vulnerabilities_txt=true "
        "to emit vulnerabilities.txt listing every finding."
    ),
)


@mcp.tool()
def check_secrets(code: str | None = None, path: str | None = None) -> dict:
    """Detect hardcoded secrets (API keys, tokens, private keys) in code or a file."""
    try:
        return check_secrets_sync(code=code, path=path)
    except FileNotFoundError as e:
        raise ToolError(str(e)) from e
    except ValueError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
async def validate_api_key(
    provider: str | None = None,
    key: str | None = None,
    code: str | None = None,
    path: str | None = None,
    supabase_url: str | None = None,
    aws_secret: str | None = None,
) -> dict:
    """Check whether an API key is still valid. Never returns the full key."""
    try:
        return await validate_key_for_tool(
            provider=provider,
            key=key,
            code=code,
            path=path,
            supabase_url=supabase_url,
            aws_secret=aws_secret,
        )
    except FileNotFoundError as e:
        raise ToolError(str(e)) from e
    except ValueError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
def scan_vibe_bugs(code: str | None = None, path: str | None = None) -> dict:
    """Scan for common AI-generated security and configuration issues."""
    try:
        return scan_vibe_bugs_sync(code=code, path=path)
    except FileNotFoundError as e:
        raise ToolError(str(e)) from e
    except ValueError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
async def get_security_score(
    code: str | None = None,
    path: str | None = None,
    validate_keys: bool = False,
    supabase_url: str | None = None,
    write_vulnerabilities_txt: bool = False,
    vulnerabilities_path: str | None = None,
) -> dict:
    """Overall security score; directory path walks the repo. Optional vulnerabilities.txt export."""
    try:
        return await security_score_async(
            code=code,
            path=path,
            validate_keys=validate_keys,
            supabase_url=supabase_url,
            write_vulnerabilities_txt=write_vulnerabilities_txt,
            vulnerabilities_path=vulnerabilities_path,
        )
    except FileNotFoundError as e:
        raise ToolError(str(e)) from e
    except ValueError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
def list_available_rules() -> dict:
    """List loaded declarative YAML rules (name, severity, category)."""
    return list_rules_summary()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
