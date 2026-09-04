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

## Line Breaks

A line break is part of the writing, and the two kinds of text want different things from it.
The builder writes the breaks; `validate_spec` / `verify_deck` name what it cannot fix.

- **Labels — chevron labels, headings, outcome lines, table headers — break on meaning.**
  A renderer passes `role="label"` for these; text with no role is treated as a label only
  when it has no punctuation, fits `tokens.line_break.label_max_chars_ja`, and ends on a noun
  (a short sentence ending on a verb, "chintai-igai no michi wo tsukuru", is body copy). The
  break lands on a phrase boundary (bunsetsu) and line lengths are balanced, so the phrasing
  shows in the shape of the block. Particles and symbols stay with the word they belong to, a
  number stays with its counter, okurigana stays with its stem, and a prenominal adjective
  (tsugi-no, onaji, kono) stays with its noun. Break these properly.
- **Body copy — sentences and item bodies — gets no authored breaks (2026-09-04).** The text
  is handed to the renderer as written and wraps naturally; kanji and kana may wrap anywhere,
  as Japanese text does. The builder inserts a break in two cases only
  (`deck_text.wrap_natural`), and only at that spot: the natural wrap would fall inside a
  katakana word, a Latin word or name (Pre-Market, City Making Intelligence), or a number and
  its counter — or the last line would hold a single character. Every other line end is left
  to the renderer. Lines are never shortened, balanced, or broken at clause boundaries for
  shape. A sentence that would need two more lines than the natural wrap, or that holds such a
  word wider than the column, is left entirely to the renderer and `verify_deck` names it.
- **A line never opens on a character that cannot open one.** A comma, a full stop, a middle
  dot or a closing bracket stays on the line above — and when it does not fit there, the
  character before it moves down with it, because renderers do not hang punctuation past the
  margin and a line handed over too wide wraps early and leaves an empty line. An opening
  bracket never ends a line.
- **A number keeps the size that fits its card.** A value and its unit are one line; the
  builder steps the numeral down until the line fits, and uses one size across the cards so
  the comparison is not distorted.
- **A symbolic message is composed as a form.** See the message-slide contract in
  `grid-and-flex-strategy.md`: measure, balance and breathing are chosen together.
- **Copy that fits its column is copy that survives layout.** When a single word is wider than
  its column, `verify_deck` names it: shorten the word or widen the column. Type size stays as
  designed.
- **Meaning is carried by commas and by line breaks.** A slide reads at a glance, so a clause
  break is a comma and an emphasis break is a new line. When a point deserves to stand alone,
  give it its own line — a statement slide gives it the `lead`. (`validate_spec` flags a dash
  in slide-visible text and points to those two moves.)
- A hand-typed `\n` is honoured as a forced break, which is what makes it right for the few
  slots that require an exact line count (the cover subtitle's two lines).

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

