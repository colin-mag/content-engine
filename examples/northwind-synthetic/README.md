# Example: Northwind (synthetic)

**Everything in this folder is synthetic.** Northwind, Brightledger, Countwell and the SME are
fictional, and the AI-search "answers" were written by hand to exercise the tracker. Nothing here
describes a real company or a real engine response. It exists so anyone can run the engine end to
end without an API key or private data.

| File | What it is |
|---|---|
| `interview.md` | A 30-minute SME interview transcript, the input to the pipeline |
| `claude_baseline.md` | What Claude wrote from a one-line generic prompt, used in [BEAT_CLAUDE.md](../../BEAT_CLAUDE.md) |
| `claude_baseline.lint.md` | The linter's report on that baseline (generated) |
| `ai-search/` | Brand config, 6 buyer questions, sample answers from 2 engines, and the scored output (`tracker.csv`, `summary.md`, `ai_search_gaps.md`) |
| `content_inventory.csv` | A 12-page content inventory with traffic, citations, pipeline and cost |
| `scorecard.csv` / `scorecard.md` | The scorecard's PROTECT / REFRESH / CONSOLIDATE / KILL / WATCH calls (generated) |

Regenerate everything:

```bash
python -m engine lint examples/northwind-synthetic/claude_baseline.md > examples/northwind-synthetic/claude_baseline.lint.md
python -m engine ai-search score examples/northwind-synthetic/ai-search
python -m engine scorecard examples/northwind-synthetic/content_inventory.csv
```
