import json
import shutil
from pathlib import Path

import pytest

from engine import ai_search, lint, pipeline, scorecard

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "northwind"


# ---------- linter ----------

def test_lint_flags_ai_tells():
    r = lint.lint_text("In today's fast-paced landscape, we leverage robust tools.\n")
    kinds = {f.kind for f in r.findings}
    assert "tic" in kinds and "banned" in kinds
    assert r.score < 100


def test_lint_requires_number_labels():
    bad = lint.lint_text("Teams cut close time by 40%.\n")
    good = lint.lint_text("Teams cut close time by 40% [Observed: 2025 cohort].\n")
    linked = lint.lint_text("Teams cut close time by 40% ([report](https://example.com)).\n")
    assert any(f.kind == "unsourced-number" for f in bad.findings)
    assert not any(f.kind == "unsourced-number" for f in good.findings)
    assert not any(f.kind == "unsourced-number" for f in linked.findings)


def test_lint_ignores_years_list_numbers_and_code():
    text = "1. Start in 2024 with 3 vendors.\n```\nx = 500\n```\n"
    assert not any(f.kind == "unsourced-number" for f in lint.lint_text(text).findings)


def test_baseline_scores_worse_than_clean_copy():
    baseline = lint.lint_file(EXAMPLE / "claude_baseline.md")
    clean = lint.lint_text("Start with recurring vendors. The controller trusts the system sooner.\n")
    assert baseline.score < 60 < clean.score


# ---------- human gates ----------

@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = tmp_path / "run"
    r.mkdir()
    shutil.copy(EXAMPLE / "interview.md", r / "interview.md")
    return r


def test_brief_needs_a_human_chosen_angle(run):
    with pytest.raises(pipeline.GateError):
        pipeline.run_stage(run, "brief")


def test_draft_and_repurpose_need_approvals(run):
    (run / "brief.md").write_text("brief")
    with pytest.raises(pipeline.GateError):
        pipeline.run_stage(run, "draft")
    pipeline.approve(run, "brief", "Editor")
    out = pipeline.run_stage(run, "draft")  # no key -> dry run writes prompt
    assert out[0].name == "draft.prompt.md"
    (run / "draft.md").write_text("draft")
    with pytest.raises(pipeline.GateError):
        pipeline.run_stage(run, "repurpose")
    pipeline.approve(run, "draft", "Editor")
    assert json.loads((run / "approvals.json").read_text())["draft"]["by"] == "Editor"


def test_review_always_writes_lint_report(run):
    (run / "brief.md").write_text("brief")
    (run / "draft.md").write_text("We leverage synergy.\n")
    outs = pipeline.run_stage(run, "review")
    assert (run / "lint_report.md").exists() and outs[0].name == "lint_report.md"


# ---------- AI search ----------

def test_ai_search_scores_example(tmp_path):
    proj = tmp_path / "ai"
    shutil.copytree(EXAMPLE / "ai-search", proj)
    res = ai_search.score(proj)
    assert res["answers"] == 12
    assert res["share_of_voice"]["Northwind"] == 4
    assert res["gaps"] == 6
    assert (proj / "ai_search_gaps.md").read_text().count("\n- ") == 6


def test_score_answer_rank_and_citation():
    us = ai_search.Brand("Northwind", [], "northwind.example")
    them = [ai_search.Brand("Brightledger", [])]
    s = ai_search.score_answer("Brightledger first, then Northwind (northwind.example).", us, them)
    assert s["brand_rank"] == 2 and s["brand_cited"] is True


# ---------- scorecard ----------

def test_scorecard_decisions():
    results = {r["url"]: r["decision"] for r in scorecard.decide(scorecard.load(EXAMPLE / "content_inventory.csv"))}
    assert results["/blog/ap-automation-guide"] == "CONSOLIDATE"
    assert results["/blog/what-is-ap-automation"] == "REFRESH"
    assert results["/blog/ap-trends-2023"] == "KILL"
    assert results["/blog/touchless-invoice-myth"] == "WATCH"
    assert results["/compare/northwind-vs-brightledger"] == "PROTECT"
