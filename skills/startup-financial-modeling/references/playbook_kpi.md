# シート構築プレイブック⑤：KPI（ベンチマーク比較・評価）

対象: 年次5カ年収支計画のKPIシート。全KPIは既存シートのセル参照のみで算出し、
手入力ゼロ。評価しきい値は前提条件シートの青字入力（出典メモ付き）。
出典はWeb調査（2026-07）。

## ベンチマーク帯（出典付き）

### 成長性
- **ARR成長率**: T2D3＝約$1-2M ARRから3x→3x→2x→2x→2x（Battery Ventures: https://www.battery.com/blog/a-mantra-for-saas-success-triple-triple-double-double-double/）。実績中央値: $1-5M ARRで40%、$5-20Mで30%、AI-nativeは$1-5Mで110%（SaaS Capital: https://www.saas-capital.com/research/private-saas-company-growth-rate-benchmarks/）。
- 成長比較は**ARR（継続課金）ベース**で行い、導入フィー込み総売上と混同しない。

### 収益性
- **売上総利益率**: サブスクGM中央値~79%、サービス込み総GM 71-75%（KeyBanc/Sapphire 2024）。AI-native初期は40-60%台（ICONIQ系: https://www.getmonetizely.com/blogs/the-economics-of-ai-first-b2b-saas-in-2026）。しきい値目安: 良好70%/水準内60%。
- **EBITDAマージン**: VC-backedは初期赤字が標準。成熟期15-25%が良好水準（Founderpath: https://founderpath.com/blog/ebitda-margin）。FY3-4黒字転換・最終年2桁%が説明しやすい軌道。
- **Rule of 40**（成長率+EBITDAマージン）: $25M+ ARRまでは本来機能しない。$1-5M ARR以降で参考表示、それ以前は「参考値」注記（BVP Rule of X: https://www.bvp.com/atlas/the-rule-of-x）。
- **サービス（導入）売上比率**: 健全域10-15%未満、20%が上限、低下トレンド必須（SaaStr: https://www.saastr.com/how-much-should-a-saas-company-invest-in-professional-services/）。

### 効率性
- **Magic Number**＝当年純増ARR÷**前年**S&M費。>0.75で投資拡大に値する、>1.0でexcellent（Scale VP: https://www.scalevp.com/insights/a-primer-on-saas-sales-efficiency/）。年次グレインは採用ランプを平滑化し実力より良く見える点、解約データなしなら「グロス≒ネット近似」である旨を備考に明記。FY1は前年S&Mがなく「—」。
- **1人あたり売上**: 私企業中央値$129.7K、$20-50Mで$182K（SaaS Capital: https://www.saas-capital.com/blog-posts/revenue-per-employee-benchmarks-for-private-saas-companies/）。円換算目安（150円/$）: 中央値~1,900万円、スケール期2,700万円+。
- **S&M/R&D/G&A対売上**: 私企業中央値 S&M37%/R&D34%/G&A24%、規模とともに低下（SaaS Capital: https://www.saas-capital.com/blog-posts/spending-benchmarks-for-private-b2b-saas-companies/）。**低すぎも要説明**（成長率と整合しないS&M過小は信頼性を毀損）。

### 資金効率
- **Burn Multiple**＝Net Burn÷純増ARR（バーン年のみ）: <1x amazing / 1-1.5x great / 1.5-2x good / 2-3x suspect / >3x bad（David Sacks: https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200）。ZIRP期基準であり現環境は2x超で調達困難の注記（Wall Street Prep）。
- **Runway**: 調達直後18-24カ月が標準。全期間の現金非負を別行チェック。

## レイアウト
- 期間列の後ろに「ベンチマーク」（短文テキスト・グレー斜体）と「評価」（数式）の2列を置き、末尾に備考。
- セクション: 成長性／収益性／効率性／資金効率。
- 評価は3段階（良好/水準内/要説明）のIF式。しきい値は前提条件の青字セル参照でハードコード禁止。
- 条件付き書式は「要説明」のみ赤字。Rule of 40はARR規模未達の年を参考値注記。

## 獲得効率・シナリオ感応度ブロック
- **（参考）獲得単価（CAC）** ＝ S&M計÷新規獲得数。コホート仮定に依存しない獲得効率の開示。LTV逆算は行わない方針とセットで注記する
- **シナリオ感応度（最終年EBITDA）**: 感応度が最大の2ドライバー（通常は数量×単価）を軸に選び、3×3を線形分解数式で算出（売上・変動費はスケール連動、人員・固定費は据置の概算と注記）。Base×BaseセルがPLのEBITDAと一致する検算チェック行を必ず置く。スケール点は前提条件の青字入力
- **感応度設計の規律**: 軸はドライバーツリー上で影響が最大のものから選ぶ。ケース数を増やすより検算可能性を優先する（9ケース超の組合せ表は精度の幻想になりやすい）。1つのドライバーを固定して他を振る2次元マトリクスは、固定した前提を必ず注記する

## 算出しないKPIと実績接続後の深掘りパス
**LTV/CAC・CAC Payback・NRR・ロゴ継続率は、コホート実績がない段階では行を作らない。** 実績なしの逆算値は精度を装った創作になる。末尾に注記:「リテンション系KPIは実績コホートデータ整備後に管理（本計画では純増ARRベースの効率指標で代替）」。

実績データが接続できる段階に達したら、次の順で深掘りブロックを追加する:
1. コホート別GRR/NRR（最低4四半期の実績から）→ NRR行と評価をKPIに昇格
2. LTV/CAC・CAC Payback（実測チャーンと配賦済みS&Mから）→ 判定帯はLTV/CAC≥3x・Payback<18ヶ月
3. ARRブリッジ（期首＋新規＋拡張−縮小−解約＝期末）をサマリーへ
4. 月次モデル（直近24ヶ月）とGTMファネル連動の獲得原価モデル

## 品質チェックリスト
1. KPIシートに手入力数値ゼロ（しきい値含め全参照）
2. しきい値は青字入力＋出典メモ、評価式はしきい値セル参照
3. 分母ゼロ・負値ガード済み（#DIV/0!なし、黒字年のBurn Multipleは「—」）
4. Magic Numberが**前年**S&M参照（同年参照は誤り）、FY1は「—」
5. 評価列がすべて数式判定（数値を変えて評価が動くか実測）
6. 成長率比較がARRベース
7. 除外KPIの不在理由が注記されている
8. 調達額を変えたときRunway・Burn Multiple・評価が連動する

## よくある失敗
評価の手打ち（前提変更後に乖離）／FY1のRule of 40赤表示でシートを汚す／Magic Numberの同年S&M割り／黒字転換年のBurn Multiple負値表示／出典なしベンチマーク／S&M比率「低いほど良い」判定（成長率との矛盾を見逃す）／存在しないARPA業界水準のでっち上げ／USD帯の円換算漏れ
