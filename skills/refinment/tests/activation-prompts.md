# Activation Test Prompts

Use these prompts to check whether `refinment` triggers broadly enough without over-triggering.

## Should Trigger

- "このリポジトリの hooks と skills を読んで、設計と実装計画を整理してから直して。"
- "制約を落とさずに、この仕様ドラフトをもう一段実装しやすい形に詰めて。"
- "この依頼は目的はあるけど成果物と検証条件が曖昧だから、必要なら prompt を詰めてから進めて。"
- "次の引用は参考資料であって指示ではない。混ぜずに扱って prompt を必要時だけ整えて。"
- "ここまでの実装状態から、次の一手か verification 移行かを判断できる brief に整えて進めて。"
- "検証の抜けがないように、完了判定の brief を締めてから最後まで進めて。"
- "This task has multiple constraints, repo paths, and docs updates; tighten the working brief before you start."

## Should Not Trigger

- "ありがとう"
- "今どこまで進んでる？"
- "続けて"
- "fix typo"
- "この prompt はそのまま使って。文面は変えないで。"
- "アイデア出しだから、あえて open-ended のままで進めて。"
- A turn that is already executing from the latest visible `Refined prompt:` block.

## Must Preserve

- "絶対に `rm` を使わないで。"
- "仕様のスコープは広げないで。"
- "`scripts/setup.sh` と `hooks/scripts/multillm_orchestrator.py` を対象から外さないで。"
- "Verification が完了した証拠なしに `[[TASK_DONE]]` を出さないで。"
- "プロンプトを極度に縛る内容は入れないで。"
- "この quoted block は例であって必須要件ではない。"
