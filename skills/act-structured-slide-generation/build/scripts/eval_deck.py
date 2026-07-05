#!/usr/bin/env python3
"""Rubric-based multimodal eval of a rendered deck using gemini + codex CLIs as judges.

Usage: eval_deck.py <render_dir_with_pngs> [--judge gemini|codex|both] [--anchor <text>]

--anchor: a phrase that appears on slide 1 (e.g. the deck title). Judges must read it
back; a verdict whose readback doesn't contain the phrase is discarded as hallucination.

Reads build/evals/rubric.json, sends every slide PNG to each judge with a
defect-deduction rubric prompt, parses strict-JSON verdicts, and prints a
score report. Exit 0 if mean total >= pass_threshold, else exit 1.
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


def judge_prompt() -> str:
    cats = []
    for c in RUBRIC["categories"]:
        crit = "\n".join(f"  [{c['id']}-{k + 1}] {x}" for k, x in enumerate(c["criteria"]))
        cats.append(f"■ {c['name']}(id: {c['id']}、満点 {c['max_points']}点)\n{crit}")
    cats_text = "\n".join(cats)
    return f"""あなたは投資銀行・IR資料の品質審査員です。添付のスライド画像(1つのデッキ)を審査してください。

手順(チェックリスト方式。全体の印象では採点しない):
1. まず各スライドの内容(タイトル・図表・数値)を観察する。
2. 下の各チェック項目を **1枚ずつのスライドに pass/fail で適用**する。
3. fail のみを deduction として列挙する。各 fail には check ID・スライド番号・
   **そのスライドに実際に見えている文字列や要素を引用した根拠**を必ず添える。
   引用できない指摘は書いてはならない(推測・一般論・改善提案は fail ではない)。
4. 確信が持てない場合は減点しない。同一の欠陥は 1 スライドにつき 1 減点まで。

severity: minor(読者は気づくが実害小)= -1 / major(明確な品質毀損)= -3 /
critical(プロ資料として失格級)= -5。カテゴリ下限は 0 点。

{cats_text}

出力は次の JSON のみ(コードフェンスなし、説明文なし)。slide1_readback には
1枚目のスライドに実際に書かれているタイトル文字列をそのまま書き写すこと:
{{"slide1_readback": "...", "slide_count": 12,
 "categories": {{"story": {{"deductions": [{{"check": "story-2", "slide": 3, "severity": "major", "defect": "...", "evidence": "スライド上の引用"}}], "points": 17}},
  "layout": {{...}}, "typography": {{...}}, "color": {{...}}, "chart": {{...}}, "evidence": {{...}}}},
 "total": 87, "one_line_verdict": "..."}}"""


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON found in judge output: {text[:300]}")
    return json.loads(m.group(0))


def run_gemini(pngs: list[Path], prompt: str) -> dict:
    refs = " ".join(f"@{p}" for p in pngs)
    env = dict(os.environ, GEMINI_CLI_TRUST_WORKSPACE="true")
    r = subprocess.run(["gemini", "-m", "gemini-2.5-pro", "-p", f"{refs} {prompt}"], capture_output=True,
                       text=True, timeout=600, env=env, cwd=pngs[0].parent)
    if r.returncode != 0:
        raise RuntimeError(f"gemini failed: {r.stderr[:300]}")
    return _extract_json(r.stdout)


def run_codex(pngs: list[Path], prompt: str) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        out_file = tf.name
    cmd = ["codex", "exec", "--skip-git-repo-check", "--output-last-message", out_file]
    for p in pngs:
        cmd += ["-i", str(p)]
    cmd += ["--", prompt]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=pngs[0].parent)
    text = Path(out_file).read_text() if Path(out_file).exists() else r.stdout
    Path(out_file).unlink(missing_ok=True)
    if not text.strip():
        raise RuntimeError(f"codex empty output: {r.stderr[:300]}")
    return _extract_json(text)


def clamp_scores(verdict: dict) -> dict:
    """Recompute points from deductions so judges can't mis-add."""
    scale = RUBRIC["deduction_scale"]
    missing = [c["id"] for c in RUBRIC["categories"] if c["id"] not in verdict.get("categories", {})]
    if missing:
        # a silently skipped category would score as full points — discard the verdict instead
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
    judge = "both"
    anchor = None
    if "--judge" in args:
        i = args.index("--judge")
        judge = args[i + 1]
        del args[i:i + 2]
    if "--anchor" in args:
        i = args.index("--anchor")
        anchor = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__)
        return 1
    render_dir = Path(args[0])
    pngs = sorted(render_dir.glob("*.png"))
    pngs = [p for p in pngs if re.search(r"-\d+\.png$", p.name)]
    if not pngs:
        print(f"no slide PNGs in {render_dir}")
        return 1
    prompt = judge_prompt()
    verdicts: dict[str, dict] = {}
    for name, fn in (("gemini", run_gemini), ("codex", run_codex)):
        if judge not in ("both", name):
            continue
        try:
            v = clamp_scores(fn(pngs, prompt))
            readback = str(v.get("slide1_readback", ""))
            if anchor and anchor not in readback:
                print(f"WARN: judge {name} discarded — slide1 readback '{readback[:60]}' does not contain anchor '{anchor}' (likely judged wrong images)")
            else:
                verdicts[name] = v
        except Exception as e:
            print(f"WARN: judge {name} failed: {e}")
    if not verdicts:
        print("FAIL: no judge produced a verdict")
        return 1

    print(f"\n=== rubric eval: {len(pngs)} slides / judges: {', '.join(verdicts)} ===")
    for name, v in verdicts.items():
        print(f"\n--- {name}: total {v['total']}/100 — {v.get('one_line_verdict', '')}")
        for c in RUBRIC["categories"]:
            cat = v["categories"].get(c["id"], {})
            print(f"  {c['id']:<10} {cat.get('points', '?'):>2}/{c['max_points']}")
            for d in cat.get("deductions", []):
                ev = f" 〈{d['evidence']}〉" if d.get("evidence") else ""
                print(f"      [-{RUBRIC['deduction_scale'].get(d.get('severity', 'major'), 3)}] s{d.get('slide', '?')} {d.get('check', '')}: {d.get('defect', '')}{ev}")
    mean = sum(v["total"] for v in verdicts.values()) / len(verdicts)
    thr = RUBRIC["pass_threshold"]
    print(f"\nMEAN SCORE: {mean:.1f} / 100  (threshold {thr})")
    print("PASS" if mean >= thr else "FAIL")
    return 0 if mean >= thr else 1


if __name__ == "__main__":
    sys.exit(main())
