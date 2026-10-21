# Example: Northwind

Northwind sells accounts-payable automation to mid-market finance teams. This folder is one full
run of the engine against its content program, end to end and without an API key.

| File | What it is |
|---|---|
| `interview.md` | A 30-minute SME interview transcript, the input to the pipeline |
| `claude_baseline.md` | What Claude wrote from a one-line generic prompt, used in [BEAT_CLAUDE.md](../../BEAT_CLAUDE.md) |
| `claude_baseline.lint.md` | The linter's report on that baseline (generated) |
| `ai-search/` | Brand config, 6 buyer questions, answers from 2 engines, and the scored output (`tracker.csv`, `summary.md`, `ai_search_gaps.md`) |
| `content_inventory.csv` | A 12-page content inventory with traffic, citations, pipeline and cost |
| `scorecard.csv` / `scorecard.md` | The scorecard's PROTECT / REFRESH / CONSOLIDATE / KILL / WATCH calls (generated) |

Regenerate everything:

```bash
python -m engine lint examples/northwind/claude_baseline.md > examples/northwind/claude_baseline.lint.md
python -m engine ai-search score examples/northwind/ai-search
python -m engine scorecard examples/northwind/content_inventory.csv
```
