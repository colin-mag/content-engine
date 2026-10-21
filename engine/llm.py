"""Thin wrapper around the Anthropic API.

Every stage goes through `complete()`. With --dry-run (or no API key) the
assembled prompt is written out instead, so the pipeline can be inspected
and reviewed without spending tokens.
"""

from __future__ import annotations

import os

DEFAULT_MODEL = os.environ.get("CONTENT_ENGINE_MODEL", "claude-sonnet-4-5")


class DryRun(Exception):
    """Raised when a stage is run without calling the model."""


def complete(system: str, user: str, *, max_tokens: int = 4000, dry_run: bool = False) -> str:
    if dry_run or not os.environ.get("ANTHROPIC_API_KEY"):
        raise DryRun(f"# SYSTEM\n\n{system}\n\n# USER\n\n{user}\n")

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise SystemExit("Install the SDK first: pip install -r requirements.txt") from exc

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")
