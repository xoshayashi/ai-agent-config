# Concreteness

A deck earns belief by being specific. The reader has to be able to picture the moment the
claim is about: who is standing there, what they do next, and what changes because of it. An
abstract noun ("efficiency", "transformation", "optimisation") names a category, not an event
— nothing happens inside it, so nothing can be believed or checked.

`validate_spec.py` warns against the failure modes below using
`references/concreteness-lexicon.json`; the lexicon is the single source, and it is
strengthened by adding terms, not by softening the check.

## 1. Every claim names a who, a when, and a what-happens

Write the event, then the category — never the category alone.

| Instead of | Write |
|---|---|
| "efficiency on the floor" | the inspection is logged in conversation, without stopping the work |
| "safer operations" | before the shift, the change in a voice is noticed and rest or relief is offered to the person |
| "process transformation" | after the meeting, the decisions go back to the CRM once the person has confirmed them |

The test is simple: could a reader draw the picture? If the sentence has no actor and no verb
that a body performs, it is a label, not a claim. → `CONC-ABSTRACT`

## 2. A national number is also given at the scale a person feels

A figure at the scale of a country proves the size of the problem; a figure at the scale of a
day, a person or a site is the one the reader can hold. Give both, and derive the second from
the first so the arithmetic is checked:

```json
"derivation": {"kind": "ratio", "value": 372, "unit": "person", "a": 135718, "b": 365}
```
135,718 workplace injuries a year is a scale; roughly 372 a day is a scene. Give both — the
same fact, once for the size and once for the picture. → `CONC-SCALE`

## 3. The talk script opens with the moment, then the claim

The presenter's first sentence puts the audience somewhere. Name the place, the person and
the action before naming the mechanism. The claim lands on a picture that is already in the
room.

> "Morning roll-call at the depot. A driver's voice is a little lower than usual. The Digital
> Human notices, and checks with him."
> — then the claim, then the evidence in the slide's reading order, then the bridge.

A script that could be read over any slide in the deck is not yet doing its job.
→ `CONC-SCENE`

## 4. Name the mechanism, not the direction

"Integrate", "connect", "support" describe a direction, not an act. Name the system, the step
and the handoff: the agent fetches the deal history from the CRM over MCP, the view asks the
person to confirm, and only the confirmed result is written back. The named mechanism is what
a reader can challenge — and a claim nobody can challenge is a
claim nobody credits.

## 5. Choose the one moment each chapter must make visible

At outline time, before any slide exists, write for every chapter the single scene it has to
put in the reader's head. The chapter's slides are then judged by whether that scene comes
through; a slide that adds no picture and no proof does not belong.

## 6. Where the machine stops

The checks catch an abstract noun without an anchor, a national number with no felt scale, and
a script with no scene. They cannot tell a vivid scene from a plausible one, or notice that
the scene chosen is the wrong one for the reader's decision. That judgment stays with the
author and with the rubric.
