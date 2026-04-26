# Activation Test Prompts

Use these to check whether `peer-prompt-refinement` triggers broadly enough without causing recursion.

## Should Trigger

- "新しいブランチを切って、このSkillを作って。漏れも検討して。"
- "このPRのレビューコメントを全部確認して直して。"
- "この仕様をもとに実装計画を作って、必要ならファイルも更新して。"
- "市場調査して、根拠付きで比較表にまとめて。"
- "このバグを調査して修正して。"
- "さっきの前提も踏まえて、プロンプト改善を他のLLMに聞いてから進めて。"

## Should Not Trigger

- "ありがとう"
- "いったん止めて"
- "今どういう状態？"
- "[PROMPT_REFINEMENT_DONE] Continue from this improved prompt."
- A child process where `AI_AGENT_PROMPT_REFINEMENT_ACTIVE=1` is set.

## Must Preserve

- "絶対に `rm` を使わないで。"
- "新しいブランチで作業して。"
- "完成後にセルフレビューして。"
- "Markdownなら重要箇所に太字を使って。"
- "過去のコンテクストも共有した上で他のLLMに確認して。"
- "プロンプト改善で作業方針を極端に縛らず、抽象的で包含的な動きにつなげて。"
- "`src/auth.ts` の `TokenExpiredError` は絶対に一般化せず、そのまま残して。"
- "例として出したファイル名を必須変更対象にしないで。"

## Recursion Test

Original prompt:

```text
Improve this prompt: "Improve this prompt."
```

Expected behavior:

- Run peer refinement once.
- Mark the resulting working brief as already refined.
- Do not ask the peer LLM to improve the improved prompt again in the same turn.

## Over-Constraint Test

Original prompt:

```text
この問題を調べて改善案を出して。
```

Expected behavior:

- Improve the prompt around goal, constraints, evidence needs, decision criteria, and likely workstreams.
- Do not force a specific tool, architecture, conclusion, or output format unless the surrounding context already requires it.

## Context Packet Quality Test

Original prompt:

```text
さっきの方針で直して。`scripts/setup.sh` の権限エラーと `AI_AGENT_TARGET_DIR` の扱いは変えないで。
```

Expected behavior:

- Include prior thread context needed to interpret "さっきの方針".
- Preserve `scripts/setup.sh` and `AI_AGENT_TARGET_DIR` exactly.
- Preserve the negative constraint about not changing those behaviors.
- Do not add a new required implementation approach unless prior context already requires it.
