#!/usr/bin/env python3
"""Multimodal rubric eval of a rendered deck, judged by an independent reviewer running in
the *other* CLI's non-interactive mode.

Pairing (independent perspective — a different model/tool reviews than the one that built):
  - host Claude Code  → judge with Codex:        --judge codex
  - host Codex        → judge with Claude Code:   --judge claude
  (legacy: --judge gemini)

Usage:
  eval_deck.py <render_dir> --judge codex|claude [--anchor "<slide-1 title phrase>"]
  eval_deck.py <render_dir> --judge codex|claude --resume        # continue the same
                                                                 # judge session with the
                                                                 # revised images

Iterate-to-95 loop (driven by SKILL.md, no round cap):
  1. render the deck, run this with a fresh judge → score.
  2. if total < pass_threshold: fix deck.json, re-render, run again with --resume so the
     SAME judge session scores the revised images (it remembers its prior findings).
  3. repeat until total >= pass_threshold (exit 0).

--anchor: a phrase from slide 1's *title*. The judge reads it back; a verdict whose readback
omits it is discarded as a hallucination (it judged the wrong images). Only meaningful on the
first pass (fresh session).

Reads build/evals/rubric.json (categories, deduction_scale, pass_threshold). Points are
recomputed from the listed deductions so a judge cannot mis-add. Exit 0 iff total >=
pass_threshold, else 1.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUBRIC = json.loads((HERE.parent / "evals" / "rubric.json").read_text())

REVIEWER_ROLE = (
    "あなたは投資銀行・IR資料を専門に審査する独立の品質レビュアーです。資料の作成者とは"
    "別人格として、忖度なく、実際に画像に見えているものだけを根拠に評価します。"
)


def rubric_body() -> str:
    cats = []
    for c in RUBRIC["categories"]:
        crit = "\n".join(f"  [{c['id']}-{k + 1}] {x}" for k, x in enumerate(c["criteria"]))
        cats.append(f"■ {c['name']}(id: {c['id']}、満点 {c['max_points']}点)\n{crit}")
    return "\n".join(cats)


def judge_prompt() -> str:
    return f"""{REVIEWER_ROLE}

添付のスライド画像(1つのデッキ)を審査してください。

手順(チェックリスト方式。全体の印象では採点しない):
1. まず各スライドの内容(タイトル・図表・数値・レイアウト)を1枚ずつ観察する。
2. 下の各チェック項目を **1枚ずつのスライドに pass/fail で適用**する。
3. fail のみを deduction として列挙する。各 fail には check ID・スライド番号・
   **そのスライドに実際に見えている文字列や要素を引用した根拠**を必ず添える。
   引用できない指摘は書いてはならない(推測・一般論・改善提案は fail ではない)。
4. 確信が持てない場合は減点しない。同一の欠陥は 1 スライドにつき 1 減点まで。

severity: minor(読者は気づくが実害小)= -1 / major(明確な品質毀損)= -3 /
critical(プロ資料として失格級)= -5。カテゴリ下限は 0 点。

{rubric_body()}

出力は次の JSON のみ(コードフェンスなし、説明文なし)。slide1_readback には
1枚目のスライドに実際に書かれているタイトル文字列をそのまま書き写すこと:
{{"slide1_readback": "...", "slide_count": 12,
 "categories": {{"story": {{"deductions": [{{"check": "story-2", "slide": 3, "severity": "major", "defect": "...", "evidence": "スライド上の引用"}}], "points": 17}},
  "layout": {{...}}, "typography": {{...}}, "color": {{...}}, "chart": {{...}}, "evidence": {{...}}}},
 "total": 87, "one_line_verdict": "..."}}"""


RESUME_PROMPT = (
    "改善版のスライド画像です。前回あなたが指摘した欠陥が直っているかを最優先で確認し、"
    "同じルーブリック・同じ手順で採点し直してください。新たな欠陥があれば追加し、解消した"
    "指摘は除いてください。出力は前回と同一の JSON 形式のみ(コードフェンス・説明文なし)。"
)


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON found in judge output: {text[:300]}")
    return json.loads(m.group(0))


def run_codex(pngs: list[Path], resume: bool) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        out_file = tf.name
    base = ["codex", "exec"]
    if resume:
        base += ["resume", "--last"]
    cmd = base + ["--skip-git-repo-check", "--output-last-message", out_file]
    for p in pngs:
        cmd += ["-i", str(p)]
    cmd += ["--", RESUME_PROMPT if resume else judge_prompt()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=pngs[0].parent)
    text = Path(out_file).read_text() if Path(out_file).exists() else ""
    Path(out_file).unlink(missing_ok=True)
    if not text.strip():
        text = r.stdout
    if not text.strip():
        raise RuntimeError(f"codex empty output: {r.stderr[:300]}")
    return _extract_json(text)


def run_claude(pngs: list[Path], resume: bool) -> dict:
    listing = "\n".join(str(p) for p in pngs)
    instr = RESUME_PROMPT if resume else judge_prompt()
    full = (f"{instr}\n\n審査対象スライド画像(番号順、Read ツールで1枚ずつ開いて観察):\n"
            f"{listing}\n\n全画像を Read で確認したうえで、上記 JSON のみを最終メッセージに出力。")
    # prompt goes on stdin: --allowedTools is variadic and would otherwise swallow it
    cmd = ["claude", "-p", "--output-format", "json", "--permission-mode", "bypassPermissions"]
    if resume:
        cmd.append("-c")  # continue the most recent conversation (this project dir)
    r = subprocess.run(cmd, input=full, capture_output=True, text=True, timeout=1800,
                       cwd=pngs[0].parent)
    if not r.stdout.strip():
        raise RuntimeError(f"claude empty output: {r.stderr[:300]}")
    try:
        env = json.loads(r.stdout)
        text = env.get("result", r.stdout) if isinstance(env, dict) else r.stdout
    except json.JSONDecodeError:
        text = r.stdout
    return _extract_json(text)


def run_gemini(pngs: list[Path], resume: bool) -> dict:
    refs = " ".join(f"@{p}" for p in pngs)
    env = dict(os.environ, GEMINI_CLI_TRUST_WORKSPACE="true")
    r = subprocess.run(["gemini", "-m", "gemini-2.5-pro", "-p", f"{refs} {judge_prompt()}"],
                       capture_output=True, text=True, timeout=900, env=env, cwd=pngs[0].parent)
    if r.returncode != 0:
        raise RuntimeError(f"gemini failed: {r.stderr[:300]}")
    return _extract_json(r.stdout)


JUDGES = {"codex": run_codex, "claude": run_claude, "gemini": run_gemini}


def clamp_scores(verdict: dict) -> dict:
    """Recompute points from deductions so a judge cannot mis-add."""
    scale = RUBRIC["deduction_scale"]
    missing = [c["id"] for c in RUBRIC["categories"] if c["id"] not in verdict.get("categories", {})]
    if missing:
        raise ValueError(f"verdict missing rubric categories: {', '.join(missing)}")
    total = 0
    for c in RUBRIC["categories"]:
        cat = verdict.get("categories", {}).get(c["id"], {})
        ded = sum(scale.get(d.get("severity", "major"), 3) for d in cat.get("deductions", []))
        pts = max(0, c["max_points"] - ded)
        cat["points"] = pts
        verdict.setdefault("categories", {})[c["id"]] = cat
        total += pts
    verdict["total"] = total
    return verdict


def main() -> int:
    args = sys.argv[1:]
    judge = "codex"
    anchor = None
    resume = False
    if "--judge" in args:
        i = args.index("--judge"); judge = args[i + 1]; del args[i:i + 2]
    if "--anchor" in args:
        i = args.index("--anchor"); anchor = args[i + 1]; del args[i:i + 2]
    if "--resume" in args:
        resume = True; args.remove("--resume")
    if len(args) != 1 or judge not in JUDGES:
        print(__doc__)
        return 1
    render_dir = Path(args[0])
    pngs = sorted((p for p in render_dir.glob("*.png") if re.search(r"-\d+\.png$", p.name)),
                  key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))
    if not pngs:
        print(f"no slide PNGs in {render_dir}")
        return 1
    try:
        v = clamp_scores(JUDGES[judge](pngs, resume))
    except Exception as e:
        if resume:
            # session continuation is best-effort; a fresh scoring pass always backstops it
            print(f"NOTE: {judge} resume gave no usable verdict ({e}); re-scoring with a fresh session")
            try:
                v = clamp_scores(JUDGES[judge](pngs, False))
            except Exception as e2:
                print(f"FAIL: judge {judge} produced no usable verdict: {e2}")
                return 1
        else:
            print(f"FAIL: judge {judge} produced no usable verdict: {e}")
            return 1
    if anchor and not resume:
        readback = str(v.get("slide1_readback", ""))
        if anchor not in readback:
            print(f"FAIL: judge {judge} discarded — slide1 readback '{readback[:60]}' "
                  f"lacks anchor '{anchor}' (likely judged the wrong images)")
            return 1

    thr = RUBRIC["pass_threshold"]
    print(f"\n=== rubric eval: {len(pngs)} slides / judge: {judge}"
          f"{' (resumed)' if resume else ''} ===")
    print(f"--- total {v['total']}/100 — {v.get('one_line_verdict', '')}")
    for c in RUBRIC["categories"]:
        cat = v["categories"].get(c["id"], {})
        print(f"  {c['id']:<10} {cat.get('points', '?'):>2}/{c['max_points']}")
        for d in cat.get("deductions", []):
            ev = f" 〈{d['evidence']}〉" if d.get("evidence") else ""
            sev = RUBRIC["deduction_scale"].get(d.get("severity", "major"), 3)
            print(f"      [-{sev}] s{d.get('slide', '?')} {d.get('check', '')}: {d.get('defect', '')}{ev}")
    passed = v["total"] >= thr
    print(f"\nSCORE: {v['total']} / 100  (threshold {thr})")
    if passed:
        print("PASS")
    else:
        print(f"BELOW THRESHOLD — fix deck.json, re-render, then rerun with --judge {judge} "
              f"--resume so the same reviewer scores the revised images.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
