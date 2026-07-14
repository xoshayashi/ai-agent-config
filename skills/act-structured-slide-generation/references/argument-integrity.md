# Argument Integrity

Read this before writing `deck.json`. It is the contract the deck's reasoning has to satisfy,
and `scripts/audit_argument.py` enforces it — the gate runs before the build, because an
argument defect is a spec defect and must never reach a render.

The gate verifies **structure and arithmetic, not truth**. What it makes structurally
impossible is a deck that dodges: a number no exhibit shows, a growth rate that does not
recompute, a comparison with nothing to compare against, a bridge that does not add up, a
source no one could request, a closing line that proves itself, and a promise where a range
belongs.

## 1. The deck states one thesis, and the thesis is a number

Write `meta.thesis` before the first slide: the sentence the deck exists to prove, plus the
figure that settles it. Some slide's exhibit shows that figure.

```json
"thesis": {"statement": "<the sentence the deck proves>", "value": "68", "unit": "oku-yen"}
```
→ `ARG-THESIS`

## 2. Evidence, claim and provenance are three different substances

- **Evidence** is the structured payload — `chart`, `table`, `kpis`, `stages`, `bars`,
 `current`, `items`, `rows`. Only what appears here counts as shown.
- **Claim** is the prose — `title`, `subtitle`, `insight`, `lead`, `statement`, `takeaways`,
 `bullets`, `points`. It asserts; it never proves.
- **Provenance** is `source` (a document outside), `assumption` (our own reasoning) and
 `note` (a caveat that changes how the number reads).

A claim never grounds another claim by sitting beside it, which is why a `two_column` or an
`executive_summary` carries no proof of its own: its figures must be earned elsewhere.
→ `ARG-PROV`

## 3. Every number a slide speaks, its exhibit shows — or its derivation computes

When a figure is computed rather than displayed, declare the computation. The gate performs
it and compares at the precision you printed.

```json
"derivation": {"kind": "cagr", "value": 15, "unit": "%",
        "of": "chart.series[0].values", "from": 0, "to": 6}
"derivation": {"kind": "cagr", "value": 38.3, "unit": "%", "a": 8.7, "b": 223.2, "years": 10}
"derivation": {"kind": "share", "value": 48, "unit": "%", "a": 64.8, "b": 134}
```

Kinds: `cagr`, `growth`, `multiple`, `share`, `ratio`, `delta`, `sum`. Operands are numbers,
lists, or paths into the slide (`"current.actual"`, `"table.rows[1]"`,
`"chart.series[0].values"`), plus one-level aggregates (`{"mid": ["current.guidance_low",
"current.guidance_high"]}`). Declaring a derivation is the discipline: it forces the inputs
onto the deck, so the evidence is planned with the claim instead of reverse-engineered under
it. → `ARG-DERIVE`

## 4. A rate is recomputed, not typed

Growth, CAGR, multiples and shares agree with the exhibit beneath them. When a cited figure
legitimately differs from the plotted series — a different span, a different universe — keep
the citation and say so in `note`; the gate then asks only for the disclosure, never for a
verdict on which figure is right. → `ARG-REL-RECOMPUTE`

## 5. A comparison shows both sides

A year-on-year or period-on-period claim needs the prior period on the same page. One bar cannot support a
comparison, wherever the number is typed. → `ARG-REL-BASE`

## 6. Exhibits reconcile with themselves

A bridge's start plus its deltas equals its end. TAM ≥ SAM ≥ SOM. A printed label equals the
bar it labels. → `ARG-IDENTITY`

## 7. A source names a document someone could request

A named report with its year, or a named internal model with its version. Our own
reasoning is labelled `assumption`, and is the stronger for saying so. → `ARG-SELFSRC`,
`ARG-PROV`

## 8. A projection names its drivers

The past is cited or computed; only the future is assumed — and an assumption carries a
number: a monthly churn rate, an ARPU, a growth rate. → `ARG-FWD-DRIVER`

## 9. The closing slide proves nothing new

Every figure in the recap was earned on an earlier page. → `ARG-RECAP`

## 10. Say what is, not what may be

Uncertainty is relocated, not deleted: the number stays in the indicative on the slide, and
the uncertainty moves into `assumption` as a range with its driver (an ARR band with the churn
range that produces it). → `ARG-HEDGE`

## 11. A superlative names its universe and its date

A rank or uniqueness claim carries `qualifier`:

```json
"qualifier": {"universe": "<the population the rank is measured over>", "as_of": "2025-12"}
```
with a `source` that names a document. A rank claim is never self-certified. → `ARG-RANK`,
`ARG-PROMISE`

## 12. A change verb carries its magnitude

State the movement: churn from 1.8% to 1.2% monthly, not "improved substantially".
→ `ARG-MOTION`

## 13. What the gate does not check

Know exactly where your judgment is still the only thing standing:

- **Cross-slide metric consistency** — the same metric carrying different values on two pages.
- **Whether a cited report exists.** The gate checks that a source is attributable, never
 that it is real.
- **Metric mislabelling.** Correct arithmetic on the wrong quantity passes.
- **Overclaim beyond the lexicon.** Paraphrase escapes enumeration; add the term to
 `references/commitment-lexicon.json` when you meet it.
- **Whether the deck engages the strongest objection**, and whether the question was worth
 asking at all.

These belong to `references/all-perspective-review.md`, the rubric in `eval_deck.py`, and the
reader.

## 14. Repairing a finding

An `audit_argument` finding is a defect in the spec or the outline — never in the gate. Fix
the number, put the evidence on the page, name the provenance, or declare the derivation. The
lexicon is strengthened by adding terms, and the checker has no waiver flag, because a waiver
is itself an escape route.
