"""Content-to-pipeline scorecard.

Traffic is a leading indicator. The board asks about pipeline. This takes a
content inventory export (one row per piece) and returns a decision for each:

  PROTECT     earns pipeline and is still ranking or cited; leave it alone
  REFRESH     earned pipeline before but is decaying; update it this quarter
  CONSOLIDATE overlaps with a stronger piece on the same buyer question; merge and redirect
  KILL        no pipeline, no traffic, no citations after 12+ months; noindex or remove
  WATCH       too new or too little data to judge

Thresholds live in RULES so a team can argue about them in one place.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

RULES = {
    "min_age_months": 6,            # [Assumed] younger pieces get WATCH
    "decay_threshold": -0.30,       # [Assumed] 30%+ drop in sessions vs. prior period = decaying
    "kill_max_sessions": 50,        # [Assumed] monthly sessions under this...
    "kill_min_age_months": 12,      # ...after a year, with no pipeline and no AI citations
}

NUMERIC = ["sessions_now", "sessions_prior", "ai_citations", "influenced_pipeline", "sourced_pipeline", "cost", "age_months"]


def load(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in NUMERIC:
            r[k] = float(r.get(k) or 0)
    return rows


def decide(rows: list[dict], rules: dict = RULES) -> list[dict]:
    by_question = defaultdict(list)
    for r in rows:
        by_question[r["buyer_question"].strip().lower()].append(r)

    out = []
    for r in rows:
        prior = r["sessions_prior"]
        change = (r["sessions_now"] - prior) / prior if prior else 0.0
        earns = r["influenced_pipeline"] + r["sourced_pipeline"]
        siblings = by_question[r["buyer_question"].strip().lower()]
        strongest = max(siblings, key=lambda s: (s["influenced_pipeline"] + s["sourced_pipeline"], s["sessions_now"]))

        if r["age_months"] < rules["min_age_months"]:
            decision, why = "WATCH", "Too new to judge"
        elif len(siblings) > 1 and strongest is not r:
            decision, why = "CONSOLIDATE", f"Overlaps with {strongest['url']} on the same buyer question"
        elif earns > 0 and change <= rules["decay_threshold"]:
            decision, why = "REFRESH", f"Earns pipeline but sessions are down {abs(change):.0%}"
        elif earns > 0 or r["ai_citations"] > 0:
            decision, why = "PROTECT", "Earning pipeline or AI citations"
        elif r["sessions_now"] < rules["kill_max_sessions"] and r["age_months"] >= rules["kill_min_age_months"]:
            decision, why = "KILL", "No pipeline, no citations, negligible traffic after a year"
        else:
            decision, why = "WATCH", "Traffic but no pipeline yet; check conversion path"

        roi = earns / r["cost"] if r["cost"] else None
        out.append({**r, "session_change": round(change, 2), "pipeline_per_dollar": round(roi, 1) if roi is not None else "", "decision": decision, "reason": why})
    return out


def to_markdown(results: list[dict]) -> str:
    counts = defaultdict(int)
    for r in results:
        counts[r["decision"]] += 1
    total_pipe = sum(r["influenced_pipeline"] + r["sourced_pipeline"] for r in results)
    total_cost = sum(r["cost"] for r in results)
    lines = [
        "# Content scorecard",
        "",
        f"{len(results)} pieces · pipeline touched ${total_pipe:,.0f} · production cost ${total_cost:,.0f} (computed from the input file)",
        "",
        "| Decision | Count |",
        "|---|---:|",
        *[f"| {d} | {counts[d]} |" for d in ["PROTECT", "REFRESH", "CONSOLIDATE", "KILL", "WATCH"]],
        "",
        "| URL | Decision | Why | Sessions Δ | Pipeline per $1 |",
        "|---|---|---|---:|---:|",
    ]
    order = {"REFRESH": 0, "CONSOLIDATE": 1, "KILL": 2, "PROTECT": 3, "WATCH": 4}
    for r in sorted(results, key=lambda r: order[r["decision"]]):
        ppd = f"${r['pipeline_per_dollar']}" if r["pipeline_per_dollar"] != "" else "–"
        lines.append(f"| {r['url']} | {r['decision']} | {r['reason']} | {r['session_change']:+.0%} | {ppd} |")
    return "\n".join(lines) + "\n"


def write(results: list[dict], out_csv: Path) -> None:
    fields = list(results[0].keys()) if results else []
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)
