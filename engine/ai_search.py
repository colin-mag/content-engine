"""AI-search visibility tracker.

Buyers now ask ChatGPT, Perplexity, Gemini and Claude before they ever see a
search results page. This scores whether a brand shows up in those answers.

How it works:
1. List the buyer questions in queries.csv (query, intent, priority).
2. Save each engine's answer as answers/<engine>/<query-slug>.md. Paste them in
   by hand, or capture the Claude ones with `engine ai-search capture`.
3. `engine ai-search score` reads them and writes:
   - tracker.csv: one row per query x engine
   - summary.md: share of voice by brand, and the gaps
   - ai_search_gaps.md: the high-priority questions we're absent from, which
     the brief stage reads so new content targets them

Matching is deliberately simple (names and domains, case-insensitive). It
undercounts paraphrased mentions, so a human spot-checks the gaps list.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .llm import DryRun, complete


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


@dataclass
class Brand:
    name: str
    aliases: list[str]
    domain: str | None = None

    def patterns(self) -> list[re.Pattern]:
        return [re.compile(rf"\b{re.escape(a)}\b", re.I) for a in [self.name, *self.aliases]]


def load_config(project: Path) -> tuple[Brand, list[Brand]]:
    cfg = json.loads((project / "brands.json").read_text())
    us = Brand(**cfg["brand"])
    them = [Brand(**c) for c in cfg.get("competitors", [])]
    return us, them


def load_queries(project: Path) -> list[dict]:
    with open(project / "queries.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def first_mention(text: str, brand: Brand) -> int | None:
    hits = [m.start() for p in brand.patterns() for m in [p.search(text)] if m]
    return min(hits) if hits else None


def score_answer(text: str, us: Brand, them: list[Brand]) -> dict:
    brands = [us, *them]
    positions = {b.name: first_mention(text, b) for b in brands}
    mentioned = [b for b in brands if positions[b.name] is not None]
    ranked = sorted(mentioned, key=lambda b: positions[b.name])
    cited = bool(us.domain and re.search(re.escape(us.domain), text, re.I))
    return {
        "brand_mentioned": positions[us.name] is not None,
        "brand_rank": (ranked.index(us) + 1) if us in ranked else "",
        "brand_cited": cited,
        "competitors_mentioned": ";".join(b.name for b in ranked if b is not us),
    }


def score(project: Path) -> dict:
    project = Path(project)
    us, them = load_config(project)
    queries = load_queries(project)
    answers_root = project / "answers"
    engines = sorted(p.name for p in answers_root.iterdir() if p.is_dir()) if answers_root.exists() else []

    rows, sov, gaps = [], Counter(), []
    totals = defaultdict(int)
    for q in queries:
        slug = slugify(q["query"])
        for eng in engines:
            f = answers_root / eng / f"{slug}.md"
            if not f.exists():
                continue
            s = score_answer(f.read_text(encoding="utf-8"), us, them)
            rows.append({"query": q["query"], "intent": q.get("intent", ""), "priority": q.get("priority", ""), "engine": eng, **s})
            totals[eng] += 1
            if s["brand_mentioned"]:
                sov[us.name] += 1
            for c in filter(None, s["competitors_mentioned"].split(";")):
                sov[c] += 1
            if not s["brand_mentioned"] and q.get("priority", "").lower() == "high":
                gaps.append((q["query"], eng, s["competitors_mentioned"] or "nobody"))

    answered = len(rows)
    with open(project / "tracker.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["query", "intent", "priority", "engine", "brand_mentioned", "brand_rank", "brand_cited", "competitors_mentioned"])
        w.writeheader()
        w.writerows(rows)

    lines = [f"# AI-search visibility: {us.name}", "", f"[Observed] {answered} answers scored across {len(engines)} engine(s): {', '.join(engines) or 'none'}.", ""]
    lines += ["## Share of voice", "", "| Brand | Answers mentioning | Share |", "|---|---:|---:|"]
    for name in [us.name, *[b.name for b in them]]:
        pct = (100 * sov[name] / answered) if answered else 0
        lines.append(f"| {name} | {sov[name]} | {pct:.0f}% |")
    cited = sum(1 for r in rows if r["brand_cited"])
    lines += ["", f"[Observed] {us.name} was linked or cited by domain in {cited} of {answered} answers.", ""]
    lines += ["## High-priority gaps", ""]
    lines += [f"- **{q}** ({eng}): we're absent; mentioned instead: {who}" for q, eng, who in gaps] or ["- None. Check the medium-priority list next."]
    summary = "\n".join(lines) + "\n"
    (project / "summary.md").write_text(summary, encoding="utf-8")

    gap_md = "\n".join(["# Buyer questions we are not cited for (high priority)", ""] + [f"- {q} — engine: {eng}; cited instead: {who}" for q, eng, who in gaps]) + "\n"
    (project / "ai_search_gaps.md").write_text(gap_md, encoding="utf-8")
    return {"answers": answered, "share_of_voice": dict(sov), "gaps": len(gaps)}


def capture_claude(project: Path, dry_run: bool = False) -> int:
    """Ask Claude each buyer question cold, the way a buyer would, and save the answer.

    Note: without a web-search tool this reflects the model's training data,
    which is still a useful read on long-term brand association.
    """
    project = Path(project)
    out_dir = project / "answers" / "claude"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for q in load_queries(project):
        target = out_dir / f"{slugify(q['query'])}.md"
        if target.exists():
            continue
        try:
            text = complete("You are a helpful assistant. Answer the user's question directly and name specific vendors where relevant.", q["query"], max_tokens=1200, dry_run=dry_run)
        except DryRun:
            continue
        target.write_text(text, encoding="utf-8")
        n += 1
    return n
