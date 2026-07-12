#!/usr/bin/env python3
"""IB流スタートアップ収支計画ジェネレーター。

YAML入力から7シート（サマリー/前提条件/売上計画/人員計画/費用計画/損益計画/
資金繰り）の年次収支計画xlsxを生成する。書式契約は references/ib_format_spec.md、
シート構成は references/sheet_architecture.md に従う。

使い方:
    python3 build_workbook.py --input plan.yaml --output plan.xlsx
"""
from __future__ import annotations

import argparse
import os
import re
import shutil

import yaml
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.pagebreak import Break
from openpyxl.worksheet.properties import PageSetupProperties

FONT = "Arial"
SIZE = 10
BLUE = "FF0000FF"
BLACK = "FF000000"
GREEN = "FF008000"
GRAY = "FF808080"
WHITE = "FFFFFFFF"
NAVY = "FF1F3864"
RED = "FFFF0000"

FMT_M = '#,##0,,_);(#,##0,,);"-"_)'      # 百万円表示（値は生円）
FMT_YEN = '#,##0_);(#,##0);"-"_)'        # 円表示
FMT_PCT = "0.0%_);(0.0%)"
FMT_CNT = '#,##0_);(#,##0);"-"_)'
FMT_D1 = '#,##0.0_);(#,##0.0);"-"_)'
FMT_X = '0.0"x"_);(0.0"x");"-"_)'

THIN = Side(style="thin", color="FF000000")
DOUBLE = Side(style="double", color="FF000000")

PURE_LINK = re.compile(r"^='[^'!]+'!\$?[A-Z]{1,3}\$?\d+$")

UNITS_NOTE = ("単位：百万円（単価・給与・件数・人数は行ラベルに明記）。"
              "費用は正表示し、利益行で控除。青字＝入力、黒字＝計算、緑字＝他シート直接参照（単一リンク）。")


def font(color=BLACK, bold=False, italic=False):
    return Font(name=FONT, size=SIZE, color=color, bold=bold, italic=italic)


def b2b_indices(cfg):
    return [i for i, s in enumerate(cfg["segments"])
            if "cogs_pct_of_revenue" not in s]


def toc_indices(cfg):
    return [i for i, s in enumerate(cfg["segments"])
            if "cogs_pct_of_revenue" in s]


def alloc_map(cfg):
    m = {}
    for i, hc in enumerate(cfg["headcount"]):
        m.setdefault(hc["allocation"], []).append(i)
    return m


def col_of(t):
    """期間インデックスt（0起点）の列文字。E列起点（B/C/Dはラベル・インデント列）。"""
    return get_column_letter(5 + t)


class Registry:
    def __init__(self):
        self.rows: dict[str, tuple[str, int]] = {}
        self.cells: dict[str, tuple[str, str]] = {}
        self.checks: list[dict] = []   # 整合性チェック行（サマリーで集計）

    def row(self, name, sheet, r):
        self.rows[name] = (sheet, r)

    def cell(self, name, sheet, addr):
        self.cells[name] = (sheet, addr)


class Sheet:
    """1シート分のライター。A列スペーサー、B列起点、期間列C..、末尾に備考列。"""

    HEADER_ROW = 5

    def __init__(self, wb, reg, name, cfg, header_labels=None, extra_cols=()):
        self.ws = wb.create_sheet(name)
        self.reg = reg
        self.title = name
        labels = header_labels or [f"FY{cfg['start_year'] + i}"
                                   for i in range(cfg["periods"])]
        self.p = len(labels)
        self.extra_cols = tuple(extra_cols)
        self.first_col = 5
        self.last_col = 4 + self.p
        self.note_col = 5 + self.p + len(self.extra_cols)
        self.r = 1
        self._title_band(f"{cfg['company']}｜{cfg['model_title']}｜{name}")
        self._period_header(labels)
        self._layout()

    def _title_band(self, title_text):
        # 1行目は空け、2行目から開始する
        ws = self.ws
        for c in range(2, self.note_col + 1):
            ws.cell(row=2, column=c).fill = PatternFill("solid", fgColor=NAVY)
        ws.cell(row=2, column=2, value=title_text).font = font(WHITE, bold=True)
        ws.cell(row=3, column=2, value=UNITS_NOTE).font = font(GRAY, italic=True)

    def _period_header(self, labels):
        ws = self.ws
        for i, label in enumerate(labels):
            c = ws.cell(row=self.HEADER_ROW, column=self.first_col + i, value=label)
            c.font = font(bold=True)
            c.alignment = Alignment(horizontal="right")
            c.border = Border(bottom=THIN)
        for c in range(2, self.first_col):
            ws.cell(row=self.HEADER_ROW, column=c).border = Border(bottom=THIN)
        for j, label in enumerate(self.extra_cols):
            c = ws.cell(row=self.HEADER_ROW,
                        column=self.last_col + 1 + j, value=label)
            c.font = font(bold=True)
            c.alignment = Alignment(horizontal="right")
            c.border = Border(bottom=THIN)
        nc = ws.cell(row=self.HEADER_ROW, column=self.note_col, value="備考")
        nc.font = font(GRAY, italic=True)
        nc.border = Border(bottom=THIN)
        self.r = self.HEADER_ROW + 1

    def _layout(self):
        ws = self.ws
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 2
        ws.column_dimensions["B"].width = 2.14   # インデント列（Google Sheets 20px相当）
        ws.column_dimensions["C"].width = 2.14   # インデント列
        ws.column_dimensions["D"].width = 34     # ラベル本体列
        for c in range(self.first_col, self.last_col + 1):
            ws.column_dimensions[get_column_letter(c)].width = 11.5
        extra_widths = (24, 12)
        for j in range(len(self.extra_cols)):
            ws.column_dimensions[
                get_column_letter(self.last_col + 1 + j)].width = (
                extra_widths[j] if j < len(extra_widths) else 14)
        ws.column_dimensions[get_column_letter(self.note_col)].width = 44
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)

    # --- 参照 ---------------------------------------------------------
    def ref(self, name, col="C"):
        sheet, row = self.reg.rows[name]
        if sheet == self.title:
            return f"{col}{row}"
        return f"'{sheet}'!{col}{row}"

    def sref(self, name):
        sheet, addr = self.reg.cells[name]
        if sheet == self.title:
            return addr
        return f"'{sheet}'!{addr}"

    # --- 行の書き込み --------------------------------------------------
    def blank(self):
        self.r += 1

    def section(self, label, note=None):
        self.blank()
        ws = self.ws
        ws.cell(row=self.r, column=2, value=label).font = font(bold=True)
        for c in range(2, self.note_col + 1):
            ws.cell(row=self.r, column=c).border = Border(bottom=THIN)
        if note:
            ws.cell(row=self.r, column=self.note_col, value=note).font = font(
                GRAY, italic=True)
        self.r += 1

    def _write_cell(self, row, t, content, fmt, bold, italic, is_input):
        cell = self.ws.cell(row=row, column=5 + t)
        cell.value = content
        if is_input:
            color = BLUE
        elif isinstance(content, str) and content.startswith("="):
            color = GREEN if PURE_LINK.match(content) else BLACK
        else:
            color = BLACK
        cell.font = font(color, bold=bold, italic=italic)
        cell.number_format = fmt
        cell.alignment = Alignment(horizontal="right")
        return cell

    def row(self, label, fmt, values=None, formula=None, name=None, indent=1,
            note=None, bold=False, italic=False, total=False, grand=False,
            skip_first=False, bench=None, evaluation=None):
        """1行を書く。values=入力(青) / formula(col,t)->数式(黒/緑自動)。
        formulaがNoneを返した期間は空欄。bench/evaluationは追加列に書く。"""
        ws = self.ws
        lab = ws.cell(row=self.r, column=2 + indent, value=label)
        lab.font = font(bold=bold)
        border = Border(top=THIN, bottom=DOUBLE) if grand else (
            Border(top=THIN) if total else None)
        for t in range(self.p):
            content = None
            if skip_first and t == 0:
                cell = self.ws.cell(row=self.r, column=5 + t)
                cell.number_format = fmt
            elif values is not None:
                v = values[t] if t < len(values) else values[-1]
                cell = self._write_cell(self.r, t, v, fmt, bold, italic, True)
            else:
                content = formula(col_of(t), t)
                if content is None:
                    cell = self.ws.cell(row=self.r, column=5 + t)
                    cell.number_format = fmt
                else:
                    cell = self._write_cell(self.r, t, content, fmt,
                                            bold, italic, False)
            if border:
                cell.border = border
        if bench is not None:
            bc = ws.cell(row=self.r, column=self.last_col + 1, value=bench)
            bc.font = font(GRAY, italic=True)
            bc.alignment = Alignment(horizontal="right")
        if evaluation is not None:
            ec = ws.cell(row=self.r, column=self.last_col + 2,
                         value=evaluation)
            ec.font = font()
            ec.alignment = Alignment(horizontal="right")
        if border:
            for c in range(2, self.first_col):
                ws.cell(row=self.r, column=c).border = border
            for c in range(self.last_col + 1, self.note_col + 1):
                ws.cell(row=self.r, column=c).border = border
        if note:
            ws.cell(row=self.r, column=self.note_col, value=note).font = font(
                GRAY, italic=True)
        if name:
            self.reg.row(name, self.title, self.r)
        self.r += 1
        return self.r - 1

    def patch(self, name, formula):
        """登録済み行の数式を後決めで差し替える（前方参照の解決用）。"""
        _, row = self.reg.rows[name]
        for t in range(self.p):
            f = formula(col_of(t), t)
            if f is None:
                continue
            cell = self.ws.cell(row=row, column=5 + t)
            keep = cell.font
            cell.value = f
            color = GREEN if PURE_LINK.match(f) else BLACK
            cell.font = font(color, bold=keep.bold, italic=keep.italic)

    def scalar(self, label, value, fmt, name=None, indent=1, note=None,
               italic=False):
        """全期間共通の入力。全期間列に同値を複製し、参照は同列参照を基本とする。
        期間整合しないシートからは先頭期間列への絶対参照（sref）を使う。"""
        merged = "全期間共通" + ("。" + note if note else "")
        r = self.row(label, fmt, values=[value] * self.p, name=name,
                     indent=indent, note=merged, italic=italic)
        if name:
            col = get_column_letter(self.first_col)
            self.reg.cell(name, self.title, f"${col}${r}")
        return r

    def check(self, label, formula, fmt=FMT_CNT, note=None, tolerance=0.5):
        tol_note = f"許容誤差±{tolerance}（表示スケールに対して実質ゼロ）"
        note = f"{note}。{tol_note}" if note else tol_note
        row = self.row(label, fmt, formula=formula, note=note, italic=True)
        self.reg.checks.append({
            "label": label, "sheet": self.title, "row": row,
            "c0": col_of(0), "c1": col_of(self.p - 1), "tol": tolerance})
        rng = f"{col_of(0)}{row}:{col_of(self.p - 1)}{row}"
        red = Font(name=FONT, size=SIZE, color=RED, bold=True)
        self.ws.conditional_formatting.add(rng, CellIsRule(
            operator="greaterThan", formula=[str(tolerance)], font=red))
        self.ws.conditional_formatting.add(rng, CellIsRule(
            operator="lessThan", formula=[str(-tolerance)], font=red))
        return row


KPI_TH = [
    # (key, label, default, fmt, note)
    ("growth_good", "ARR成長率：良好", 0.40, "pct", "SaaS Capital: $1-5M ARR帯の中央値40%"),
    ("growth_ok", "ARR成長率：水準内", 0.25, "pct", "全体中央値25%"),
    ("gm_good", "売上総利益率：良好", 0.70, "pct", "KeyBanc: サービス込み総GM中央値71-75%"),
    ("gm_ok", "売上総利益率：水準内", 0.60, "pct", "AI-native帯50-65%を考慮"),
    ("ebitda_good", "EBITDAマージン：良好", 0.15, "pct", "成熟期15-25%（Founderpath）"),
    ("ebitda_ok", "EBITDAマージン：水準内", 0.00, "pct", "黒字転換"),
    ("r40_good", "Rule of 40：良好", 0.40, "pct", "Wall Street Prep"),
    ("r40_ok", "Rule of 40：水準内", 0.20, "pct", None),
    ("svc_good", "サービス売上比率：良好", 0.10, "pct", "SaaStr: 10-15%未満・低下傾向"),
    ("svc_max", "サービス売上比率：上限", 0.20, "pct", "Dave Kellogg: 20%上限"),
    ("magic_good", "Magic Number：良好", 1.00, "x", "Scale VP: >1.0 excellent"),
    ("magic_ok", "Magic Number：水準内", 0.75, "x", "Scale VP: >0.75で投資拡大に値する"),
    ("rpe_good", "一人当たり売上：良好", 20000000, "m", "SaaS Capital中央値$130K≒2,000万円"),
    ("rpe_ok", "一人当たり売上：水準内", 12000000, "m", "初期ステージ$94K≒1,400万円弱"),
    ("sm_low", "S&M比率：下限", 0.30, "pct", "過小は成長率と不整合（要説明）"),
    ("sm_high", "S&M比率：上限", 0.50, "pct", "SaaS Capital中央値37%、$100M時点48%"),
    ("rd_low", "R&D比率：下限", 0.15, "pct", None),
    ("rd_high", "R&D比率：上限", 0.40, "pct", "私企業中央値34%、AI企業は重め"),
    ("ga_low", "G&A比率：下限", 0.06, "pct", None),
    ("ga_high", "G&A比率：上限", 0.25, "pct", "中央値24%→規模拡大で10%台"),
    ("burn_good", "Burn Multiple：良好", 1.5, "x", "Sacks: 1.5x以下=great"),
    ("burn_ok", "Burn Multiple：水準内", 2.0, "x", "2x超は現環境で調達困難"),
    ("runway_good", "ランウェイ：良好（月）", 18, "cnt", "調達直後18-24ヶ月"),
    ("runway_ok", "ランウェイ：水準内（月）", 12, "cnt", None),
    ("band_tol", "費目比率帯の水準内許容幅", 0.05, "pct", "帯±この幅までを水準内と判定"),
]


# ----------------------------------------------------------------------
def build_assumptions(wb, reg, cfg):
    s = Sheet(wb, reg, "前提条件", cfg)
    src = cfg.get("source_note", "")

    for i, seg in enumerate(cfg["segments"]):
        is_b2b = "cogs_pct_of_revenue" not in seg
        s.section(f"セグメント：{seg['name']}", note=seg.get("note"))
        s.row(f"期末稼働数（{seg['unit_label']}）", FMT_CNT,
              values=seg["ending_customers"], name=f"a_end{i}",
              note=seg.get("ramp_note", "最終年はソース記載値、中間年は逆算設計"))
        s.scalar("解約率（年）", seg["churn_rate"], FMT_PCT, name=f"a_churn{i}", italic=True,
                 note="記載なし・仮置き" if seg["churn_rate"] else "解約織り込みなし")
        s.scalar("月額固定利用料（円/月）", seg["fixed_fee_monthly"], FMT_YEN,
                 name=f"a_fix{i}",
                 note="ソース記載" if is_b2b else "ソース記載の月額（純額）")
        if is_b2b:
            s.scalar("月額従量利用料（円/月）", seg["usage_fee_monthly"],
                     FMT_YEN, name=f"a_ufee{i}", note="ソース記載")
            s.scalar("従量単価（円/分）", seg["usage_rate_per_min"], FMT_YEN,
                     name=f"a_rate{i}",
                     note="ソース記載。稼働分数＝従量料÷単価")
            s.scalar("導入費（円/件）", seg["implementation_fee"], FMT_YEN,
                     name=f"a_impl{i}", note="ソース記載")
            s.row("従量原価（円/分）", FMT_YEN, values=seg["cost_per_min"],
                  name=f"a_cpm{i}",
                  note="フェーズ別原価低減（ソース記載）の年次展開")
        else:
            s.row("原価率（対売上）", FMT_PCT,
                  values=seg["cogs_pct_of_revenue"], name=f"a_cogspct{i}",
                  italic=True, note="推論・配信原価率。仮置き")

    s.section("導入原価")
    s.row("導入原価率（対導入売上）", FMT_PCT,
          values=cfg["implementation_cost_pct"], name="a_implcost", italic=True,
          note="導入時の外部費・稼働原価。仮置き")

    s.section("人員・人件費", note="記載なし・仮置き")
    for i, hc in enumerate(cfg["headcount"]):
        s.row(f"{hc['function']}（人・期末）", FMT_CNT, values=hc["fte"],
              name=f"a_fte{i}")
        s.scalar("平均年収（円）", hc["avg_salary"], FMT_YEN, name=f"a_sal{i}",
                 indent=2)
    s.scalar("法定福利・諸手当率", cfg["payroll_burden_rate"], FMT_PCT,
             name="a_burden", italic=True)
    s.scalar("採用単価（円/人）", cfg["recruiting_cost_per_hire"], FMT_YEN,
             name="a_recruit")

    op = cfg["opex"]
    s.section("営業費用ドライバー", note="記載なし・仮置き")
    s.row("広告宣伝・販促（対売上）", FMT_PCT, values=op["sm_pct_of_revenue"],
          name="a_smpct", italic=True)
    s.row("モデル開発・GPU・データ", FMT_M, values=op["rd_program_yen"],
          name="a_rdprog", note=op.get("rd_note", "研究開発プログラム投資"))
    s.scalar("オフィス・情報システム（円/人/年）", op["office_cost_per_fte"],
             FMT_YEN, name="a_office")
    s.scalar("士業・保険・その他管理（対売上）", op["ga_pct_of_revenue"], FMT_PCT,
             name="a_gapct", italic=True)

    s.section("投資・税・運転資本", note="記載なし・仮置き")
    s.row("設備投資（開発設備・GPU）", FMT_M, values=cfg["capex_yen"],
          name="a_capex")
    s.scalar("償却年数（年・定額法）", cfg["depreciation_years"], FMT_CNT,
             name="a_depyears")
    s.scalar("実効税率", cfg["tax_rate"], FMT_PCT, name="a_tax",
             italic=True, note="繰越欠損金を考慮")
    s.scalar("売掛回収サイト（日）", cfg["ar_days"], FMT_CNT, name="a_ar")
    s.scalar("買掛支払サイト（日）", cfg["ap_days"], FMT_CNT, name="a_ap")
    s.scalar("年間前払比率（リカーリング）", cfg.get("prepay_share", 0.0),
             FMT_PCT, name="a_prepay", italic=True,
             note="年間契約の前受金。残高＝リカーリング×比率×平均残存月数/12の簡便法。仮置き")
    s.scalar("前受平均残存月数", cfg.get("prepay_residual_months", 6),
             FMT_CNT, name="a_prepay_m", note="年間前払の期央평均。仮置き")

    s.section("期初残高（事業開始時点）", note="仮置き")
    s.scalar("期初稼働数（全セグメント）", 0, FMT_CNT, name="a_start0",
             note="事業開始時点の稼働ゼロ")
    s.scalar("期初繰越欠損金", 0, FMT_M, name="a_nol0",
             note="設立初年度から本計画を開始する前提")

    fin = cfg["financing"]
    s.section("資金調達", note="記載なし・仮置き")
    s.scalar("期初現金", fin["beginning_cash"], FMT_M, name="a_cash0")
    raise_series = [0] * cfg["periods"]
    labels = []
    for rd in fin["rounds"]:
        raise_series[rd["year_index"]] += rd["amount"]
        labels.append(f"{rd['label']}（FY{cfg['start_year'] + rd['year_index']}）")
    s.row("エクイティ調達額", FMT_M, values=raise_series, name="a_raise",
          note="・".join(labels))

    sc = cfg.get("story_checks", {})
    if sc:
        s.section("ソース記載値（照合用）", note=src)
        if "y5_recurring_revenue" in sc:
            s.scalar("最終年Recurring収益", sc["y5_recurring_revenue"], FMT_M,
                     name="a_ck_rec", note="ソース記載値（照合用）")
        if "y5_implementation_revenue" in sc:
            s.scalar("最終年導入費収益", sc["y5_implementation_revenue"],
                     FMT_M, name="a_ck_impl", note="ソース記載値（照合用）")
        if "y5_total_som" in sc:
            s.scalar("最終年売上合計（SOM）", sc["y5_total_som"], FMT_M,
                     name="a_ck_som", note="ソース記載値（照合用）")
        if "y5_b2b_units" in sc:
            s.scalar("最終年B2B稼働導入単位", sc["y5_b2b_units"], FMT_CNT,
                     name="a_ck_b2b", note="B2Bセグメント期末稼働の合計（ソース記載値）")
        if "y5_toc_paid_users" in sc:
            s.scalar("最終年ToC/B2B2C有料ユーザー", sc["y5_toc_paid_users"],
                     FMT_CNT, name="a_ck_toc")
    if "tam" in sc:
        s.scalar("TAM（記載値）", sc["tam"], FMT_M, name="a_ck_tam",
                 note="トップダウン検証用。市場規模の再推計はソース資料側の責務")
        s.scalar("Net SAM（記載値）", sc["net_sam"], FMT_M, name="a_ck_sam")
        s.scalar("SOM/Net SAM（記載値）", sc["som_sam_share"], FMT_PCT,
                 name="a_ck_som_sam", italic=True)
        s.scalar("SOM/TAM（記載値）", sc["som_tam_share"], FMT_PCT,
                 name="a_ck_som_tam", italic=True)

    if cfg.get("scenario_reference"):
        s.section("ケース参考値（ストーリー記載の5年目SOM）")
        for i, case in enumerate(cfg["scenario_reference"]):
            s.scalar(f"{case['case']} Case", case["som"], FMT_M,
                     name=f"a_case{i}", note=case.get("note"))

    sc_cfg = cfg.get("scenario_scales", {})
    vol = sc_cfg.get("volume", [0.75, 1.0, 1.25])
    prc = sc_cfg.get("price", [0.9, 1.0, 1.1])
    s.section("シナリオ感応度スケール", note="仮置き。KPIシートの最終年EBITDA感応度で使用")
    for i, lab in enumerate(("低位", "Base", "高位")):
        s.scalar(f"稼働スケール：{lab}", vol[i], FMT_PCT, name=f"a_sc_vol{i}",
                 italic=True)
    for i, lab in enumerate(("低位", "Base", "高位")):
        s.scalar(f"単価スケール：{lab}", prc[i], FMT_PCT, name=f"a_sc_pr{i}",
                 italic=True)

    th_cfg = cfg.get("kpi_thresholds", {})
    fmts = {"pct": FMT_PCT, "x": FMT_X, "m": FMT_M, "cnt": FMT_CNT}
    s.section("KPI評価しきい値", note="ベンチマーク出典付き。評価式はここを参照（仮置き・変更可）")
    for key, label, default, fk, note in KPI_TH:
        s.scalar(label, th_cfg.get(key, default), fmts[fk],
                 name=f"a_th_{key}", italic=(fk in ("pct", "x")), note=note)

    ct = cfg.get("cap_table")
    if ct:
        s.section("資本政策", note="記載なし・仮置き。最終条件はタームシートによる")
        s.scalar("創業者株数（設立時）", ct["founder_shares"], FMT_CNT,
                 name="a_ct_founder")
        s.scalar("SOプール株数（設立時）", ct.get("initial_pool_shares", 0),
                 FMT_CNT, name="a_ct_pool0")
        s.scalar("SOプール拡大株数（ラウンド前）", ct["pool_expansion_shares"],
                 FMT_CNT, name="a_ct_poolexp",
                 note="調達前拡大＝希薄化は創業者側負担（実務慣行）")
        s.scalar("ポストマネー評価額", ct["post_money"], FMT_M,
                 name="a_ct_post")
        s.scalar("創業者持分帯：下限", ct.get("founder_band", [0.60, 0.75])[0],
                 FMT_PCT, name="a_ct_flow", italic=True,
                 note="シリーズA後の目安60-75%（Gazelle Capital等）")
        s.scalar("創業者持分帯：上限", ct.get("founder_band", [0.60, 0.75])[1],
                 FMT_PCT, name="a_ct_fhigh", italic=True)
        s.scalar("SOプール比率帯：下限", ct.get("pool_band", [0.10, 0.15])[0],
                 FMT_PCT, name="a_ct_plow", italic=True,
                 note="上場審査実務は発行済の約10%が目安（GVA）")
        s.scalar("SOプール比率帯：上限", ct.get("pool_band", [0.10, 0.15])[1],
                 FMT_PCT, name="a_ct_phigh", italic=True)
        s.scalar("ラウンド希薄化率帯：下限", ct.get("dilution_band", [0.10, 0.25])[0],
                 FMT_PCT, name="a_ct_dlow", italic=True,
                 note="1ラウンド10-25%目安。シリーズAは約15-20%が近年水準")
        s.scalar("ラウンド希薄化率帯：上限", ct.get("dilution_band", [0.10, 0.25])[1],
                 FMT_PCT, name="a_ct_dhigh", italic=True)

    v = cfg.get("valuation")
    if v:
        s.section("バリュエーション前提", note="仮置き。出典・取得日はバリュエーションシート備考参照")
        for i, lab in enumerate(("低位", "中位", "高位")):
            s.scalar(f"要求収益率：{lab}", v["discount_rate"][i], FMT_PCT,
                     name=f"a_v_dr{i}", italic=True,
                     note="シリーズA段階20-30%（Damodaran／Pepperdine PCM 2025。2026-07取得）")
        s.scalar("Gordon永久成長率", v["gordon_g"], FMT_PCT, name="a_v_g",
                 italic=True, note="実務レンジ1.5-3.0%（Wall Street Prep）")
        for i, lab in enumerate(("低位", "中位", "高位")):
            s.scalar(f"EBITDA Exit倍率：{lab}", v["ebitda_exit_multiple"][i],
                     FMT_X, name=f"a_v_em{i}",
                     note="SaaS M&A中央値22.1x（aventis-advisors.com 2015-25。2026-07取得）から保守化")
        for i, lab in enumerate(("低位", "中位", "高位")):
            s.scalar(f"売上Exit倍率（類似上場）：{lab}", v["rev_exit_multiple"][i],
                     FMT_X, name=f"a_v_rm{i}",
                     note="低3.0x=国内中央値3.3x比の保守値／中5.0x=成長20-30%帯5.5x近傍／高8.0x=AIプレミアム刈込。2026-07取得")
        for i, lab in enumerate(("低位", "中位", "高位")):
            s.scalar(f"売上Exit倍率（類似取引）：{lab}", v["txn_multiple"][i],
                     FMT_X, name=f"a_v_tm{i}",
                     note="非公開SaaS M&A中央値3.8-4.7x・戦略案件は二桁（Aventis/SEG 2026-07取得）を保守化")
        s.scalar("非流動性ディスカウント（DLOM）", v["dlom"], FMT_PCT,
                 name="a_v_dlom", italic=True,
                 note="実証研究20-35%（Damodaran liquidity.pdf／stout.com。2026-07取得）")
        s.scalar("シリーズA目標MOIC", v["moic_target"], FMT_X,
                 name="a_v_moic", note="シリーズA 10-15x（kruzeconsulting.com。2026-07取得）")
        s.scalar("採用レンジ：下限（現在価値EV）", v["adopted_range"][0], FMT_M,
                 name="a_v_adopt_lo",
                 note="類似上場中位〜DCF中位の重なり帯から設定")
        s.scalar("採用レンジ：上限（現在価値EV）", v["adopted_range"][1], FMT_M,
                 name="a_v_adopt_hi")
        s.scalar("Exit年数（計画期間）", cfg["periods"], FMT_CNT, name="a_v_n",
                 note="割引・IRRの年数。計画期間と一致させる")
    return s


def build_revenue(wb, reg, cfg):
    s = Sheet(wb, reg, "売上計画", cfg)
    rec_rows, impl_rows, end_rows = [], [], []

    for i, seg in enumerate(cfg["segments"]):
        is_b2b = "cogs_pct_of_revenue" not in seg
        s.section(seg["name"], note=seg.get("note"))
        r0 = s.r  # 期首行。解約=r0+1、新規=r0+2、期末=r0+3
        s.row(f"期首稼働数（{seg['unit_label']}）", FMT_CNT,
              formula=lambda col, t, r0=r0:
              f"={s.ref('a_start0', col)}" if t == 0
              else f"={col_of(t - 1)}{r0 + 3}",
              name=f"r_start{i}", note="前期末稼働")
        s.row("解約（▲）", FMT_CNT,
              formula=lambda col, t, i=i, r0=r0:
              f"=-{col}{r0}*{s.ref(f'a_churn{i}', col)}",
              name=f"r_churn{i}")
        s.row("新規獲得", FMT_CNT,
              formula=lambda col, t, r0=r0:
              f"={col}{r0 + 3}-{col}{r0}-{col}{r0 + 1}",
              name=f"r_new{i}",
              note="期末－期首－解約。Y1-Y4ランプはY5目標からの逆算設計。実績取得後はGTMファネル連動で精緻化")
        s.row(f"期末稼働数（{seg['unit_label']}）", FMT_CNT,
              formula=lambda col, t, i=i: f"={s.ref(f'a_end{i}', col)}",
              name=f"r_end{i}", bold=True, total=True)
        end_rows.append(reg.rows[f"r_end{i}"][1])
        s.row("月額ARPU（円/月）", FMT_YEN,
              formula=lambda col, t, i=i:
              f"={s.ref(f'a_fix{i}', col)}+{s.ref(f'a_ufee{i}', col)}" if is_b2b
              else f"={s.ref(f'a_fix{i}', col)}",
              name=f"r_arpu{i}",
              note="固定利用料＋従量利用料" if is_b2b else "月額課金（純額）")
        s.row("リカーリング売上", FMT_M,
              formula=lambda col, t, i=i:
              f"={col}{reg.rows[f'r_end{i}'][1]}*{col}{reg.rows[f'r_arpu{i}'][1]}*12",
              name=f"r_rec{i}", note="期末稼働×ARPU×12（新規は期初稼働と仮定）")
        rec_rows.append(reg.rows[f"r_rec{i}"][1])
        if is_b2b:
            s.row("導入費売上", FMT_M,
                  formula=lambda col, t, i=i:
                  f"={col}{reg.rows[f'r_new{i}'][1]}*{s.ref(f'a_impl{i}', col)}",
                  name=f"r_impl{i}")
            impl_rows.append(reg.rows[f"r_impl{i}"][1])
            s.row("セグメント売上計", FMT_M,
                  formula=lambda col, t, i=i:
                  f"={col}{reg.rows[f'r_rec{i}'][1]}+{col}{reg.rows[f'r_impl{i}'][1]}",
                  total=True, bold=True)

    s.section("全社売上")
    s.row("リカーリング売上合計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in rec_rows),
          name="r_rec_total",
          note="＝期末ARR（期初稼働仮定のためランレートと一致）")
    s.row("導入費売上合計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in impl_rows),
          name="r_impl_total")
    s.row("売上高合計", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['r_rec_total'][1]}+{col}{reg.rows['r_impl_total'][1]}",
          name="r_total", bold=True, grand=True)
    s.row("売上高成長率（YoY）", FMT_PCT,
          formula=lambda col, t:
          f"={col}{reg.rows['r_total'][1]}/{col_of(t - 1)}{reg.rows['r_total'][1]}-1",
          skip_first=True, italic=True, name="r_growth")
    s.row("（参考）期中平均稼働ベース売上", FMT_M,
          formula=lambda col, t: "=" + "+".join(
              f"({col}{reg.rows[f'r_start{i}'][1]}+{col}{reg.rows[f'r_end{i}'][1]})"
              f"/2*{col}{reg.rows[f'r_arpu{i}'][1]}*12"
              for i in range(len(cfg["segments"])))
          + f"+{col_of(t)}{reg.rows['r_impl_total'][1]}",
          italic=True, name="r_avg_basis",
          note="認識基準の感応度：期中平均稼働と仮定した場合の参考値")
    b2b = [end_rows[i] for i in b2b_indices(cfg)]
    toc = [end_rows[i] for i in toc_indices(cfg)]
    if b2b:
        s.row("B2B期末稼働導入単位（社・単位）", FMT_CNT,
              formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in b2b),
              name="r_b2b_units", note="B2Bセグメント期末稼働の合計")
    if toc:
        s.row("ToC/B2B2C有料ユーザー（期末・人）", FMT_CNT,
              formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in toc),
              name="r_toc_users")
    return s


def build_headcount(wb, reg, cfg):
    s = Sheet(wb, reg, "人員計画", cfg)
    alloc_note = {"COGS": "→売上原価へ配賦", "S&M": "→S&Mへ配賦",
                  "R&D": "→R&Dへ配賦", "G&A": "→G&Aへ配賦"}
    s.section("人員数（期末・人）", note="記載なし・仮置き")
    fte_rows = []
    for i, hc in enumerate(cfg["headcount"]):
        r = s.row(hc["function"], FMT_CNT,
                  formula=lambda col, t, i=i: f"={s.ref(f'a_fte{i}', col)}",
                  name=f"h_fte{i}")
        fte_rows.append(r)
    total = s.row("合計人員数", FMT_CNT,
                  formula=lambda col, t:
                  "=" + "+".join(f"{col}{r}" for r in fte_rows),
                  name="h_fte_total", bold=True, total=True)
    s.row("新規採用数（純増）", FMT_CNT,
          formula=lambda col, t:
          f"={col}{total}" if t == 0 else f"={col}{total}-{col_of(t - 1)}{total}",
          name="h_hires", note="純増ベース（退職補充は含まず・仮置き）")

    s.section("人件費（法定福利・諸手当込み）")
    cost_rows = []
    for i, hc in enumerate(cfg["headcount"]):
        r = s.row(hc["function"], FMT_M,
                  formula=lambda col, t, i=i:
                  f"={col}{reg.rows[f'h_fte{i}'][1]}*{s.ref(f'a_sal{i}', col)}"
                  f"*(1+{s.ref('a_burden', col)})",
                  name=f"h_cost{i}", note=alloc_note[hc["allocation"]])
        cost_rows.append(r)
    s.row("人件費合計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in cost_rows),
          name="h_cost_total", bold=True, grand=True)

    s.section("生産性")
    s.row("一人当たり売上高", FMT_M,
          formula=lambda col, t:
          f"={s.ref('r_total', col)}/{col}{reg.rows['h_fte_total'][1]}",
          italic=True, name="h_rev_per_fte")
    return s


def build_opex(wb, reg, cfg):
    s = Sheet(wb, reg, "費用計画", cfg)
    am = alloc_map(cfg)

    def payroll_expr(col, key):
        idxs = am.get(key, [])
        if not idxs:
            return None
        return "+".join(s.ref(f"h_cost{i}", col) for i in idxs)

    s.section("売上原価")
    cogs_rows = []
    for i, seg in enumerate(cfg["segments"]):
        if "cogs_pct_of_revenue" in seg:
            r = s.row(f"{seg['name']}　推論・配信原価", FMT_M,
                      formula=lambda col, t, i=i:
                      f"={s.ref(f'r_rec{i}', col)}*{s.ref(f'a_cogspct{i}', col)}",
                      name=f"o_toccogs{i}", note="売上×原価率")
        else:
            r = s.row(f"{seg['name']}　従量原価", FMT_M, name=f"o_usage{i}",
                      formula=lambda col, t, i=i:
                      f"={s.ref(f'a_end{i}', col)}*{s.ref(f'a_ufee{i}', col)}"
                      f"/{s.ref(f'a_rate{i}', col)}*{s.ref(f'a_cpm{i}', col)}*12",
                      note="期末稼働×稼働分（従量料÷単価）×原価/分×12")
        cogs_rows.append(r)
    cogs_rows.append(s.row(
        "導入原価", FMT_M, name="o_implcogs",
        formula=lambda col, t:
        f"={s.ref('r_impl_total', col)}*{s.ref('a_implcost', col)}",
        note="導入売上×導入原価率"))
    if am.get("COGS"):
        cogs_rows.append(s.row(
            "デリバリー人件費（COGS配賦人員）", FMT_M, name="o_delivery",
            formula=lambda col, t: f"={payroll_expr(col, 'COGS')}"))
    s.row("売上原価合計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in cogs_rows),
          name="o_cogs", bold=True, total=True)

    s.section("S&M（セールス・マーケティング）")
    sm1 = s.row("広告宣伝・販促", FMT_M, name="o_ad",
                formula=lambda col, t:
                f"={s.ref('r_total', col)}*{s.ref('a_smpct', col)}",
                note="売上×比率（仮置き）")
    sm_rows = [sm1]
    if am.get("S&M"):
        sm_rows.append(s.row("セールス・マーケ人件費", FMT_M,
                             formula=lambda col, t:
                             f"={payroll_expr(col, 'S&M')}"))
    s.row("S&M計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in sm_rows),
          name="o_sm", bold=True, total=True)

    s.section("R&D（研究開発）")
    rd1 = s.row("モデル開発・GPU・データ", FMT_M,
                formula=lambda col, t: f"={s.ref('a_rdprog', col)}",
                note="日本語特化モデル内製化投資")
    rd_rows = [rd1]
    if am.get("R&D"):
        rd_rows.append(s.row("プロダクト・R&D人件費", FMT_M,
                             formula=lambda col, t:
                             f"={payroll_expr(col, 'R&D')}"))
    s.row("R&D計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in rd_rows),
          name="o_rd", bold=True, total=True)

    s.section("G&A（管理部門）")
    ga_rows = []
    if am.get("G&A"):
        ga_rows.append(s.row("コーポレート人件費", FMT_M,
                             formula=lambda col, t:
                             f"={payroll_expr(col, 'G&A')}"))
    ga2 = s.row("オフィス・情報システム", FMT_M,
                formula=lambda col, t:
                f"={s.ref('h_fte_total', col)}*{s.ref('a_office', col)}",
                note="人員数×単価")
    ga3 = s.row("採用費", FMT_M,
                formula=lambda col, t:
                f"={s.ref('h_hires', col)}*{s.ref('a_recruit', col)}",
                note="新規採用×採用単価")
    ga4 = s.row("士業・保険・その他管理", FMT_M, name="o_gapctrev",
                formula=lambda col, t:
                f"={s.ref('r_total', col)}*{s.ref('a_gapct', col)}")
    ga_rows += [ga2, ga3, ga4]
    s.row("G&A計", FMT_M,
          formula=lambda col, t: "=" + "+".join(f"{col}{r}" for r in ga_rows),
          name="o_ga", bold=True, total=True)

    s.blank()
    s.row("営業費用合計（S&M＋R&D＋G&A）", FMT_M,
          formula=lambda col, t:
          f"={s.ref('o_sm', col)}+{s.ref('o_rd', col)}+{s.ref('o_ga', col)}",
          name="o_opex", bold=True, grand=True)
    s.row("（参考）非人件費費用計", FMT_M,
          formula=lambda col, t:
          f"={s.ref('o_cogs', col)}+{s.ref('o_opex', col)}"
          f"-{s.ref('h_cost_total', col)}",
          italic=True, name="o_nonpay",
          note="原価＋営業費用－人件費。資金繰りの買掛対象")
    return s


def build_pl(wb, reg, cfg):
    s = Sheet(wb, reg, "損益計画", cfg)
    capex_row = reg.rows["a_capex"][1]

    s.section("損益計算書")
    s.row("リカーリング売上", FMT_M,
          formula=lambda col, t: f"={s.ref('r_rec_total', col)}", name="p_rec")
    s.row("導入費売上", FMT_M,
          formula=lambda col, t: f"={s.ref('r_impl_total', col)}", name="p_impl")
    s.row("売上高", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['p_rec'][1]}+{col}{reg.rows['p_impl'][1]}",
          name="p_rev", bold=True, total=True)
    s.row("売上原価", FMT_M,
          formula=lambda col, t: f"={s.ref('o_cogs', col)}", name="p_cogs")
    s.row("売上総利益", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['p_rev'][1]}-{col}{reg.rows['p_cogs'][1]}",
          name="p_gp", bold=True, total=True)
    s.row("売上総利益率", FMT_PCT,
          formula=lambda col, t:
          f"={col}{reg.rows['p_gp'][1]}/{col}{reg.rows['p_rev'][1]}",
          name="p_gm", italic=True,
          note=cfg.get("gm_phase_note", "粗利率はドライバーから導出（率の直打ちなし）"))
    s.blank()
    s.row("S&M", FMT_M, formula=lambda col, t: f"={s.ref('o_sm', col)}",
          name="p_sm")
    s.row("R&D", FMT_M, formula=lambda col, t: f"={s.ref('o_rd', col)}",
          name="p_rd")
    s.row("G&A", FMT_M, formula=lambda col, t: f"={s.ref('o_ga', col)}",
          name="p_ga")
    s.row("営業費用計", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['p_sm'][1]}+{col}{reg.rows['p_rd'][1]}"
          f"+{col}{reg.rows['p_ga'][1]}",
          name="p_opex", total=True)
    s.row("EBITDA", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['p_gp'][1]}-{col}{reg.rows['p_opex'][1]}",
          name="p_ebitda", bold=True, total=True)
    s.row("EBITDAマージン", FMT_PCT,
          formula=lambda col, t:
          f"={col}{reg.rows['p_ebitda'][1]}/{col}{reg.rows['p_rev'][1]}",
          name="p_ebitda_m", italic=True)
    s.row("減価償却費", FMT_M,
          formula=lambda col, t:
          f"=SUM('前提条件'!$E${capex_row}:{col}{capex_row})"
          f"/{s.ref('a_depyears', col)}",
          name="p_dep", note="定額法（投資年度から均等償却の簡便法）")
    s.row("営業利益", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['p_ebitda'][1]}-{col}{reg.rows['p_dep'][1]}",
          name="p_op", bold=True, total=True)
    s.row("法人税等", FMT_M, formula=lambda col, t: "=0",
          name="p_tax", note="課税所得（繰越欠損金控除後）×実効税率")
    s.row("当期純利益", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['p_op'][1]}-{col}{reg.rows['p_tax'][1]}",
          name="p_ni", bold=True, grand=True)
    s.row("当期純利益率", FMT_PCT,
          formula=lambda col, t:
          f"={col}{reg.rows['p_ni'][1]}/{col}{reg.rows['p_rev'][1]}",
          italic=True)

    s.section("繰越欠損金スケジュール", note="仮置き：期初残高ゼロ")
    s.row("期首繰越欠損金", FMT_M, formula=lambda col, t: "=0",
          name="p_nol_start")
    s.row("課税所得", FMT_M,
          formula=lambda col, t:
          f"=MAX(0,{col}{reg.rows['p_op'][1]}-{col}{reg.rows['p_nol_start'][1]})",
          name="p_taxable", note="営業利益－期首繰越欠損金（下限0）")
    s.row("期末繰越欠損金", FMT_M,
          formula=lambda col, t:
          f"=MAX(0,{col}{reg.rows['p_nol_start'][1]}"
          f"-MAX(0,{col}{reg.rows['p_op'][1]}))"
          f"+MAX(0,-{col}{reg.rows['p_op'][1]})",
          name="p_nol_end", note="期首－利益による使用＋損失による積み上がり")

    # 前方参照の解決: 法人税＝課税所得×税率、期首NOL＝前期末NOL
    s.patch("p_tax", lambda col, t:
            f"={col}{reg.rows['p_taxable'][1]}*{s.ref('a_tax', col)}")
    s.patch("p_nol_start", lambda col, t:
            f"={s.ref('a_nol0', col)}" if t == 0
            else f"={col_of(t - 1)}{reg.rows['p_nol_end'][1]}")
    return s


def build_cash(wb, reg, cfg):
    s = Sheet(wb, reg, "資金繰り", cfg)
    s.section("フリーキャッシュフロー")
    s.row("EBITDA", FMT_M,
          formula=lambda col, t: f"={s.ref('p_ebitda', col)}", name="c_ebitda")
    s.row("法人税等支払（▲）", FMT_M,
          formula=lambda col, t: f"=-{s.ref('p_tax', col)}", name="c_tax")
    ar = s.row("売掛金残高", FMT_M,
               formula=lambda col, t:
               f"={s.ref('r_total', col)}*{s.ref('a_ar', col)}/365",
               name="c_ar", note="売上×回収サイト÷365")
    ap = s.row("買掛金残高", FMT_M,
               formula=lambda col, t:
               f"={s.ref('o_nonpay', col)}*{s.ref('a_ap', col)}/365",
               name="c_ap", note="非人件費費用計×支払サイト÷365")
    dr_ = s.row("前受収益残高", FMT_M,
                formula=lambda col, t:
                f"={s.ref('r_rec_total', col)}*{s.ref('a_prepay', col)}"
                f"*{s.ref('a_prepay_m', col)}/12",
                name="c_dr",
                note="年間前払比率×リカーリング×平均残存6ヶ月（簡便法）")
    s.row("運転資本増減", FMT_M,
          formula=lambda col, t:
          f"=-{col}{ar}+{col}{ap}+{col}{dr_}" if t == 0
          else f"=-({col}{ar}-{col_of(t - 1)}{ar})"
               f"+({col}{ap}-{col_of(t - 1)}{ap})"
               f"+({col}{dr_}-{col_of(t - 1)}{dr_})",
          name="c_wc", note="売掛増は現金減、買掛・前受増は現金増")
    s.row("設備投資（▲）", FMT_M,
          formula=lambda col, t: f"=-{s.ref('a_capex', col)}", name="c_capex")
    s.row("フリーキャッシュフロー", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['c_ebitda'][1]}+{col}{reg.rows['c_tax'][1]}"
          f"+{col}{reg.rows['c_wc'][1]}+{col}{reg.rows['c_capex'][1]}",
          name="c_fcf", bold=True, total=True)

    s.section("資金調達・現金残高")
    s.row("エクイティ調達", FMT_M,
          formula=lambda col, t: f"={s.ref('a_raise', col)}", name="c_raise")
    s.row("現金増減", FMT_M,
          formula=lambda col, t:
          f"={col}{reg.rows['c_fcf'][1]}+{col}{reg.rows['c_raise'][1]}",
          name="c_delta")
    begin = s.row("期首現金", FMT_M, formula=lambda col, t: "=0",
                  name="c_begin")
    s.row("期末現金", FMT_M,
          formula=lambda col, t:
          f"={col}{begin}+{col}{reg.rows['c_delta'][1]}",
          name="c_end", bold=True, grand=True)
    s.patch("c_begin", lambda col, t:
            f"={s.ref('a_cash0', col)}" if t == 0
            else f"={col_of(t - 1)}{reg.rows['c_end'][1]}")
    s.row("ランウェイ（月）", FMT_D1,
          formula=lambda col, t:
          f"=IF({col}{reg.rows['c_fcf'][1]}>=0,0,"
          f"{col}{reg.rows['c_end'][1]}/(-{col}{reg.rows['c_fcf'][1]}/12))",
          italic=True, name="c_runway",
          note="期末現金÷月次バーン。FCF黒字時はダッシュ表示")

    s.section("チェック")
    s.check("現金残高チェック（0=OK）",
            formula=lambda col, t:
            f"=IF({col}{reg.rows['c_end'][1]}>=0,0,1)",
            note="期末現金が負なら1（資金ショート）")
    s.check("売上タイアウト（売上計画－損益計画）",
            formula=lambda col, t:
            f"={s.ref('r_total', col)}-{s.ref('p_rev', col)}",
            fmt=FMT_M, note="0=OK")
    s.check("EBITDAタイアウト（損益計画－本表）",
            formula=lambda col, t:
            f"={s.ref('p_ebitda', col)}-{col}{reg.rows['c_ebitda'][1]}",
            fmt=FMT_M, note="0=OK")
    return s


def build_summary(wb, reg, cfg):
    s = Sheet(wb, reg, "サマリー", cfg)
    s.section("損益ハイライト")
    s.row("売上高", FMT_M, formula=lambda col, t: f"={s.ref('p_rev', col)}",
          name="s_rev", bold=True)
    s.row("売上高成長率（YoY）", FMT_PCT,
          formula=lambda col, t: f"={s.ref('r_growth', col)}",
          skip_first=True, italic=True)
    s.row("売上総利益", FMT_M, formula=lambda col, t: f"={s.ref('p_gp', col)}")
    s.row("売上総利益率", FMT_PCT,
          formula=lambda col, t: f"={s.ref('p_gm', col)}", italic=True,
          note=cfg.get("gm_phase_note", "原価ドライバーから導出"))
    s.row("EBITDA", FMT_M, formula=lambda col, t: f"={s.ref('p_ebitda', col)}",
          bold=True)
    s.row("EBITDAマージン", FMT_PCT,
          formula=lambda col, t: f"={s.ref('p_ebitda_m', col)}", italic=True)
    s.row("当期純利益", FMT_M, formula=lambda col, t: f"={s.ref('p_ni', col)}")

    s.section("事業KPI")
    s.row("ARR（期末ランレート）", FMT_M,
          formula=lambda col, t: f"={s.ref('r_rec_total', col)}",
          note="期初稼働仮定のためリカーリング売上と一致")
    if "r_b2b_units" in reg.rows:
        s.row("B2B稼働導入単位（社・単位）", FMT_CNT,
              formula=lambda col, t: f"={s.ref('r_b2b_units', col)}")
    if "r_toc_users" in reg.rows:
        s.row("ToC/B2B2C有料ユーザー（人）", FMT_CNT,
              formula=lambda col, t: f"={s.ref('r_toc_users', col)}")
    s.row("従業員数（人）", FMT_CNT,
          formula=lambda col, t: f"={s.ref('h_fte_total', col)}")
    s.row("一人当たり売上高", FMT_M,
          formula=lambda col, t: f"={s.ref('h_rev_per_fte', col)}", italic=True)

    s.section("資金")
    s.row("エクイティ調達", FMT_M,
          formula=lambda col, t: f"={s.ref('c_raise', col)}",
          note="調達額・時期は仮置き（ソースに記載なし）")
    s.row("フリーキャッシュフロー", FMT_M,
          formula=lambda col, t: f"={s.ref('c_fcf', col)}")
    s.row("期末現金", FMT_M, formula=lambda col, t: f"={s.ref('c_end', col)}",
          bold=True)
    hdr_row = s.HEADER_ROW
    ebitda_rng = (f"'損益計画'!{col_of(0)}{reg.rows['p_ebitda'][1]}:"
                  f"{col_of(cfg['periods'] - 1)}{reg.rows['p_ebitda'][1]}")
    fcf_rng = (f"'資金繰り'!{col_of(0)}{reg.rows['c_fcf'][1]}:"
               f"{col_of(cfg['periods'] - 1)}{reg.rows['c_fcf'][1]}")
    lbl_rng = f"{col_of(0)}${hdr_row}:{col_of(cfg['periods'] - 1)}${hdr_row}"
    s.row("EBITDA黒字化年度", "General",
          formula=lambda col, t:
          (f'=IF(COUNTIF({ebitda_rng},">0")=0,"計画期間内なし",'
           f'INDEX({lbl_rng},COUNTIF({ebitda_rng},"<=0")+1))')
          if t == 0 else None,
          note="損失先行→黒字継続の単調推移を前提とした導出")
    s.row("FCF黒字化年度", "General",
          formula=lambda col, t:
          (f'=IF(COUNTIF({fcf_rng},">0")=0,"計画期間内なし",'
           f'INDEX({lbl_rng},COUNTIF({fcf_rng},"<=0")+1))')
          if t == 0 else None,
          note="税・運転資本・投資によりEBITDA黒字化年とズレうる（本計画では前受金の現金前倒しにより同年）")

    # --- 照合ブロック（最終年度、モデル値 vs 記載値） -------------------
    last = col_of(cfg["periods"] - 1)
    s.section(
        f"エクイティストーリー照合（FY{cfg['start_year'] + cfg['periods'] - 1}）",
        note=cfg.get("source_note"))
    ws = s.ws
    hdr = s.r
    for c, label in ((5, "モデル値"), (6, "記載値"), (7, "差異")):
        cell = ws.cell(row=hdr, column=c, value=label)
        cell.font = font(bold=True)
        cell.alignment = Alignment(horizontal="right")
        cell.border = Border(bottom=THIN)
    for c in range(2, 5):
        ws.cell(row=hdr, column=c).border = Border(bottom=THIN)
    s.r += 1
    ties = []
    if "a_ck_rec" in reg.cells:
        ties.append(("Recurring基盤収益", f"={s.ref('r_rec_total', last)}",
                     f"={s.sref('a_ck_rec')}", FMT_M))
    if "a_ck_impl" in reg.cells and "r_impl_total" in reg.rows:
        ties.append(("導入費収益", f"={s.ref('r_impl_total', last)}",
                     f"={s.sref('a_ck_impl')}", FMT_M))
    if "a_ck_som" in reg.cells:
        ties.append(("SOM（基盤収益合計）", f"={s.ref('r_total', last)}",
                     f"={s.sref('a_ck_som')}", FMT_M))
    if "a_ck_b2b" in reg.cells and "r_b2b_units" in reg.rows:
        ties.append(("B2B稼働導入単位", f"={s.ref('r_b2b_units', last)}",
                     f"={s.sref('a_ck_b2b')}", FMT_CNT))
    if "a_ck_toc" in reg.cells and "r_toc_users" in reg.rows:
        ties.append(("ToC/B2B2C有料ユーザー", f"={s.ref('r_toc_users', last)}",
                     f"={s.sref('a_ck_toc')}", FMT_CNT))
    ties = [t + (0.01,) for t in ties]
    if "a_ck_sam" in reg.cells:
        ties += [
            ("SOM/Net SAMシェア（±5%）",
             f"={s.ref('r_total', last)}/{s.sref('a_ck_sam')}",
             f"={s.sref('a_ck_som_sam')}", FMT_PCT, 0.05),
            ("SOM/TAMシェア（±5%）",
             f"={s.ref('r_total', last)}/{s.sref('a_ck_tam')}",
             f"={s.sref('a_ck_som_tam')}", FMT_PCT, 0.05),
        ]
    red = Font(name=FONT, size=SIZE, color=RED, bold=True)
    tie_cells = []
    for label, f_model, f_stated, fmt, tol in ties:
        lab = ws.cell(row=s.r, column=3, value=label)
        lab.font = font()
        for c, f in ((5, f_model), (6, f_stated)):
            cell = ws.cell(row=s.r, column=c, value=f)
            cell.font = font(GREEN if PURE_LINK.match(f) else BLACK)
            cell.number_format = fmt
            cell.alignment = Alignment(horizontal="right")
        d = ws.cell(row=s.r, column=7, value=f"=E{s.r}/F{s.r}-1")
        d.font = font(italic=True)
        d.number_format = FMT_PCT
        d.alignment = Alignment(horizontal="right")
        ws.conditional_formatting.add(f"G{s.r}", CellIsRule(
            operator="greaterThan", formula=[str(tol)], font=red))
        ws.conditional_formatting.add(f"G{s.r}", CellIsRule(
            operator="lessThan", formula=[str(-tol)], font=red))
        tie_cells.append((s.r, tol))
        s.r += 1
    tie_diff_expr = "+".join(
        f"(ABS(G{r})>{tol})*1" for r, tol in tie_cells)

    # --- ケース比較（参考） --------------------------------------------
    if cfg.get("scenario_reference"):
        s.section("ケース比較（参考・ストーリー記載の5年目SOM）")
        for i, case in enumerate(cfg["scenario_reference"]):
            lab = ws.cell(row=s.r, column=3, value=f"{case['case']} Case")
            lab.font = font()
            c = ws.cell(row=s.r, column=5, value=f"={s.sref(f'a_case{i}')}")
            c.font = font(GREEN)
            c.number_format = FMT_M
            c.alignment = Alignment(horizontal="right")
            note = case.get("note", "")
            if case["case"] == "Base":
                note += "（本モデルの前提）"
            ws.cell(row=s.r, column=s.note_col, value=note).font = font(
                GRAY, italic=True)
            s.r += 1

    # --- 整合性チェック集約（全シートのチェック行をNG件数で集計） --------
    s.ws.row_breaks.append(Break(id=s.r))
    s.section("整合性チェック集約",
              note="全シートのチェック行のNG件数を数式集計。全行0で総合判定OK")
    agg_rows = []
    for ck in reg.checks:
        rng_ck = f"'{ck['sheet']}'!{ck['c0']}{ck['row']}:{ck['c1']}{ck['row']}"
        short = ck["label"].split("（")[0]
        r = s.row(f"{ck['sheet']}：{short}", FMT_CNT,
                  formula=lambda col, t, rng_ck=rng_ck, tol=ck["tol"]:
                  f"=SUMPRODUCT(--(ABS({rng_ck})>{tol}))" if t == 0 else None,
                  note=f"許容誤差±{ck['tol']}")
        agg_rows.append(r)
    r = s.row("サマリー：エクイティストーリー照合", FMT_CNT,
              formula=lambda col, t:
              f"={tie_diff_expr}" if t == 0 else None,
              note="金額・数量±1%、市場シェア±5%（記載値の2桁丸めに対応）")
    agg_rows.append(r)
    first = col_of(0)
    total = s.row("総合判定", "General",
                  formula=lambda col, t:
                  "=IF(SUM(" + ",".join(f"{first}{r}" for r in agg_rows)
                  + f')=0,"OK","要確認")' if t == 0 else None,
                  bold=True, grand=True)
    ws.conditional_formatting.add(
        f"{first}{total}",
        CellIsRule(operator="equal", formula=['"要確認"'],
                   font=Font(name=FONT, size=SIZE, color=RED, bold=True)))
    return s


def build_kpi(wb, reg, cfg):
    s = Sheet(wb, reg, "KPI", cfg, extra_cols=("ベンチマーク", "評価"))
    p = s.p
    last = col_of(p - 1)
    fy3 = col_of(2) if p >= 3 else last

    def rng(row):
        return f"{col_of(0)}{row}:{col_of(p - 1)}{row}"

    s.section("成長性", note="成長率はARR（継続課金）ベース。導入フィー込み売上と区別")
    arr = s.row("ARR（期末ランレート）", FMT_M,
                formula=lambda col, t: f"={s.ref('r_rec_total', col)}",
                name="k_arr")
    growth = s.row("ARR成長率（YoY）", FMT_PCT,
                   formula=lambda col, t:
                   None if t == 0 else f"={col}{arr}/{col_of(t - 1)}{arr}-1",
                   italic=True, name="k_growth",
                   bench="$1-5M ARR帯 +40%以上",
                   evaluation=f"=IF({last}{s.r}>={s.sref('a_th_growth_good')},"
                              f"\"良好\",IF({last}{s.r}>="
                              f"{s.sref('a_th_growth_ok')},\"水準内\",\"要説明\"))",
                   note="SaaS Capital Growth Benchmarks。最終年で評価")
    netnew = s.row("純増ARR", FMT_M,
                   formula=lambda col, t:
                   f"={col}{arr}" if t == 0
                   else f"={col}{arr}-{col_of(t - 1)}{arr}",
                   name="k_netnew",
                   note="Burn Multiple / Magic Numberの分子。初年度は期初ARRゼロのため=ARR")

    s.section("収益性")
    s.row("売上総利益率", FMT_PCT,
          formula=lambda col, t: f"={s.ref('p_gm', col)}", italic=True,
          name="k_gm", bench="70%以上（AI型50%+）",
          evaluation=f"=IF({last}{s.r}>={s.sref('a_th_gm_good')},\"良好\","
                     f"IF({last}{s.r}>={s.sref('a_th_gm_ok')},\"水準内\",\"要説明\"))",
          note="KeyBanc 2024: 総GM中央値71-75%。最終年で評価")
    s.row("EBITDAマージン", FMT_PCT,
          formula=lambda col, t: f"={s.ref('p_ebitda_m', col)}", italic=True,
          name="k_em", bench="最終年15%以上",
          evaluation=f"=IF({last}{s.r}>={s.sref('a_th_ebitda_good')},\"良好\","
                     f"IF({last}{s.r}>={s.sref('a_th_ebitda_ok')},\"水準内\",\"要説明\"))",
          note="成熟期15-25%（Founderpath）。最終年で評価")
    r40 = s.row("Rule of 40（ARR成長率＋EBITDAマージン）", FMT_PCT,
                formula=lambda col, t:
                None if t == 0
                else f"={col}{growth}+{s.ref('p_ebitda_m', col)}",
                italic=True, name="k_r40", bench="40%以上",
                evaluation=f"=IF({last}{s.r}>={s.sref('a_th_r40_good')},\"良好\","
                           f"IF({last}{s.r}>={s.sref('a_th_r40_ok')},\"水準内\",\"要説明\"))",
                note="ARR約$25M未満の年は参考値（BVP Rule of X）。最終年で評価")
    svc = s.row("サービス（導入費）売上比率", FMT_PCT,
                formula=lambda col, t:
                f"={s.ref('r_impl_total', col)}/{s.ref('r_total', col)}",
                italic=True, name="k_svc", bench="20%未満・低下傾向",
                evaluation=f"=IF(AND({last}{s.r}<={s.sref('a_th_svc_good')},"
                           f"{last}{s.r}<{fy3}{s.r}),\"良好\","
                           f"IF({last}{s.r}<={s.sref('a_th_svc_max')},\"水準内\",\"要説明\"))",
                note="SaaStr/Dave Kellogg: 上限20%。水準＋低下傾向の複合判定")

    s.section("効率性")
    magic = s.row("Magic Number（純増ARR÷前年S&M）", FMT_X,
                  formula=lambda col, t:
                  None if t == 0
                  else f"={col}{netnew}/{s.ref('o_sm', col_of(t - 1))}",
                  name="k_magic", bench="0.75x以上",
                  note="Scale VP。FY3-5平均で評価。年次は採用ランプを平滑化、解約近似（グロス≒ネット）の概算値")
    s.ws.cell(row=magic, column=s.last_col + 2,
              value=f"=IF(AVERAGE({fy3}{magic}:{last}{magic})>="
                    f"{s.sref('a_th_magic_good')},\"良好\","
                    f"IF(AVERAGE({fy3}{magic}:{last}{magic})>="
                    f"{s.sref('a_th_magic_ok')},\"水準内\",\"要説明\"))"
              ).font = font()
    s.ws.cell(row=magic, column=s.last_col + 2).alignment = Alignment(
        horizontal="right")
    rpe = s.row("一人当たり売上高", FMT_M,
                formula=lambda col, t: f"={s.ref('h_rev_per_fte', col)}",
                name="k_rpe", bench="2,000万円以上",
                evaluation=f"=IF({last}{s.r}>={s.sref('a_th_rpe_good')},\"良好\","
                           f"IF({last}{s.r}>={s.sref('a_th_rpe_ok')},\"水準内\",\"要説明\"))",
                note="SaaS Capital中央値$130K≒2,000万円（150円/$）。最終年で評価")
    band_notes = {
        "o_sm": cfg.get("sm_ratio_note", "SaaS Capital帯30-50%で帯判定。帯外の場合は前提の説明を注記する"),
        "o_rd": "SaaS Capital Spending Benchmarks。最終年で帯判定",
        "o_ga": "SaaS Capital Spending Benchmarks。最終年で帯判定",
    }
    for key, nm, lowk, highk in (
            ("o_sm", "S&M比率（対売上）", "a_th_sm_low", "a_th_sm_high"),
            ("o_rd", "R&D比率（対売上）", "a_th_rd_low", "a_th_rd_high"),
            ("o_ga", "G&A比率（対売上）", "a_th_ga_low", "a_th_ga_high")):
        s.row(nm, FMT_PCT,
              formula=lambda col, t, key=key:
              f"={s.ref(key, col)}/{s.ref('r_total', col)}",
              italic=True, bench="帯内（過小も要説明）",
              evaluation=f"=IF(AND({last}{s.r}>={s.sref(lowk)},"
                         f"{last}{s.r}<={s.sref(highk)}),\"良好\","
                         f"IF(AND({last}{s.r}>={s.sref(lowk)}-{s.sref('a_th_band_tol')},"
                         f"{last}{s.r}<={s.sref(highk)}+{s.sref('a_th_band_tol')}),"
                         f"\"水準内\",\"要説明\"))",
              note=band_notes[key])

    b2b_ix = b2b_indices(cfg)
    if b2b_ix:
        s.row("（参考）B2B獲得単価（円/導入単位）", FMT_YEN,
              formula=lambda col, t:
              f"={s.ref('o_sm', col)}/("
              + "+".join(s.ref(f"r_new{i}", col) for i in b2b_ix) + ")",
              name="k_cac", bench="参考値",
              note="S&M計÷新規B2B導入単位。コホート仮定に依存しない獲得効率。LTV逆算は行わない方針")

    s.section("資金効率")
    burn = s.row("Burn Multiple（Net Burn÷純増ARR）", FMT_X,
                 formula=lambda col, t:
                 f"=IF({s.ref('c_fcf', col)}>=0,\"—\","
                 f"-{s.ref('c_fcf', col)}/{col}{netnew})",
                 name="k_burn", bench="1.5x以下",
                 note="Sacks: <1x amazing / 1.5-2x good / 2x超は要注意（バーン年のみ）")
    s.ws.cell(row=burn, column=s.last_col + 2,
              value=f"=IF(COUNT({rng(burn)})=0,\"該当なし\","
                    f"IF(MAX({rng(burn)})<={s.sref('a_th_burn_good')},\"良好\","
                    f"IF(MAX({rng(burn)})<={s.sref('a_th_burn_ok')},"
                    f"\"水準内\",\"要説明\")))").font = font()
    s.ws.cell(row=burn, column=s.last_col + 2).alignment = Alignment(
        horizontal="right")
    run = s.row("ランウェイ（月）", FMT_D1,
                formula=lambda col, t: f"={s.ref('c_runway', col)}",
                italic=True, name="k_runway", bench="18ヶ月以上（調達直後）",
                note="バーン年のみ対象。黒字年はダッシュ")
    min_pos = (f"SMALL({rng(run)},COUNTIF({rng(run)},\"<=0\")+1)")
    s.ws.cell(row=run, column=s.last_col + 2,
              value=f"=IF(COUNTIF({rng(run)},\">0\")=0,\"該当なし\","
                    f"IF({min_pos}>={s.sref('a_th_runway_good')},\"良好\","
                    f"IF({min_pos}>={s.sref('a_th_runway_ok')},"
                    f"\"水準内\",\"要説明\")))").font = font()
    s.ws.cell(row=run, column=s.last_col + 2).alignment = Alignment(
        horizontal="right")
    cash = s.row("期末現金", FMT_M,
                 formula=lambda col, t: f"={s.ref('c_end', col)}",
                 name="k_cash", bench="全期間 > 0",
                 evaluation=f"=IF(MIN({rng(s.r)})>0,\"良好\",\"要説明\")")

    # --- シナリオ感応度（最終年EBITDA・線形分解） ---
    s.section("シナリオ感応度：最終年EBITDA（稼働スケール × 単価スケール）",
              note="線形分解による概算（人員・固定費・R&D投資は据置）。Base×BaseはPLのEBITDAと一致")
    L = col_of(p - 1)
    rev = f"'売上計画'!{L}{reg.rows['r_total'][1]}"
    usage = "+".join(f"'費用計画'!{L}{reg.rows[f'o_usage{i}'][1]}"
                     for i in b2b_ix) or "0"
    mixed_parts = [f"'費用計画'!{L}{reg.rows[f'o_toccogs{i}'][1]}"
                   for i in toc_indices(cfg)]
    mixed_parts.append(f"'費用計画'!{L}{reg.rows['o_implcogs'][1]}")
    mixed = "+".join(mixed_parts)
    fixed_cogs = (f"'費用計画'!{L}{reg.rows['o_delivery'][1]}"
                  if "o_delivery" in reg.rows else "0")
    ad_gap = (f"'費用計画'!{L}{reg.rows['o_ad'][1]}"
              f"+'費用計画'!{L}{reg.rows['o_gapctrev'][1]}")
    opx = f"'費用計画'!{L}{reg.rows['o_opex'][1]}"
    d1 = s.row("分解：売上（最終年・稼働×単価連動）", FMT_M,
               formula=lambda col, t: f"={rev}" if t == 0 else None,
               italic=True, note="1行1計算のための分解行。感応度セルはここを参照")
    d2 = s.row("分解：稼働連動原価（従量原価）", FMT_M,
               formula=lambda col, t: f"={usage}" if t == 0 else None,
               italic=True)
    d3 = s.row("分解：稼働×単価連動費（ToC原価＋導入原価＋売上比例費）", FMT_M,
               formula=lambda col, t:
               f"={mixed}+{ad_gap}" if t == 0 else None, italic=True)
    d4 = s.row("分解：固定費（人員・R&D・オフィス等＝据置）", FMT_M,
               formula=lambda col, t:
               f"={fixed_cogs}+({opx})-({ad_gap})" if t == 0 else None,
               italic=True)
    E0 = col_of(0)
    mini_h = ["単価：低位", "単価：Base", "単価：高位"]
    ws = s.ws
    for j, h in enumerate(mini_h):
        c = ws.cell(row=s.r, column=5 + j, value=h)
        c.font = font(bold=True)
        c.alignment = Alignment(horizontal="right")
        c.border = Border(bottom=THIN)
    for cc in range(2, 5):
        ws.cell(row=s.r, column=cc).border = Border(bottom=THIN)
    s.r += 1
    sc_rows = []
    for i, lab in enumerate(("低位", "Base", "高位")):
        def f_sc(col, t, i=i):
            if t >= 3:
                return None
            a = s.sref(f"a_sc_vol{i}")
            b = s.sref(f"a_sc_pr{t}")
            return (f"={a}*{b}*{E0}{d1}-{a}*{E0}{d2}"
                    f"-{a}*{b}*{E0}{d3}-{E0}{d4}")
        r = s.row(f"稼働スケール：{lab}", FMT_M, formula=f_sc)
        sc_rows.append(r)
    s.check("感応度整合（Base×Base−EBITDA・0=OK）",
            formula=lambda col, t:
            f"={col_of(1)}{sc_rows[1]}-'損益計画'!{L}{reg.rows['p_ebitda'][1]}"
            if t == 1 else None,
            fmt=FMT_M, note="線形分解式とPLの整合検算")

    s.blank()
    s.row("（注記）LTV/CAC・CAC Payback・NRR等のリテンション系KPIは、"
          "実績コホートデータ整備後に管理する", "General",
          formula=lambda col, t: None, indent=1,
          note="仮定チャーンからの逆算は精度を装うため作成しない（本計画は純増ARRベースの効率指標で代替）")
    s.row("（注記）ARPAは価格表入力から直接導出しており、定義上価格表と一致する", "General",
          formula=lambda col, t: None, indent=1)

    # 評価列の条件付き書式（要説明のみ赤字）
    ev_col = get_column_letter(s.last_col + 2)
    red = Font(name=FONT, size=SIZE, color=RED, bold=True)
    s.ws.conditional_formatting.add(
        f"{ev_col}{s.HEADER_ROW + 1}:{ev_col}{s.r}",
        CellIsRule(operator="equal", formula=['"要説明"'], font=red))
    return s


def build_captable(wb, reg, cfg):
    events = ["設立時", "増資前", "増資後", "予備"]
    s = Sheet(wb, reg, "資本政策", cfg, header_labels=events)
    A = col_of(2)  # ラウンド後列
    round0 = cfg["financing"]["rounds"][0]
    raise_col = col_of(round0["year_index"])  # 実施年の資金繰り列

    s.section("ラウンド前提（シリーズA＝増資列）", note="ポスト入力→プレ差引→株価＝プレ÷既存FD株数の順で循環を回避")
    raise_r = s.row("調達額", FMT_M,
                    formula=lambda col, t:
                    f"={s.ref('c_raise', raise_col)}" if t == 2 else None,
                    name="ct_raise",
                    note=f"資金繰りシートの調達額（FY{cfg['start_year'] + round0['year_index']}実施年列）を参照。再入力しない")
    post_r = s.row("ポストマネー評価額", FMT_M,
                   formula=lambda col, t:
                   f"={s.sref('a_ct_post')}" if t == 2 else None,
                   name="ct_post", note="仮置き（記載なし）")
    pre_r = s.row("プレマネー評価額", FMT_M,
                  formula=lambda col, t:
                  f"={A}{post_r}-{A}{raise_r}" if t == 2 else None,
                  name="ct_pre")
    prefd_r = s.row("ラウンド前FD株数", FMT_CNT,
                    formula=lambda col, t: None, name="ct_prefd",
                    note="プール拡大後の完全希薄化株数")
    price_r = s.row("株価（円/株）", FMT_YEN,
                    formula=lambda col, t:
                    f"={A}{pre_r}/{A}{prefd_r}" if t == 2 else None,
                    name="ct_price")
    new_r = s.row("新規発行株数", FMT_CNT,
                  formula=lambda col, t:
                  f"=ROUND({A}{raise_r}/{A}{price_r},0)" if t == 2 else None,
                  name="ct_new", note="端数は整数丸め（チェックで1株未満誤差を許容）")

    s.section("株主構成（完全希薄化株数）", note="残高＝前イベント残高＋当イベント増減。%は導出のみ")
    f_r = s.row("創業者", FMT_CNT,
                formula=lambda col, t:
                f"={s.sref('a_ct_founder')}" if t == 0
                else f"={col_of(t - 1)}{s.r}",
                name="ct_f")
    p_r = s.row("SOプール（潜在株式）", FMT_CNT,
                formula=lambda col, t:
                f"={s.sref('a_ct_pool0')}" if t == 0
                else (f"={col_of(0)}{s.r}+{s.sref('a_ct_poolexp')}" if t == 1
                      else f"={col_of(t - 1)}{s.r}"),
                name="ct_p", note="ラウンド前に拡大（希薄化は創業者側負担）")
    i_r = s.row("シリーズA投資家", FMT_CNT,
                formula=lambda col, t:
                None if t < 2 else (f"={A}{new_r}" if t == 2
                                    else f"={col_of(t - 1)}{s.r}"),
                name="ct_i")
    tot_r = s.row("FD合計株数", FMT_CNT,
                  formula=lambda col, t:
                  f"={col}{f_r}+{col}{p_r}+{col}{i_r}",
                  name="ct_tot", bold=True, total=True)
    s.patch("ct_prefd", lambda col, t:
            f"={col_of(1)}{tot_r}" if t == 2 else None)
    fp_r = s.row("創業者持分（%FD）", FMT_PCT,
                 formula=lambda col, t: f"={col}{f_r}/{col}{tot_r}",
                 italic=True, name="ct_fp")
    pp_r = s.row("SOプール比率（%FD）", FMT_PCT,
                 formula=lambda col, t: f"={col}{p_r}/{col}{tot_r}",
                 italic=True, name="ct_pp")
    ip_r = s.row("シリーズA投資家持分（%FD）", FMT_PCT,
                 formula=lambda col, t: f"={col}{i_r}/{col}{tot_r}",
                 italic=True, name="ct_ip")
    sum_r = s.row("持分合計", FMT_PCT,
                  formula=lambda col, t:
                  f"={col}{fp_r}+{col}{pp_r}+{col}{ip_r}",
                  italic=True, total=True)

    s.section("希薄化・整合チェック")
    dil_r = s.row("ラウンド希薄化率（創業者）", FMT_PCT,
                  formula=lambda col, t:
                  f"=1-{A}{fp_r}/{col_of(1)}{fp_r}" if t == 2 else None,
                  italic=True, name="ct_dil",
                  note="目安10-25%（シリーズAは約15-20%が近年水準）")
    s.row("希薄化率帯評価（ラウンド後）", "General",
          formula=lambda col, t:
          (f"=IF(AND({A}{dil_r}>={s.sref('a_ct_dlow')},"
           f"{A}{dil_r}<={s.sref('a_ct_dhigh')}),\"帯内\",\"要確認\")")
          if t == 2 else None,
          note="帯は前提条件の青字入力")
    s.row("創業者持分帯評価（ラウンド後）", "General",
          formula=lambda col, t:
          (f"=IF(AND({A}{fp_r}>={s.sref('a_ct_flow')},"
           f"{A}{fp_r}<={s.sref('a_ct_fhigh')}),\"帯内\",\"要確認\")")
          if t == 2 else None,
          note="シリーズA後60-75%目安（Gazelle Capital等）")
    s.row("SOプール比率帯評価（ラウンド後）", "General",
          formula=lambda col, t:
          (f"=IF(AND({A}{pp_r}>={s.sref('a_ct_plow')},"
           f"{A}{pp_r}<={s.sref('a_ct_phigh')}),\"帯内\",\"要確認\")")
          if t == 2 else None,
          note="10-15%目安（上場審査実務は約10%）")
    s.check("持分合計100%チェック（0=OK）",
            formula=lambda col, t: f"=ABS({col}{sum_r}-1)",
            fmt=FMT_PCT, tolerance=0.0001)
    s.check("調達額タイアウト（対調達額比・0=OK）",
            formula=lambda col, t:
            (f"=({A}{price_r}*{A}{new_r}-{A}{raise_r})/{A}{raise_r}")
            if t == 2 else None,
            fmt=FMT_PCT, tolerance=0.00001, note="1株未満の端数誤差のみ許容")
    s.check("ポスト整合（対ポスト比）",
            formula=lambda col, t:
            (f"=({A}{price_r}*{A}{tot_r}-{A}{post_r})/{A}{post_r}")
            if t == 2 else None,
            fmt=FMT_PCT, tolerance=0.005)

    s.blank()
    s.row("（注記）優先株式条件・転換証券は本表に含まない", "General",
          formula=lambda col, t: None, indent=1,
          note="残余財産優先分配は日本では1x参加型が大勢（1x非参加型が増加）。J-KISS等があれば転換後ベースの参考行を追加")
    s.row("（免責）本シートは指示的シミュレーション", "General",
          formula=lambda col, t: None, indent=1,
          note="株価・株数・優先条件等の最終条件はタームシートおよび投資契約による")
    return s


def build_valuation(wb, reg, cfg):
    """三大手法（DCF／類似上場会社／類似取引）・Exit Value・投資家リターン。"""
    v = cfg["valuation"]
    p = cfg["periods"]
    labels = (["低位", "中位", "高位"] + [""] * max(0, p - 3))[:max(3, p)]
    s = Sheet(wb, reg, "バリュエーション", cfg, header_labels=labels)
    lo, mid, hi = col_of(0), col_of(1), col_of(2)
    fcf = reg.rows["c_fcf"][1]
    last_fy = col_of(p - 1)
    ebitda_ref = f"'損益計画'!{last_fy}{reg.rows['p_ebitda'][1]}"
    rev_ref = f"'売上計画'!{last_fy}{reg.rows['r_total'][1]}"
    cash_end_ref = f"'資金繰り'!{last_fy}{reg.rows['c_end'][1]}"

    def mini_header(hdrs, note=None):
        ws = s.ws
        for j, h in enumerate(hdrs):
            c = ws.cell(row=s.r, column=5 + j, value=h)
            c.font = font(bold=True)
            c.alignment = Alignment(horizontal="right")
            c.border = Border(bottom=THIN)
        for cc in range(2, 5):
            ws.cell(row=s.r, column=cc).border = Border(bottom=THIN)
        if note:
            ws.cell(row=s.r, column=s.note_col, value=note).font = font(
                GRAY, italic=True)
        s.r += 1

    def pv_fcf(r_ref):
        return "+".join(
            f"'資金繰り'!{col_of(t)}{fcf}/(1+{r_ref})^{t + 1}"
            for t in range(p))

    # ---- 手法① DCF：FY展開（中位ケース） ----
    s.section("手法① DCF（FY展開・中位ケース）",
              note="FCFは資金繰りシート参照。期末主義（mid-year conventionは年次モデルでは不採用）")
    mini_header([f"FY{cfg['start_year'] + i}" for i in range(p)])
    fcf_row = s.row("フリーキャッシュフロー", FMT_M,
                    formula=lambda col, t: f"={s.ref('c_fcf', col)}",
                    name="v_fcf")
    disc_row = s.row("割引係数（中位）", FMT_D1,
                     formula=lambda col, t:
                     f"=1/(1+{s.sref('a_v_dr1')})^{t + 1}",
                     italic=True)
    pv_row = s.row("PV（FCF・中位）", FMT_M,
                   formula=lambda col, t:
                   f"={col}{fcf_row}*{col}{disc_row}")
    s.row("ΣPV（FCF・中位）", FMT_M,
          formula=lambda col, t:
          f"=SUM({col_of(0)}{pv_row}:{col_of(p - 1)}{pv_row})" if t == 0
          else None,
          total=True, note="低位・高位は下のレンジ表で割引率を差し替えた同式")

    # ---- 手法① DCF：レンジ ----
    s.section("手法① DCF（レンジ）")
    mini_header(["低位", "中位", "高位"])
    dr = s.row("要求収益率", FMT_PCT,
               formula=lambda col, t:
               f"={s.sref(f'a_v_dr{t}')}" if t < 3 else None,
               italic=True, name="v_dr",
               note="低位=30%（保守）/中位25%/高位20%。ベンチャー段階レート（Damodaran/Pepperdine）")
    em = s.row("EBITDA Exit倍率", FMT_X,
               formula=lambda col, t:
               f"={s.sref(f'a_v_em{t}')}" if t < 3 else None,
               name="v_em", note="TV算定用。SaaS M&A中央値22.1xから保守化（Aventis）")
    tv = s.row("ターミナルバリュー（Exit Multiple法）", FMT_M,
               formula=lambda col, t:
               f"={ebitda_ref}*{col}{em}" if t < 3 else None,
               name="v_tv", note=f"FY{cfg['start_year'] + p - 1} EBITDA×倍率")
    pvtv = s.row("PV（TV）", FMT_M,
                 formula=lambda col, t:
                 f"={col}{tv}/(1+{col}{dr})^{s.sref('a_v_n')}"
                 if t < 3 else None,
                 name="v_pvtv")
    pvf = s.row("ΣPV（FCF）", FMT_M,
                formula=lambda col, t:
                f"={pv_fcf(f'{col}{dr}')}" if t < 3 else None,
                name="v_pvf")
    ev_dcf = s.row("EV（DCF）", FMT_M,
                   formula=lambda col, t:
                   f"={col}{pvtv}+{col}{pvf}" if t < 3 else None,
                   name="v_ev_dcf", bold=True, total=True)
    eq_dcf = s.row("株式価値（DCF）＝EV＋評価時点現預金", FMT_M,
                   formula=lambda col, t:
                   f"={col}{ev_dcf}+{s.sref('a_cash0')}" if t < 3 else None,
                   name="v_eq_dcf", bold=True,
                   note="評価時点＝計画期首・調達前。無借金前提")
    gtv = s.row("（参考）Gordon法TV（中位）", FMT_M,
                formula=lambda col, t:
                f"='資金繰り'!{last_fy}{fcf}*(1+{s.sref('a_v_g')})"
                f"/({mid}{dr}-{s.sref('a_v_g')})" if t == 1 else None,
                italic=True, name="v_gtv",
                note="g=2.5%。Exit倍率TVが大きく出るのが通常（倍率は計画期間後の成長を内包）")
    s.row("（参考）Gordon法との乖離率（中位）", FMT_PCT,
          formula=lambda col, t:
          f"={mid}{gtv}/{mid}{tv}-1" if t == 1 else None,
          italic=True, note="乖離の説明責任: Exit倍率は残存成長期待込み、Gordonは定常成長の下限")

    # ---- 手法② 類似上場会社 ----
    s.section("手法② 類似上場会社（トレーディングマルチプル）",
              note="stockanalysis.com 2026-07-11/12取得。LTMベース")
    mini_header(["EV/売上(LTM)", "売上成長率"])
    comp_rows = []
    for c in v["comps"]:
        r = s.row(c["name"], FMT_X, values=[c["ev_rev"], None],
                  note=c.get("note"))
        cell = s.ws.cell(row=r, column=6, value=c["growth"])
        cell.font = font(BLUE, italic=True)
        cell.number_format = FMT_PCT
        cell.alignment = Alignment(horizontal="right")
        comp_rows.append(r)
    med = s.row("国内コンプ中央値", FMT_X,
                formula=lambda col, t:
                f"=MEDIAN({lo}{comp_rows[0]}:{lo}{comp_rows[-1]})"
                if t == 0 else None,
                bold=True, total=True, name="v_comp_med")
    s.row("第1四分位／第3四分位", FMT_X,
          formula=lambda col, t:
          f"=QUARTILE({lo}{comp_rows[0]}:{lo}{comp_rows[-1]},1)" if t == 0
          else (f"=QUARTILE({lo}{comp_rows[0]}:{lo}{comp_rows[-1]},3)"
                if t == 1 else None),
          italic=True, note="低位＝Q1近傍、高位＝Q3超（AIプレミアム）を適用倍率の目安に")
    s.row("（参考）成長調整倍率（中央値EV/売上÷中央値成長率%）", FMT_D1,
          formula=lambda col, t:
          f"={lo}{med}/(MEDIAN({mid}{comp_rows[0]}:{mid}{comp_rows[-1]})*100)"
          if t == 0 else None,
          italic=True,
          note="成長率当たり倍率。適用倍率の妥当性検証用（高成長ほど高倍率が正当化される）")
    for c in v.get("reference_comps", []):
        r = s.row(f"（参考）{c['name']}", FMT_X, values=[c["ev_rev"], None],
                  note=(c.get("note") or "") + "。中央値算定外")
        cell = s.ws.cell(row=r, column=6, value=c["growth"])
        cell.font = font(BLUE, italic=True)
        cell.number_format = FMT_PCT
        cell.alignment = Alignment(horizontal="right")
    s.blank()
    mini_header(["低位", "中位", "高位"])
    rm = s.row("適用倍率（Exit年売上に適用）", FMT_X,
               formula=lambda col, t:
               f"={s.sref(f'a_v_rm{t}')}" if t < 3 else None,
               name="v_rm",
               note="現在売上への直当ては計画価値を無視するため不可（VC法）")
    exit_comp = s.row("Exit時EV（類似上場）", FMT_M,
                      formula=lambda col, t:
                      f"={rev_ref}*{col}{rm}" if t < 3 else None,
                      name="v_exit_comp", bold=True, total=True)
    pv_comp = s.row("現在価値EV（DLOM調整後）", FMT_M,
                    formula=lambda col, t:
                    f"={col}{exit_comp}/(1+{mid}{dr})^{s.sref('a_v_n')}"
                    f"*(1-{s.sref('a_v_dlom')})" if t < 3 else None,
                    name="v_pv_comp", bold=True,
                    note="Exit時EV÷(1+中位要求収益率)^n×(1−DLOM25%)。実証20-35%（Damodaran/Stout）")

    # ---- 手法③ 類似取引 ----
    s.section("手法③ 類似取引（プリシデント・トランザクション）",
              note="戦略案件は二桁倍率、ディストレスは2x前後に二極化。倍率は保守側に刈り込み")
    mini_header(["EV/売上"])
    txn_rows = []
    for c in v["transactions"]:
        r = s.row(c["name"], FMT_X,
                  values=[c["ev_rev"]] + [None] * (s.p - 1),
                  note=c.get("note"))
        txn_rows.append(r)
    s.row("取引中央値", FMT_X,
          formula=lambda col, t:
          f"=MEDIAN({lo}{txn_rows[0]}:{lo}{txn_rows[-1]})" if t == 0 else None,
          bold=True, total=True)
    s.blank()
    mini_header(["低位", "中位", "高位"])
    tm = s.row("適用倍率（Exit年売上に適用）", FMT_X,
               formula=lambda col, t:
               f"={s.sref(f'a_v_tm{t}')}" if t < 3 else None,
               name="v_tm",
               note="コントロールプレミアム25-30%は取引倍率に内包（上乗せの二重計上禁止）")
    exit_txn = s.row("Exit時EV（類似取引）", FMT_M,
                     formula=lambda col, t:
                     f"={rev_ref}*{col}{tm}" if t < 3 else None,
                     name="v_exit_txn", bold=True, total=True)
    pv_txn = s.row("現在価値EV（割引後）", FMT_M,
                   formula=lambda col, t:
                   f"={col}{exit_txn}/(1+{mid}{dr})^{s.sref('a_v_n')}"
                   if t < 3 else None,
                   name="v_pv_txn", bold=True,
                   note="Exit時EV÷(1+中位要求収益率)^n。取引価格ベースのためDLOM不適用")

    # ---- Exit Value・投資家リターン ----
    s.section("Exit Value・投資家リターン（説明責任）",
              note="将来ラウンドの希薄化は未反映（仮置き）。計画完全達成が前提")
    mini_header(["低位", "中位", "高位"])
    exit_ev = s.row("採用Exit EV", FMT_M,
                    formula=lambda col, t:
                    (f"=MIN({col}{exit_comp},{col}{exit_txn})" if t == 0
                     else (f"=AVERAGE({col}{exit_comp},{col}{exit_txn})"
                           if t == 1
                           else f"=MAX({col}{exit_comp},{col}{exit_txn})"))
                    if t < 3 else None,
                    name="v_exit_ev", bold=True, total=True,
                    note="手法②③のExit時EVから採用。DCFは現在価値手法のため対象外")
    exit_eq = s.row("Exit時株式価値（＋最終年期末現金）", FMT_M,
                    formula=lambda col, t:
                    f"={col}{exit_ev}+{cash_end_ref}" if t < 3 else None,
                    name="v_exit_eq", bold=True)
    fdist = s.row("創業者分配", FMT_M,
                  formula=lambda col, t:
                  f"={col}{exit_eq}*'資本政策'!{col_of(2)}{reg.rows['ct_fp'][1]}"
                  if t < 3 else None,
                  note="資本政策シートの増資後持分を参照")
    idist = s.row("シリーズA投資家分配", FMT_M,
                  formula=lambda col, t:
                  f"={col}{exit_eq}*'資本政策'!{col_of(2)}{reg.rows['ct_ip'][1]}"
                  if t < 3 else None,
                  name="v_idist")
    s.row("SOプール分配", FMT_M,
          formula=lambda col, t:
          f"={col}{exit_eq}*'資本政策'!{col_of(2)}{reg.rows['ct_pp'][1]}"
          if t < 3 else None)
    round0 = cfg["financing"]["rounds"][0]
    moic = s.row("投資家MOIC（直近ラウンド）", FMT_X,
                 formula=lambda col, t:
                 f"={col}{idist}/'資金繰り'!"
                 f"{col_of(round0['year_index'])}{reg.rows['c_raise'][1]}"
                 if t < 3 else None,
                 name="v_moic", bold=True, total=True,
                 note="優先分配・参加権は未考慮（普通株換算）")
    s.row("シリーズA投資家IRR（n年Exit）", FMT_PCT,
          formula=lambda col, t:
          f"=({col}{moic})^(1/{s.sref('a_v_n')})-1" if t < 3 else None,
          italic=True)
    s.row("目標MOIC比較（シリーズA 10x+）", "General",
          formula=lambda col, t:
          f'=IF({col}{moic}>={s.sref("a_v_moic")},"目標超過","要説明")'
          if t < 3 else None,
          note="シリーズA目標10-15x（Kruze）。計画達成時のリターン説明力の検証")
    if "a_case2" in reg.cells and "a_case0" in reg.cells:
        s.row("（参考）DownsideケースMOIC（売上比例縮約）", FMT_X,
              formula=lambda col, t:
              f"={mid}{moic}*{s.sref('a_case2')}/{s.sref('a_case0')}"
              if t == 1 else None,
              italic=True,
              note="ソース記載のDownsideケース売上をExit売上に比例適用した概算。"
                   "確率加重（First Chicago法）は実績データ取得後に導入")

    # ---- フットボールフィールド ----
    s.section("フットボールフィールド（レンジサマリー・現在価値EVベース）")
    mini_header(["低位", "中位", "高位"])
    s.row("手法① DCF（株式価値）", FMT_M,
          formula=lambda col, t: f"={col}{eq_dcf}" if t < 3 else None)
    s.row("手法② 類似上場（DLOM後・現在価値）", FMT_M,
          formula=lambda col, t: f"={col}{pv_comp}" if t < 3 else None)
    s.row("手法③ 類似取引（現在価値）", FMT_M,
          formula=lambda col, t: f"={col}{pv_txn}" if t < 3 else None)
    s.row("（参考）直近調達ポストマネー", FMT_M,
          formula=lambda col, t:
          f"={s.sref('a_ct_post')}" if t == 1 else None,
          italic=True, note="シリーズA調達価格。アーリー段階の価格＝計画達成価値とは乖離するのが通常")
    s.row("採用レンジ", FMT_M,
          formula=lambda col, t:
          f"={s.sref('a_v_adopt_lo')}" if t == 0
          else (f"={s.sref('a_v_adopt_hi')}" if t == 2 else None),
          bold=True, grand=True,
          note="類似上場中位〜DCF中位の重なり帯から設定（青字入力・根拠は前提条件）")

    # ---- 感応度（5×5） ----
    s.ws.row_breaks.append(Break(id=s.r))
    s.section("感応度：株式価値（EBITDA Exit倍率 × 要求収益率）",
              note="中位×中位セルはDCF中位株式価値と一致（式整合の検算行あり）。点列は低位・中位・高位入力からの内挿")
    def five(a, b, c):
        return [a, f"(({a}+{b})/2)", b, f"(({b}+{c})/2)", c]
    r_pts = five(s.sref("a_v_dr0"), s.sref("a_v_dr1"), s.sref("a_v_dr2"))
    m_pts = five(s.sref("a_v_em0"), s.sref("a_v_em1"), s.sref("a_v_em2"))
    mini_header(["割引率:低位", "低中間", "中位", "中高間", "高位"])
    rate_r = s.row("割引率（点列）", FMT_PCT,
                   formula=lambda col, t:
                   f"={r_pts[t]}" if t < 5 else None, italic=True)
    pv_r = s.row("ΣPV（FCF・点列）", FMT_M,
                 formula=lambda col, t:
                 f"={pv_fcf(f'{col}{rate_r}')}" if t < 5 else None,
                 italic=True, note="1行1計算のための分解行。感応度セルはここを参照")
    sens_rows = []
    m_labels = ("低位", "低中間", "中位", "中高間", "高位")
    for i in range(5):
        r = s.row(f"EBITDA倍率：{m_labels[i]}", FMT_M,
                  formula=lambda col, t, i=i:
                  (f"={col}{pv_r}+{m_pts[i]}*{ebitda_ref}"
                   f"/(1+{col}{rate_r})^{s.sref('a_v_n')}"
                   f"+{s.sref('a_cash0')}") if t < 5 else None)
        sens_rows.append(r)
    s.check("感応度整合（中位×中位−DCF中位・0=OK）",
            formula=lambda col, t:
            f"={col_of(2)}{sens_rows[2]}-{mid}{eq_dcf}" if t == 2 else None,
            fmt=FMT_M, tolerance=1000)

    s.blank()
    s.row("（免責）本シートは参考値（indicative）でありフェアネスオピニオンではない",
          "General", formula=lambda col, t: None, indent=1,
          note="ベンチマークは取得日時点の公開情報。前提はすべて仮置きで、前提条件シートの青字を変更すると全値が連動する")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", help="出力xlsxパス（--outdir指定時は不要）")
    ap.add_argument("--outdir", help="出力フォルダー。xlsx・入力YAMLコピーをまとめて出力する")
    ap.add_argument("--name", help="--outdir時のベース名（既定: 入力YAMLのcompany_収支計画）")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if args.outdir:
        os.makedirs(args.outdir, exist_ok=True)
        base = args.name or f"{cfg.get('company', 'model')}_収支計画"
        args.output = os.path.join(args.outdir, f"{base}.xlsx")
        shutil.copyfile(args.input,
                        os.path.join(args.outdir, f"{base}_入力ドライバー.yaml"))
    elif not args.output:
        ap.error("--output か --outdir のいずれかを指定してください")

    wb = Workbook()
    wb.remove(wb.active)
    reg = Registry()

    build_assumptions(wb, reg, cfg)
    build_revenue(wb, reg, cfg)
    build_headcount(wb, reg, cfg)
    build_opex(wb, reg, cfg)
    build_pl(wb, reg, cfg)
    build_cash(wb, reg, cfg)
    build_kpi(wb, reg, cfg)
    if cfg.get("cap_table"):
        build_captable(wb, reg, cfg)
    if cfg.get("valuation") and cfg.get("cap_table"):
        build_valuation(wb, reg, cfg)
    build_summary(wb, reg, cfg)

    order = ["サマリー", "前提条件", "売上計画", "人員計画", "費用計画",
             "損益計画", "資金繰り", "KPI"]
    if cfg.get("cap_table"):
        order.append("資本政策")
    if cfg.get("valuation") and cfg.get("cap_table"):
        order.append("バリュエーション")
    wb._sheets = [wb[name] for name in order]
    for ws in wb.worksheets:
        # 備考列のはみ出しテキスト用に空のバッファ列を1列含めて印刷する
        buf_col = ws.max_column + 1
        ws.column_dimensions[get_column_letter(buf_col)].width = 70
        ws.print_area = f"A1:{get_column_letter(buf_col)}{ws.max_row}"
        ws.print_title_rows = "1:5"
    wb.save(args.output)
    print(f"[ok] generated: {args.output} ({len(wb.sheetnames)} sheets)")


if __name__ == "__main__":
    main()
