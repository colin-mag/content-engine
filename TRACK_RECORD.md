# Track record

14 years building content strategies, teams and operating systems across technology, healthcare and
regulated industries.

| | |
|---:|---|
| **1,400%** | increase in Google AI Overview mentions (Thatch) |
| **871%** | increase in ChatGPT visibility (Thatch) |
| **$220K+** | annual content operating costs cut (Thatch) |
| **$200M+** | in digital ad investment supported by content strategy (Right Percent) |
| **2** | major technology IPOs supported by content strategy |
| **15+** | writers, designers, SEO specialists and marketers directed (Right Percent) |

**Clients served:** Reddit · Uber · DoorDash · Ramp · MetaMask · Brightwheel · Zenefits · Podium · Owner.com · IDEO U

---

## Thatch: Content Lead (May 2025–present)

Led company-wide content for a high-growth healthcare startup: website, AI search, SEO, executive
communications, product launches, sales enablement, broker education, campaigns and editorial
operations, partnering with the founder on positioning and market communications.

- **AI search:** grew ChatGPT visibility **871%**, AI citations **130%** and Google AI Overview mentions
  **1,400%** through a structured AI-search and editorial optimization program
- **Cost:** cut annual content operating costs by **$220K+** by replacing three agencies with a lean
  specialist contractor model, while improving speed and consistency
- **Organic growth:** grew organic users **41%**, sessions **33%** and core conversions **28%** while leading
  a full website migration with no loss of organic traffic
- **Regulated content:** built accredited continuing-education programs approved in **21 states**,
  translating healthcare reimbursement and policy into broker education with Legal, Compliance,
  Clinical and Policy teams
- **Flagship program:** directed the *2026 Health Benefits Outlook*, expanding one report into webinars,
  video, podcasts, outbound campaigns, broker education, sales enablement and executive communications
- **Engine:** built and led the content marketing engine across editorial, SEO, AI search, product
  marketing, campaigns, executive thought leadership and distribution, tied directly to GTM priorities
  and pipeline

## Right Percent: Director of Content Strategy (2020–2025)

Led content strategy, content marketing and growth for venture-backed and high-growth companies across
SaaS, fintech, healthcare, education and consumer technology.

- Directed teams of **15+** writers, designers, SEO specialists and marketers as lead strategist and
  executive client partner
- Ran content strategy supporting acquisition programs representing **$200M+** in digital ad investment
- Built AI content infrastructure and workflows from scratch to speed up research, production,
  optimization and quality control across client programs
- Built messaging frameworks, website strategies, SEO programs, executive communications and
  conversion-focused content for founders, CMOs and executive teams
- Aligned content with paid acquisition, lifecycle marketing and product positioning to improve
  acquisition and conversion

## Layover Marketing: Co-founder (2015–2020)

Co-founded and ran a content marketing company built on SEO-led blog programs, landing pages and
executive ghostwriting.

- Built organic content programs and led long-form editorial engagements, including contributions to
  several published books
- Led client strategy and editorial planning from concept through publication

---

## Open Athletes: built the content and distribution system (2026)

A live show and media platform helping former athletes and military veterans move into the
workforce.

**Scope:** growth strategy, positioning, YouTube and social, distribution systems and paid media.

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

## NYU Stern: Guest instructor (fall 2024–present)

I teach graduate students practical frameworks for B2B content strategy, brand positioning, growth
marketing and AI search: how buyers' discovery is moving from search results to
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
