# Copy And Title Rules

Use this file when writing slide-visible text. The manual is English; generated slide copy is
usually Japanese.

## Titles And Subtitles (the header contract)

Every slide carries a main title and a subtitle, and each occupies exactly the number of
lines the contract declares — one line, except the cover subtitle, which is two. The
contract lives in `tokens.json` → `header_contract` and is resolved by
`deck_text.header_slots(pattern)`; the validator and the renderer both read it, so there is
one source of truth and no per-slide-type rules to remember:

- **Slots.** By default the slots are `title` + `subtitle`, one line each — this default
  applies to every pattern, including any new one. `cover` overrides the subtitle to exactly
  two lines (authored with `\n`). `section_divider` has no header chrome, so its subtitle
  slot is the `desc` field; writing `subtitle` there is an error because it would never be
  drawn.
- **One line means one line.** No `\n` in a one-line slot, and no wrapping. The per-line
  limit is derived from the render geometry (box width ÷ type size), not a number you copy
  from a table. `validate_spec.py` rejects overflow as an error.
- **Fix overflow by sharpening the copy.** Never shrink the type, never let it wrap, never
  split the claim across two header lines.
- The title states the conclusion, not the topic. The subtitle scopes it (period, segment,
  audience, metric) and is not a second claim.
- One title carries one claim. Split the slide if two claims compete.
- Evidence-slide titles should include the key number when the number is the proof.
- Do not use a kicker line above the title.
- Avoid empty labels such as overview, background, approach, or summary unless the page is
  genuinely structural.

## Body Copy

- Use concrete nouns, metrics, periods, and named mechanisms.
- Prefer short labels over full sentences in charts, tables, and diagrams.
- Remove generic adjectives unless they are quantified or evidenced.
- Keep cause and effect close: action -> metric moved -> business implication.
- Do not ask the reader to infer the implication from the visual alone; write the read-out
  into the exhibit or interpretation rail.

## Japanese Slide Copy Discipline

- Use noun-ending / headline style for visible slide text.
- Avoid sentence-final full stops in titles, bullets, labels, and callouts.
- Avoid polite spoken endings in visible slide text.
- Use half-width alphanumerics.
- Keep labels short enough to avoid awkward wrapping.
- Treat YoY, QoQ, vs plan, prior-year, and delta text as metric sublines with their own
  spacing, not as glued suffixes.

## Line Breaks (文節)

Where a line breaks is part of the writing, not an accident of box width. A renderer wraps
on geometry alone and will happily split a word (`導入費＋固定利用/料`), an okurigana stem
(`問い合/わせ`), a quantity and its unit (`2030/年`), or leave a particle stranded at the
head of a line (`実行文脈 / へ変換`). Each of those fills the line and breaks the sentence.

The builder breaks display text at 文節 boundaries automatically
(`deck_text.wrap_display`), so the rules below are about what you write, not about where you
type a newline:

- **Do not hand-break display text.** Labels, headings, bullets, cell text, callouts and
  conclusion lines are wrapped by the builder at the boundary that reads best for the width
  it will actually be drawn at. A `\n` you type is a *forced* break the builder preserves —
  reserve it for the few slots that require an exact line count (the cover subtitle's two
  lines), not for fixing a wrap you did not like.
- **A break lands after a particle, after a punctuation or a list separator, or between two
  content words.** Nothing else is a break: okurigana never leaves its stem, a number never
  leaves its counter, a suffix never starts a line.
- **If a word cannot fit the box on one line, the copy is too long.** The engine refuses to
  mangle it and lets the renderer wrap naturally, so the defect stays visible. Shorten the
  copy or widen the container — do not shrink the type.
- **Long body copy is left alone.** Beyond `tokens.line_break.max_display_chars_ja`, text is
  body, not display text: forced breaks there rot the moment anyone edits a word.
- Write phrases that survive wrapping: put the metric and its unit in one chunk, and avoid
  clause-length labels that only fit by breaking mid-word.

## Words To Replace

Replace generic language with proof. (This section owns REPLACE-WITH-PROOF mappings;
the banned generic-filler word list — "industry-leading", "seamless", … — lives only in
`humanize.md`. Add new banned words there, not here.)

- strong -> name the metric or evidence
- efficient -> state hours, cost, margin, or process step reduced
- scalable -> state the scaling mechanism
- differentiated -> state the axis and evidence
- market tailwind -> state the driver, timing, and source
- significant -> quantify or remove

