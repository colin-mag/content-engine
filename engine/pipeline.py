"""The content pipeline: SME interview -> angles -> brief -> draft -> review -> repurpose.

Each run lives in its own folder, and every stage writes a file a person can
read and edit before the next stage runs. Two gates cannot be skipped in code:

* the brief needs a human-chosen angle (chosen_angle.md)
* drafting needs an approved brief, and repurposing needs an approved draft
  (recorded in approvals.json by `engine approve`)

A model never decides what the brand believes or what gets published.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import lint
from .llm import DryRun, complete

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
VOICE = ROOT / "voice" / "voice.md"

STAGES = ["angles", "brief", "draft", "review", "repurpose"]


class GateError(RuntimeError):
    """A human checkpoint hasn't been cleared."""


def _read(p: Path) -> str:
    if not p.exists():
        raise FileNotFoundError(f"Missing {p.name} in {p.parent}")
    return p.read_text(encoding="utf-8")


def _approvals(run: Path) -> dict:
    f = run / "approvals.json"
    return json.loads(f.read_text()) if f.exists() else {}


def approve(run: Path, artifact: str, approver: str) -> dict:
    if artifact not in {"brief", "draft"}:
        raise ValueError("Only 'brief' and 'draft' take approvals.")
    if not (run / f"{artifact}.md").exists():
        raise FileNotFoundError(f"No {artifact}.md to approve yet.")
    data = _approvals(run)
    data[artifact] = {"by": approver, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (run / "approvals.json").write_text(json.dumps(data, indent=2))
    return data


def _require(run: Path, artifact: str) -> None:
    if artifact not in _approvals(run):
        raise GateError(f"{artifact}.md isn't approved. Review it, then run: engine approve {run} {artifact} --by \"Your Name\"")


def _system(prompt_file: str) -> str:
    return f"{_read(PROMPTS / prompt_file)}\n\n---\n\n# Voice spec\n\n{_read(VOICE)}\n\n# Banned phrases\n\n" + ", ".join(lint.load_banned())


def _run_model(run: Path, stage: str, system: str, user: str, dry_run: bool) -> Path:
    out = run / f"{stage}.md"
    try:
        text = complete(system, user, dry_run=dry_run)
    except DryRun as dr:
        out = run / f"{stage}.prompt.md"
        text = str(dr)
    out.write_text(text, encoding="utf-8")
    return out


def run_stage(run: Path, stage: str, dry_run: bool = False) -> list[Path]:
    run = Path(run)
    interview = _read(run / "interview.md")

    if stage == "angles":
        return [_run_model(run, stage, _system("01_angles.md"), f"# SME material\n\n{interview}", dry_run)]

    if stage == "brief":
        angle = run / "chosen_angle.md"
        if not angle.exists():
            raise GateError("Pick an angle first: write it (edited however you like) to chosen_angle.md in the run folder.")
        tracker = run / "ai_search_gaps.md"
        extra = f"\n\n# AI-search gaps\n\n{tracker.read_text()}" if tracker.exists() else ""
        user = f"# Chosen angle\n\n{angle.read_text()}\n\n# SME material\n\n{interview}{extra}"
        return [_run_model(run, stage, _system("02_brief.md"), user, dry_run)]

    if stage == "draft":
        _require(run, "brief")
        return [_run_model(run, stage, _system("03_draft.md"), f"# Approved brief\n\n{_read(run / 'brief.md')}", dry_run)]

    if stage == "review":
        draft = _read(run / "draft.md")
        report = lint.lint_text(draft, path="draft.md")
        lint_path = run / "lint_report.md"
        lint_path.write_text(report.to_markdown(), encoding="utf-8")
        user = f"# Brief\n\n{_read(run / 'brief.md')}\n\n# Draft\n\n{draft}\n\n# Lint report\n\n{report.to_markdown()}"
        return [lint_path, _run_model(run, stage, _system("04_editorial_review.md"), user, dry_run)]

    if stage == "repurpose":
        _require(run, "draft")
        return [_run_model(run, stage, _system("05_repurpose.md"), f"# Approved article\n\n{_read(run / 'draft.md')}", dry_run)]

    raise ValueError(f"Unknown stage {stage!r}. Choose from: {', '.join(STAGES)}")
