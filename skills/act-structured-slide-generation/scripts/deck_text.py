"""Shared text/color primitives for the deck scripts.

ja_len / HW / hw / token_rgb / header_slots は build_deck・validate_spec・lint_render・
contact_sheet で共有する単一実装。複製すると validate⇔build の字数判定や lint の readback
照合が片側の変更で黙って乖離するため、ここ以外に実装を持たないこと。
"""
import json
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

TOKENS_PATH = Path(__file__).resolve().parent.parent / "references" / "tokens.json"


@lru_cache(maxsize=1)
def load_tokens() -> dict:
    """トークンは1回だけ読む。折返しの判定は文字列ごとに走るので、毎回読み直すと
    ビルド時間の2割がJSONの再パースに消える。"""
    return json.loads(TOKENS_PATH.read_text())


# --------------------------------------------------------------------------- テンプレート
# テンプレート(基本デザイン)は tokens.json への「差分」。全スクリプトがこの1か所で実効
# トークンを解決するので、測る物差しと描く物差しがテンプレート間でずれない。
# テンプレートが触れてよいのは design 層(色の役割割り当て・型スケール・余白・カード・グラフ
# 配色)だけで、行ボックス/行間モデル(leading)、光学スタックの較正(optical_stack)、フォント、
# スライド寸法、字数予算、行分割規則(line_break)は不変 — これらは「見えない幾何」であり、
# ここが動くと build と verify が黙って食い違う。standard は完全な無改変(既存デックと同一)。
TEMPLATES_DIR = TOKENS_PATH.parent / "templates"
LOCKED_TOKEN_KEYS = ("leading", "line_break", "fonts", "slide", "text_budget",
                     "header_contract", "color_policy")
LOCKED_LAYOUT_KEYS = ("optical_stack",)
# アクセント系の色は不変。validate は base の accent を「1画面1か所」で数えるので、
# テンプレートが付け替えると検査と描画がずれる(強調はサイズと濃淡で作るのが規律)。
LOCKED_COLOR_ROLES = {"accent", "accent_pale", "accent_line"}
DEFAULT_TEMPLATE = "standard"


def list_templates() -> list[str]:
    """使えるテンプレート名(references/templates/*.json)。パターン登録簿と同じく、
    有効な集合はファイルの存在から導く — 名前を二重管理しない。standard は常に含む。"""
    names = {DEFAULT_TEMPLATE}
    if TEMPLATES_DIR.is_dir():
        names |= {p.stem for p in TEMPLATES_DIR.glob("*.json")}
    return sorted(names)


def _deep_merge(base: dict, patch: dict) -> dict:
    out = dict(base)
    for k, v in patch.items():
        if k.startswith("$"):
            continue                                    # $comment はマージしない
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _assert_template_stays_in_bounds(name: str, patch: dict) -> None:
    """テンプレートが契約の内側にとどまっているか。破れば build と verify の物差しが食い違う。

    2つを弾く: (1)「見えない幾何」(行間・光学較正・フォント・行分割)への差分、(2) 公認
    パレットにない新しい色。色を新設したいときは tokens.colors に一度だけ足す — そうすれば
    色の許可集合が1か所で広がり、validate / verify がテンプレート非依存でいられる。"""
    bad = [k for k in patch if k in LOCKED_TOKEN_KEYS]
    if "layout" in patch:
        bad += [f"layout.{k}" for k in patch["layout"] if k in LOCKED_LAYOUT_KEYS]
    if bad:
        raise ValueError(f"template '{name}' overrides locked keys {bad} — テンプレートは"
                         "色・型スケール・余白・グラフ配色のみを変えられる(行間・光学較正・"
                         "フォント・行分割は不変)")
    palette = set(load_tokens()["colors"].values())
    new_hex = sorted(set(patch.get("colors", {}).values()) - palette)
    if new_hex:
        raise ValueError(f"template '{name}' introduces colors outside the sanctioned palette "
                         f"{new_hex} — 新しい色は references/tokens.json の colors に一度だけ足す"
                         "(そこで許可集合が広がる)")
    # アクセントは1画面1か所の固定アイデンティティ。validate は base の accent を数えるので、
    # テンプレートがここを付け替えると数え間違える — アクセント系の役割は動かさせない。
    protected = LOCKED_COLOR_ROLES & set(patch.get("colors", {}))
    if protected:
        raise ValueError(f"template '{name}' remaps protected colour roles {sorted(protected)} — "
                         "アクセント系は不変(強調はサイズと濃淡で作る)")


@lru_cache(maxsize=None)
def resolve_tokens(template: str | None = None) -> dict:
    """テンプレート名 → 実効トークン。standard(既定)は base をそのまま返す(完全な無改変)。"""
    if template in (None, "", DEFAULT_TEMPLATE):
        return load_tokens()
    patch_path = TEMPLATES_DIR / f"{template}.json"
    if not patch_path.exists():
        raise ValueError(f"unknown template '{template}'. valid: {list_templates()}")
    try:
        patch = json.loads(patch_path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"template '{template}' is not valid JSON ({patch_path.name}): {e}")
    _assert_template_stays_in_bounds(template, patch)
    return _deep_merge(load_tokens(), patch)


def template_of(deck: dict) -> str:
    """デッキが選んだテンプレート。meta.template 未指定なら standard。"""
    return ((deck.get("meta") or {}).get("template") or DEFAULT_TEMPLATE)


def ja_len(s: str) -> float:
    """Approximate display length: full-width chars count 1, half-width 0.55."""
    return sum(1.0 if ord(ch) > 0x2E7F else 0.55 for ch in s or "")


def one_line_chars(width_in: float, size_pt: float) -> float:
    """1行に収まる字数(全角相当) = 描画ボックス幅 ÷ 字送り(pt/72)。

    見出しの字数上限をトークンへ直書きせず、ここで幾何から導出する。型スケールや
    レイアウト幅を変えれば上限も自動で追従し、validate の判定と build の折返し推定が
    同じ式を共有する(片側だけ古い定数を持つ事故が起きない)。"""
    return width_in / (size_pt / 72.0)


def _box_width_in(box: str, tokens: dict) -> float:
    """ヘッダー契約が参照する描画ボックスの実効幅。名前で引ける3種だけを持ち、
    レンダラ(build_deck)と検証(validate_spec)が同じ幅を見るようにする。"""
    lay, slide = tokens["layout"], tokens["slide"]
    if box == "header":
        return lay["header"]["title_w_in"]
    if box == "content":
        return slide["width_in"] - 2 * lay["margin_x_in"]
    if box == "divider":
        d = lay["divider"]
        return d["panel_x_in"] - lay["margin_x_in"] - d["text_gap_in"]
    raise KeyError(f"unknown header box '{box}'")


def header_slots(pattern: str, tokens: dict | None = None) -> list[dict]:
    """パターンのヘッダー契約(見出しスロット)を解決して返す。

    契約は tokens.json の `header_contract` に宣言する。`default` が全パターンに効き、
    描画のしかたが本当に違うパターン(cover / section_divider)だけが上書きする —
    パターンを増やしても既定の契約(タイトル+サブタイトル、各1行)が自動で適用される。

    返す各スロット: {slot, field, type, lines, width_in, size_pt, max_chars}
      field    : deck.json 上のキー名(章扉の副題は 'desc' のように別名になる)
      lines    : そのスロットが占めるべき行数(cover の副題だけ 2)
      max_chars: 1行あたりの上限字数(全角相当) — 幾何から導出した実測容量
    """
    tokens = tokens or load_tokens()
    contract = tokens["header_contract"]
    spec = {**contract["default"], **contract.get(pattern, {})}
    slots = []
    for slot, cfg in spec.items():
        if slot.startswith("$"):
            continue
        width_in = _box_width_in(cfg["box"], tokens)
        size_pt = tokens["type_scale_pt"][cfg["type"]]
        slots.append({
            "slot": slot,
            "field": cfg.get("field", slot),
            "type": cfg["type"],
            "lines": cfg.get("lines", 1),
            "width_in": width_in,
            "size_pt": size_pt,
            # 切り捨て: 端数を許すと「上限ちょうど」の見出しが実描画で折り返しうる
            "max_chars": math.floor(one_line_chars(width_in, size_pt)),
        })
    return slots


def clean_source(src: str) -> str:
    """出典欄には実際に参照した外部出所だけを残す。自社の内部分析を指す「Act分析」単独の
    断片は出典として表示しない(「各社IR資料を基にAct作成」等の実在の作成主体表記は残す)。
    全断片が内部分析なら空文字を返し Source 行ごと省く。"""
    keep = [f.strip() for f in (src or "").split("、") if f.strip() and f.strip() != "Act分析"]
    return "、".join(keep)


def footer_text(spec: dict) -> str:
    """フッターに実際に描かれる1本の文字列。build_deck の描画と validate_spec の字数判定が
    同じ実装を見るための単一実装 — 別々に組むと、区切りや Act分析 の除去の有無で
    「検証は通るのに描画は溢れる(逆もある)」がすぐ起きる。"""
    frags = []
    src = clean_source(spec.get("source", ""))
    if src:
        frags.append("Source: " + src)
    if spec.get("assumption"):
        frags.append("Assumption: " + spec["assumption"])
    if spec.get("note"):
        frags.append("Note: " + spec["note"])
    return "   ".join(frags)      # 断片の「間」だけを3スペースで区切る(末尾には付けない)


# Full-width alnum/% → half-width. Applied to every rendered string so spec
# sloppiness cannot leak mixed-width digits into the deliverable (執筆規律).
HW = {c: c - 0xFEE0 for c in [*range(0xFF10, 0xFF1A), *range(0xFF21, 0xFF3B),
                              *range(0xFF41, 0xFF5B), 0xFF05, 0xFF0D]}


def hw(s):
    return s.translate(HW) if isinstance(s, str) else s


_token_warned = False


def token_rgb(key: str, fallback: tuple) -> tuple:
    """tokens.json の色を (r, g, b) で返す。読めないときは fallback に退避するが、
    黙って退避すると lint の基準色ずれに気づけないため一度だけ警告を出す。"""
    global _token_warned
    try:
        tokens = json.loads((Path(__file__).resolve().parent.parent
                             / "references" / "tokens.json").read_text())
        return tuple(int(tokens["colors"][key][i:i + 2], 16) for i in (0, 2, 4))
    except Exception as e:
        if not _token_warned:
            print(f"WARN: tokens.json unreadable for color '{key}' ({e}); "
                  "falling back to hardcoded colors", file=sys.stderr)
            _token_warned = True
        return fallback


# ---------------------------------------------------------------------------
# 実測(フォントメトリクス)
# ---------------------------------------------------------------------------
# 折返しの判定を「全角相当の字数」で近似すると、欧文まじり(Core / SaaS)や太字で実際の
# 折返しとずれる。ビルドも検証も同じ物差し(Noto Sans JP の実測)で測る。
_FONT_DIRS = [Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path(__file__).resolve().parent]


def _font_file(family: str, weight: int) -> Path | None:
    for base in _FONT_DIRS:
        f = base / f"{family}-{weight}.ttf"
        if f.exists():
            return f
    return None


try:
    from PIL import ImageFont
    _FONT_FILES = {(fam, w): (str(f) if (f := _font_file(fam, w)) else None)
                   for fam in ("NotoSansJP", "Geist") for w in (400, 600, 700)}
    MEASURE_OK = all(_FONT_FILES[("NotoSansJP", w)] for w in (400, 600, 700))
    GEIST_OK = all(_FONT_FILES[("Geist", w)] for w in (400, 600, 700))
except ImportError:
    MEASURE_OK = GEIST_OK = False


@lru_cache(maxsize=None)
def _pil_font(family: str, weight: int, size_px: int):
    return ImageFont.truetype(_FONT_FILES[(family, weight)], size=size_px)


# 走りの切り方は、測るときと描くときで同じでなければ意味がない — build_deck もこれを使う
SCRIPT_RUN = re.compile(r"[\x20-\x7E]+")                              # 欧文・数字の連続区間
EA_DIGIT_RUN = re.compile(r"^[0-9 /:.,()%+\-]*[0-9][0-9 /:.,()%+\-]*$")  # 和文中の数字だけの区間


def text_width_in(text: str, size_pt: float, weight: int = 400) -> float:
    """描画される文字列の幅(in)。描くときと同じフォントで測る — 欧文は Geist、和文は Noto、
    和文中の数字だけの区間は Noto の半角数字(build_deck の _add_script_runs と同じ割り当て)。
    片方のフォントだけで測ると、欧文の多い行で実幅を読み違え、レンダラが先に折り返す。"""
    if not text:
        return 0.0
    if not MEASURE_OK:
        return ja_len(text) * size_pt / 72.0
    w = weight if weight in (400, 600, 700) else 400
    px = int(size_pt * 4)
    s = hw(text)                                   # 描くときと同じ正規化(全角英数は半角へ)
    has_cjk = any(ord(ch) > 0x2E7F for ch in s)
    total, pos = 0.0, 0
    for m in SCRIPT_RUN.finditer(s):
        if m.start() > pos:
            total += _pil_font("NotoSansJP", w, px).getlength(s[pos:m.start()])
        seg = m.group()
        latin_is_ea = has_cjk and EA_DIGIT_RUN.match(seg) is not None
        fam = "NotoSansJP" if (latin_is_ea or not GEIST_OK) else "Geist"
        total += _pil_font(fam, w, px).getlength(seg)
        pos = m.end()
    if pos < len(s):
        total += _pil_font("NotoSansJP", w, px).getlength(s[pos:])
    return total / 4 / 72.0


# ---------------------------------------------------------------------------
# 行間(leading)
# ---------------------------------------------------------------------------
# 行間は級数が決める。同じ級数の文字は、どのスライドのどのカードでも同じ行間で組む
# (tokens.leading が単一ソース)。役割で例外を置きたいときだけ role で上書きする。


def drawn_line_h(size_pt: float, role: str | None = None,
                 line_spacing: float | None = None) -> float:
    """実際に描かれる1行の高さ(in)。

    レンダラはフォント本来の行高(natural_em)より低い行ボックスを作らない。指定した行間が
    それを上回るときだけ行が伸びる(和文の行ボックス補正 cjk_line_box 込み)。塊の高さも、
    段落間の余白も、この「描かれる高さ」から計算する — 公称値で計算すると、行の高い側
    (大きな数字)で余白が食い違う。"""
    tok = load_tokens()["leading"]
    ls = line_spacing if line_spacing else leading(size_pt, role)
    em = max(float(tok.get("natural_em", 1.28)), ls * float(tok.get("cjk_line_box", 1.15)))
    return size_pt / 72.0 * em


def leading(size_pt: float, role: str | None = None) -> float:
    """その級数で組むときの行間(倍率)。"""
    tok = load_tokens()["leading"]
    if role and role in tok["roles"]:
        return float(tok["roles"][role])
    for min_pt, value in tok["by_size"]:
        if size_pt >= min_pt:
            return float(value)
    return 1.28


# ---------------------------------------------------------------------------
# 光学的な積み(インク基準の縦組み)
# ---------------------------------------------------------------------------
# 箱(行ボックス)の間隔で組むと、和文は下のディセンダ余白ぶん、欧文数字は字面が上寄りな
# ぶんだけ、目に見える間隔がずれる。ラベル→数値→注記のような縦積みは「インク(字面)の
# 間隔」で組む。較正値は tokens.layout.optical_stack が単一ソース(300dpi の実測で決めた)。


def ink_kind(text: str) -> str:
    """その文字列を数値として測るか、和文テキストとして測るか。"""
    body = [c for c in (text or "") if not c.isspace()]
    if not body:
        return "text"
    digits = sum(1 for c in body if c.isdigit() or c in ".,%-+")
    return "numeral" if digits / len(body) >= 0.6 else "text"


def ink_center_offset_in(size_pt: float, kind: str = "text") -> float:
    """縦中央寄せした箱の中心から、実際のインク中心までのズレ(in)。"""
    opt = load_tokens()["layout"]["optical_stack"]
    return size_pt / 72.0 * opt["ink_center_offset_em"][kind]


def ink_slacks(size_pt: float, kind: str = "text", line_spacing: float | None = None) -> tuple[float, float]:
    """1行の「行ボックスの上端からインク上端まで」と「インク下端から行ボックス下端まで」(in)。

    段落を積むときの余白(spcAft)は、この2つを差し引いて決める — 行ボックスの隙間ではなく
    インクの隙間が目に見える間隔だから。和文は下にディセンダ余白を持ち、欧文数字は字面が
    上寄りに座る(較正値は tokens.optical_stack)。"""
    opt = load_tokens()["layout"]["optical_stack"]
    line_h = drawn_line_h(size_pt, None, line_spacing)
    ink_h = size_pt / 72.0 * opt["ink_ratio"][kind]
    offset = size_pt / 72.0 * opt["ink_center_offset_em"][kind]
    above = line_h / 2 + offset - ink_h / 2
    below = line_h / 2 - offset - ink_h / 2
    return max(0.0, above), max(0.0, below)


def ink_height_in(size_pt: float, kind: str = "text", lines: int = 1,
                  line_spacing: float = 1.2) -> float:
    """インク(字面)の高さ(in)。折返し行は行送りぶん積み、最後の行だけ字面高で数える。"""
    opt = load_tokens()["layout"]["optical_stack"]
    n = max(1, lines)
    return (n - 1) * size_pt / 72.0 * line_spacing + size_pt / 72.0 * opt["ink_ratio"][kind]


# ---------------------------------------------------------------------------
# 表示テキストの改行(文節で割る)
# ---------------------------------------------------------------------------
# 意味の切れ目と行の切れ目を一致させる:
#   導入費＋/固定利用料      基盤利用量の/複利成長      HCPで/実行文脈へ/変換
#
# 日本語の文節は「自立語(漢字・カタカナ・英数)＋付属語(送り仮名・助詞)」でできている。
# 切ってよいのはその切れ目だけで、送り仮名の途中(問い/合わせ)、数量と単位の間(2030/年)、
# 接尾辞の前(スイート/化)で割ると、行は埋まっても文がほどける。
#
# 方針は3段:
#   1. 文字列を表記の連続(英数・カタカナ・漢字・かな)へ割る
#   2. 境界ごとに「切ってよいか」を採点し、0点の境界は塊へ融合して候補から外す
#      (句読点・並列記号の後 3.0 > 助詞の後 2.0 > 自立語どうしの表記替わり 1.0)
#   3. 行長の揃いと切れ目の良さを総合して最良の分割を選ぶ(DP)
# 禁則(行頭に来てはいけない字・行末に置いてはいけない字)も 2 の採点で 0 点にして守る。

# 行頭禁則: これらで行が始まらない
_NO_LINE_START = "、。，．・：；！？）］｝」』〉》】〕”’ー々ぁぃぅぇぉっゃゅょゎヵヶ%％℃ "
# 行末禁則: これらで行が終わらない
_NO_LINE_END = "（［｛「『〈《【〔“‘￥＄＃"
# 語を閉じる接尾(「1日あたり」「1件ごと」)。ここまでで1語 — 次の語とはくっつけない
_SUFFIX_TAILS = ("あたり", "ごと", "ずつ", "など", "ほど", "くらい", "ぐらい")
# 付属語(助詞)。文節はここで終わる — 直後は切ってよい
_PARTICLES = ("の", "を", "に", "が", "は", "で", "と", "へ", "や", "も", "から", "まで",
              "より", "など", "への", "での", "とは", "には", "では", "からの", "による",
              "における", "としての", "として", "について", "によって", "にとって", "に対して",
              "とともに", "ながら")
# 句読点・並列記号・空白の直後は強い切れ目
_STRONG_AFTER = "、。，．・／/＋+：；)）」』】〕〉》 "


def _char_class(ch: str) -> str:
    o = ord(ch)
    if ch.isascii() and (ch.isalnum() or ch in ".,%$"):
        return "ascii"
    if 0x30A0 <= o <= 0x30FF or ch == "ー":          # カタカナ(長音符含む)
        return "kana_kata"
    if 0x3040 <= o <= 0x309F:                        # ひらがな
        return "kana_hira"
    if 0x4E00 <= o <= 0x9FFF or 0x3005 <= o <= 0x3007:
        return "kanji"
    return "other"


def _break_score(left: str, right: str) -> float:
    """left の直後で改行することの「良さ」。0 は切ってはいけない境界。

    ひらがなが右に来る境界を一律に禁じるのが要点 — 送り仮名(問い/合わせ)も助詞(文脈/へ)も
    前の自立語の一部として扱われ、切れ目は「助詞で終わったあと」にだけ現れる。"""
    if not left or not right:
        return 0.0
    if right[0] in _NO_LINE_START or left[-1] in _NO_LINE_END:
        return 0.0                                   # 禁則
    lc, rc = _char_class(left[-1]), _char_class(right[0])
    if rc == "other":
        return 0.0                                   # 記号(＋ / → 等)を行頭に置かない。切れ目は記号の後ろ
    if left[-1] in _STRONG_AFTER:
        return 3.0                                   # 句読点・並列記号・空白の直後
    if rc == "kana_hira":
        return 0.0                                   # 送り仮名・助詞は前の語から離さない
    if (right[0].isdigit() and lc != "kana_hira") or (left[-1].isdigit() and rc == "kanji"):
        return 0.0                                   # 数量と単位・接頭辞を割らない(2030/年、第/2位)
    if lc == "kana_hira":
        for part in sorted(_PARTICLES, key=len, reverse=True):
            if left.endswith(part):
                return 2.0                           # 助詞の直後 = 文節の切れ目
        return 0.0                                   # 送り仮名の途中
    if rc == "kanji" and len(right) == 1 and lc in ("kana_kata", "ascii"):
        return 0.0                                   # 外来語に付く1字の漢字は接尾辞(スイート/化)
    if lc != rc:
        return 1.0                                   # 自立語どうしの表記替わり(漢字|カタカナ|英字)
    return 0.0                                       # 同じ表記の連続 = 語の途中


def _segments(text: str) -> tuple[list[str], list[float]]:
    """文節相当の塊と、その直後の切れ目の点数を返す。点数 0 の境界は塊へ融合済み。"""
    atoms: list[str] = []
    i = 0
    while i < len(text):
        cls = _char_class(text[i])
        j = i + 1
        if cls in ("ascii", "kana_kata", "kanji", "kana_hira"):
            while j < len(text) and _char_class(text[j]) == cls:
                j += 1
        atoms.append(text[i:j])
        i = j
    if not atoms:
        return [], []
    chunks, scores = [atoms[0]], []
    for a in atoms[1:]:
        sc = _break_score(chunks[-1], a)
        # 大文字で始まる英単語が空白で続く固有名詞(Earned Ownership、City Making Intelligence)は
        # 1塊。ラベルの行がその途中で変わると名前が割れて見える(2026-09-04)
        if sc > 0 and chunks[-1].endswith(" ") and _is_cap_latin(chunks[-1].rstrip().split(" ")[-1]) \
                and _is_cap_latin(a):
            sc = 0.0
        # ハイフンで結ばれた欧文(Off-Market、GPT-4)も1塊 — 「Off- / Market」で行を変えない
        if sc > 0 and chunks[-1].endswith(("-", "‐", "–")) and _char_class(a[0]) == "ascii" \
                and len(chunks[-1]) >= 2 and _char_class(chunks[-1][-2]) == "ascii":
            sc = 0.0
        if sc > 0:
            chunks.append(a)
            scores.append(sc)
        else:
            chunks[-1] += a                          # 切れない境界 = 同じ文節の続き
    scores.append(0.0)                               # 末尾の後ろに切れ目はない
    return chunks, scores


# 文章とラベルでは、改行に求めるものが逆になる。
#   ラベル・見出し・結論句・列挙 : 意味の切れ目と行の切れ目を一致させたい(文節で割る)
#   文章(読点を持つ文)           : 行はできるだけ埋めたい。文節ごとに割ると短い行が階段状に
#                                並び、読み進めるリズムが崩れる — 折返しはレンダラに委ねる
_SENTENCE_MARKS = "、。，．"
# 数値に続く助数詞・単位(語の一部として扱い、数字から引き離さない)
_COUNTERS = "千万億兆円年月日時分秒人件社名倍割点回個台歳週期版号"


def is_prose(text: str) -> bool:
    """その文字列を「文章」として扱うか。文章の改行位置には手を出さない。

    判定は「節でできているか」— 読点・句点は、文が節に分かれている印である。長さでは
    判定しない: スライドの表示テキストは体言止めが原則で、長い名詞句(「電子帳簿保存法と
    インボイス制度への対応を単一のワークフローで完結」)は文ではなくラベルであり、
    レンダラに任せれば「ワークフ/ロー」のように語の途中で割れる。"""
    if not text:
        return False
    return any(ch in text for ch in _SENTENCE_MARKS)


def _words(text: str) -> list[str]:
    """行の途中で割ってはいけない最小単位に割る。

    同じ表記の連なりは1つの語として扱う — 漢字の連なり(予約・接続・承認)、カタカナ語
    (ワークフロー)、欧文語、数値。読みが壊れるのは、この連なりが途中で割れたときで、
    表記の変わり目(漢字→かな、かな→漢字)で行が変わるぶんには読める。
    """
    out: list[str] = []
    i = 0
    while i < len(text):
        cls = _char_class(text[i])
        j = i + 1
        if cls in ("ascii", "kana_kata", "kanji", "kana_hira"):
            while j < len(text) and _char_class(text[j]) == cls:
                j += 1
            if cls == "ascii":                        # 数値に続く単位・助数詞まで含める
                while j < len(text) and text[j] in "%％":
                    j += 1
                # 「13万5,718人」のように、助数詞のあとに数が続くこともある。数と助数詞が
                # 交互に続くかぎり1語として扱う(数を途中で割らない)
                while j < len(text) and (text[j] in _COUNTERS or text[j].isdigit()
                                         or (text[j] == "," and j + 1 < len(text)
                                             and text[j + 1].isdigit())):
                    j += 1
                # 「Operation-centric」「GPT-4」— つなぎ字で結ばれた欧文は1語
                while (j + 1 < len(text) and text[j] in "-‐–/"
                       and _char_class(text[j + 1]) == "ascii"):
                    j += 1
                    while j < len(text) and _char_class(text[j]) == "ascii":
                        j += 1
            if cls in ("ascii", "kana_kata", "kanji"):
                # 続くひらがなは送り仮名・助詞。語から引き離さない(「跨/いで」「文脈/を」)
                while j < len(text) and _char_class(text[j]) == "kana_hira":
                    j += 1
        out.append(text[i:j])
        i = j
    # 次の語に掛かる前置き(「その場」「約1,630人」)は、そこで切ると意味が宙に浮く
    # 連体詞は後ろの名詞に掛かる(「次の/世代」「同じ/場所」で切ると意味が宙に浮く。2026-09-04)
    _DEMONSTRATIVE = ("その", "この", "あの", "どの", "わが", "次の", "同じ", "前の", "翌")
    _APPROX = ("約", "およそ", "最大", "最小", "上限", "下限")
    # 送り仮名で終わる語のあとに自立語が続くのは、複合語の途中(「積み/上げ」「問い/合わせ」)。
    # 助詞で終わっているときだけ、そこが語の切れ目になる
    merged: list[str] = []
    for w in out:
        if merged and _char_class(merged[-1][-1]) == "kana_hira" and _char_class(w[0]) in ("kanji", "kana_kata"):
            tail_closes = any(merged[-1].endswith(p) for p in _PARTICLES + _SUFFIX_TAILS)
            if not tail_closes:
                merged[-1] += w
                continue
        merged.append(w)
    bound: list[str] = []
    for w in merged:
        prev = bound[-1] if bound else ""
        binds = prev.endswith(_DEMONSTRATIVE) or (
            prev.endswith(_APPROX) and w[:1].isdigit())
        if binds:
            bound[-1] += w
        else:
            bound.append(w)
    return bound


def _natural_lines(text: str, cap: float, size_pt: float, weight: int) -> list[str]:
    """レンダラがそのまま折り返したときの行(1文字ずつ詰める。行頭禁則だけ守る)。"""
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if cur and text_width_in(trial, size_pt, weight) > cap and ch not in _NO_LINE_START:
            lines.append(cur)
            cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _wrap_words(text: str) -> list[str]:
    """折り返しの単位。行頭に立てない字は前の語に付けたまま扱う(あとから戻すと行が溢れる)。"""
    words: list[str] = []
    for wd in _words(text):
        if words and wd and wd[0] in _NO_LINE_START:
            words[-1] += wd
        else:
            words.append(wd)
    return words


def wrap_prose(text: str, width_in: float, size_pt: float, weight: int = 400) -> str:
    """文章は行を埋めて流し、語の切れ目でだけ改行する。

    1行に収まる文には手を出さない。はみ出す文は、こちらが行を組む — 語を割らないまま、
    入るところまで詰めた行にする。折返しをレンダラに任せると、字送りのわずかな差で語の
    途中に切れ目が落ちる(「結果まで続/く運用は」)。行が埋まっていることと、語が割れない
    ことは両立する。最終行が極端に短いとき(2字相当)だけ、前の行から1語下ろす。
    行数が増えるのは、その列にコピーが多すぎるということ — verify_deck が名指しする。
    """
    if not text or "\n" in text:
        return text
    cap = max(0.05, width_in - 0.3 * size_pt / 72.0)
    if text_width_in(text, size_pt, weight) <= cap:
        return text

    words = _wrap_words(text)

    def w_of(ln):
        return text_width_in(ln, size_pt, weight)

    lines: list[list[str]] = [[]]
    cur_w = 0.0
    for word in words:
        w = w_of(word)
        if lines[-1] and cur_w + w > cap:
            # 行末が句読点でなく、2語以内に句読点で終わる語があり、そこで切っても行が幅の 75% 以上
            # 残るなら、句読点の直後で切る(「地域と企業、行政と / 住民」のような対の分断を避ける)
            cur = lines[-1]
            if not cur[-1].endswith(tuple(_SENTENCE_MARKS)):
                for back in (1, 2):
                    if len(cur) > back and cur[-1 - back].endswith(tuple(_SENTENCE_MARKS)):
                        kept = cur[:-back]
                        if w_of("".join(kept)) >= cap * 0.75:
                            lines[-1] = kept
                            lines.append(cur[-back:])
                            cur_w = w_of("".join(lines[-1]))
                        break
            if lines[-1] and cur_w + w > cap:
                lines.append([word])
                cur_w = w
            else:
                lines[-1].append(word)
                cur_w += w
        else:
            lines[-1].append(word)
            cur_w += w
    lines = ["".join(ln) for ln in lines if ln]
    if len(lines) < 2:
        return text


    # 最終行が極端に短いとき(2字相当、または幅の15%未満)だけ、前の行から1語下ろす。それ以外は
    # 行を埋めたまま置く — 行長をそろえるための早い改行は入れない(2026-09-04)
    if w_of(lines[-1]) < min(2.0 * size_pt / 72.0, cap * 0.15) and len(lines) >= 2:
        prev = _wrap_words(lines[-2])
        if len(prev) >= 2:
            cand_prev, cand_last = "".join(prev[:-1]), prev[-1] + lines[-1]
            if cand_prev and w_of(cand_last) <= cap and w_of(cand_prev) <= cap:
                lines[-2], lines[-1] = cand_prev, cand_last
    if any(w_of(ln) > cap for ln in lines):
        return text                                   # 1語で溢れる行がある = レンダラに委ねる
    return "\n".join(lines)


_PARTICLE_TAILS = tuple(sorted(_PARTICLES + ("な",), key=len, reverse=True))


def _is_cap_latin(word: str) -> bool:
    return bool(word) and word[0].isupper() and word.isascii() and word.isalpha()


def _break_classes(text: str) -> dict[int, str]:
    """改行を打ってよい位置(text[i] の直前)と、その強さ。

      strong: 句読点の直後(「つながり、|」)、て形の直後(「投じて|実現」)= 節の切れ目
      weak  : 助詞・連体の「の/な」の直後(「自分の|場所」「意思を|重ね」)、動詞が名詞に掛かる境界
              (「支える|人」「実現する|未来予想図」)、漢字・カタカナ・英字の変わり目(「衛星|データ」)、
              英単語のあいだの空白
    それ以外は語の途中(送り仮名、複合語、複合動詞、数量と単位、ハイフンや大文字で結ばれた
    英語の固有名詞「Pre-Market」「Earned Ownership」)で、切ってはいけない。
    本文の折返し(wrap_natural)は強弱を使わず、切ってよい位置の集合としてだけ読む — 本文には
    改行を入れず、語が途切れるときだけ最寄りの境界へ下げる(利用者の指示、2026-09-04)。"""
    out: dict[int, str] = {}
    if not text:
        return out
    runs: list[tuple[int, int]] = []
    i = 0
    while i < len(text):
        j = i + 1
        while j < len(text) and _char_class(text[j]) == _char_class(text[i]):
            j += 1
        runs.append((i, j))
        i = j
    for idx, ((a0, a1), (b0, b1)) in enumerate(zip(runs, runs[1:])):
        left, right = text[a0:a1], text[b0:b1]
        if right[0] in _NO_LINE_START or left[-1] in _NO_LINE_END:
            continue
        lc, rc = _char_class(left[-1]), _char_class(right[0])
        if right[0] in _NO_LINE_END:
            out[b0] = "weak"                             # 開き括弧の手前では切れる(「 が行頭に立つのは自然)
            continue
        if left[-1] in _STRONG_AFTER:
            if left.strip() == "":
                # 英単語のあいだの空白。大文字で始まる語が続く固有名詞(Earned Ownership)は1語
                prev = text[runs[idx - 1][0]:runs[idx - 1][1]] if idx > 0 else ""
                if _is_cap_latin(prev) and _is_cap_latin(right):
                    continue
                out[b0] = "weak"
            else:
                out[b0] = "strong"                       # 句読点・矢印などの記号の直後(「→ |Earned」)
            continue
        if left in ("-", "‐", "–", "/") and idx > 0 and rc == "ascii" \
                and _char_class(text[runs[idx - 1][0]]) == "ascii":
            continue                                     # Pre-Market、GPT-4 は1語
        if rc == "kana_hira":
            continue                                     # 送り仮名・助詞は前の語から離さない
        if lc == "kana_hira":
            if rc not in ("kanji", "kana_kata", "ascii"):
                continue
            if len(left) == 1 and left not in _PARTICLES:
                continue                                 # 「呼び|込む」「取り|組む」複合動詞の途中
            if len(left) >= 2 and left.endswith(("て", "で")) and not left.endswith(_PARTICLE_TAILS):
                out[b0] = "strong"                       # て形の直後 = 節の切れ目(投じて|実現)
            else:
                # 助詞・連体の直後(自分の|場所、意思を|重ね)も、動詞が名詞に掛かる連体修飾
                # (支える|人、実現する|未来予想図)も、切れるが弱い
                out[b0] = "weak"
            continue
        if _break_score(left, right) > 0:
            out[b0] = "weak"                             # 漢字|カタカナ|英字の変わり目
    # ひらがなの連なりの中でも、先頭が助詞ならその直後は切れる(「を|つくる」「に|なった」)。
    # 助詞のあとで行が変わるのは自然折返しとして普通の位置で、語が途切れるわけではない。
    # 最長一致で助詞を決め(「として」を「と|して」にしない)、連なり全体が助詞なら切らない
    for (a0, a1) in runs:
        if _char_class(text[a0]) != "kana_hira" or a0 == 0:
            continue
        run = text[a0:a1]
        for part in sorted(_PARTICLES, key=len, reverse=True):
            if run.startswith(part):
                if len(run) > len(part) and run[len(part)] not in _NO_LINE_START:
                    out[a0 + len(part)] = "weak"
                break
    return out


# 数字に続く複数字の単位(長いものから照合)。1字の助数詞は _COUNTERS
_MULTI_UNITS = tuple(sorted(("百万円", "万時間", "千時間", "カ月", "ヶ月", "か月", "週間", "時間", "万円", "億円", "兆円",
                             "千円", "万人", "億人", "千人", "万件", "千件", "万社", "千社", "万台", "千台",
                             "億円超", "pt", "％", "%"),
                            key=len, reverse=True))


def _unbreakable_spans(text: str) -> list[tuple[int, int]]:
    """レンダラの自然折返しで割れると読みづらい語の範囲 [start, end)。カタカナ語、英単語
    (ハイフンや大文字始まりの空白で結ばれた名前も1語)、数量と単位。漢字・ひらがなの境界は
    含めない — 和文は本来どこでも折り返せるので、そこで手を入れると本文中に改行が増える
    (利用者の指示、2026-09-04: 本文には改行を入れない)。"""
    spans: list[tuple[int, int]] = []
    n = len(text)
    i = 0
    while i < n:
        cls = _char_class(text[i])
        if cls == "kana_kata":
            j = i + 1
            while j < n and _char_class(text[j]) == "kana_kata":
                j += 1
            spans.append((i, j))
            i = j
            continue
        if cls == "ascii":
            j = i + 1
            while j < n:
                if _char_class(text[j]) == "ascii":
                    j += 1
                elif text[j] in "-‐–/" and j + 1 < n and _char_class(text[j + 1]) == "ascii":
                    j += 1                                       # Pre-Market、GPT-4
                elif text[j] == " " and j + 1 < n and _is_cap_latin(text[i:j].split(" ")[-1]) \
                        and text[j + 1].isupper():
                    j += 1                                       # Earned Ownership、City Making
                else:
                    break
            # 数量と単位(2030年、8,420社、14カ月、3週間)。複数字の単位は丸ごと、そのあと1字の助数詞
            if text[i:j].replace(",", "").replace(".", "").isdigit():
                for unit in _MULTI_UNITS:
                    if text.startswith(unit, j):
                        j += len(unit)
                        break
                while j < n and text[j] in _COUNTERS:
                    j += 1
            spans.append((i, j))
            i = j
            continue
        i += 1
    return [(a, b) for a, b in spans if b - a > 1]


def _inside_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(a < pos < b for a, b in spans)


def _safe_breaks(text: str) -> set[int]:
    """改行を打っても語が途切れない位置(強弱を問わない)。verify_deck が「途切れる語」の判定に使う。"""
    return set(_break_classes(text))


def _fill_end(text: str, start: int, cap: float, size_pt: float, weight: int) -> int:
    """start から幅 cap に入るだけ詰めたときの行末(排他的 index)。行頭禁則の字は前の行へぶら下げる。"""
    end = start + 1
    while end < len(text) and text_width_in(text[start:end + 1], size_pt, weight) <= cap:
        end += 1
    # 句読点・閉じ括弧は行頭に立てない。ぶら下げ(幅の外に出す)はレンダラが保証しないので、
    # 入らなければ前の字ごと次の行へ送る — 幅を超える行を渡すと、レンダラが先に折り返して
    # こちらの改行と重なり、空行が1本入る(2026-09-04 に実際に起きた)
    if end < len(text) and text[end] in _NO_LINE_START:
        j = end
        while j < len(text) and text[j] in _NO_LINE_START:
            j += 1
        if text_width_in(text[start:j], size_pt, weight) <= cap + 0.02:
            end = j
        else:
            while end - 1 > start and text[end] in _NO_LINE_START:
                end -= 1
    while end - 1 > start and text[end - 1] in _NO_LINE_END:
        end -= 1                                     # 開き括弧は行末に残さない
    return end


def wrap_natural(text: str, width_in: float, size_pt: float, weight: int = 400) -> str:
    """本文(文章)の折返し。本文には改行を入れない — レンダラの自然折返しに任せる(利用者の指示、
    2026-09-04)。手を入れるのは2つの場合だけ:
      (a) 自然折返しがカタカナ語・英単語・数量と単位の途中(デベロッ/パー、Pre-/Market、8,4/20社)
          に落ちる
      (b) 最終行が1字だけになる
    漢字とひらがなの境界(送り仮名、複合語、助詞)は守らない — 和文はどこでも折り返せる語で、
    そこまで守ると本文中に改行が増える。手を入れるときも、各行は最大限埋め、切れ目は行末に
    いちばん近い合法な位置に置く。ラベル・見出し・矢羽など短い表示テキストは wrap_display が扱う。"""
    if not text or "\n" in text:
        return text
    cap = max(0.05, width_in - 0.3 * size_pt / 72.0)
    if text_width_in(text, size_pt, weight) <= cap:
        return text
    spans = _unbreakable_spans(text)
    n = len(text)
    # 列幅より広いカタカナ語・英単語は、どう組んでも割れる。手を入れず、verify がその語を名指しする
    if any(text_width_in(text[a:b], size_pt, weight) > cap for a, b in spans):
        return text

    def _tail_ok(line: str) -> bool:
        body = line.rstrip("".join(_SENTENCE_MARKS) + "）」』】")
        return len(body) >= 2

    # 1) 自然折返しの点検。レンダラの字送りはこちらの実測と少しずれるので、箱の幅そのもの、
    #    0.3em 狭い幅、0.6em 狭い幅の3通りで折り返してみて、どれでも語が途切れず最終行が
    #    2字以上あるなら手を入れない
    def _natural_ok(width: float) -> bool:
        ends, start = [], 0
        while start < n:
            end = _fill_end(text, start, width, size_pt, weight)
            ends.append(end)
            start = end
        return all(not _inside_span(e, spans) for e in ends[:-1]) \
            and _tail_ok(text[ends[-2] if len(ends) > 1 else 0:])
    em = size_pt / 72.0
    if all(_natural_ok(max(0.05, width_in - k * em)) for k in (0.0, 0.3, 0.6)):
        return text

    # 2) 改行は「語が割れる行末」の手前にだけ打つ。それ以外の行末は打たず、レンダラに折り返させる —
    #    自然折返しの位置を改行として書き込むと、本文中に強制改行が並び、字送りのずれで二重に
    #    折り返す(利用者の指示、2026-09-04)
    safe = _safe_breaks(text)
    breaks: list[int] = []
    start = 0
    while start < n:
        end = _fill_end(text, start, cap, size_pt, weight)
        if end < n and _inside_span(end, spans):
            cands = [p for p in safe if start < p < end and not _inside_span(p, spans)]
            cands += [a for a, b in spans if start < a < end]
            # 行末禁則: 開き括弧の直後では切らない(「\nEarned Ownership」を作らない)
            cands = [p for p in cands if text[p - 1] not in _NO_LINE_END]
            if cands:
                end = max(cands)
                breaks.append(end)
        start = end
    # (b) 最終行が1字なら、その手前の合法な位置に改行を打って語を下ろす
    ends, start = [], 0
    pieces = [text[a:b] for a, b in zip([0] + breaks, breaks + [n])]
    last_start = sum(len(pc) for pc in pieces[:-1])
    tail_ends, st = [], last_start
    while st < n:
        st = _fill_end(text, st, cap, size_pt, weight)
        tail_ends.append(st)
    if len(tail_ends) >= 2 and not _tail_ok(text[tail_ends[-2]:]):
        prev_start = tail_ends[-3] if len(tail_ends) >= 3 else last_start
        # 泣き別れの修復は、守る語の外で禁則に触れない位置ならどこでもよい — 漢字の連なりの途中も
        # 含める(「電子帳簿保存法対」+「応」を「電子帳簿保存法」+「対応」に)。安全な境界だけに
        # 限ると、同じ表記が続く文で候補が空になり、1字の最終行が残る(Codex レビュー指摘、PR #158)
        cands = [p for p in range(prev_start + 1, tail_ends[-2])
                 if not _inside_span(p, spans) and text[p] not in _NO_LINE_START
                 and text[p - 1] not in _NO_LINE_END]
        if cands:
            p_ = max(cands)
            if text_width_in(text[p_:], size_pt, weight) <= cap:
                breaks.append(p_)
    if not breaks:
        return text
    breaks = sorted(set(breaks))
    lines = [text[a:b] for a, b in zip([0] + breaks, breaks + [n])]
    natural_n = 0
    st = 0
    while st < n:
        natural_n += 1
        st = _fill_end(text, st, cap, size_pt, weight)
    drawn = sum(max(1, len(_natural_lines(ln, cap, size_pt, weight))) for ln in lines)
    if drawn > natural_n + 1:
        return text                                          # 語を守ると2行以上増える = コピーが長すぎる
    return "\n".join(ln for ln in lines if ln)


def wrap_display(text: str, width_in: float, size_pt: float, max_lines: int = 3,
                 weight: int = 400, *, force: bool = False) -> str:
    """短い表示テキスト(ラベル・見出し・矢羽・結論句)を文節の切れ目で折り返した文字列("\n" 入り)に
    して返す。本文(文章)は wrap_natural が扱う。

    1行に収まるならそのまま返す。max_lines に収まらない長文にも手を出さない(本文は無理に
    改行を打つより自然折返しに任せたほうが崩れない)。幅はすべて実測(in)で扱う。
    """
    # force: 呼び出し側が役割を「ラベル」と明示したとき(結論帯・矢羽・見出し)は、句読点を含んでいても
    # 文節で組む。推定だけに頼ると「Off-Marketを探さず、生み出す」が本文扱いになり、
    # レンダラが「生み / 出す」で割る(PR #158 で実際に起きた)
    if not text or "\n" in text or (is_prose(text) and not force):
        return text
    # 行はレンダラの折返し閾値の手前で切る。閾値ぎりぎりの行を作ると、レンダラ側が先に
    # 折り返し、こちらのソフト改行がそこへ重なって「空行」が1本入る(実測とレンダラの
    # 字送りは完全には一致しない)。0.3em の余裕でその競合を避ける
    cap = max(0.05, width_in - 0.3 * size_pt / 72.0)
    if text_width_in(text, size_pt, weight) <= cap:
        return text
    chunks, scores = _segments(text)
    widths = [text_width_in(c, size_pt, weight) for c in chunks]
    # 大文字始まりの英単語を結んだ塊(Earned Ownership Program)が列幅より広いときは、空白で
    # 結び直しを解く — 結んだまま「入らない」と諦めると、wrap=False の矢羽では文字が枠の外へ出る
    if any(w > cap and " " in c.strip() for c, w in zip(chunks, widths)):
        re_chunks, re_scores = [], []
        for c, w, sc in zip(chunks, widths, scores):
            if w > cap and " " in c.strip():
                parts = [pt + " " for pt in c.split(" ") if pt]
                parts[-1] = parts[-1].rstrip(" ") if not c.endswith(" ") else parts[-1]
                re_chunks.extend(parts)
                re_scores.extend([3.0] * (len(parts) - 1) + [sc])
            else:
                re_chunks.append(c)
                re_scores.append(sc)
        chunks, scores = re_chunks, re_scores
        widths = [text_width_in(c, size_pt, weight) for c in chunks]
    if any(w > cap for w in widths):
        # 1行に入らない語がある = その列幅にはコピーが長すぎる。ここでソフト改行を打っては
        # いけない: はみ出した行はレンダラ側が先に折り返す(句読点はぶら下がる)ので、こちらの
        # 改行がその後ろへ重なり、空行が1本入る。丸ごと自然折返しへ委ね、verify が警告する
        return text
    n = len(chunks)
    if n < 2:
        return text

    # ラベル・見出し・矢羽・結論句は、意味の切れ目で行を変え、行長をそろえる(2026-09-04、
    # 利用者の指示: 矢羽ラベルや見出しはしっかり改行してよい。本文は wrap_natural で入れすぎない)
    INF = float("inf")
    dp = [[INF] * (max_lines + 1) for _ in range(n + 1)]     # dp[i][k]: 塊 i 以降を k 行で組む最小コスト
    nxt = [[0] * (max_lines + 1) for _ in range(n + 1)]
    for k in range(max_lines + 1):
        dp[n][k] = 0.0
    for i in range(n - 1, -1, -1):
        for k in range(1, max_lines + 1):
            w = 0.0
            for j in range(i, n):
                w += widths[j]
                if w > cap and j > i:                        # この行に入りきらない
                    break
                slack = cap - w
                # 行長の不揃いを罰する。最終行の余りは自然なので咎めないが、最終行が極端に
                # 短い「泣き別れ」(…物理ツールへ / 接続)は読みを損ねるので、そこだけ罰する
                if j == n - 1:
                    cost = (cap * 0.35 - w) ** 2 if w < cap * 0.35 else 0.0
                else:
                    cost = slack * slack
                if j < n - 1:
                    cost += (3.0 - scores[j]) * cap * 0.6    # 切れ目の悪さ
                rest = dp[j + 1][k - 1]
                if rest == INF:
                    continue
                if cost + rest < dp[i][k]:
                    dp[i][k] = cost + rest
                    nxt[i][k] = j + 1
    feasible = [k for k in range(1, max_lines + 1) if dp[0][k] < INF]
    if not feasible:
        return text                                          # max_lines に収まらない = 長文。触らない
    best_k = min(feasible, key=lambda k: dp[0][k])
    lines, i, k = [], 0, best_k
    while i < n and k > 0:
        j = nxt[i][k]
        lines.append("".join(chunks[i:j]))
        i, k = j, k - 1
    return "\n".join(lines) if i >= n else text


# ---------------------------------------------------------------------------
# トークスクリプトの読み上げ(TTS)
# ---------------------------------------------------------------------------
# スライドは目で読むので記号のままでよい。speaker_notes は声で読むので、記号のままだと
# 読み飛ばされるか英語で綴られる。開くのは「声が詰まるところ」だけ — すべてをカタカナに
# すると、こんどは人(発表者)が自分のメモを読めなくなる。読み方の表は
# references/tts_readings.json、選び方の理屈は talk-script-and-tts.md。

TTS_PATH = Path(__file__).resolve().parent.parent / "references" / "tts_readings.json"


@lru_cache(maxsize=1)
def load_tts_readings() -> dict:
    return json.loads(TTS_PATH.read_text())


def tts_risks(text: str) -> list[tuple[str, str]]:
    """読み上げに耐えない断片と、その読み方の提案を返す [(断片, 提案), ...]。

    提案であって置換ではない — 「×」は式では「かける」、倍率では「倍」であり、
    正しい読みは文が決める。判断は書き手に残す(検証は警告どまり)。"""
    if not text:
        return []
    table = load_tts_readings()
    found: list[tuple[str, str]] = []
    for sym in table["symbols"]:
        if sym["pattern"] in text:
            readings = [r for r in sym["readings"] if r]
            hint = "／".join(readings) if readings else "文を切るか接続詞に置き換える"
            found.append((sym["pattern"], hint))
    for pat in table["patterns"]:
        for m in re.finditer(pat["regex"], text):
            guard = pat.get("guard")
            if guard == "fraction" and not _looks_like_fraction(m):
                continue                             # 「9/1」は日付、「2025/26」は年度 — 分数ではない
            if guard == "date" and not _looks_like_date(m):
                continue
            hint, label = pat["hint"], pat.get("label", "{0}")
            for i, g in enumerate((m.group(0),) + m.groups()):
                hint = hint.replace("{%d}" % i, g or "")
                label = label.replace("{%d}" % i, g or "")
            found.append((label, hint))
            break
    seen, out = set(), []
    for frag, hint in found:
        if frag not in seen:
            seen.add(frag)
            out.append((frag, hint))
    return out


def _looks_like_fraction(m) -> bool:
    """「1/3」は分数、「9/1」は日付、「2025/26」は年度。分子<分母、分母12以下のときだけ分数。"""
    try:
        num, den = int(m.group(1)), int(m.group(2))
    except (TypeError, ValueError):
        return False
    return num < den <= 12


def _looks_like_date(m) -> bool:
    """月/日として読める組(1-12 / 1-31)で、分数として読めないもの。"""
    try:
        month, day = int(m.group(1)), int(m.group(2))
    except (TypeError, ValueError):
        return False
    return 1 <= month <= 12 and 1 <= day <= 31 and not _looks_like_fraction(m)
