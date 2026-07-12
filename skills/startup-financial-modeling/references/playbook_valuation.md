# シート構築プレイブック⑥：バリュエーション（三大手法・Exit Value・説明責任）

対象: 収支計画ワークブック内の「バリュエーション」シート。三大手法（DCF／類似上場
会社／類似取引）をレンジで算出し、Exit Valueと投資家リターンの説明責任を持たせる。
出典はWeb調査（2026-07）。全青字入力に出典＋取得日を付ける。

## 列構成
- FYルーラーは使わない。資本政策と同じイベント列型で **低位/中位/高位の3列** を基本とし、末尾に出典・注記列。
- 例外はDCFのFCF展開のみ: FY5列のサブブロックを1か所置き、全セル `=資金繰り!` 参照（再入力禁止）。低位/中位/高位はFCFでなく割引率・倍率の入力で分岐（シナリオ別FCFを作らず二重管理を防ぐ。First Chicago型確率加重は注記言及に留める — WSP: https://www.wallstreetprep.com/knowledge/first-chicago-method/）。

## 手法① DCF
1. FCFサブブロック: FCF（資金繰り参照）、割引係数 =1/(1+割引率_中位)^t（期末主義。mid-yearは年次モデルでは採らない旨注記）、PV、ΣPV。
2. 割引率（青字3点）: 低30%/中25%/高20%。ベンチャー段階の要求収益率はシード50-60%→レイター25-30%（Equidam: https://www.equidam.com/the-discount-rate-in-the-valuation-of-a-startup/, KNAV）。WACC 8-12%は段階不適合。
3. TV（Exit Multiple法）: 最終年EBITDA×EBITDA倍率（青字 低8x/中12x/高16x。SaaS M&A中央値22.1xから市況不確実性を保守化 — Aventis: https://aventis-advisors.com/saas-valuation-multiples/）。PV(TV)=TV/(1+r)^n。
4. Gordonクロスチェック行: TV_G=FCF×(1+g)/(r−g)、g=2.5%（1.5-3.0%レンジ — WSP: https://www.wallstreetprep.com/knowledge/terminal-value/）。乖離率行を表示。
5. EV=ΣPV(FCF)+PV(TV)、株式価値=EV＋現預金−有利子負債（資金繰り参照）。

## 手法② 類似上場会社
1. コンプ表（6-8社、青字＋出典列）: 社名/EV/売上/EV÷売上(数式)/成長率/出典/取得日。国内SaaS・AI＋海外AI 2-3社。
2. 統計行: MEDIAN/QUARTILE。成長調整（EV/Rev÷成長率）を参考表示。
3. 適用: **Exit年売上に倍率適用→Exit時EV→要求収益率で現在に割引**（VC法の骨格 — Equidam: https://www.equidam.com/vc-method-startup-valuation/）。現在売上への直当ては計画価値を無視する誤り。
4. 非流動性ディスカウント（青字）: 25%（DLOM実証20-35% — Stout: https://www.stout.com/en/insights/article/sj17-dloms-common-valuation-approaches-to-the-illiquidity-discount）。
5. 現在EV = Exit売上×倍率÷(1+r)^n×(1−DLOM)。

## 手法③ 類似取引
1. 取引表（4-6件、青字＋出典列）。非公開SaaS M&A中央値 EV/売上3.8x（2025）、長期中央値~4.7x、上位四分位8x超（Aventis / SEG: https://softwareequity.com/research/annual-saas-report）。
2. コントロールプレミアム25-30%は取引倍率に内包（WSP: https://www.wallstreetprep.com/knowledge/control-premium/）— 上乗せの二重計上禁止を注記。
3. Exit時EV=Exit年売上×倍率、現在価値=÷(1+r)^n（DLOMは適用しない旨注記）。

## Exit Value・投資家リターン（説明責任）
1. 採用Exit EVレンジ: 低=MIN(手法②③低位)/高=MAX(同高位)/中=AVERAGE(同中位)。DCFは現在価値手法のためExit値に含めない旨注記。
2. Exit時株式価値=Exit EV＋最終年期末現金−有利子負債。
3. 持分別分配: 資本政策シートの持分%への数式リンク（創業者/投資家/プール）。将来ラウンド希薄化未反映を明記。
4. 投資家リターン: MOIC=分配÷調達額、IRR=MOIC^(1/n)−1。
5. サニティ: シリーズA目標10-15x、レイター3-5x（Kruze: https://kruzeconsulting.com/blog/what-vcs-return-expectations/）。IF式で判定。

## フットボールフィールド（レンジサマリー）
- 表形式（xlsxではチャートより堅牢）。行=DCF/類似上場（DLOM後現在価値）/類似取引（現在価値）/参考:直近調達ポスト、列=低位/中位/高位（全てセル参照）。
- 最下行「採用レンジ」: 手法間の重なり帯から選定（青字＋選定根拠の文章）。WSP実例準拠: https://www.wallstreetprep.com/knowledge/football-field-valuation-real-example-excel-template/

## 感応度（2-way）
- 株式価値: EBITDA Exit倍率5点×割引率5点。各セルは完全な明示的数式（データテーブル機能はopenpyxl非互換のため禁止）。中位セルを枠線強調し、DCF本体の中位株式価値と一致することを検算。

## チェック・注記
- FCFタイアウト、持分リンク整合、Gordon乖離チェック（Exit倍率TV>Gordonが通常。乖離の説明を注記）。
- 免責:「本シートは参考値（indicative）でありフェアネスオピニオンではない。ベンチマークは取得日時点の公開情報」。全前提に仮置きタグ。

## 品質チェックリスト
1. 3手法すべて低位/中位/高位のレンジ（単一ポイント提示なし）
2. 全ベンチマークに出典名＋URL＋取得日
3. 事業数値（FCF・EBITDA・売上・現金・持分）はすべてセル参照でベタ打ちゼロ
4. TVはExit Multiple＋Gordonの両建てで乖離チェック付き
5. 上場コンプにDLOM適用、取引倍率にはプレミアム二重計上なしの注記
6. フットボールフィールドに「参考:直近調達ポスト」行と採用レンジの文章根拠
7. 感応度の中位セル＝DCF本体の中位株式価値（式整合の検算）
8. 投資家MOIC/IRRがVC目標バンドと比較され、未達なら説明注記

## よくある失敗
現在売上への倍率直当て（過小）／Exit値を割引かず現在価値と称する（過大）／WACC使用による過大評価／DLOM無適用／コントロールプレミアム二重計上／データテーブル使用で再計算不能／恣意的コンプ選定／希薄化前提の不開示
