# Activation Test Prompts

Use these prompts to check whether `skill-design-research` triggers for the right design work without colliding with `refinment` or routine edits.

## Should Trigger

- "Instructions が肥大化していないかを見て、最新論文と公式 docs を踏まえて research-backed に整理して。"
- "この skill がほとんど発火しない。description と activation 条件を realistic prompt ベースで見直して。"
- "新しい reusable workflow を作りたい。論文と公式ガイドを読んで trigger 設計まで固めて。"
- "この instruction module を global に置くべきか、skill に寄せるべきか、根拠付きで設計して。"
- "slash command を作る前に、workflow 設計と should-trigger / should-not-trigger を research-backed に詰めて。"
- "Use recent papers and official references to audit this skill's trigger surface and reduce prompt bloat."
- "Skill improvement logs も見て、どの trigger が弱いか evidence-backed に修正して。"
- "今のInstructionをエージェントを起動させて多面的に評価し、十分な品質になるまで徹底的にブラッシュアップして。"

## Should Not Trigger

- "この brief が曖昧だから、必要なら整えてから実装して。"
- "この prompt を少しだけ言い換えて。"
- "SKILL.md の typo を 1 個直して。"
- "agents/openai.yaml のこの一行だけ和訳して。"
- "fix README wording"
- "この verification brief は clear なので、そのままテストして結果をまとめて。"

## Cross-Skill Boundary Checks

- If the job is one-off prompt tightening, route to `refinment`, not `skill-design-research`.
- If the job is a tiny copyedit with no design implication, do not trigger either skill.
- If the user asks for papers, best practices, activation design, or evidence-backed restructuring of a reusable workflow, `skill-design-research` should trigger.
- If the user asks for a multi-angle audit of instructions, skills, or workflow architecture, `skill-design-research` should trigger even when code edits will follow.
