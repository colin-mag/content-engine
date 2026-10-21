"""Editorial linter: the deterministic quality gate every draft passes.

It runs without an API key. It catches the things that make content read as
unedited AI output, and the things that get a content team in trouble:

* generic AI phrasing (from voice/banned_phrases.txt)
* AI rhetorical tics ("not just X, but Y", "in today's ... landscape")
* numbers with no source label or link
* vague claims and unearned superlatives
* sentences too long to read on a phone

It does NOT judge whether the argument is any good. That stays human.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNED_FILE = ROOT / "voice" / "banned_phrases.txt"

SOURCE_LABEL = re.compile(r"\[(?:Observed|Estimated|Benchmarked|Assumed|Source)\b", re.I)

TIC_PATTERNS = {
    "not-just-but": re.compile(r"\bnot (?:just|only|merely)\b[^.?!]{0,80}?\bbut\b", re.I),
    "its-not-its": re.compile(r"\b(?:it'?s|this is|that'?s) not (?:about )?[^.?!]{1,60}?[,;—-]+\s*(?:it'?s|this is|that'?s)\b", re.I),
    "landscape-opener": re.compile(r"\bin today'?s [a-z\s-]{0,30}(?:landscape|world|era|environment)\b", re.I),
    "rhetorical-q-opener": re.compile(r"^(?:ever wondered|have you ever|what if i told you)", re.I | re.M),
}

VAGUE_WORDS = re.compile(
    r"\b(?:significantly|dramatically|various|numerous|many experts|studies show|"
    r"research shows|it is widely known|countless|a lot of)\b",
    re.I,
)
SUPERLATIVES = re.compile(r"\b(?:the best|best-in-class|world-class|industry-leading|leading|#1|number one|unparalleled)\b", re.I)

NUMBER = re.compile(r"(?<![\w/.#-])(\$?\d[\d,]*(?:\.\d+)?\s?(?:%|percent|x|k|m|b)?)(?![\w/])", re.I)
YEAR = re.compile(r"^(?:19|20)\d{2}$")
LINK = re.compile(r"\[[^\]]*\]\([^)]+\)|https?://\S+")
CODE = re.compile(r"```.*?```|`[^`]*`", re.S)

PENALTY = {"banned": 4, "tic": 5, "unsourced-number": 3, "vague": 2, "superlative": 2, "long-sentence": 1}


@dataclass
class Finding:
    kind: str
    line: int
    excerpt: str
    note: str


@dataclass
class Report:
    path: str
    words: int
    findings: list[Finding] = field(default_factory=list)

    @property
    def score(self) -> int:
        penalty = sum(PENALTY[f.kind] for f in self.findings)
        return max(0, 100 - penalty)

    def to_markdown(self) -> str:
        out = [f"## Editorial lint: `{self.path}`", "", f"**Score: {self.score}/100** · {self.words} words · {len(self.findings)} findings", ""]
        if not self.findings:
            out.append("Clean. Now read it out loud anyway.")
            return "\n".join(out)
        out += ["| Line | Check | Excerpt | Fix |", "|---:|---|---|---|"]
        for f in self.findings:
            ex = f.excerpt.replace("|", "\\|")
            out.append(f"| {f.line} | {f.kind} | {ex} | {f.note} |")
        return "\n".join(out)


def load_banned(path: Path = BANNED_FILE) -> list[str]:
    if not path.exists():
        return []
    return [ln.strip().lower() for ln in path.read_text().splitlines() if ln.strip() and not ln.startswith("#")]


def _sentences(line: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.?!])\s+", line) if s.strip()]


def _clip(text: str, n: int = 70) -> str:
    text = text.strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def lint_text(text: str, path: str = "<text>", banned: list[str] | None = None) -> Report:
    banned = load_banned() if banned is None else banned
    stripped = CODE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    report = Report(path=path, words=len(re.findall(r"\b\w+\b", stripped)))

    for i, raw in enumerate(stripped.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(("|", ">", "<!--")):
            continue
        heading = line.startswith("#")
        low = line.lower()

        for phrase in banned:
            if re.search(rf"\b{re.escape(phrase)}\b", low):
                report.findings.append(Finding("banned", i, phrase, "Cut it or say the specific thing."))

        for name, pat in TIC_PATTERNS.items():
            m = pat.search(line)
            if m:
                report.findings.append(Finding("tic", i, _clip(m.group(0)), f"AI tic ({name}). Make the claim directly."))

        for m in VAGUE_WORDS.finditer(line):
            report.findings.append(Finding("vague", i, m.group(0), "Replace with the number or the named source."))

        for m in SUPERLATIVES.finditer(line):
            report.findings.append(Finding("superlative", i, m.group(0), "Earn it with proof or drop it."))

        if heading:
            continue

        body = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", line)
        for sentence in _sentences(body):
            if len(sentence.split()) > 35:
                report.findings.append(Finding("long-sentence", i, _clip(sentence), f"{len(sentence.split())} words. Split it."))
            if SOURCE_LABEL.search(sentence) or LINK.search(sentence):
                continue
            nums = [n for n in NUMBER.findall(LINK.sub("", sentence)) if not YEAR.match(n.strip())]
            nums = [n for n in nums if not re.fullmatch(r"[0-9]", n.strip())]  # single digits: list counts, steps
            if nums:
                report.findings.append(
                    Finding("unsourced-number", i, _clip(sentence), f"Label {nums[0].strip()} as Observed/Estimated/Benchmarked/Assumed or link the source.")
                )
    return report


def lint_file(path: str | Path) -> Report:
    p = Path(path)
    return lint_text(p.read_text(encoding="utf-8"), path=str(p))
