#!/usr/bin/env python3
"""Stress fixture for dynamic (spec-driven, variable-n) deck generation.

Usage: stress_deck.py [-o OUTDIR] [--variant max|min|overload|all] [--template NAME] [--images] [--lint]

Generates a synthetic deck.json that exercises EVERY pattern at its minimum and maximum
cardinality with long, wrap-prone Japanese copy, then builds it and audits the .pptx with
verify_deck. A layout engine that survives this fixture does not break when a real spec
pushes a pattern to its edges — that is the regression guard behind "dynamic generation
without design breakage". Exit 0 = every variant builds with 0 verify failures.

The copy is synthetic by design (it is a layout fixture, not an argument), so the deck is not
meant to pass audit_argument; validate_spec must still report 0 errors (header contract,
cardinality caps, data shape) — that is asserted here too.

--images adds the image-asset patterns (diagram, combo chart); they need matplotlib/Graphviz.
--lint renders the max variant (LibreOffice) and runs lint_render on it; its findings gate the exit code.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

LONG = "電子帳簿保存法とインボイス制度への対応を単一のワークフローで完結させる統合基盤"
MID = "会計事務所チャネルで中堅企業120社を獲得"
SHORT = "経理で足場"


def _n(variant: str, lo: int, hi: int) -> int:
    return lo if variant == "min" else hi


def _txt(variant: str, long_: str, short: str) -> str:
    return short if variant == "min" else long_


# 変種: min = 最小要素数・短い語 / max = 文書化された上限の要素数と現実的に長いコピー /
# overload = max の要素数に極端に長いコピー(入り切らない)。max は 0 failures が契約、
# overload は「枠がスライドの外に出ない・図形が縁をまたがない」だけを契約にする(溢れは
# verify が名指しする、それが正しい振る舞い)
VARIANTS = ("max", "min", "overload")


def make_deck(variant: str = "max", template: str | None = None, images: bool = False) -> dict:
    v = variant
    overload = variant == "overload"
    T = lambda long_, short: _txt(v, long_, short)  # noqa: E731
    N = lambda lo, hi: _n(v, lo, hi)  # noqa: E731
    # 上限要素数のときの現実的なコピー長(overload は LONG のまま)
    CELL = LONG if overload else MID                      # roadmap のセル
    BULLET = LONG if overload else "初月20社の導入体制"     # 5ステップの箇条書き
    PILLAR_BODY = LONG if overload else MID               # 柱・2列の本文
    N_TWO = 4 if overload else 3                          # two_column の項目数
    cats = ["FY22", "FY23", "FY24", "FY25", "FY26E", "FY27E", "FY28E", "FY29E"][: N(3, 8)]
    vals = [1.4, 1.6, 1.8, 2.1, 2.4, 2.8, 3.2, 3.6][: len(cats)]
    take = [{"heading": T("クラウドシフトの不可逆性と中堅企業への波及", "後押し"),
             "body": T("クラウド移行は大企業から中堅企業へ波及し、2026年以降は従業員300-999名の中堅企業が主役"
                       if overload else "クラウド移行は中堅企業へ波及、2026年以降は中堅企業が主役", "制度対応が契機")}
            for _ in range(N(1, 3))]
    slides = [
        {"pattern": "cover", "title": T("国内SaaS参入戦略 ストレス版", "参入戦略"),   # bold の表紙容量(16字)に収める
         "subtitle": T("市場機会の評価と参入シナリオの提言\n経理領域を起点とした中堅企業セグメント参入", "提言\n概要"),
         "date": "2026年9月", "author": "Act Strategy Team"},
        {"pattern": "agenda", "title": "本日の論点", "subtitle": "論点構成",
         "items": [{"label": T(f"論点{i+1} 市場と競争環境の見立て", f"論点{i+1}"), "desc": T(LONG, SHORT)}
                   for i in range(N(2, 6))]},
        {"pattern": "executive_summary", "title": T("中堅企業向けSaaS参入で5年でARR 68億円を構築", "結論"),
         "subtitle": "Executive Summary",
         "points": [{"kicker": T("市場機会", "市場"), "heading": T("国内SaaS市場は2030年に3.2兆円へ拡大", "拡大"),
                     "body": T("年平均成長率13%、特に従業員300-999名の中堅企業セグメントはSaaS浸透率が24%と低く、今後の成長余地が最大", "余地が最大")}
                    for _ in range(N(2, 4))]},
        {"pattern": "section_divider", "number": 1, "title": T("市場・競争環境の見立て", "市場"),
         "desc": T("国内SaaS市場の規模と主要プレイヤーのポジショニング", "規模と位置")},
        {"pattern": "kpi_dashboard", "title": T("初年度は導入社数とNRRの2指標で検証", "2指標で検証"),
         "subtitle": "FY2027 主要KPIターゲット",
         "kpis": [{"label": T("CAC回収期間(月数)", "NRR"), "value": ["120", "4.3", "112", "14", "1,284", "10,590", "72.4", "2.1"][i],
                   "unit": ["社", "億円", "%", "カ月", "社", "千円", "%", "億円"][i],
                   "delta": T("前年同期比 +18.2pt 改善", "+4.3"), "delta_dir": "up",
                   "note": T("S&M費用 ÷ 新規獲得粗利で算出、上位プラン移行が寄与", "目標"), "focal": i == 0}
                  for i in range(N(2, 8))]},
        {"pattern": "chart_insight", "title": T("国内SaaS市場は年率15%成長で2030年に3.2兆円へ", "3.2兆円へ"),
         "subtitle": T("国内SaaS市場規模の推移と予測(2024-2030年)", "推移"),
         "chart": {"type": "column", "unit": "兆円", "categories": cats,
                   "series": [{"name": "市場規模", "values": vals}], "focal_category": len(cats) - 1,
                   "number_format": "0.0", "annotation": {"badge": "CAGR 15%"}},
         "takeaways": take, "source": "富士キメラ総研「ソフトウェアビジネス新市場2025年版」を基にAct作成",
         "insight": T("市場全体の成長に加え、中堅企業セグメントの浸透率拡大が2026年以降の主要ドライバー", "浸透率拡大が主因")},
        {"pattern": "chart_insight", "layout": "chart_top",
         "title": T("構成比は経理から人事・法務へ、3年で逆転", "構成比が逆転"),
         "subtitle": "モジュール別ARR構成比の推移",
         "chart": {"type": "stacked_column_100", "unit": "%", "categories": cats[: max(3, len(cats) - 2)],
                   "series": [{"name": "経理", "values": [70, 60, 50, 40, 35, 30][: max(3, len(cats) - 2)]},
                              {"name": "人事", "values": [20, 25, 30, 35, 35, 35][: max(3, len(cats) - 2)]},
                              {"name": "法務", "values": [10, 15, 20, 25, 30, 35][: max(3, len(cats) - 2)]}],
                   "segment_labels": True, "number_format": "0"},
         "takeaways": take, "source": "Act事業計画モデル v2.1"},
        {"pattern": "market_sizing", "title": T("獲得可能市場は1,800億円、経理領域が420億円", "SOM 420億円"),
         "subtitle": "段階的推計(2030年時点)",
         "stages": [{"label": lb, "value": val, "numeric": num, "name": T(LONG, nm), "desc": T(LONG, "内訳")}
                    for lb, val, num, nm in [("TAM", "3.2兆円", 32000, "全体"), ("SAM", "1,800億円", 1800, "中堅"),
                                            ("SOM", "420億円", 420, "経理")][: N(2, 3)]],
         "source": "富士キメラ総研データを基にAct推計"},
        {"pattern": "comparison_table", "title": T("新興2社との比較で機能カバレッジの優位を確保", "優位を確保"),
         "subtitle": "機能・価格・サポート体制の比較",
         "table": {"headers": ["評価軸", "当社(構想)", "freee", "マネーフォワード"][: N(3, 4)],
                   "col_widths": [0.28, 0.24, 0.24, 0.24][: N(3, 4)], "align": ["l", "c", "c", "c"][: N(3, 4)],
                   "emphasis_col": 1,
                   "rows": [[T(LONG[:18], "経理"), T("◎(3年目に標準対応へ引き上げ)", "◎"), "○", "△"][: N(3, 4)]
                            for _ in range(N(3, 8))]},
         "source": "各社公開料金・機能一覧(2026年6月時点)を基にAct作成"},
        {"pattern": "competitive_landscape", "title": T("中堅×統合型の象限は空白、先行者利益を取れる", "象限は空白"),
         "subtitle": "主要プレイヤーのポジショニング(2026年時点)",
         "x_axis": {"low": T("単機能特化", "単機能"), "high": T("統合スイート", "統合")},
         "y_axis": {"low": "小規模企業", "high": "大企業"},
         "players": [{"name": nm, "x": xx, "y": yy, "focal": nm == "当社"}
                     for nm, xx, yy in [("SAP", 0.85, 0.9), ("Oracle", 0.82, 0.86), ("OBIC", 0.7, 0.72),
                                        ("freee", 0.45, 0.2), ("マネーフォワード", 0.5, 0.32), ("ラクス", 0.2, 0.28),
                                        ("当社", 0.72, 0.5), ("ジョブカン", 0.3, 0.4), ("弥生", 0.15, 0.15),
                                        ("PCA", 0.35, 0.55)][: N(3, 10)]],
         "notes": take, "source": "各社IR資料・公開情報を基にAct作成"},
        {"pattern": "financial_summary", "title": T("売上は5年で17倍、FY2031に単年黒字化", "17倍"),
         "subtitle": "5カ年財務サマリー",
         "table": {"headers": ["(億円)", "FY27", "FY28", "FY29", "FY30", "FY31"], "col_widths": [0.28, 0.18, 0.18, 0.18, 0.18, 0.18],
                   "align": ["l", "r", "r", "r", "r", "r"], "emphasis_row": 3, "color_negatives": True,
                   "rows": [["ARR", "4.3", "12.0", "28.0", "46.0", "68.0"], ["売上高", "3.5", "9.8", "23.0", "39.0", "60.0"],
                            ["売上総利益", "2.5", "7.4", "18.4", "32.0", "50.4"], ["営業利益", "△18.0", "△22.0", "△15.0", "△6.0", "3.2"],
                            ["FCF", "△19.5", "△24.0", "△17.5", "△8.0", "1.0"]][: N(3, 5)]},
         "chart": {"type": "column", "unit": "億円", "categories": ["FY27", "FY28", "FY29", "FY30", "FY31"],
                   "series": [{"name": "売上高", "values": [3.5, 9.8, 23.0, 39.0, 60.0]}], "focal_category": 4,
                   "number_format": "0.0"},
         "source": "Act事業計画モデル v2.1"},
        {"pattern": "waterfall", "title": T("FY2031のARR 68億円は新規獲得とクロスセルで実現", "ARR 68億円"),
         "subtitle": "ARRブリッジ(FY2027実績 → FY2031計画)", "unit": "億円",
         "items": [{"label": "FY27\nARR", "value": 4.3, "kind": "start"},
                   *[{"label": T(f"新規顧客\n(経理領域{i})", f"項目{i}"), "value": [22.0, 18.5, 16.8, 9.2, -2.8, 3.1, -1.1][i]}
                     for i in range(N(2, 7))],
                   {"label": "FY31\nARR", "value": 4.3 + sum([22.0, 18.5, 16.8, 9.2, -2.8, 3.1, -1.1][: N(2, 7)]), "kind": "end", "forecast": True}],
         "source": "Act事業計画モデル v2.1"},
        {"pattern": "roadmap", "title": T("経理で足場を築きFY31に統合スイートへ拡張", "拡張"),
         "subtitle": "参入ロードマップ(FY2027-FY2031)",
         "phases": [{"label": T(f"Phase {i+1}: 参入と足場づくり", f"P{i+1}"), "period": f"FY{27+i}-{28+i}"} for i in range(N(2, 4))],
         "focal_phase": 0,
         "rows": [{"label": T("プロダクト", "PD"), "cells": [T(CELL, SHORT)] * N(2, 4)} for _ in range(N(1, 4))],
         "source": "Act事業計画モデル v2.1"},
        {"pattern": "two_column", "title": T("速度と機能完成度の両面でM&A活用が優位", "M&Aが優位"),
         "subtitle": "人事・法務モジュール獲得手段の比較",
         "left": {"heading": "Option A: 自社開発", "items": [{"heading": T("投資規模: 25億円 / 24カ月", "投資"), "body": T(PILLAR_BODY, SHORT)} for _ in range(N(1, N_TWO))]},
         "right": {"heading": "Option B: M&A活用(推奨)", "focal": True,
                   "items": [{"heading": T("投資規模: 40億円 / 9カ月", "投資"), "body": T(PILLAR_BODY, SHORT)} for _ in range(N(1, N_TWO))]},
         "assumption": "Act事業計画モデルに基づく試算"},
        {"pattern": "process_flow", "title": T("参入判断後は90日でローンチ準備を完了させる", "90日で準備"),
         "subtitle": "ローンチまでの実行ステップ",
         "steps": [{"label": T(f"Step {i+1}: 体制構築とパートナー選定", f"S{i+1}"),
                    "items": [T(BULLET, SHORT)] * N(1, 3), "outcome": T("初月20社の導入", "20社") if v != "min" else None}
                   for i in range(N(2, 5))],
         "assumption": "Act事業計画モデルに基づく試算"},
        {"pattern": "column_framework", "title": T("3本の柱で中堅企業の業務複雑性に応える", "3本の柱"),
         "subtitle": "参入後の提供価値フレームワーク",
         "columns": [{"label": f"0{i+1}", "heading": T("統合データモデルによる部門横断の一元化", "統合"), "focal": i == 1,
                      "items": [{"heading": T("投資規模: 25億円 / 24カ月", "投資"), "body": T(PILLAR_BODY, SHORT)}
                                for _ in range(N(1, 3 if overload else 2))],     # 4本柱+結論帯の現実的な上限は2項目
                      "outcome": T("導入120社 / NRR 112%", "120社") if v != "min" else None}
                     for i in range(N(2, 4))],
         "assumption": "Act事業計画モデルに基づく試算"},
        {"pattern": "metric_proof", "title": T("ARRは5四半期で30%増、12.8億円に到達", "ARR 12.8億円"),
         "subtitle": "ARR推移(四半期末、億円)",
         "hero": {"label": "ARR", "value": "12.8", "unit": "億円", "delta": "+30% YoY", "delta_dir": "up",
                  "note": T("直近5四半期の累計純増 2.95億円、QoQ +0.85億円", "QoQ +0.85")},
         "chart": {"type": "column", "unit": "億円", "categories": ["Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26"],
                   "series": [{"name": "ARR", "values": [9.85, 10.52, 11.28, 11.95, 12.80]}], "focal_category": 4,
                   "number_format": "0.00"},
         "facts": [{"label": T("有料顧客数(社)", "顧客"), "value": "8,420"}, {"label": "ARPA", "value": "152万円"},
                   {"label": "NRR", "value": "114%"}, {"label": "解約率", "value": "3.2%"}][: N(0, 4)],
         "source": "決算短信(2026年4月開示)"},
        {"pattern": "logic_tree", "title": T("ARR成長は顧客数×単価×継続率の3本に分解", "3本に分解"),
         "subtitle": "ARRドライバーツリー(FY2026 Q2)",
         "root": {"label": "ARR", "value": "12.8", "unit": "億円"},
         "branches": [{"label": T("有料顧客数の純増(エンタープライズ移行)" if overload else "有料顧客数の純増", "顧客数"),
                       "value": "8,420", "unit": "社", "focal": i == 0,
                       "leaves": [{"label": T("従業員1,000名超の新規42社(累計380社)", "新規42社"), "value": "42"}
                                  for _ in range(N(0, [3, 3, 2, 0][i]))]}
                      for i in range(N(2, 4 if overload else 3))],   # 行数 8 が上限(3+3+2)
         "assumption": "社内管理数値(月次KPIレポート 2026年4月版)"},
        {"pattern": "financial_highlights", "title": T("上期売上64.8億円(+28%)で計画超過", "計画超過"),
         "subtitle": "FY2026 上期ハイライト",
         "groups": [{"label": T("業績", "業績"), "claim": T("増収と黒字幅拡大が両立、投資回収が前倒し" if overload else "増収と黒字拡大が両立", "両立"),
                     "metrics": [{"label": "売上高", "value": "64.8", "unit": "億円", "delta": "+28% YoY", "delta_dir": "up"},
                                 *[{"label": T("調整後営業利益", "利益"), "value": "2.1", "unit": "億円", "delta": T("+1.8億円 YoY", "+1.8"), "delta_dir": "up"}] * N(0, 3 if overload else 1)],
                     "note": T("NRR は過去12カ月の既存顧客収益の増減率", "注") if v != "min" else None}
                    for _ in range(N(1, 3))],
         "source": "決算短信(2026年4月開示)"},
        {"pattern": "metrics_rows", "title": T("Q2単体でも全指標プラス成長、改善する成長の質", "全指標プラス"),
         "subtitle": "FY2026 Q2 会計期間サマリ",
         "columns": [{"heading": T("FY2026 Q2(2025年12月-2026年2月)", "Q2"),
                      "rows": [{"label": T("調整後EBITDA", "売上"), "value": "33.6", "unit": "億円", "delta": T("+31.2% YoY", "+31%"), "delta_dir": "up", "emphasis": r == 0}
                               for r in range(N(2, 5))]} for _ in range(N(1, 2))],
         "source": "決算短信(2026年4月開示)"},
        {"pattern": "guidance_progress", "title": T("上期進捗率48%で通期レンジ達成は射程圏内", "進捗率48%"),
         "subtitle": "通期ガイダンス進捗(売上高)", "unit": "億円",
         "bars": [{"label": "FY2024", "value": 78.2, "display": "78.2"}, {"label": "FY2025", "value": 104.5, "display": "104.5"}][: N(0, 2)],
         "current": {"label": "FY2026", "actual": 64.8, "actual_display": "上期実績 64.8", "guidance_low": 132, "guidance_high": 136,
                     "range_display": "132 - 136(予想)", "progress_display": "48%"},
         "side_heading": "上期進捗",
         "side": [{"label": T("過去2年平均の同時期進捗", "進捗率"), "value": "45%"}] * N(1, 4),
         "source": "決算短信(2026年4月開示)"},
        {"pattern": "driver_decomposition", "title": T("顧客数と単価の両輪でARR 136億円ペースに到達", "両輪"),
         "subtitle": "ARR ドライバー分解(2026年2月末時点)",
         "factors": [{"label": T("顧客単価(ARPA)", "単価"), "value": "10,590", "unit": "千円", "delta": T("+7.2% YoY", "+7%"),
                      "note": T("上位プランへの移行が寄与、エンタープライズ比率31%", "寄与")} for _ in range(N(2, 5))],
         "assumption": "社内管理数値(月次KPIレポート 2026年4月版)"},
        {"pattern": "chart_grid", "title": T("3指標とも5四半期連続で伸長、CAGRは20%超", "CAGR 20%超"),
         "subtitle": "主要KPIの推移(小さな多重図)",
         "charts": [{"title": T("ARR(億円)", "ARR"),
                     "chart": {"type": "column", "unit": "億円", "categories": ["Q2/25", "Q3/25", "Q4/25", "Q1/26", "Q2/26"],
                               "series": [{"name": "ARR", "values": [9.85, 10.52, 11.28, 11.95, 12.80]}], "focal_category": 4,
                               "number_format": "0.0", "annotation": {"badge": "+30%"}}} for _ in range(N(2, 4))],
         "source": "決算短信(2026年4月開示)"},
        {"pattern": "statement", "title": "結論", "subtitle": "参入提言と5年後の到達点",
         "lead": T("今後3年が参入の最終ウィンドウ、経理から段階参入", "段階参入を提言"),
         "statement": T("経理領域からの段階参入とM&A活用で、5年でARR 68億円の事業構築を提言する", "5年でARR 68億円"),
         "variant": "evidence_strip" if v != "min" else "center_hero",
         "recap": [{"label": T("FY2031 ARR", "ARR"), "value": "68", "unit": "億円", "focal": True, "note": T("新規獲得とクロスセルの積み上げ", "積み上げ")}] * N(1, 4),
         "attribution": "Act Strategy Team, 2026年9月"},
    ]
    if images:
        slides.insert(-1, {"pattern": "diagram", "title": T("5つの工程が循環して顧客価値を積み上げる", "循環"),
                           "subtitle": "オペレーション・フライホイール",
                           "diagram": {"kind": "ring", "segments": [{"label": T(f"工程{i+1} 計測", f"工程{i+1}"), "value": 1} for i in range(N(3, 5))], "center": "顧客価値"},
                           "takeaways": take, "assumption": "Act分析モデル v1"})
        slides.insert(-1, {"pattern": "chart_insight", "title": T("売上と粗利率は同時に改善、FY26は78%へ", "粗利率78%"),
                           "subtitle": "売上高と売上総利益率の推移",
                           "chart": {"kind": "combo", "categories": cats,
                                     "bar": {"name": "売上高", "values": [v_ * 10 for v_ in vals], "unit": "億円"},
                                     "line": {"name": "粗利率", "values": [70 + i for i in range(len(cats))], "unit": "%"}},
                           "takeaways": take, "source": "決算短信(2026年4月開示)"})
    # drop None outcome keys so validate sees the real spec shape
    def _clean(o):
        if isinstance(o, dict):
            return {k: _clean(x) for k, x in o.items() if x is not None}
        if isinstance(o, list):
            return [_clean(x) for x in o]
        return o
    meta = {"title": "Stress deck", "thesis": {"statement": "5年でARR 68億円", "value": "68", "unit": "億円"}}
    if template:
        meta["template"] = template
    return _clean({"meta": meta, "slides": slides})


HARD = ("out of slide bounds",)   # どの変種でも許されない欠陥: 枠がスライドの外に出る。
# (overload では文字が器から溢れて縁をまたぐ — それは verify が名指しすべき溢れであって、契約違反ではない)


def run_variant(outdir: Path, variant: str, template: str | None, images: bool,
                lint: bool = False) -> dict:
    """Write, validate, build and audit one variant.

    Returns {"validate_errors", "verify_failures", "hard_failures", "messages"}. `hard_failures`
    counts the one defect no variant may produce — a frame outside the slide (HARD). Text
    straddling a shape edge under `overload` is copy overflow that verify names, not a contract
    violation, so it is reported in `verify_failures` but does not gate the exit code; `verify_failures` is the full count and must be 0 for max / min."""
    import build_deck
    import verify_deck
    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"stress-{variant}" + (f"-{template}" if template else "")
    spec = outdir / f"{tag}.json"
    spec.write_text(json.dumps(make_deck(variant, template, images), ensure_ascii=False, indent=1))
    r = subprocess.run([sys.executable, str(HERE / "validate_spec.py"), str(spec)], capture_output=True, text=True)
    v_err = [ln for ln in r.stdout.splitlines() if ln.startswith("ERROR")]
    pptx = outdir / f"{tag}.pptx"
    build_deck.build(spec, pptx)
    issues, _warns, _n = verify_deck.audit(pptx)
    hard = [i for i in issues if any(k in i for k in HARD)]
    lint_findings = None
    if lint and variant == "max":
        # 描画後の占有率ゲート(lint_render)も回す — verify が通っても本文帯が空くと lint が落ちる
        # (evals.json の主張をここで実際に検証する。Codex レビュー指摘、PR #158)
        rdir = outdir / f"{tag}-render"
        subprocess.run(["sh", str(HERE / "render_deck.sh"), str(pptx), str(rdir)],
                       capture_output=True, text=True, check=True)
        lr = subprocess.run([sys.executable, str(HERE / "lint_render.py"), str(rdir), "--spec", str(spec)],
                            capture_output=True, text=True)
        lint_findings = [ln for ln in lr.stdout.splitlines() if ln.startswith(("FAIL", "WARN"))]
    return {"validate_errors": len(v_err), "verify_failures": len(issues), "hard_failures": len(hard),
            "lint_findings": lint_findings, "messages": v_err + issues + (lint_findings or []),
            "pptx": pptx, "spec": spec}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", type=Path, default=Path("stress"))
    ap.add_argument("--variant", choices=[*VARIANTS, "all"], default="all")
    ap.add_argument("--template", default=None)
    ap.add_argument("--images", action="store_true")
    ap.add_argument("--lint", action="store_true", help="render the max variant and run lint_render (needs LibreOffice)")
    args = ap.parse_args()
    bad = 0
    for variant in (VARIANTS if args.variant == "all" else [args.variant]):
        res = run_variant(args.out, variant, args.template, args.images, args.lint)
        for m in res["messages"]:
            print(f"  {m}")
        lint_note = "" if res["lint_findings"] is None else f" / lint findings {len(res['lint_findings'])}"
        print(f"{variant:8} template={args.template or 'standard':11} validate errors {res['validate_errors']}"
              f" / verify failures {res['verify_failures']} (hard {res['hard_failures']}){lint_note}")
        # overload は溢れて当然。契約は「枠が外に出ない」だけ。max / min は validate・verify(・lint)が 0
        bad += res["hard_failures"] if variant == "overload" else res["validate_errors"] + res["verify_failures"]
        bad += len(res["lint_findings"] or [])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
