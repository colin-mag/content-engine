# Beat Claude

**Claude can write the article. It can't decide what a company believes, which questions buyers
are asking AI about it, or which half of the blog to delete.** This repo is built around that gap.

The test below is simple. I gave Claude the generic brief most teams actually give it, then ran
the same company's SME interview through the engine. Everything here can be reproduced from the
files in [`examples/northwind/`](examples/northwind/).

---

## Round 1: the prompt most teams use

> "Write a blog post about AP automation for mid-market finance teams."

Output: [`claude_baseline.md`](examples/northwind/claude_baseline.md). It's fluent,
well structured and on topic. It's also unpublishable:

| Problem | Where it shows up | Why it matters |
|---|---|---|
| **It contradicts the company's own expert** | "Start with your highest-volume, most complex vendors." The SME says the opposite: complex vendors are why rollouts stall. | Generic advice published under your brand teaches the market the wrong thing about your product. |
| **It repeats the category myth the company wants to kill** | "Aim for 100% touchless processing." The SME calls that "a bad goal." | The most differentiated idea in the interview is gone, replaced by the competitor's talking point. |
| **It invents numbers** | "Reduce invoice processing time by up to 80%," "save thousands of dollars per month." No source. | One screenshot of a fake stat from a skeptical CFO and the brand's credibility is gone. |
| **It misses the buyer's real fear** | Nothing about audit or approval trails. | The SME says audit is what closes deals. |
| **It sounds like everyone else** | "In today's fast-paced business landscape…", "game-changer," "unlock." | It fails the swap test: any competitor could publish it unchanged. |

**Editorial lint score: 44/100** with 15 findings
([report](examples/northwind/claude_baseline.lint.md)). Reproduce it:

```bash
python -m engine lint examples/northwind/claude_baseline.md
```

None of this is Claude being bad at writing. It's Claude doing exactly what it was asked with
no point of view, no source material and no editor.

---

## Round 2: the same model inside a system

The engine uses the same model. What changes is what it's given, what it's forbidden to do, and
where a person has to sign off.

| Baseline failure | What the engine does about it | Where |
|---|---|---|
| Contradicts the expert | Every angle must quote the SME transcript. No quote, no angle. | [`prompts/01_angles.md`](prompts/01_angles.md) |
| Loses the differentiated idea | At least 2 of 5 angles must disagree with category advice, and a **person** picks the angle. The brief stage won't run until `chosen_angle.md` exists. | [`engine/pipeline.py`](engine/pipeline.py) |
| Invents numbers | The brief carries a proof inventory. The draft may only use numbers on it, each with a source label. Gaps become `[NEEDS PROOF]`, never a made-up stat. The SME approves the inventory before drafting. | [`prompts/02_brief.md`](prompts/02_brief.md), [`prompts/03_draft.md`](prompts/03_draft.md) |
| Misses what buyers ask | The AI-search tracker shows which buyer questions the brand is absent from in ChatGPT and Perplexity answers, and the gaps feed straight into the brief. | [`engine/ai_search.py`](engine/ai_search.py) |
| Sounds generic | A deterministic linter blocks banned phrases, AI tics and unlabeled numbers. A review stage runs the swap test. | [`engine/lint.py`](engine/lint.py), [`prompts/04_editorial_review.md`](prompts/04_editorial_review.md) |
| Nobody owns the result | `engine approve` records who approved the brief and the draft. Repurposing for the SME's LinkedIn won't run without it. | [`engine/pipeline.py`](engine/pipeline.py) |

On the Northwind data, the tracker also shows the brand is absent from the answer for
"which invoices should I automate first" in both engines
([summary](examples/northwind/ai-search/summary.md)). That is the exact question the SME has
the strongest opinion on. That's the first piece I'd commission, and no blank-prompt Claude
session would have found it.

---

## Where Claude still wins (and should)

This isn't a case against AI. In this system the model does most of the hours:

- Turning a 30-minute interview into five grounded angles in minutes instead of an afternoon [Estimated]
- Writing briefs a freelancer can execute without a call
- First drafts, and every repurposed asset after approval
- Capturing and re-scoring AI-search answers every month

What it doesn't do is decide what the company believes, approve a number, publish under a
person's name, or delete content. Those stay human. See [PLAYBOOK.md](PLAYBOOK.md#what-stays-human).

---

## What breaks it

- **Bad interviews in, bad angles out.** If the SME gives safe answers, the angle stage has nothing
  contrarian to quote. The fix is a better interviewer, not a better prompt.
- **The linter can be gamed.** A draft can score 100 and still be boring. It is a floor, not a judge.
- **AI-search matching is literal.** It counts names and domains, so it misses paraphrased mentions.
  A person spot-checks the gaps list before acting on it.
- **The scorecard is only as honest as the attribution behind it.** If "influenced pipeline" is
  computed loosely in the CRM, the REFRESH/KILL calls inherit that error.
