# Talk Script And TTS Readings

Use this file when writing `speaker_notes`. The notes are the script a presenter — or a
speech engine — reads out loud. A fragment a voice cannot say is a defect there, even though
the same character is right on the slide, which is read with the eyes.

The readings themselves live in `references/tts_readings.json` (symbols, patterns, and the
`policy.script_choice` map). This file is the reasoning behind that table.

## Contents

- Writing the script: fidelity, scene, narrative, depth
- The rule (readings)
- Choosing the form
- What the tooling does

## Writing the script

**Only the spoken script.** Design metadata (judgment fields, `reader_question`, `composition`,
`focal`, rhythm labels) never appears in `speaker_notes`: a presenter reads these notes verbatim.

**Content fidelity: the script and the slide are the same argument.** Write the scripts against
the final slide bodies (after visual QA) and re-check them whenever a slide's copy changes; notes
that describe an older body are a defect ("script drift").

- Every number, date and proper noun you speak exists on that slide (or in its note or
  assumption). A number that appears only in the script is a hallucination risk, and
  `validate_spec.py` flags unit-bearing numbers absent from the slide.
- Touch every load-bearing element: the title claim (paraphrased), the focal object, the key
  rows, steps or columns, the insight band, and any caveat, spoken in natural language.
- Do not open by reading the title string verbatim; restate the claim in spoken form.

**Open on the scene, then the claim.** The first sentence puts the audience somewhere: a person,
a place, an action. Then the claim, then the evidence in the slide's reading order. A script that
could be read over any slide in the deck is not yet doing its job; `validate_spec.py` warns when
a slide's notes carry no scene.

**Narrative: the deck reads as one story, not per-slide captions.** Each script

1. picks up from the previous slide's bridge (no reset openings such as "on this slide", and no
   three slides in a row opening with the same connective),
2. opens with the claim in spoken language, then walks the evidence in the slide's visual reading
   order, naming the actual labels and numbers the audience should look at,
3. states the implication (the so-what) before leaving the slide,
4. ends with a bridge that hands off to the next slide's question.

Use a natural spoken polite register throughout: full sentences, no noun-ending fragments, no
bullet dumps. Read the finished set aloud once from start to finish; if a transition jars, or a
slide's script could be moved elsewhere without anyone noticing, the narrative is not done.

**Depth.** About 150-300 Japanese characters per content slide (30-60 seconds of speech);
calibrate the deck total against `meta.talk_minutes` (about 300 characters per minute). A one-line
note is a defect on every slide except the cover. `validate_spec.py` warns on metadata leakage,
thin scripts, a non-spoken register, title-verbatim openings and slide-absent numbers.

## The rule

**Open only what a voice would stumble over, and open it into the words a person would
actually say.** Two failure modes, both real:

- **Symbols left in the script.** Arrows, range tildes, math and relation signs, the
  accounting triangle for negatives, `&`, inline fractions, `2.4x`, `vs`, `CAGR`, `YoY`, an
  em-dash used as a pause. A speech engine skips them, spells them out, or reads them in
  English, and the listener hears a hole in the sentence.
- **Over-conversion.** Rewriting every Latin string into katakana leaves the presenter
  unable to read their own notes. The script has to survive both a voice and a pair of eyes.

The slide keeps the symbol. The script speaks it. Never apply these conversions to
slide-visible text.

## Choosing the form

Pick by what kind of fragment it is, not by one global rule:

| Fragment | Form | Why |
|---|---|---|
| Operators and relations (arrow, multiply, divide, plus-minus, approximately, at-least, range tilde, accounting triangle) | kanji or hiragana | They are *words* in speech. Written as kana or kanji they also read naturally on the page. |
| Units written as symbols (currency sign, "pt", "@") | katakana or kanji | The unit is spoken as a word. |
| Ratios and fractions | kanji, reordered | Japanese says the denominator first, so `1/3` is spoken as "three-parts-of, one". A slash between nouns is "and" or "or" — decide which from the sentence. |
| Acronyms read letter by letter (KPI, ARR, ROI, API) | leave as Latin | Engines say the letters, which is what the presenter says. Converting them only hurts the reader. |
| Acronyms read as a word (SaaS, CAGR, YoY) | katakana, or the Japanese term | Left alone they are mispronounced or spelled out; CAGR and YoY are better spoken as their Japanese terms. |
| English words and product names | katakana | Give the katakana reading once at first mention and reuse it. |
| Numbers | leave as digits | Engines read them, comma grouping included. Open the *unit* beside them, not the number. |

Two habits keep the script honest:

- Say the sentence out loud before keeping it. If you would not say it that way to a room,
  the engine will not either.
- Opening a range or a symbol must not change the value. Restating a figure is drift; the
  spoken form and the slide's number stay identical.

## What the tooling does

`validate_spec.py` warns on every speaker_notes fragment the reading table marks as
un-speakable and names the reading to use. It warns rather than errors, and it never
rewrites: the right reading depends on the sentence (the multiply sign is "times" in a
formula and "-fold" in a multiple), so the judgment stays with the writer.
