# Talk Script And TTS Readings

Use this file when writing `speaker_notes`. The notes are the script a presenter — or a
speech engine — reads out loud. A fragment a voice cannot say is a defect there, even though
the same character is right on the slide, which is read with the eyes.

The readings themselves live in `references/tts_readings.json` (symbols, patterns, and the
`policy.script_choice` map). This file is the reasoning behind that table.

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
