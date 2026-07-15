#!/usr/bin/env python3
"""v3エンジンの汎用性スモークテスト。

ドライバーツリーが異なる収益アーキタイプ（ハードウェア単品販売＋SaaSアタッチ、
プロフェッショナルサービス）を表現でき、生成・機械検査・再計算ゲートが
通ることを確認する。

使い方: python3 smoke_test.py   （終了コード 0=全パス）
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).parent


def base_common(periods, extra_tree, roles, company, title):
    return {
        "company": company, "model_title": title,
        "start_year": 2027, "periods": periods,
        "source_note": "スモークテスト（合成データ）",
        "tree": extra_tree + [
            {"section": "9. 人員", "sheet": "headcount", "drivers": [
                {"id": "fte_all", "label": "総人員（期末）", "unit": "人",
                 "fmt": "cnt", "kind": "input", "basis": "仮置き",
                 "source": "採用計画", "values": [8, 16, 28, 40, 52][:periods]},
                {"id": "hires", "label": "新規採用数（純増）", "unit": "人",
                 "fmt": "cnt", "formula": "fte_all - prev(fte_all)"},
                {"id": "sal", "label": "平均年収", "unit": "円/年",
                 "fmt": "yen", "kind": "input", "basis": "仮置き",
                 "source": "市場相場", "values": 9000000},
                {"id": "burden", "label": "法定福利率", "unit": "%",
                 "fmt": "pct", "kind": "input", "basis": "ベンチマーク",
                 "source": "法定福利約16%", "values": 0.16},
                {"id": "payroll", "label": "人件費合計", "unit": "百万円",
                 "fmt": "m", "formula": "fte_all * sal * (1 + burden)",
                 "bold": True, "total": True},
            ]},
            {"section": "10. 営業費用・投資・税", "sheet": "costs",
             "drivers": [
                {"id": "mkt_rate", "label": "マーケ費率（対売上）", "unit": "%",
                 "fmt": "pct", "kind": "input", "basis": "仮置き",
                 "source": "初期GTM投資", "values": 0.12},
                {"id": "mkt", "label": "マーケティング費", "unit": "百万円",
                 "fmt": "m", "formula": "rev_all * mkt_rate"},
                {"id": "office_unit", "label": "オフィス単価", "unit": "円/人/年",
                 "fmt": "yen", "kind": "input", "basis": "仮置き",
                 "source": "都内相場", "values": 800000},
                {"id": "office", "label": "オフィス・ツール費", "unit": "百万円",
                 "fmt": "m", "formula": "fte_all * office_unit"},
                {"id": "capex", "label": "設備投資", "unit": "百万円",
                 "fmt": "m", "kind": "input", "basis": "仮置き",
                 "source": "開発設備", "values": 30000000},
                {"id": "dep_years", "label": "償却年数", "unit": "年",
                 "fmt": "cnt", "kind": "input", "basis": "仮置き",
                 "source": "税法耐用年数目安", "values": 5},
                {"id": "tax_rate", "label": "実効税率", "unit": "%",
                 "fmt": "pct", "kind": "input", "basis": "ベンチマーク",
                 "source": "日本実効税率30-34%", "values": 0.30},
                {"id": "nol0", "label": "期初繰越欠損金", "unit": "百万円",
                 "fmt": "m", "kind": "input", "basis": "仮置き",
                 "source": "設立時", "values": 0},
                {"id": "ar_days", "label": "売掛回収サイト", "unit": "日",
                 "fmt": "cnt", "kind": "input", "basis": "ベンチマーク",
                 "source": "末締め翌月末", "values": 45},
                {"id": "ap_days", "label": "買掛支払サイト", "unit": "日",
                 "fmt": "cnt", "kind": "input", "basis": "仮置き",
                 "source": "同上", "values": 30},
                {"id": "cash0", "label": "期初現金", "unit": "百万円",
                 "fmt": "m", "kind": "input", "basis": "仮置き",
                 "source": "手元資金", "values": 400000000},
            ]},
        ],
        "roles": roles,
        "statements": {"dep_years_driver": "dep_years",
                       "tax_rate_driver": "tax_rate",
                       "nol_opening_driver": "nol0"},
        "financing": {"rounds": [
            {"year_index": 1, "label": "シリーズA", "amount": 2500000000}]},
    }


def hardware_attach(periods=4):
    """アーキタイプ5+8: 単品販売（コストダウンカーブ）＋SaaSアタッチ。"""
    tree = [
        {"section": "1. 需要｜出荷とインストールベース", "sheet": "revenue",
         "drivers": [
            {"id": "units", "label": "出荷台数", "unit": "台", "fmt": "cnt",
             "kind": "input", "basis": "逆算",
             "source": "販売計画（最終年目標からの逆算）",
             "values": [200, 800, 2000, 4000][:periods],
             "cases": {"Upside": [300, 1200, 3000, 6000][:periods],
                       "Downside": [120, 480, 1200, 2400][:periods]}},
            {"id": "base_units", "label": "累計インストールベース", "unit": "台",
             "fmt": "cnt", "formula": "prev(base_units) + units",
             "note": "リタイアメントなしの簡便法"},
        ]},
        {"section": "2. 単価と原価カーブ", "sheet": "revenue", "drivers": [
            {"id": "asp", "label": "平均販売単価（ASP）", "unit": "円/台",
             "fmt": "yen", "kind": "input", "basis": "記載",
             "source": "価格表", "values": 1200000},
            {"id": "bom", "label": "BOM＋製造原価/台", "unit": "円/台",
             "fmt": "yen", "kind": "input", "basis": "仮置き",
             "source": "コストダウンカーブ（量産効果）",
             "values": [800000, 680000, 580000, 500000][:periods]},
            {"id": "attach", "label": "SaaSアタッチ率", "unit": "%",
             "fmt": "pct", "kind": "input", "basis": "仮置き",
             "source": "同種HW+SaaSの実務水準", "values": 0.6},
            {"id": "saas_fee", "label": "SaaS月額/台", "unit": "円/月",
             "fmt": "yen", "kind": "input", "basis": "記載",
             "source": "価格表", "values": 20000},
        ]},
        {"section": "3. 収益（HW＋アタッチSaaS）", "sheet": "revenue",
         "drivers": [
            {"id": "hw_rev", "label": "ハードウェア売上", "unit": "百万円",
             "fmt": "m", "formula": "units * asp"},
            {"id": "saas_subs", "label": "SaaS課金台数（期末）", "unit": "台",
             "fmt": "cnt", "formula": "base_units * attach",
             "note": "リカーリングはインストールベース×アタッチに整合"},
            {"id": "saas_rev", "label": "SaaS売上", "unit": "百万円",
             "fmt": "m", "formula": "saas_subs * saas_fee * 12"},
            {"id": "rev_all", "label": "売上高合計（参照用）", "unit": "百万円",
             "fmt": "m", "formula": "hw_rev + saas_rev"},
        ]},
        {"section": "4. 原価", "sheet": "costs", "drivers": [
            {"id": "hw_cogs", "label": "ハードウェア原価", "unit": "百万円",
             "fmt": "m", "formula": "units * bom"},
            {"id": "saas_cogs_rate", "label": "SaaS原価率", "unit": "%",
             "fmt": "pct", "kind": "input", "basis": "仮置き",
             "source": "ホスティング等", "values": 0.2},
            {"id": "saas_cogs", "label": "SaaS原価", "unit": "百万円",
             "fmt": "m", "formula": "saas_rev * saas_cogs_rate"},
        ]},
    ]
    roles = {
        "revenue_lines": [
            {"driver": "hw_rev", "label": "ハードウェア売上",
             "onetime": True, "scales": "vol"},
            {"driver": "saas_rev", "label": "SaaS売上", "scales": "both"}],
        "cogs_lines": [
            {"driver": "hw_cogs", "label": "ハードウェア原価", "scales": "vol"},
            {"driver": "saas_cogs", "label": "SaaS原価", "scales": "both"}],
        "opex_sm_lines": [{"driver": "mkt", "label": "マーケティング費",
                           "scales": "both"}],
        "opex_rd_lines": [{"driver": "payroll", "label": "人件費（全社）",
                           "scales": "fixed"}],
        "opex_ga_lines": [{"driver": "office", "label": "オフィス・ツール",
                           "scales": "fixed"}],
        "variable_cost_lines": [{"driver": "hw_cogs"}, {"driver": "saas_cogs"},
                                {"driver": "mkt"}],
        "arr": "saas_rev", "onetime_revenue": "hw_rev",
        "new_units": ["units"], "fte_total": "fte_all",
        "payroll_total": "payroll", "hires": "hires", "capex": "capex",
        "ar_days": "ar_days", "ap_days": "ap_days",
        "beginning_cash": "cash0",
    }
    cfg = base_common(periods, tree, roles, "SmokeHW",
                      "HW＋SaaSアタッチ スモーク")
    cfg["scenario"] = {"cases": ["Base", "Upside", "Downside"],
                       "active": "Base"}
    cfg["scenario_scales"] = {"volume": [0.8, 1.0, 1.2],
                              "price": [0.95, 1.0, 1.05]}
    # units は最終年目標からの逆算なので、照合とセットにする（分解ガイドS2）。
    # 逆算値が販売計画の最終年目標と整合していることを突き合わせる。
    cfg["source_bounds"] = [{
        "driver": "units", "label": "販売計画の最終年目標（台）",
        "value": [200, 800, 2000, 4000][:periods][-1],
        "fmt": "cnt", "unit": "台",
        "note": "逆算した出荷台数が販売計画の最終年目標と整合（記載）",
    }]
    return cfg


def services(periods=5):
    """アーキタイプ6: 稼働人員×稼働率×単価のサービス業（供給キャップ）。"""
    tree = [
        {"section": "1. 供給能力（ビラブル人員）", "sheet": "revenue",
         "drivers": [
            {"id": "billable", "label": "ビラブル人員（期末）", "unit": "人",
             "fmt": "cnt", "kind": "input", "basis": "仮置き",
             "source": "採用計画", "values": [10, 20, 35, 50, 70][:periods]},
            {"id": "hours_pm", "label": "月間稼働可能時間/人", "unit": "時間",
             "fmt": "cnt", "kind": "input", "basis": "ベンチマーク",
             "source": "160h/月", "values": 160},
            {"id": "util", "label": "稼働率", "unit": "%", "fmt": "pct",
             "kind": "input", "basis": "ベンチマーク",
             "source": "PS業界70-80%帯（Kantata）", "values": 0.75},
            {"id": "bill_rate", "label": "請求単価", "unit": "円/時間",
             "fmt": "yen", "kind": "input", "basis": "記載",
             "source": "料金表", "values": 15000},
        ]},
        {"section": "2. 収益（供給キャップ）", "sheet": "revenue", "drivers": [
            {"id": "bill_hours", "label": "請求可能時間", "unit": "時間",
             "fmt": "cnt", "formula": "billable * hours_pm * util * 12"},
            {"id": "svc_rev", "label": "サービス売上", "unit": "百万円",
             "fmt": "m", "formula": "bill_hours * bill_rate",
             "note": "供給キャップ型: 需要が供給を超える計画は不可"},
            {"id": "rev_all", "label": "売上高合計（参照用）", "unit": "百万円",
             "fmt": "m", "formula": "svc_rev"},
        ]},
        {"section": "3. 原価（デリバリー）", "sheet": "costs", "drivers": [
            {"id": "delivery_rate", "label": "外注・ツール原価率", "unit": "%",
             "fmt": "pct", "kind": "input", "basis": "仮置き",
             "source": "外注比率", "values": 0.15},
            {"id": "delivery_cogs", "label": "外注・ツール原価", "unit": "百万円",
             "fmt": "m", "formula": "svc_rev * delivery_rate"},
        ]},
    ]
    roles = {
        "revenue_lines": [{"driver": "svc_rev", "label": "サービス売上",
                           "scales": "both"}],
        "cogs_lines": [
            {"driver": "delivery_cogs", "label": "外注・ツール原価",
             "scales": "both"},
            {"driver": "payroll", "label": "デリバリー人件費",
             "scales": "fixed"}],
        "opex_sm_lines": [{"driver": "mkt", "label": "マーケティング費",
                           "scales": "both"}],
        "opex_ga_lines": [{"driver": "office", "label": "オフィス・ツール",
                           "scales": "fixed"}],
        "variable_cost_lines": [{"driver": "delivery_cogs"},
                                {"driver": "mkt"}],
        "new_units": ["billable"], "fte_total": "fte_all",
        "payroll_total": "payroll", "hires": "hires", "capex": "capex",
        "ar_days": "ar_days", "ap_days": "ap_days",
        "beginning_cash": "cash0",
    }
    return base_common(periods, tree, roles, "SmokePS",
                       "プロフェッショナルサービス スモーク")


def run(name, cfg):
    with tempfile.TemporaryDirectory() as td:
        y = Path(td) / "plan.yaml"
        y.write_text(yaml.safe_dump(cfg, allow_unicode=True),
                     encoding="utf-8")
        out = Path(td) / "out"
        r = subprocess.run([sys.executable, str(HERE / "build_workbook.py"),
                            "--input", str(y), "--outdir", str(out),
                            "--name", "smoke"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL {name}: build\n{r.stderr[-1500:]}")
            return False
        r = subprocess.run([sys.executable, str(HERE / "inspect_workbook.py"),
                            str(out / "smoke.xlsx"), "--recalc"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL {name}: inspect\n{r.stdout[-1500:]}")
            return False
        print(f"PASS {name}")
        return True


def expect_build_fail(name, cfg, needle):
    """変異入力でビルドが**失敗し、狙ったエラーが出る**ことを確認する負テスト。

    ゲートは「鳴らないなら偽の保証」。正常系がPASSするだけでは、誰かがゲートの
    述語を弱めても気づけない。ここで実際に変異を注入し、ModelErrorが出ることを
    アサートして、ゲートの実効性そのものを回帰させる。
    """
    with tempfile.TemporaryDirectory() as td:
        y = Path(td) / "plan.yaml"
        y.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        r = subprocess.run([sys.executable, str(HERE / "build_workbook.py"),
                            "--input", str(y), "--outdir", str(Path(td) / "o"),
                            "--name", "smoke"], capture_output=True, text=True)
        blob = r.stdout + r.stderr
        if r.returncode == 0:
            print(f"FAIL {name}: ゲートが発火せずビルド成功（偽の保証）")
            return False
        if needle not in blob:
            print(f"FAIL {name}: 別の理由で失敗\n{blob[-800:]}")
            return False
        print(f"PASS {name}（ゲート発火を確認）")
        return True


def _mutate(cfg_fn, mutate):
    cfg = cfg_fn
    import copy
    c = copy.deepcopy(cfg)
    mutate(c)
    return c


def _drop_reconciliation(c):
    c["source_bounds"] = []
    c["story_checks"] = {}
    c.pop("scenario_reference", None)


def _identical_cases(c):
    for sec in c["tree"]:
        for d in sec["drivers"]:
            if "cases" in d:
                base = d["values"]
                for cn in d["cases"]:
                    d["cases"][cn] = base   # 全ケースを base と同値に
                return


def main():
    ok = True
    ok &= run("hardware_attach_4y_scenario", hardware_attach(4))
    ok &= run("services_5y_minimal", services(5))
    # --- ゲートの実効性回帰（負テスト）: 変異を注入して発火を確認 ---
    ok &= expect_build_fail(
        "neg_S2_no_reconciliation",
        _mutate(hardware_attach(4), _drop_reconciliation), "停止条件S2")
    ok &= expect_build_fail(
        "neg_S3_identical_cases",
        _mutate(hardware_attach(4), _identical_cases), "停止条件S3")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
