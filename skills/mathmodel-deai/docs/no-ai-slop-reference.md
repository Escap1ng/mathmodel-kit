# No-AI-Slop reference (English)

> Adapted from [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) — `skills/no-ai-slop/SKILL.md` and
> `skills/no-ai-slop/eval.md` at commit `000650b156983f5159695b441477f4e63b25dc85` (MIT License, Copyright (c) 2026
> Peter Yang). The upstream text is condensed, reordered and lightly reworded for this project; the pattern taxonomy
> and most examples are taken from it.
>
> **Scope.** This file is the English counterpart of the Chinese rules in [`deai-rules.md`](deai-rules.md). The
> machine-checkable English rules live in [`../code/phrasing-blacklist.json`](../code/phrasing-blacklist.json)
> (`en-slop-word` / `en-slop-phrase` / `en-slop-pattern`). Use this reference for English abstracts, figure captions,
> and quoted material, and as the cross-reference for pattern names.
>
> In this file slop words and phrases appear inside backticks so that the catalogue itself stays readable; running
> `check_phrasing.py` over this file is expected to report the examples.

## Purpose

Act as a sharp human editor: preserve the writer's point and personal voice while making the writing clearer and more
alive. Remove AI patterns **without** turning distinctive writing into generic polished prose.

**Edit (default).** Fix a draft with the rules below; return the edited draft plus a short *What changed* section.

**Detect.** If asked whether a draft reads as AI, name each pattern from this skill that appears, quote the line, and
give the fix in a few words. Do not rewrite, do not score, and do not claim to know whether AI wrote it. Named
patterns are evidence the reader can check; detectors only guess. Offer to edit afterwards.

## Editing principles

- **Preserve the writer's real voice.** Notice vocabulary, cadence, bluntness, humor, uncertainty, digressions and level
  of polish; keep what is personal. Do not make every paragraph equally tidy.
- **Make the minimum effective edit.** Fix AI patterns, errors, repetition and unclear passages; leave strong human
  sentences alone.
- **Lead with the point when the setup adds nothing.** Cut generic throat-clearing; keep a personal aside when it adds
  context, tension or character.
- **Front-load only when it improves clarity.** Do not force every paragraph into the same point-detail-background shape.
- **Keep the user's meaning.** Never invent claims, examples, statistics or opinions. If something is unclear, ask.
- **Open it up, don't dumb it down.** Keep substance, nuance and precision; strip only jargon, long sentences, abstract
  nouns and tangled structure.
- **Use active voice.** Prefer "The team shipped it Tuesday" over "the decision emerged". Never let inanimate things do
  human verbs.
- **Make every sentence earn its place.** Cut empty qualifiers and throat-clearing; keep "I think", "maybe", "to be
  honest" only when they express real uncertainty, self-awareness or a spoken rhythm.
- **Untangle sentences without flattening the cadence.** Split what is genuinely hard to follow; keep clear fragments
  and changes of pace that are characteristic.
- **Be concrete and specific.** "The integration improved efficiency" becomes "The integration cut deploy time from 40
  minutes to 4." Names, numbers, dates, mechanisms and examples beat abstractions.
- **Use the portability test.** If a sentence could move unchanged to another person, company, country or product, it is
  probably filler.
- **Show, don't tell the reader what to think.** Let facts, actions and consequences carry the emphasis; cut commentary
  that labels a point important, surprising, subtle or obvious.
- **Protect the specific fact.** Do not smooth a useful detail into generic importance.
- **Make verbs do the work.** "Made a decision" → "decided"; "has the ability to" → "can".
- **Know the job.** Before structure or word choice, know what the piece is for and who it is for.
- **Preserve useful edge and character.** Keep strong opinions, blunt language, humor and honest admissions when they
  belong to the writer.
- **Keep structure unless it is hurting the piece.** If you reorganize, say why in *What changed*.

## Words to cut

**Banned outright:** `delve`, `foster`, `leverage`, `utilize`, `facilitate`, `empower`, `streamline`, `cutting-edge`,
`paradigm shift`, `game changer`, `this is huge`, `this changes everything`, `tapestry`, `realm`, `beacon`,
`multifaceted`, `meticulous`, `intricate`, `paramount`, `transformative`, `elevate`, `embark`, `supercharge`,
`harness`, `ever-evolving`.

**Often-empty adverbs:** `just`, `literally`, `honestly`, `simply`, `actually`, `truly`, `fundamentally`,
`importantly`, `crucially`, `inherently`, `inevitably`. Cut when they add nothing; keep when they carry emphasis,
uncertainty, contrast or a natural spoken rhythm.

**Often-empty phrases:** `it's worth noting`, `it's important to note`, `at the end of the day`, `when it comes to`,
`at its core`, `in today's world`, `in the age of`, `in the world of`, `the reality is`, `the truth is`, `in terms of`,
`with regard to`, `going forward`, `in this article`, `let's dive in`. Cut when they delay the point.

> Note on academic English: `in order to`, `in terms of`, `with regard to` and `robust`/`robustness` are treated as
> legitimate technical register in this project, so they are **excluded** from the machine-checkable English rules,
> even though the upstream list is stricter. The other categories above are enforced by `check_phrasing.py`.

## Patterns to cut

**Binary contrasts.** `This is not X. It's Y.` / `It's not just X but Y.` State Y directly.
`The question isn't the model. It's the eval.` → `The eval matters more than the model.`

**Throat-clearing openers.** `Here's the thing`, `Here's what I mean`, `Let me be clear`, `I'll be honest`,
`The uncomfortable truth is`. Cut them and state the point.

**Faux-insight setups.** `This is the part most people skip`, `What most people get wrong`, `Here's what nobody tells
you`, `The part everyone misses`. These flatter the writer as the lone expert; cut the setup and make the claim stand
alone. `The part everyone misses: distribution is the real moat` → `Distribution is the moat.`

**Colon reveals.** A noun phrase, a colon, then a lowercase dramatic reveal: `The best part: it learns.` Rewrite as a
plain sentence. Use colons for lists, labels and quotes, not fake drama; prefer sentence case after a colon unless
grammar, a proper noun, a title or code requires otherwise.

**Superficial analysis.** Cut trailing `-ing` clauses that pretend to explain meaning: `highlighting`, `underscoring`,
`reflecting`, `showcasing`. `The launch adds file search, highlighting the team's commitment...` → `The launch adds file
search, so users can find old drafts without leaving the editor.`

**Importance puffery.** `Stands as a testament`, `marks a pivotal moment`, `plays a vital role`, `solidifies its
position`, `underscores its significance`. State the fact and let the reader judge. `The launch marks a pivotal moment
for the company` → `The launch is the company's first paid product.`

**Interpretive metadiscourse.** Cut lines that step outside the subject to tell the reader what to notice: `That last
part matters more than it sounds`, `The key point is`, `As you can see`, `This distinction matters`, and redundant
`In other words`.

**Weasel attribution.** `Experts agree`, `industry reports suggest`, `many argue`, `widely regarded as`, `studies show`.
Name the source or cut the claim; if there is no source, ask instead of inventing one. (Mirrors the Chinese
`fake-authority` rule and the project's anti-fabrication red line.)

**Fake-strong verbs.** Prefer `is` and `has` when clearer. `The app serves as a centralized hub for sponsor management`
→ `The app tracks sponsors, drafts, due dates and approvals in one place.`

**Synonym cycling.** If the clear word is right, repeat it; do not rotate terms for style. `The agent reviews the draft.
The assistant scores the piece. The tool suggests fixes` → `The agent reviews the draft, scores it, and suggests fixes.`

**Negative listing.** `Not a X. Not a Y. A Z.` Just say Z.

**Dramatic fragmentation.** `X. And Y. And Z.` / `That's it. That's the whole thing.` Use complete sentences.

**Robotic rhythm.** Avoid repeated sentence shapes, identical paragraph structures and stacked punchy fragments. (This
is what the structural checker `check_style.py` measures as `repeated-opening` and `sentence-rhythm`.)

**Rhetorical setups.** `What if I told you...`, `Think about it:`, `Plot twist:`, and self-answered `Question? Answer.`
pairs. Drop them and make the point.

**Fake-profound kickers.** Cut the final "deep" line when it turns the point into a metaphor, aphorism or mic-drop.
Do not rewrite it into a better metaphor and do not preserve its rhythm: delete it, then end on the clearest concrete
sentence already in the draft.

**Summary-recap endings.** `In conclusion`, `Ultimately`, `Overall`, or a final paragraph that restates the piece. End
on the last concrete point, takeaway or next action.

**Formatting slop.** Emoji in headings, bold sprinkled mid-sentence, bullet lists where two sentences of prose read
better, headers over two-sentence sections. Format should follow the content, not decorate it.

**Em dashes.** Do not use them as a default rhythm crutch. None in short copy; 1-2 in longer drafts only if they clearly
beat commas, periods or parentheses. Remove clusters and decorative dashes.

## Eval checklist (run after rewriting)

Answer each with pass or fail; fix the draft before returning if any fails.

*Editing principles.* (1) preserves the point without adding claims/examples/stats/quotes/opinions; (2) preserves the
writer's distinctive vocabulary, cadence, bluntness, humor, uncertainty and polish; (3) leaves strong human sentences
alone; (4) cuts proportionally to the actual slop, without stripping character; (5) leads with what the reader needs
while keeping personal setup that adds context; (6) front-loads only where it helps; (7) sentences earn their place with
concrete facts, protected details and direct verbs; (8) every generic sentence passes the portability test or was cut;
(9) active voice with human subjects where possible; (10) keeps useful edge and preserves structure unless it hurt the
piece; (11) tangled sentences fixed while clear cadence, fragments and pace changes remain.

*Words to cut.* (1) banned words, filler phrases, often-empty adverbs and inflated claims removed unless quoted as
examples.

*Patterns to cut.* (1) binary contrasts, negative listings, rhetorical setups and throat-clearing openers removed;
(2) faux-insight setups, colon reveals, superficial analysis, fake-strong verbs, synonym cycling, dramatic fragments and
robotic rhythm fixed; (3) importance puffery and weasel attribution replaced with plain facts and named sources, or
flagged when no source exists; (4) interpretive metadiscourse removed; (5) fake-profound kickers deleted, not rewritten;
(6) summary-recap endings cut; (7) formatting slop removed; (8) colons in sentence case unless otherwise required;
(9) em dashes used sparingly.

*Final read.* (1) avoids robotic symmetry and stacked fragments; (2) the writer would recognize it as their own voice;
(3) it reads naturally aloud; (4) the output includes the full edited draft and a short *What changed* section; (5) for
detect requests, each pattern is named with a quoted line and a short fix, without rewriting, scoring or claiming AI
authorship.

## Mapping to this module

| Upstream pattern | Rule id in `phrasing-blacklist.json` / checker |
|---|---|
| Binary contrasts, negative listing | `binary-contrast` |
| Throat-clearing openers, rhetorical setups, interpretive metadiscourse | `en-slop-phrase` |
| Faux-insight setups | `faux-insight`, `en-slop-pattern` |
| Colon reveals | `colon-reveal` |
| Importance puffery | `empty-elevation`, `en-slop-pattern` |
| Weasel attribution | `fake-authority`, `en-slop-pattern` |
| Fake-profound kickers | `fake-profound-end`, `en-slop-pattern` |
| Summary-recap endings | `verbose-connective`, `en-slop-pattern` |
| Banned / inflated words | `en-slop-word` |
| Robotic rhythm, repeated sentence shapes | `check_style.py` → `repeated-opening`, `sentence-rhythm` |
| Synonym cycling, dramatic fragmentation, fake-strong verbs | structural editing (human); partly `repeated-opening` |
| Formatting slop, em dashes | human checklist (`deai-rules.md` §6.2) |

## License notice (upstream)

```
MIT License

Copyright (c) 2026 Peter Yang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
