# Track record

Where I've led content and growth, and the AI systems I'm building now. Client results and
references from agency and in-house roles are available on request; I don't publish client
numbers without permission.

---

## Open Athletes: Co-founder, growth (2026–present)

A live show and media platform helping former athletes and military veterans move into the
workforce, plus an athlete-entrepreneurship venture built around it.

**What I own:** the growth thesis and go-to-market, positioning, YouTube and social strategy,
distribution systems and paid media.

**What I built: Launchcodex**, a pre-publish production system for every episode, run with Claude:

1. **Caption QC audit:** checks the transcript for mis-heard names, brands and numbers before anything is indexed
2. **Keyword clustering:** keyword targets drawn strictly from what's actually said on camera, never from keyword tools alone
3. **Metadata drafting:** titles, descriptions and chapters for YouTube
4. **Platform-native distribution:** separate captions and copy for YouTube, TikTok, Instagram, Facebook, X, Spotify and Apple Podcasts, each anchored on one shareable moment

**Proof it works:** a retroactive audit of an already-live episode found search engines indexing
two transcription errors: "85000" where the guest said "Inc. 5000," and a misspelling of former NFL
linebacker Luke Kuechly's name. It also caught an inconsistency between "Mind Ready" and "MindReady."
Errors like these quietly cost discovery, and nobody catches them by hand at publishing speed.
The same checks now run before every new episode ships.

The [`engine/lint.py`](engine/lint.py) quality gate in this repo comes from the same idea:
automate the checks so the people can spend their time on judgment.

---

## RSA Growth Engine: AI Google Ads diagnostic system (in development)

From my paid search consulting work. It's a multi-stage reasoning system that diagnoses ad
performance problems across accounts at scale. I'm building it with Claude Code, Conductor
(parallel Claude Code sessions in isolated git worktrees) and GitHub.

**Design choices I made deliberately:**

- **Separate reasoning modes:** diagnose, then challenge the diagnosis, then generate hypotheses. A
  single prompt that does all three agrees with itself.
- **Read-only first stage, confidence calibration and shadow mode:** it recommends alongside a human
  before it's trusted to act.
- **Validation before orchestration:** each prompt contract is hand-tested against real account
  evidence before anything gets automated. The expensive failure isn't broken infrastructure. It's
  flawless execution of flawed logic, which produces confidently wrong diagnoses at scale.

Same principle as this repo: the human gates come first, then the automation.

---

## Thatch: Content Lead (2025)

Led content at Thatch.

## Right Percent: Director of Content Strategy (2020–2025)

Five years leading content strategy.

## Layover Marketing: Co-founder (2015–2020)

Co-founded and ran the agency for five years.

## NYU Stern: Guest instructor (fall 2024–present)

I teach B2B content strategy and AI search: how buyers' discovery is moving from search results to
AI answers, and what content teams have to change because of it. The
[AI-search tracker](engine/ai_search.py) in this repo is the working version of what I teach.

---

## How I use AI day to day

- **Claude Code + Conductor + GitHub** to build my own tools (like this repo and the Ads diagnostic
  system), with several agent sessions working in parallel on separate branches
- **Claude** as the production layer for content: pre-publish caption QC, keyword clustering,
  metadata and multi-platform distribution copy for every Open Athletes episode
- **Granola** for meeting notes, connected to Claude so decisions from calls turn straight into briefs and docs
- **A rule I hold to:** AI drafts and checks; a person decides what we believe, approves every
  number, and signs off on anything published under someone's name
