#!/usr/bin/env python3
"""Local skill-improvement automation for AI Agent Config.

The bot scans local LLM CLI logs, extracts redacted improvement signals, writes
proposal reports, and can optionally create or maintain GitHub pull requests.
Raw logs stay local; reports contain only summarized and redacted evidence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {
    ".jsonl",
    ".json",
    ".log",
    ".md",
    ".txt",
}

MAX_SKILL_CONTEXT_LINES = 80

SKIP_NAME_RE = re.compile(
    r"(auth|credential|token|secret|keychain|oauth|cookie|session\.db|\.sqlite|\.png|\.jpg|\.jpeg|\.gif|\.pdf)$",
    re.IGNORECASE,
)

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
]

CORRECTION_KEYWORDS = [
    "修正",
    "直して",
    "やり直",
    "漏れ",
    "抜け",
    "足り",
    "不足",
    "違う",
    "だめ",
    "ダメ",
    "再度",
    "もう一回",
    "セルフレビュー",
    "レビュー",
    "改善",
    "確認した",
    "確かめ",
    "fix",
    "missing",
    "wrong",
    "again",
    "review",
    "should have",
    "not enough",
    "did you",
]

CATEGORY_KEYWORDS = {
    "activation": ["起動", "発動", "trigger", "activation", "使われ", "呼び出"],
    "evidence": ["論文", "研究", "根拠", "source", "citation", "evidence", "公式"],
    "search": ["検索", "web search", "query", "検索ワード", "絞り込"],
    "delegation": ["agent", "sub-agent", "委任", "並列", "delegate"],
    "formatting": ["markdown", "md記法", "太字", "書式", "format", "見出し"],
    "validation": ["検証", "test", "validate", "self-review", "セルフレビュー"],
    "privacy": ["ログ", "個人情報", "secret", "token", "privacy", "redact"],
    "setup": ["setup", "install", "リンク", "更新頻度", "health-check"],
    "pr-review": ["pull request", "pr", "claude", "review", "マージ"],
}

AUTO_PR_ALLOWED_PATHS = (
    ".github/workflows/",
    "compatibility/",
    "docs/",
    "instructions/",
    "reports/skill-improvement/",
    "scripts/",
    "setup.md",
    "README.md",
    "skills/",
    "tests/",
)


@dataclass
class Skill:
    name: str
    path: str
    description: str = ""


@dataclass
class Signal:
    skill: str
    category: str
    source: str
    line: int
    fingerprint: str
    summary: str
    snippet: str = ""


@dataclass
class Proposal:
    skill: str
    category: str
    signals: list[Signal] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.signals)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan LLM CLI logs and prepare skill improvement proposals."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan logs and print redacted proposals.")
    add_scan_args(scan)
    scan.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")

    run = sub.add_parser("run", help="Scan, write a report, optionally apply changes and create a PR.")
    add_scan_args(run)
    run.add_argument("--apply-with-llm", choices=["claude", "codex", "gemini"], default=os.getenv("AI_AGENT_IMPROVEMENT_LLM", ""))
    run.add_argument("--create-pr", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_CREATE_PR") == "1")
    run.add_argument("--base", default=os.getenv("AI_AGENT_IMPROVEMENT_BASE", "main"))
    run.add_argument("--branch", default="")
    run.add_argument("--title", default="")
    run.add_argument("--dry-run", action="store_true", default=os.getenv("AI_AGENT_DRY_RUN") == "1")

    cycle = sub.add_parser("cycle", help="Run a scan/PR pass, then inspect existing automation PRs.")
    add_scan_args(cycle)
    cycle.add_argument("--create-pr", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_CREATE_PR") == "1")
    cycle.add_argument("--apply-with-llm", choices=["claude", "codex", "gemini"], default=os.getenv("AI_AGENT_IMPROVEMENT_LLM", ""))
    cycle.add_argument("--apply-claude-feedback", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_APPLY_REVIEW") == "1")
    cycle.add_argument("--auto-merge", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_AUTO_MERGE") == "1")
    cycle.add_argument("--base", default=os.getenv("AI_AGENT_IMPROVEMENT_BASE", "main"))
    cycle.add_argument("--branch", default="")
    cycle.add_argument("--title", default="")
    cycle.add_argument("--head-prefix", default=os.getenv("AI_AGENT_IMPROVEMENT_HEAD_PREFIX", "bot/skill-improvement-"))
    cycle.add_argument("--dry-run", action="store_true", default=os.getenv("AI_AGENT_DRY_RUN") == "1")

    review = sub.add_parser("review-pr", help="Inspect a PR's Claude review state and optionally continue automation.")
    review.add_argument("pr", help="PR number or URL.")
    review.add_argument("--apply-claude-feedback", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_APPLY_REVIEW") == "1")
    review.add_argument("--auto-merge", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_AUTO_MERGE") == "1")
    review.add_argument("--dry-run", action="store_true", default=os.getenv("AI_AGENT_DRY_RUN") == "1")

    review_open = sub.add_parser("review-open-prs", help="Inspect open bot PRs and optionally continue automation.")
    review_open.add_argument("--head-prefix", default=os.getenv("AI_AGENT_IMPROVEMENT_HEAD_PREFIX", "bot/skill-improvement-"))
    review_open.add_argument("--apply-claude-feedback", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_APPLY_REVIEW") == "1")
    review_open.add_argument("--auto-merge", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_AUTO_MERGE") == "1")
    review_open.add_argument("--dry-run", action="store_true", default=os.getenv("AI_AGENT_DRY_RUN") == "1")
    return parser.parse_args()


def add_scan_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--days", type=int, default=int(os.getenv("AI_AGENT_LOG_DAYS", "14")))
    parser.add_argument("--max-files", type=int, default=int(os.getenv("AI_AGENT_LOG_MAX_FILES", "300")))
    parser.add_argument("--max-bytes", type=int, default=int(os.getenv("AI_AGENT_LOG_MAX_BYTES", "120000")))
    parser.add_argument("--include-snippets", action="store_true", default=os.getenv("AI_AGENT_IMPROVEMENT_INCLUDE_SNIPPETS") == "1")
    parser.add_argument("--log-root", action="append", default=[], help="Additional log root. Can be passed more than once.")


def privacy_mode() -> str:
    return os.getenv("AI_AGENT_IMPROVEMENT_PRIVACY_MODE", "high").lower()


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def configured_log_roots(extra_roots: list[str]) -> list[Path]:
    env_roots = os.getenv("AI_AGENT_LOG_ROOTS", "")
    roots: list[Path] = []
    for item in env_roots.split(os.pathsep):
        if item:
            roots.append(expand_path(item))
    for item in extra_roots:
        roots.append(expand_path(item))

    if os.getenv("AI_AGENT_LOG_ROOTS_ONLY") == "1":
        return unique_existing_paths(roots)

    home = Path.home()
    codex_home = expand_path(os.getenv("CODEX_HOME", str(home / ".codex")))
    claude_home = expand_path(os.getenv("CLAUDE_CONFIG_DIR", str(home / ".claude")))
    gemini_home = expand_path(os.getenv("GEMINI_HOME", str(home / ".gemini")))
    defaults = [
        codex_home / "sessions",
        codex_home / "history.jsonl",
        codex_home / "log",
        codex_home / "logs",
        claude_home / "projects",
        claude_home / "file-history",
        gemini_home / "history",
        gemini_home / "tmp",
    ]
    roots.extend(defaults)

    return unique_existing_paths(roots)


def unique_existing_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen and path.exists():
            unique.append(path)
            seen.add(key)
    return unique


def load_skills(root: Path) -> list[Skill]:
    skills: list[Skill] = []
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        name = path.parent.name
        description = ""
        for line in text.splitlines()[:30]:
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip()
        skills.append(Skill(name=name, path=str(path.relative_to(root)), description=description))
    return skills


def iter_log_files(roots: list[Path], days: int, max_files: int) -> list[Path]:
    cutoff = now_utc().timestamp() - days * 86400
    candidates: list[tuple[float, Path]] = []
    for root in roots:
        if root.is_file():
            paths = [root]
        else:
            paths = [p for p in root.rglob("*") if p.is_file()]
        for path in paths:
            name = path.name
            if SKIP_NAME_RE.search(name):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES and path.suffix:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff:
                continue
            candidates.append((stat.st_mtime, path))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return [path for _mtime, path in candidates[:max_files]]


def read_tail(path: Path, max_bytes: int) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes), os.SEEK_SET)
            data = handle.read(max_bytes)
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def redact(text: str) -> str:
    value = text
    for pattern in SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    value = re.sub(r"/Users/[^/\s]+", "/Users/[REDACTED]", value)
    value = re.sub(r"/home/[^/\s]+", "/home/[REDACTED]", value)
    value = re.sub(r"/root(?:/|\b)", "/root/[REDACTED]/", value)
    value = re.sub(r"\b[0-9a-f]{32,}\b", "[REDACTED_HASH]", value, flags=re.IGNORECASE)
    return value


def compact_line(text: str, limit: int = 280) -> str:
    one_line = re.sub(r"\s+", " ", redact(text)).strip()
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1].rstrip() + "..."


def extract_text_events(raw: str) -> list[tuple[int, str, str]]:
    events: list[tuple[int, str, str]] = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        text = stripped
        role = ""
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                payload = json.loads(stripped)
                role = str(payload.get("role", payload.get("type", ""))).lower()
                text = json_to_text(payload)
            except json.JSONDecodeError:
                text = stripped
        if text:
            events.append((idx, role, text))
    return events


def json_to_text(value: Any) -> str:
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            if len(node) > 2:
                parts.append(node)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for key in ("role", "type", "text", "content", "message", "prompt", "query", "body"):
                if key in node:
                    walk(node[key])

    walk(value)
    return " ".join(parts)


def detect_skill(text: str, skills: list[Skill]) -> str | None:
    lower = text.lower()
    for skill in skills:
        names = {skill.name.lower(), Path(skill.path).parent.name.lower()}
        for name in names:
            if name and name in lower:
                return skill.name
    return None


def detect_categories(text: str) -> list[str]:
    lower = text.lower()
    scored: list[tuple[int, str]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in lower)
        if score:
            scored.append((score, category))
    if not scored:
        return ["workflow"]
    scored.sort(reverse=True)
    return [category for _score, category in scored[:3]]


def is_correction(text: str) -> bool:
    lower = text.lower()
    return any(keyword.lower() in lower for keyword in CORRECTION_KEYWORDS)


def fingerprint(source: Path, line: int, text: str) -> str:
    digest = hashlib.sha256(f"{source}:{line}:{text}".encode("utf-8", errors="ignore")).hexdigest()
    return digest[:16]


def scan_logs(args: argparse.Namespace, root: Path) -> tuple[list[Proposal], dict[str, Any]]:
    skills = load_skills(root)
    roots = configured_log_roots(args.log_root)
    files = iter_log_files(roots, args.days, args.max_files)
    signals: list[Signal] = []

    for path in files:
        raw = read_tail(path, args.max_bytes)
        if not raw:
            continue
        events = extract_text_events(raw)
        recent_skill: str | None = None
        recent_skill_line = 0
        for line_no, role, text in events:
            if role and role not in {"user", "human", "input", "request"}:
                skill = detect_skill(text, skills)
                if skill:
                    recent_skill = skill
                    recent_skill_line = line_no
                continue
            previous_skill = recent_skill
            if previous_skill and line_no - recent_skill_line > MAX_SKILL_CONTEXT_LINES:
                previous_skill = None
                recent_skill = None
                recent_skill_line = 0
            skill = detect_skill(text, skills)
            if skill:
                recent_skill = skill
                recent_skill_line = line_no
            # Require a prior assistant anchor to reduce false positives from
            # user-only generic correction messages.
            active_skill = previous_skill or (recent_skill if line_no > recent_skill_line else None)
            if not active_skill or not is_correction(text):
                continue
            try:
                source = str(path.relative_to(Path.home()))
            except ValueError:
                source = path.name
            for category in detect_categories(text):
                snippet = compact_line(text, 480) if args.include_snippets else ""
                summary = summarize_signal(text, category)
                signals.append(
                    Signal(
                        skill=active_skill,
                        category=category,
                        source=source,
                        line=line_no,
                        fingerprint=fingerprint(path, line_no, f"{category}:{text}"),
                        summary=summary,
                        snippet=snippet,
                    )
                )

    grouped: dict[tuple[str, str], Proposal] = {}
    for signal in signals:
        key = (signal.skill, signal.category)
        grouped.setdefault(key, Proposal(skill=signal.skill, category=signal.category)).signals.append(signal)

    proposals = sorted(grouped.values(), key=lambda item: (-item.count, item.skill, item.category))
    meta = {
        "generated_at": now_utc().isoformat(),
        "days": args.days,
        "files_scanned": len(files),
        "log_roots": [str(root) for root in roots],
        "skills_loaded": len(skills),
        "signals": len(signals),
        "snippets_included": bool(args.include_snippets),
    }
    return proposals, meta


def summarize_signal(text: str, category: str) -> str:
    lower = text.lower()
    if category == "activation":
        return "Skill activation or trigger wording may be too weak for realistic requests."
    if category == "evidence":
        return "The skill may need stronger source requirements or evidence-routing guidance."
    if category == "search":
        return "The workflow may need bounded search-query guidance to avoid over-narrow results."
    if category == "delegation":
        return "Delegation rules may need clearer scope splitting, context sharing, or synthesis checks."
    if category == "formatting":
        return "Documentation output rules may need stronger formatting and medium-specific guidance."
    if category == "validation":
        return "The skill may need a stricter self-review or verification checkpoint."
    if category == "privacy":
        return "The workflow may need stronger local-only handling and redaction requirements."
    if category == "pr-review":
        return "PR review automation may need clearer feedback handling or merge readiness checks."
    if "もう一回" in lower or "again" in lower:
        return "A repeated follow-up suggests the first skill pass did not fully satisfy the request."
    return "A post-skill correction suggests an abstractable improvement opportunity."


def proposals_to_json(proposals: list[Proposal], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "meta": meta,
        "proposals": [
            {
                "skill": proposal.skill,
                "category": proposal.category,
                "signal_count": proposal.count,
                "recommendation": recommendation_for(proposal),
                "signals": [
                    {
                        "source": signal.source,
                        "line": signal.line,
                        "fingerprint": signal.fingerprint,
                        "summary": signal.summary,
                        **({"snippet": signal.snippet} if signal.snippet else {}),
                    }
                    for signal in proposal.signals[:10]
                ],
            }
            for proposal in proposals
        ],
    }


def proposals_to_markdown(proposals: list[Proposal], meta: dict[str, Any]) -> str:
    lines = [
        "# Skill Improvement Proposals",
        "",
        "This report is generated from local LLM CLI logs. It contains redacted summaries only; raw logs are not committed.",
        "",
        "## Scan Summary",
        "",
        f"- Generated at: `{meta['generated_at']}`",
        f"- Lookback days: `{meta['days']}`",
        f"- Files scanned: `{meta['files_scanned']}`",
        f"- Skills loaded: `{meta['skills_loaded']}`",
        f"- Signals found: `{meta['signals']}`",
        f"- Snippets included: `{meta['snippets_included']}`",
        "",
    ]
    if not proposals:
        lines.extend(
            [
                "## Result",
                "",
                "No actionable skill-improvement signal was detected in the scanned window.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(["## Proposals", ""])
    for proposal in proposals:
        lines.extend(
            [
                f"### `{proposal.skill}` / `{proposal.category}`",
                "",
                f"**Signal count:** {proposal.count}",
                "",
                f"**Recommendation:** {recommendation_for(proposal)}",
                "",
                "**Evidence summary:**",
                "",
            ]
        )
        for signal in proposal.signals[:10]:
            lines.append(f"- `{signal.fingerprint}`: {signal.summary} (`{signal.source}:{signal.line}`)")
            if signal.snippet:
                lines.append(f"  - Redacted snippet: {signal.snippet}")
        if proposal.count > 10:
            lines.append(f"- ...and {proposal.count - 10} more similar signal(s).")
        lines.append("")
    return "\n".join(lines)


def recommendation_for(proposal: Proposal) -> str:
    category = proposal.category
    if category == "activation":
        return "Review the frontmatter description and should-trigger examples so realistic follow-up requests route to this skill without requiring exact internal terms."
    if category == "evidence":
        return "Move detailed source notes into references and add a lean rule that non-obvious workflow choices need official, academic, benchmark, or clearly labeled assumption support."
    if category == "search":
        return "Add concise-query guidance: start with a small set of high-signal terms, inspect result quality, then broaden or narrow one qualifier at a time."
    if category == "delegation":
        return "Clarify when to split work across agents or peer LLMs, what context to pass, and how the coordinator reconciles conflicting outputs."
    if category == "formatting":
        return "Add medium-aware writing guidance that uses native formatting deliberately without bloating the always-loaded instructions."
    if category == "validation":
        return "Add a concrete self-review checkpoint that inspects the actual loaded skill, trigger surface, verification path, and output quality before completion."
    if category == "privacy":
        return "Require local-only handling, secret redaction, no raw-log commits, and explicit opt-in before sending any summarized context to a peer LLM or external service."
    if category == "pr-review":
        return "Tighten PR review automation around unresolved review threads, check status, Claude readiness wording, and head-SHA matched auto-merge."
    return "Abstract the repeated correction into a lean rule, test prompt, or reference note for the target skill."


def write_report(root: Path, markdown: str) -> Path:
    stamp = now_utc().strftime("%Y%m%d-%H%M%S")
    directory = root / "reports" / "skill-improvement"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stamp}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def run_command(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=check)


def require_tool(name: str) -> None:
    if not shutil.which(name):
        raise SystemExit(f"error: required tool not found on PATH: {name}")


def enforce_report_privacy(args: argparse.Namespace) -> None:
    if args.create_pr and args.include_snippets and privacy_mode() == "high":
        raise SystemExit(
            "error: high privacy mode blocks committing log snippets. Disable snippets or set AI_AGENT_IMPROVEMENT_PRIVACY_MODE=standard explicitly."
        )


def ensure_clean(root: Path) -> None:
    status = run_command(["git", "status", "--porcelain"], root).stdout.strip()
    if status and os.getenv("AI_AGENT_IMPROVEMENT_ALLOW_DIRTY") != "1":
        raise SystemExit(
            "error: repository has local changes. Set AI_AGENT_IMPROVEMENT_ALLOW_DIRTY=1 only when the automation owns the current changes."
        )


def apply_with_llm(root: Path, report_path: Path, provider: str, dry_run: bool) -> None:
    if not provider:
        return
    require_tool(provider)
    prompt = build_llm_patch_prompt(report_path)
    if dry_run:
        print(f"dry-run: would ask {provider} to update target skill(s) from {report_path}")
        return
    if provider == "claude":
        cmd = [
            "claude",
            "-p",
            prompt,
            "--permission-mode",
            "default",
            "--allowedTools",
            "Read,Edit,MultiEdit,Bash(git diff:*),Bash(git status:*),Bash(sh scripts/validate-repo.sh:*)",
        ]
    elif provider == "codex":
        # Codex and Gemini do not expose the same file-edit allowlist shape as
        # Claude here; keep the prompt narrow and rely on the post-run staging
        # allowlist before any PR is created.
        cmd = [
            "codex",
            "exec",
            "--cd",
            str(root),
            "--sandbox",
            "workspace-write",
            "--ask-for-approval",
            "never",
            prompt,
        ]
    elif provider == "gemini":
        # Gemini's auto_edit mode is similarly constrained after the run by
        # stage_automation_paths(), which refuses unexpected changed paths.
        cmd = [
            "gemini",
            "--prompt",
            prompt,
            "--approval-mode",
            "auto_edit",
            "--skip-trust",
        ]
    else:
        raise SystemExit(f"error: unsupported LLM provider: {provider}")
    result = run_command(cmd, root, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"error: {provider} failed to apply proposal")


def build_llm_patch_prompt(report_path: Path) -> str:
    try:
        display_path = report_path.relative_to(repo_root())
    except ValueError:
        display_path = report_path
    return f"""You are updating this AI Agent Config repository.

Read `{display_path}` and implement only the skill or instruction improvements that are clearly supported by the sanitized proposal.

Constraints:
- Do not inspect or commit raw local LLM CLI logs.
- Keep SKILL.md files lean; move detailed evidence or examples into references.
- Preserve portability across Claude Code, Codex, and Gemini CLI.
- Keep changes minimal, generalized, and reusable.
- Run `sh scripts/validate-repo.sh` after edits and fix any failures.
- Do not use shell deletion commands; if cleanup is needed, use the repository's safe deletion convention.

Return a concise summary of changed files and verification.
"""


def maybe_create_pr(root: Path, report_path: Path, args: argparse.Namespace) -> None:
    if not args.create_pr:
        return
    require_tool("gh")
    require_tool("git")
    stamp = now_utc().strftime("%Y%m%d-%H%M%S")
    branch = args.branch or f"bot/skill-improvement-{stamp}"
    title = args.title or f"Propose skill improvements from local usage signals ({stamp})"
    body = (
        "Automated skill-improvement proposal generated from redacted local LLM CLI usage signals.\n\n"
        f"Report: `{report_path.relative_to(root)}`\n\n"
        "Raw logs were not committed. Validation is expected to run before merge."
    )
    if args.dry_run:
        print(f"dry-run: would create branch {branch}, commit {report_path}, push, and open PR")
        return
    current_branch = run_command(["git", "branch", "--show-current"], root).stdout.strip()
    try:
        run_command(["git", "switch", "-c", branch], root)
        stage_automation_paths(root, report_path)
        run_command(["git", "commit", "-m", "Add automated skill improvement proposal"], root)
        run_command(["git", "push", "-u", "origin", branch], root)
        result = run_command(
            ["gh", "pr", "create", "--base", args.base, "--head", branch, "--title", title, "--body", body],
            root,
        )
    finally:
        if current_branch:
            run_command(["git", "switch", current_branch], root, check=False)
    print(result.stdout.strip())


def stage_automation_paths(root: Path, report_path: Path) -> None:
    changed = changed_paths(root)
    report_rel = str(report_path.relative_to(root))
    allowed = [path for path in changed if is_auto_pr_allowed(path, report_path.relative_to(root))]
    if report_rel not in allowed:
        allowed.append(report_rel)
    rejected = sorted(set(changed) - set(allowed))
    if rejected:
        raise SystemExit(
            "error: refusing to stage unexpected path(s): "
            + ", ".join(rejected)
            + ". Update AUTO_PR_ALLOWED_PATHS only if these are intentional automation outputs."
        )
    if not allowed:
        raise SystemExit("error: no automation-owned changes to stage")
    run_command(["git", "add", "-f", "--", *allowed], root)


def changed_paths(root: Path) -> list[str]:
    status = run_command(["git", "status", "--porcelain=v1", "-z"], root).stdout.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(status):
        entry = status[index]
        index += 1
        if not entry:
            continue
        code = entry[:2]
        path = entry[3:]
        paths.append(path)
        if "R" in code or "C" in code:
            index += 1
    return [path for path in paths if path]


def stage_allowed_changed_paths(root: Path) -> list[str]:
    changed = changed_paths(root)
    allowed = [path for path in changed if is_auto_pr_allowed(path, Path(""))]
    rejected = sorted(set(changed) - set(allowed))
    if rejected:
        raise SystemExit("error: refusing to stage unexpected review-feedback path(s): " + ", ".join(rejected))
    if allowed:
        run_command(["git", "add", "-f", "--", *allowed], root)
    return allowed


def is_auto_pr_allowed(path: str, report_path: Path) -> bool:
    normalized = path.replace("\\", "/")
    if normalized == str(report_path).replace("\\", "/"):
        return True
    for prefix in AUTO_PR_ALLOWED_PATHS:
        normalized_prefix = prefix.rstrip("/")
        if prefix.endswith("/"):
            if normalized.startswith(prefix):
                return True
            continue
        if normalized == normalized_prefix:
            return True
    return False


def inspect_pr(root: Path, pr: str) -> dict[str, Any]:
    require_tool("gh")
    view = run_command(
        [
            "gh",
            "pr",
            "view",
            pr,
            "--json",
            "number,title,url,isDraft,mergeable,mergeStateStatus,reviewDecision,headRefOid,statusCheckRollup,comments,reviews",
        ],
        root,
    )
    data = json.loads(view.stdout)
    data["unresolved_threads"] = unresolved_threads(root, int(data["number"]))
    return data


def unresolved_threads(root: Path, number: int) -> int:
    repo = json.loads(run_command(["gh", "repo", "view", "--json", "nameWithOwner"], root).stdout)["nameWithOwner"]
    owner, name = repo.split("/", 1)
    query = """
query($owner:String!, $name:String!, $number:Int!, $after:String) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          isResolved
          isOutdated
        }
      }
    }
  }
}
"""
    unresolved = 0
    after = ""
    while True:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
            "-F",
            f"number={number}",
            "-f",
            f"query={query}",
        ]
        if after:
            cmd.extend(["-f", f"after={after}"])
        result = run_command(cmd, root, check=False)
        if result.returncode != 0:
            return -1
        payload = json.loads(result.stdout)
        threads = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        unresolved += sum(1 for node in threads["nodes"] if not node.get("isResolved") and not node.get("isOutdated"))
        page = threads["pageInfo"]
        if not page.get("hasNextPage"):
            return unresolved
        after = page.get("endCursor") or ""
        if not after:
            return -1


def check_values(node: Any) -> list[str]:
    values: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {"conclusion", "status", "state"} and isinstance(value, str):
                values.append(value.lower())
            values.extend(check_values(value))
    elif isinstance(node, list):
        for item in node:
            values.extend(check_values(item))
    return values


def checks_pass(data: dict[str, Any]) -> tuple[bool, str]:
    values = check_values(data.get("statusCheckRollup", []))
    if any(value in {"failure", "failed", "cancelled", "timed_out", "action_required", "error"} for value in values):
        return False, "one or more checks failed"
    if any(value in {"queued", "pending", "in_progress", "requested", "waiting", "neutral"} for value in values):
        return False, "one or more checks are pending"
    return True, "checks are passing or no checks were reported"


def claude_ready(data: dict[str, Any]) -> tuple[bool, str]:
    events = sorted_review_events(data)
    for item in events:
        if not trusted_review_author(item):
            continue
        body = str(item.get("body", "")).lower()
        if str(item.get("state", "")).upper() == "APPROVED":
            return True, "latest Claude-related review is APPROVED"
        if any(marker in body for marker in ["ready to merge", "merge ok", "lgtm", "no changes requested", "マージ ok", "マージok"]):
            return True, "latest Claude-related review appears merge-ready"
        if any(marker in body for marker in ["request changes", "blocking", "needs changes", "要修正", "修正をお願い"]):
            return False, "Claude-related review still asks for changes"
    return False, "no merge-ready Claude review signal found"


def sorted_review_events(data: dict[str, Any]) -> list[dict[str, Any]]:
    events = list(data.get("comments", [])) + list(data.get("reviews", []))
    return sorted(events, key=review_event_timestamp, reverse=True)


def review_event_timestamp(item: dict[str, Any]) -> dt.datetime:
    raw = str(item.get("submittedAt") or item.get("createdAt") or "")
    if not raw:
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    try:
        return dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def trusted_review_author(item: dict[str, Any]) -> bool:
    author = item.get("author", {})
    login = str(author.get("login", "") if isinstance(author, dict) else "").lower()
    trusted = os.getenv(
        "AI_AGENT_TRUSTED_REVIEW_AUTHORS",
        "claude,claude-code",
    )
    return any(token.strip().lower() == login for token in trusted.split(",") if token.strip())


def has_trusted_review_activity(data: dict[str, Any]) -> bool:
    comments = data.get("comments", []) + data.get("reviews", [])
    return any(trusted_review_author(item) for item in comments)


def apply_claude_feedback(root: Path, pr: str, dry_run: bool) -> None:
    require_tool("claude")
    prompt = f"""Inspect pull request `{pr}` in this repository and address actionable Claude review feedback only.

Requirements:
- Read PR comments and review threads through available GitHub context or `gh`.
- Use GitHub API access for read-only review-thread inspection only.
- Do not broaden scope beyond review feedback.
- Run `sh scripts/validate-repo.sh` after edits.
- Do not use shell deletion commands; use the repository's safe deletion convention if cleanup is required.
- Do not commit or push; leave any changes in the worktree for this automation script to validate, commit, and push.
"""
    if dry_run:
        print(f"dry-run: would run Claude Code to address review feedback on PR {pr}")
        return
    result = run_command(
        [
            "claude",
            "-p",
            prompt,
            "--permission-mode",
            "default",
            "--allowedTools",
            "Read,Edit,MultiEdit,Bash(gh pr view:*),Bash(gh pr diff:*),Bash(gh api graphql:*),Bash(git diff:*),Bash(git status:*),Bash(sh scripts/validate-repo.sh:*)",
        ],
        root,
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit("error: Claude review-feedback pass failed")
    run_command(["sh", "scripts/validate-repo.sh"], root)
    staged = stage_allowed_changed_paths(root)
    if staged:
        run_command(["git", "commit", "-m", f"Address automated review feedback for PR #{pr}"], root)
        run_command(["git", "push", "origin", "HEAD"], root)


def maybe_auto_merge(root: Path, pr: str, data: dict[str, Any], dry_run: bool) -> None:
    ready, ready_reason = claude_ready(data)
    checks_ok, checks_reason = checks_pass(data)
    unresolved = data.get("unresolved_threads")
    mergeable = str(data.get("mergeable") or "").upper()
    blockers = []
    if data.get("isDraft"):
        blockers.append("PR is still a draft")
    if not ready:
        blockers.append(ready_reason)
    if not checks_ok:
        blockers.append(checks_reason)
    if unresolved == -1:
        blockers.append("could not inspect current review threads")
    elif unresolved and unresolved > 0:
        blockers.append(f"{unresolved} current review thread(s) are unresolved")
    if mergeable in {"CONFLICTING", "UNKNOWN"}:
        blockers.append(f"mergeable state is {mergeable}")

    if blockers:
        print(json.dumps({"ready_to_merge": False, "blockers": blockers}, ensure_ascii=False, indent=2))
        return

    head = data["headRefOid"]
    if dry_run:
        print(json.dumps({"ready_to_merge": True, "dry_run": True, "head": head}, ensure_ascii=False, indent=2))
        return
    run_command(["gh", "pr", "merge", pr, "--squash", "--auto", "--match-head-commit", head], root)
    print(json.dumps({"ready_to_merge": True, "auto_merge_requested": True, "head": head}, ensure_ascii=False, indent=2))


def cmd_scan(args: argparse.Namespace) -> None:
    root = repo_root()
    proposals, meta = scan_logs(args, root)
    payload = proposals_to_json(proposals, meta)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(proposals_to_markdown(proposals, meta))


def cmd_run(args: argparse.Namespace) -> None:
    root = repo_root()
    enforce_report_privacy(args)
    if args.create_pr and not args.dry_run:
        ensure_clean(root)
    proposals, meta = scan_logs(args, root)
    if not proposals and args.create_pr:
        print("no actionable proposal found; skipping PR creation")
        return
    markdown = proposals_to_markdown(proposals, meta)
    if args.dry_run:
        print(markdown)
        if args.apply_with_llm:
            print(f"dry-run: would ask {args.apply_with_llm} to update target skill(s) from the generated report")
        if args.create_pr:
            print("dry-run: would create a bot/skill-improvement-* branch, commit the generated report and any LLM edits, push, and open a PR")
        return
    report_path = write_report(root, markdown)
    print(f"wrote report: {report_path}")
    apply_with_llm(root, report_path, args.apply_with_llm, args.dry_run)
    run_command(["sh", "scripts/validate-repo.sh"], root)
    maybe_create_pr(root, report_path, args)


def cmd_review_pr(args: argparse.Namespace) -> None:
    root = repo_root()
    data = inspect_pr(root, args.pr)
    if args.apply_claude_feedback:
        if not has_trusted_review_activity(data):
            raise SystemExit("error: no trusted Claude review activity found; refusing automated feedback pass")
        apply_claude_feedback(root, args.pr, args.dry_run)
        data = inspect_pr(root, args.pr)
    if args.auto_merge:
        maybe_auto_merge(root, args.pr, data, args.dry_run)
    else:
        ready, ready_reason = claude_ready(data)
        checks_ok, checks_reason = checks_pass(data)
        print(
            json.dumps(
                {
                    "pr": data.get("number"),
                    "url": data.get("url"),
                    "claude_ready": ready,
                    "claude_reason": ready_reason,
                    "checks_ok": checks_ok,
                    "checks_reason": checks_reason,
                    "unresolved_threads": data.get("unresolved_threads"),
                    "is_draft": data.get("isDraft"),
                    "mergeable": data.get("mergeable"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


def cmd_review_open_prs(args: argparse.Namespace) -> None:
    root = repo_root()
    require_tool("gh")
    original_branch = run_command(["git", "branch", "--show-current"], root).stdout.strip()
    payload = run_command(
        ["gh", "pr", "list", "--state", "open", "--limit", "50", "--json", "number,title,url,headRefName"],
        root,
    )
    open_prs = json.loads(payload.stdout)
    if len(open_prs) == 50:
        print("warning: PR list may be truncated; only the first 50 open PRs were inspected", file=sys.stderr)
    prs = [
        item
        for item in open_prs
        if str(item.get("headRefName", "")).startswith(args.head_prefix)
    ]
    results = []
    for item in prs:
        number = str(item["number"])
        try:
            try:
                if args.apply_claude_feedback and not args.dry_run:
                    ensure_clean(root)
                    run_command(["gh", "pr", "checkout", number], root)
                data = inspect_pr(root, number)
                if args.apply_claude_feedback:
                    if not has_trusted_review_activity(data):
                        results.append(
                            {
                                "pr": data.get("number"),
                                "url": data.get("url"),
                                "skipped": "no trusted Claude review activity found",
                            }
                        )
                        continue
                    apply_claude_feedback(root, number, args.dry_run)
                    data = inspect_pr(root, number)
                if args.auto_merge:
                    maybe_auto_merge(root, number, data, args.dry_run)
                ready, ready_reason = claude_ready(data)
                checks_ok, checks_reason = checks_pass(data)
                results.append(
                    {
                        "pr": data.get("number"),
                        "url": data.get("url"),
                        "claude_ready": ready,
                        "claude_reason": ready_reason,
                        "checks_ok": checks_ok,
                        "checks_reason": checks_reason,
                        "unresolved_threads": data.get("unresolved_threads"),
                    }
                )
            except SystemExit as exc:
                results.append(
                    {
                        "pr": int(number) if number.isdigit() else number,
                        "url": item.get("url"),
                        "error": str(exc) or "command failed",
                    }
                )
        finally:
            if original_branch and not args.dry_run:
                run_command(["git", "switch", original_branch], root, check=False)
    print(json.dumps({"checked": len(prs), "pull_requests": results}, ensure_ascii=False, indent=2))


def cmd_cycle(args: argparse.Namespace) -> None:
    cmd_run(args)
    if args.apply_claude_feedback or args.auto_merge:
        cmd_review_open_prs(args)


def main() -> None:
    args = parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "cycle":
        cmd_cycle(args)
    elif args.command == "review-pr":
        cmd_review_pr(args)
    elif args.command == "review-open-prs":
        cmd_review_open_prs(args)
    else:
        raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
