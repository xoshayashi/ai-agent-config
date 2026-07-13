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


def _font_file(weight: int) -> Path | None:
    for d in _FONT_DIRS:
        f = d / f"NotoSansJP-{weight}.ttf"
        if f.exists():
            return f
    return None


try:
    from PIL import ImageFont
    _FONT_FILES = {w: (str(f) if (f := _font_file(w)) else None) for w in (400, 600, 700)}
    MEASURE_OK = all(_FONT_FILES.values())
except ImportError:
    MEASURE_OK = False


@lru_cache(maxsize=None)
def _pil_font(weight: int, size_px: int):
    return ImageFont.truetype(_FONT_FILES[weight], size=size_px)


def text_width_in(text: str, size_pt: float, weight: int = 400) -> float:
    """描画される文字列の幅(in)。フォントが無い環境では ja_len 近似へ落ちる。"""
    if not text:
        return 0.0
    if not MEASURE_OK:
        return ja_len(text) * size_pt / 72.0
    w = weight if weight in (400, 600, 700) else 400
    return _pil_font(w, int(size_pt * 4)).getlength(text) / 4 / 72.0


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
# 付属語(助詞)。文節はここで終わる — 直後は切ってよい
_PARTICLES = ("の", "を", "に", "が", "は", "で", "と", "へ", "や", "も", "から", "まで",
              "より", "など", "への", "での", "とは", "には", "では", "からの", "による",
              "における", "としての")
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


def is_prose(text: str) -> bool:
    """その文字列を「文章」として扱うか。文章の改行位置には手を出さない。

    判定は「節でできているか」— 読点・句点は、文が節に分かれている印である。長さでは
    判定しない: スライドの表示テキストは体言止めが原則で、長い名詞句(「電子帳簿保存法と
    インボイス制度への対応を単一のワークフローで完結」)は文ではなくラベルであり、
    レンダラに任せれば「ワークフ/ロー」のように語の途中で割れる。"""
    if not text:
        return False
    return any(ch in text for ch in _SENTENCE_MARKS)


def wrap_display(text: str, width_in: float, size_pt: float, max_lines: int = 3,
                 weight: int = 400) -> str:
    """表示テキストを文節の切れ目で折り返した文字列("\n" 入り)にして返す。

    1行に収まるならそのまま返す。max_lines に収まらない長文にも手を出さない(本文は無理に
    改行を打つより自然折返しに任せたほうが崩れない)。幅はすべて実測(in)で扱う。
    """
    if not text or "\n" in text or is_prose(text):
        return text
    # 行はレンダラの折返し閾値の手前で切る。閾値ぎりぎりの行を作ると、レンダラ側が先に
    # 折り返し、こちらのソフト改行がそこへ重なって「空行」が1本入る(実測とレンダラの
    # 字送りは完全には一致しない)。0.3em の余裕でその競合を避ける
    cap = max(0.05, width_in - 0.3 * size_pt / 72.0)
    if text_width_in(text, size_pt, weight) <= cap:
        return text
    chunks, scores = _segments(text)
    widths = [text_width_in(c, size_pt, weight) for c in chunks]
    if any(w > cap for w in widths):
        # 1行に入らない語がある = その列幅にはコピーが長すぎる。ここでソフト改行を打っては
        # いけない: はみ出した行はレンダラ側が先に折り返す(句読点はぶら下がる)ので、こちらの
        # 改行がその後ろへ重なり、空行が1本入る。丸ごと自然折返しへ委ね、verify が警告する
        return text
    n = len(chunks)
    if n < 2:
        return text

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
