# The AI-native content playbook

How I'd run a B2B content function where agents do the production work and people do the
judgment. The code in this repo is one implementation. This page is the operating model behind it.

Every number on this page is a planning assumption, labeled as such. 

---

## 1. The team

| Role | Owns | AI does |
|---|---|---|
| **Head of Content** | What we believe, what we publish, what we kill, the number we're accountable for | Research, first-pass analysis, reporting |
| **Managing editor** | Briefs, the edit, the ship decision | Briefs, drafts, lint, review notes |
| **SMEs** (customers, CS, product, execs) | The raw insight, approving their quotes and anything under their name | Turning a 30-minute interview into angles, drafts and posts |
| **Freelancers / video editor** | The pieces that need craft: reported features, design, video | Briefs they can work from without a call |

[Assumed] A lead, one editor and a freelance bench can match the output of a traditional 5–6 person
team. The constraint moves from writing hours to SME time and editorial attention, so that's what the
cadence below protects.

## 2. The weekly cadence

| Day | What happens | Human or agent |
|---|---|---|
| Mon | Two SME interviews (30 min each), recorded and transcribed | Human |
| Mon | `angles` stage on each transcript | Agent |
| Tue | Editor picks angles; `brief` stage; SME approves the proof inventory | Human → agent → human |
| Wed | `draft` → `review` (lint + editorial review) | Agent |
| Thu | Edit, approve, `repurpose` | Human → agent |
| Fri | Publish and distribute; scorecard and AI-search check on last month's pieces | Human + agent |

[Assumed] 2 pillar pieces and 10+ derivative assets a week from about 1 hour of SME time each.

## 3. What we measure (in this order)

1. **Pipeline touched by content**: sourced and influenced, from the CRM, reviewed with RevOps monthly
2. **AI-search share of voice**: how often we're named and cited for the buyer questions we target
3. **Sales usage**: how often reps send our content in deals, from the sales-enablement tool or CRM
4. **Organic sessions and rankings**: a leading indicator, never the headline

Traffic going down while pipeline and AI citations go up is a fine quarter. Reporting it the other
way round is how content teams lose budget.

## 4. The AI-search program

Buyers increasingly ask an AI assistant before they search. A content team that only optimizes for
blue links is optimizing for a shrinking slice of discovery.

1. Write down the 25–50 questions a buyer asks before shortlisting vendors. Sales and CS calls are the source, not keyword tools.
2. Capture answers from ChatGPT, Perplexity, Gemini and Claude monthly (`engine ai-search capture` plus manual pastes).
3. Score share of voice and citations (`engine ai-search score`).
4. Every high-priority gap becomes a brief, written so a model can lift a clean answer: a direct
   40–60 word answer near the top, consistent entity names, one table or list, and a named expert.
5. Earn citations off-site too: answer engines lean on third-party sources (reviews, communities,
   partner pages, analyst write-ups), so the distribution plan includes them.

## 5. The content inventory

Most B2B blogs have more pages hurting them than helping. Every quarter, run `engine scorecard` on the
full inventory and act on every row:

- **PROTECT**: earning pipeline or AI citations; don't touch it
- **REFRESH**: earned pipeline before but decaying; update facts, structure and the direct answer
- **CONSOLIDATE**: two pages answering the same buyer question; merge into the stronger one and redirect
- **KILL**: no pipeline, no citations, negligible traffic after a year; noindex or remove
- **WATCH**: too new, or traffic without pipeline; fix the conversion path first

## What stays human

These are deliberate, and the code enforces the first four:

1. **Picking the angle.** Deciding what the company believes is the job. A model can propose; it can't choose.
2. **Approving the proof.** Every number and quote gets an owner before it reaches a draft.
3. **The ship decision.** A person approves the draft. The review stage informs it and nothing more.
4. **Anything under a person's name.** SMEs approve their own posts and quotes.
5. **Killing content.** Removing pages touches SEO, sales collateral and sometimes legal. The scorecard recommends; a person decides.
6. **Customer and competitor claims.** Anything comparative or about a named customer goes through legal or the customer.
7. **The interview.** The best material comes from a follow-up question a person thought to ask.

## What breaks this model

- **SME access dries up.** Without fresh interviews the engine recycles itself. Protect the Monday slots like revenue meetings.
- **The editor becomes a rubber stamp.** Volume pressure turns approval into a click. Track how often the editor sends drafts back; if it's zero, something's wrong.
- **Attribution is weak.** If the CRM can't tell content-touched deals apart, lead with AI-search share of voice and sales usage until it can.
- **The voice spec goes stale.** Update `banned_phrases.txt` whenever an editor fixes the same thing twice.
