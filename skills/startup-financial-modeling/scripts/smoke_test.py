#!/usr/bin/env python3
"""生成器の汎用性スモークテスト。

ACT固有形状（4セグメント・年0調達・全任意ブロックあり）以外の入力でも
生成と機械検査が通ることを確認する。

使い方: python3 smoke_test.py
終了コード 0=全パス / 1=失敗
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).parent

CASES = {
    # 最小構成: B2B 2セグメントのみ・ToCなし・任意ブロックなし・
    # 調達は2年目（year_index=1）・6期・同一allocationの重複職能
    "minimal_b2b_only_6y": {
        "company": "SmokeCo",
        "model_title": "スモークテスト最小構成",
        "start_year": 2027,
        "periods": 6,
        "segments": [
            {"name": "Core", "unit_label": "社",
             "ending_customers": [10, 30, 80, 150, 240, 320],
             "churn_rate": 0.08, "fixed_fee_monthly": 200000,
             "usage_fee_monthly": 300000, "usage_rate_per_min": 10,
             "implementation_fee": 1000000,
             "cost_per_min": [8, 6, 5, 4, 3, 3]},
            {"name": "Enterprise", "unit_label": "社",
             "ending_customers": [1, 4, 10, 20, 32, 45],
             "churn_rate": 0.03, "fixed_fee_monthly": 1500000,
             "usage_fee_monthly": 2000000, "usage_rate_per_min": 25,
             "implementation_fee": 10000000,
             "cost_per_min": [18, 14, 10, 8, 6, 5]},
        ],
        "implementation_cost_pct": [0.6, 0.55, 0.5, 0.5, 0.45, 0.45],
        "headcount": [
            {"function": "R&D（基盤）", "fte": [5, 10, 18, 26, 34, 40],
             "avg_salary": 12000000, "allocation": "R&D"},
            {"function": "R&D（アプリ）", "fte": [3, 6, 12, 18, 24, 30],
             "avg_salary": 11000000, "allocation": "R&D"},
            {"function": "セールス", "fte": [2, 6, 14, 24, 34, 44],
             "avg_salary": 10000000, "allocation": "S&M"},
            {"function": "CS", "fte": [1, 3, 7, 12, 18, 24],
             "avg_salary": 8000000, "allocation": "COGS"},
            {"function": "コーポレート", "fte": [1, 2, 4, 7, 10, 13],
             "avg_salary": 10000000, "allocation": "G&A"},
        ],
        "payroll_burden_rate": 0.16,
        "recruiting_cost_per_hire": 1000000,
        "opex": {
            "sm_pct_of_revenue": [0.2, 0.18, 0.16, 0.14, 0.12, 0.12],
            "rd_program_yen": [50000000, 100000000, 200000000,
                               300000000, 400000000, 450000000],
            "office_cost_per_fte": 1000000,
            "ga_pct_of_revenue": 0.02,
        },
        "capex_yen": [50000000, 80000000, 120000000,
                      150000000, 180000000, 200000000],
        "depreciation_years": 5,
        "tax_rate": 0.30,
        "ar_days": 60,
        "ap_days": 30,
        "financing": {
            "beginning_cash": 500000000,
            "rounds": [{"year_index": 1, "label": "シリーズA",
                        "amount": 4000000000}],
        },
    },
}


def run_case(name, cfg, with_captable=False):
    if with_captable:
        cfg = dict(cfg)
        cfg["cap_table"] = {
            "founder_shares": 1000000,
            "pool_expansion_shares": 150000,
            "post_money": 6000000000,
        }
        cfg["valuation"] = {
            "discount_rate": [0.35, 0.28, 0.22],
            "gordon_g": 0.02,
            "ebitda_exit_multiple": [6, 10, 14],
            "rev_exit_multiple": [2.5, 4.0, 6.0],
            "txn_multiple": [3.0, 4.5, 6.5],
            "dlom": 0.25,
            "moic_target": 10,
            "adopted_range": [3000000000, 8000000000],
            "comps": [{"name": f"Comp{i}", "ev_rev": 2.0 + i * 0.7,
                       "growth": 0.2 + i * 0.02} for i in range(5)],
            "transactions": [{"name": f"Deal{i}", "ev_rev": 3.0 + i}
                             for i in range(3)],
        }
        # scenario_referenceは意図的に置かない（任意ブロック欠落の回帰確認）
        name += "_captable_valuation_no_scenarioref"
    with tempfile.TemporaryDirectory() as td:
        y = Path(td) / "plan.yaml"
        y.write_text(yaml.safe_dump(cfg, allow_unicode=True),
                     encoding="utf-8")
        out = Path(td) / "out"
        r = subprocess.run(
            [sys.executable, str(HERE / "build_workbook.py"),
             "--input", str(y), "--outdir", str(out), "--name", "smoke"],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL {name}: build\n{r.stderr[-1500:]}")
            return False
        r = subprocess.run(
            [sys.executable, str(HERE / "inspect_workbook.py"),
             str(out / "smoke.xlsx"), "--recalc"],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL {name}: inspect\n{r.stdout[-1500:]}")
            return False
        print(f"PASS {name}")
        return True


def main():
    ok = True
    for name, cfg in CASES.items():
        ok &= run_case(name, cfg, with_captable=False)
        ok &= run_case(name, cfg, with_captable=True)
    # 短期間（4期）でのcap_table/valuation: 感応度3点フォールバックの回帰確認
    short = dict(CASES["minimal_b2b_only_6y"])
    short["periods"] = 4
    short["segments"] = [dict(s, ending_customers=s["ending_customers"][:4],
                              cost_per_min=s["cost_per_min"][:4])
                         for s in short["segments"]]
    short["implementation_cost_pct"] = short["implementation_cost_pct"][:4]
    short["headcount"] = [dict(h, fte=h["fte"][:4]) for h in short["headcount"]]
    short["opex"] = dict(short["opex"],
                         sm_pct_of_revenue=short["opex"]["sm_pct_of_revenue"][:4],
                         rd_program_yen=short["opex"]["rd_program_yen"][:4])
    short["capex_yen"] = short["capex_yen"][:4]
    ok &= run_case("short_4y", short, with_captable=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
