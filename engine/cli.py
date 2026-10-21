"""Command line entry point.

  python -m engine new runs/my-piece --interview notes.md
  python -m engine run runs/my-piece angles            (then write chosen_angle.md)
  python -m engine run runs/my-piece brief
  python -m engine approve runs/my-piece brief --by "Colin"
  python -m engine run runs/my-piece draft
  python -m engine run runs/my-piece review
  python -m engine approve runs/my-piece draft --by "Colin"
  python -m engine run runs/my-piece repurpose

  python -m engine lint path/to/draft.md [--min-score 80]
  python -m engine ai-search score examples/northwind/ai-search
  python -m engine ai-search capture examples/northwind/ai-search
  python -m engine scorecard examples/northwind/content_inventory.csv

Add --dry-run to any model stage to write the full prompt instead of calling the API.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import ai_search, lint, pipeline, scorecard


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="engine", description="AI-native content engine with human checkpoints.")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="Start a run folder from an SME interview")
    n.add_argument("run")
    n.add_argument("--interview", required=True)

    r = sub.add_parser("run", help="Run one pipeline stage")
    r.add_argument("run")
    r.add_argument("stage", choices=pipeline.STAGES)
    r.add_argument("--dry-run", action="store_true")

    a = sub.add_parser("approve", help="Record a human approval")
    a.add_argument("run")
    a.add_argument("artifact", choices=["brief", "draft"])
    a.add_argument("--by", required=True)

    l = sub.add_parser("lint", help="Run the editorial linter")
    l.add_argument("files", nargs="+")
    l.add_argument("--min-score", type=int, default=0)

    s = sub.add_parser("ai-search", help="AI-search visibility tracker")
    s.add_argument("action", choices=["score", "capture"])
    s.add_argument("project")
    s.add_argument("--dry-run", action="store_true")

    c = sub.add_parser("scorecard", help="Content-to-pipeline decisions")
    c.add_argument("inventory")
    c.add_argument("--out", default=None)

    args = p.parse_args(argv)

    try:
        if args.cmd == "new":
            run = Path(args.run)
            run.mkdir(parents=True, exist_ok=True)
            shutil.copy(args.interview, run / "interview.md")
            print(f"Run created at {run}. Next: engine run {run} angles")
        elif args.cmd == "run":
            for out in pipeline.run_stage(Path(args.run), args.stage, dry_run=args.dry_run):
                print(f"wrote {out}")
        elif args.cmd == "approve":
            pipeline.approve(Path(args.run), args.artifact, args.by)
            print(f"{args.artifact} approved by {args.by}")
        elif args.cmd == "lint":
            worst = 100
            for f in args.files:
                rep = lint.lint_file(f)
                print(rep.to_markdown(), end="\n\n")
                worst = min(worst, rep.score)
            if worst < args.min_score:
                print(f"FAIL: lowest score {worst} is under --min-score {args.min_score}")
                return 1
        elif args.cmd == "ai-search":
            if args.action == "capture":
                print(f"captured {ai_search.capture_claude(Path(args.project), dry_run=args.dry_run)} answers")
            res = ai_search.score(Path(args.project))
            print(f"scored {res['answers']} answers, {res['gaps']} high-priority gaps. See summary.md")
        elif args.cmd == "scorecard":
            results = scorecard.decide(scorecard.load(Path(args.inventory)))
            out = Path(args.out) if args.out else Path(args.inventory).with_name("scorecard.csv")
            scorecard.write(results, out)
            md = scorecard.to_markdown(results)
            out.with_suffix(".md").write_text(md, encoding="utf-8")
            print(md)
    except (pipeline.GateError, FileNotFoundError, ValueError) as e:
        print(f"Stopped: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
