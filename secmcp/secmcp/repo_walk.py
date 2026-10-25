"""Repository file walk for Phase 2 CI (skip dirs aligned with vendor/mcp-guard, MIT)."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterable

# vendor/mcp-guard/mcp_guard/scanner.py IGNORE_FILE_NAME + ignore matching (MIT)
IGNORE_FILE_NAME = ".mcpguardignore"

# vendor/mcp-guard/mcp_guard/scanner.py SKIP_DIRS
SKIP_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        "dist",
        "build",
        ".next",
        "venv",
        ".venv",
        "__pycache__",
    }
)

MAX_FILE_BYTES = 2 * 1024 * 1024

# Binary / media extensions — skip (not secret scan targets in MVP).
BINARY_EXTENSIONS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".gz",
        ".tar",
        ".wasm",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".pyc",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
    }
)


def iter_repo_files(root: Path) -> Iterable[Path]:
    """Yield scannable files under root (or root itself if it is a file)."""
    root = root.expanduser().resolve()
    if root.is_file():
        yield root
        return
    if not root.is_dir():
        return

    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in dir_names if name not in SKIP_DIRS]
        for file_name in file_names:
            yield Path(current_root) / file_name


def should_skip_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        return path.stat().st_size > MAX_FILE_BYTES
    except OSError:
        return True


def load_ignore_patterns(root: Path) -> tuple[str, ...]:
    """Load `.mcpguardignore` patterns from scan root (directory or parent if root is a file)."""
    if root.is_file():
        ignore_file = root.parent / IGNORE_FILE_NAME
    else:
        ignore_file = root / IGNORE_FILE_NAME

    try:
        lines = ignore_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()

    patterns: list[str] = []
    for line in lines:
        pattern = line.strip()
        if not pattern or pattern.startswith("#"):
            continue
        patterns.append(pattern)
    return tuple(patterns)


def relative_display_path(path: Path, root: Path) -> str:
    if root.is_file():
        return path.name
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def is_ignored_path(rel_path: str, patterns: tuple[str, ...]) -> bool:
    normalized = rel_path.replace(os.sep, "/")
    parts = normalized.split("/")

    for pattern in patterns:
        normalized_pattern = pattern.replace(os.sep, "/").lstrip("./")
        if not normalized_pattern:
            continue

        if normalized_pattern.endswith("/"):
            directory = normalized_pattern.rstrip("/")
            if directory in parts or normalized.startswith(f"{directory}/"):
                return True
            continue

        if "/" in normalized_pattern:
            if fnmatch.fnmatch(normalized, normalized_pattern):
                return True
            continue

        if fnmatch.fnmatch(Path(normalized).name, normalized_pattern):
            return True
        if any(fnmatch.fnmatch(part, normalized_pattern) for part in parts):
            return True

    return False
