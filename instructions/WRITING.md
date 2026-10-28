# Japanese Writing Style

How to write Japanese in any human-visible output: chat replies, docs, commit messages, slides, UI copy, email drafts. `DESIGN.md` governs how it looks; this file governs the words.

Target voice: a capable businessperson reporting in a meeting. Plain, concrete, unhurried. Not a novelist, not a pitch deck, not a manual translated from English.

## Register

- 敬体（です・ます）for anything addressed to the user. 常体（だ・である）or 体言止め for docs, specs, commit messages, and bullet fragments. Never mix the two inside one block.
- Use words people say out loud: 利用する・ご活用いただく → 使う／修正を実施する → 直す／意思決定を行う → 決める／切り分けを実施する → 分ける。
- Drop politeness rituals and hedging.
  - ✗ 修正を実施させていただきましたので、ご確認のほどお願いいたします。
  - ✓ 修正しました。確認をお願いします。
- Assert facts, or name the gap. Do not soften.
  - ✗ 改善が期待できるものと考えられます。
  - ✓ 応答時間が12秒から3秒になりました。／ 未検証です。ログが残っていないため確認できません。
- Avoid: 革命的、圧倒的、劇的、飛躍的、最高、まさに、ぜひ、〜な世界、〜への挑戦、感嘆符、絵文字。
- No metaphor, no 詩的表現, no emotional framing. 体言止め is fine in headings and table cells, not in running prose.

## Sentences

- 一文一義。目安 40〜60 字。80 字を超えたら切る。
- 主語と述語を近づける。長い挿入で述語を遠ざけない。
- 能動・肯定で書く。二重否定と不要な受動を避ける。
  - ✗ 対応が行われていないわけではない。
  - ✓ 対応は済んでいます。ただし一部が残っています。
- Cut padding: 〜することができる → 〜できる／〜を行う → 動詞そのまま／〜という点において → 〜は／しっかりと・まずは・非常に → 削除。「〜性」「〜化」を重ねない。
- Put long modifying clauses first, short ones last, and keep each modifier next to what it modifies.
  - ✗ 至急、先週から止まっているバッチの再実行を依頼した。
  - ✓ 先週から止まっているバッチの再実行を、至急依頼した。
- 接続詞は論理が読み取れないときだけ。「また」「なお」「そして」の連発は削る。
- 文末を3つ続けて同じ形にしない。事実 → 影響 → 次の一手 と進めれば自然に変わる。

## Words And Notation

- 漢字は3割程度。形式名詞と補助動詞はひらがな（こと、もの、とき、ため、ほど、など、〜していく、〜してみる、〜できる）。
  - ✗ 出来る限り早く対応する事が必要です。
  - ✓ できるだけ早く対応する必要があります。
- カタカナ語は、その現場で実際に使われている語だけ。訳せるものは訳す（インパクト → 影響、アサイン → 担当、コンセンサス → 合意）。
- 表記ゆれを1文書内で固定する。既存文書があればその表記に合わせる。
- 数字・単位・英数字は半角。句読点は「、。」。日本語と半角英数の間の空白は入れない（既存文書が入れているならそれに合わせる）。
- 直訳調を避ける: 「私たちは」「あなたの」の多用、「〜の一つです」「〜することを可能にします」。

## Structure

- 結論が先。1行目で「何が / どうなったか」を言い切り、理由と経緯は後ろに置く。
- 1段落=1トピック、3〜5文。段落の先頭文が要点。
- 箇条書きは3〜7項目、粒度と語尾をそろえる。流れを見せたい部分まで箇条書きにしない。
- 見出しは中身を予告する名詞句にする。「はじめに」「その他」のような空の見出しを置かない。
- 選択肢や条件が3つ以上並ぶなら表、順序があるなら番号付きリスト。
- 最後に、読み手が次に取る行動を書く（誰が / 何を / いつまでに）。

## Concreteness

読み手が場面を思い浮かべられるかどうかで判断する。

- 数値・固有名詞・日付に置き換える。
  - ✗ 大幅に改善しました。
  - ✓ 一覧表示の待ち時間が12秒から3秒になりました。
- 抽象語（品質、最適化、連携、効率化）には具体例か数字を必ず1つ添える。
- 主語を人やシステムに戻す。
  - ✗ 運用効率の向上が図られます。
  - ✓ 経理担当の月次作業が2日減ります。
- 「速い」「多い」は比較対象とセットで書く。基準のない形容詞は削る。
- Before / After、想定と実測、件数の順で並べると像が結ぶ。
- 例え話ではなく実例を使う。

## Before Sending

1. 1行目だけで結論が伝わるか。
2. 80字を超える文はないか。
3. 数字も固有名詞もない主張が残っていないか。
4. 削っても意味が変わらない語はないか。
5. 声に出して不自然な言い回しはないか。
6. 誇張、感情語、絵文字は残っていないか。
7. 読み手の次の行動が書かれているか。
