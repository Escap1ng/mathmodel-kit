# Contributing

Thank you for helping `mathmodel-kit`. The project aims to make the **mechanically correct** parts of mathematical
modeling (figures, diagrams, typesetting, delivery checks) deterministic, reproducible and verifiable, while leaving
**modeling judgement** to the user. Contributions follow the same line.

> 中文版：[CONTRIBUTING.md](CONTRIBUTING.md)

---

**Contents**: [Collaboration overview](#1-collaboration-overview) · [Should it be a template at all](#2-should-it-be-a-template-at-all) · [Collaboration modules](#3-collaboration-modules) · [Interfaces and sync](#4-module-interfaces-and-information-sync) · [Environment, layout and style](#5-environment-layout-and-code-style) · [Roles and permissions](#6-contributor-roles-and-permissions) · [Commits and pull requests](#7-commits-and-pull-requests) · [Review criteria](#8-review-criteria) · [Attribution and licence](#9-attribution-and-licence) · [Code of conduct](#10-code-of-conduct)

---

## 1. Collaboration overview

Everything open to collaboration is organised into four modules. Each module is documented as
**standards → submission rules → review process** (section 3); cross-module hand-offs and sync rules are in section 4,
and roles and permissions in section 6.

| Module | Scope | Main deliverables | Source of truth | Reviewed by |
|---|---|---|---|---|
| **M1 Docs and examples** | Rules, guides, per-template docs, examples and previews | `docs/**`, `SKILL.md`, `README.md`, example files | The owning skill's rule files | Reviewers |
| **M2 Code and templates** | Template scripts, tools, registries and contracts | `code/templates/**`, `code/tools/**`, `manifest.json`, `*.schema.json` | The registry (single source of truth) | Reviewers |
| **M3 Testing and verification** | Local self-checks, CI gates, contract validation | Verification commands and output, green CI | `.github/workflows/ci.yml` and the validators | CI + reviewers |
| **M4 Issues and requests** | Bug reports, template requests, doc corrections | Issues (minimal reproduction or request form) | The issue forms | Reviewers / maintainers triage |

All four feed one chain: **the registry is the single source of truth → CI checks consistency → humans review only
what machines cannot**.

**Collaboration scope**: the main skill `mathmodel-core` is maintainer-owned (outsiders may file issues but not open
PRs against it); the other skills plus the root docs and CI accept external contributions. The scope is the
`contribution` field in [`skills/manifest.json`](skills/manifest.json), which also registers each skill's kind
(core / knowledge / tool).

---

## 2. Should it be a template at all?

**Do not turn one-off figures into templates** — hand-drawing per
`skills/mathmodel-diagram/docs/guides/authoring.md` or `skills/mathmodel-figure/docs/guides/nature-standard.md`
is faster.

A template is worth it only when a figure type is drawn repeatedly. Test: after swapping in new data and copy,
does the figure's **structure** still hold?

---

## 3. Collaboration modules

### M1 Docs and examples

**Standards**

- Keep one authoritative copy of each rule; other documents carry a mandatory-item summary plus a link rather than
  restating the same rule twice;
- Examples are filled with real content, never placeholders; a diagram template's doc must state per-slot **measured**
  CJK character budgets and the semantic conventions (parallel / convergent / comparative);
- Numbers, conclusions and citations must trace back to a reproducible artifact in the repo or a verifiable source;
  fabricated data and references are forbidden;
- Naming follows the existing conventions: kebab-case template ids, snake_case script names, and paths resolved
  relative to the registry's directory.

**Submission rules**

- Commit messages use `docs(<scope>): <summary>`;
- Changes to an index table (`figure-catalog.md`, or the diagram template index in `SKILL.md`) go into the same PR as
  the matching registry change;
- Rule documents must pass the word-list de-AI check (`python3 code/check_phrasing.py <file>`); project docs are not
  subject to the rhythm metrics.

**Review process**

- Reviewers judge only what machines cannot: whether the semantics are right, whether the copy is faithful to the
  source, whether budgets were measured, and whether it belongs in the docs;
- Documentation-only changes still go through a PR and a reviewer; a missing index-table or registry line is sent back.

### M2 Code and templates

**Standards**

- Code style is in section 5; a template must ship deterministic data or be driven by content JSON, and must never
  hardcode copy in the script;
- New templates obey the registry contract: fields, path resolution, artifact format and naming follow existing
  entries, with no invented fields;
- Appearance-only changes that break existing call contracts (CLI parameters, registry fields, artifact paths) are
  rejected.

**Submission rules**

- Commit messages use `<type>(<scope>): <summary>`, with `type` in `feat` / `fix` / `refactor` / `chore`;
- A new template lands as "one registry line + one index-doc line" (hand-off list in 4.2); the CLI, CI and version
  numbers stay untouched;
- Do not commit generated artifacts: workspace directories, `.aux`, PDF/PNG outputs (see `.gitignore`).

**Review process**

- Green CI is the precondition (see M3); human review covers semantics, originality and contract stability only;
- Changes to Stable contracts (CLI parameters and exit codes, registry fields, theme-contract fields) are decided by
  maintainers, and breaking changes require a `MAJOR` bump plus a `CHANGELOG.md` entry.

#### M2.1 Data-chart templates (`mathmodel-figure`)

1. Write `skills/mathmodel-figure/code/templates/make_<name>.py`
   - ship **seeded** simulated data (`np.random.default_rng(<fixed seed>)`) so results are reproducible;
   - use the shared palette via `from plot_style import ...` when needed (the renderer copies `plot_style.py`
     into the workspace automatically);
   - always emit PNG (300 DPI) + PDF + SVG named `<name>_replica.*`;
2. Register it in `skills/mathmodel-figure/code/tools/manifest.json` (fields as in existing entries:
   `id`, `script`, `title`, `group`, `aliases`, `cjk_hints`, `preview`, `author`);
3. Add a preview at `skills/mathmodel-figure/examples/previews/<name>_replica.png`;
4. Add one row to the catalogue table in `skills/mathmodel-figure/docs/templates/figure-catalog.md`.

#### M2.2 Academic diagram templates (`mathmodel-diagram`)

1. Write `skills/mathmodel-diagram/code/templates/<id>.py` (kebab-case `id`, snake_case script name)
   - build on the primitives in `code/common.py` (`Recorder` + `draw_*` + `guard` + `save_figure`);
   - fixed CLI: `<script> content.json -o out.png` and `<script> content.json --check`;
   - **measure CJK text width per slot before writing files**; on overflow, report the slot and budget and exit non-zero;
   - keep geometry constants at the top of the file and all copy in the JSON — never hardcode copy in the script;
2. Write the content contract `skills/mathmodel-diagram/code/templates/schema/<id>.schema.json`
   (JSON Schema Draft 2020-12)
   - **required fields follow the code's actual behaviour**: only fields accessed via `need()` or `c['key']` are
     required, the rest are read with `.get()` and are optional;
   - keep `additionalProperties: true` so `_comment` and similar metadata stay legal;
3. Register it in `skills/mathmodel-diagram/code/templates/manifest.json` (including `schema`, `example`, `preview`, `doc`);
4. Add `examples/<id>/example.json` (**real, fully filled content — no placeholders**) and
   `examples/<id>/preview.png`;
5. Write `docs/templates/<id>.md`: it must state each field's **CJK character budget** (compute it, never estimate),
   the allowed count ranges, and which slots are parallel / convergent / comparative;
6. Add one row to the template index in `skills/mathmodel-diagram/SKILL.md`.

> Calibration methods, the four matplotlib pitfalls, and the replication/self-check workflow are in
> `skills/mathmodel-diagram/docs/templates/adding-templates.md`.

**You do not need to touch the CLI, CI or version numbers** — the registry is the single source of truth and CI
validates everything else.

### M3 Testing and verification

**Standards**

- Run the gates you can run locally before submitting; a new or changed template must actually render non-empty
  artifacts — "it should work" is not accepted;
- Unified exit-code semantics: `0` success / `1` validation or render failure / `2` usage or environment error; every
  CLI complies today, so both an unknown template id and a missing input file exit `2`;
- Contract-touching changes (schemas, registries, word lists, scoring dimensions) update the examples and expected
  results in the same PR.

**Local self-check before submitting** (pick by scope; every check is judged by exit code):

```bash
python -m compileall -q skills                        # every script compiles

cd skills/mathmodel-figure                            # figure template changes
python code/tools/render_template.py <template-id> --project /tmp/out
python code/tools/validate_theme.py --all             # required when themes/ changes

cd ../mathmodel-diagram                               # diagram template changes
python code/tools/validate_content.py --all           # content contracts + bundled examples

cd ../mathmodel-deai                                  # docs or paper text changes
python code/check_phrasing.py <file>                  # word-list gate; required for rule docs
python code/check_style.py <paper.tex>                # structural gate; paper text only
python code/strip_invisible.py <pdf|docx|tex>         # character-level gate

cd ../mathmodel-score                                 # structure contract / score-card changes
python code/check_chapters.py examples/chapter-sample.tex
python code/score_card.py examples/example-scorecard.json
```

**Submission rules**

- The PR's "Verification" section pastes the **commands actually run and their key output**, not a plan;
- A PR that gives conclusions without commands is asked to supply evidence;
- Passing locally never replaces CI; CI is the merge gate.

**Review process**

- CI must be fully green before merge, covering:

| Check | Contents |
|---|---|
| `syntax` | All Python scripts compile |
| `manifest-consistency` | Figure/diagram registries ↔ filesystem ↔ index docs ↔ version ↔ README template badges, plus the skill registry ↔ skill directories ↔ README skill table ↔ skill badge, must all agree; schemas are valid and every bundled example passes strict validation |
| `figures` / `diagrams` | Every template renders non-empty artifacts |
| `strip-invisible` | The invisible-character scrubber round-trips correctly |
| `deai-phrasing` / `scorecard` | The de-AI gate and score-card smoke cases exit as expected |
| `Paper LaTeX build` | The paper skeleton compiles |

- What machines decide (syntax, consistency, schemas, successful rendering, exit codes) does not enter human review;
  reviewers handle the semantics and originality CI cannot judge.

### M4 Issues and requests

**Standards**

- A bug report carries a **minimal reproduction**: content JSON (or a script snippet) + command + actual output +
  expected output, with the exit code where available;
- A template request answers two questions first: will this figure recur, and does any of the existing 25 templates
  already cover it;
- A doc correction points at the section and the original text, ideally with the fix.

**Submission rules**

- Use the matching issue form (bug report / new template request) and keep the default title prefix;
- When unsure whether something is worth doing, open an issue first instead of writing code;
- Do not paste sensitive information or personal identity data beyond the problem statement itself.

**Review process**

- A reviewer or maintainer claims the issue, labels it, decides which module owns it, hands it to M1 or M2 when
  needed, and states the next step in the issue;
- Rejections (one-off figure types, out-of-scope rewrites) explain the reason and the alternative (for example,
  "hand-draw it per `nature-standard.md`");
- Accepted and merged contributions land in `CHANGELOG.md` and reach the release notes.

---

## 4. Module interfaces and information sync

### 4.1 Single sources of truth

Each fact is maintained in exactly one place; other locations read it or are aligned by CI:

| Fact | Single source | Read by | Maintained by |
|---|---|---|---|
| Skill list, kinds and contribution scope | `skills/manifest.json` | CI, README skill table, contributors | Maintainers |
| Figure template list and fields | `skills/mathmodel-figure/code/tools/manifest.json` | Renderer, CI, index docs | M2 |
| Diagram template list and fields | `skills/mathmodel-diagram/code/templates/manifest.json` | Unified entry point, CI, `SKILL.md` | M2 |
| Diagram input structure | `code/templates/schema/*.schema.json` | Validators, template scripts | M2 |
| Palette contract | `themes/theme.schema.json` + `themes/*.theme.json` | `plot_style.py`, renderer, CI | M2 |
| De-AI word list | `skills/mathmodel-deai/code/phrasing-blacklist.json` | Checkers, rule docs | M1 / M2 |
| Modeling methods and selection | `skills/mathmodel-methods/docs/method-library.md` | Main skill, other skills, users | M1 |
| Chapter-structure contract | `skills/mathmodel-score/code/chapter-checklist.json` | Checker, human-readable checklist | M2 |
| Version number | root `VERSION` | CI, `release.yml`, `CHANGELOG.md` | Maintainers |
| Change history | `CHANGELOG.md` | Users, release notes | Maintainers |

### 4.2 Hand-offs between modules

- **M4 → M1 / M2**: once an issue is triaged, its minimal reproduction or request description becomes the input to
  the owning module; the PR links back with `Closes #<issue>`.
- **M2 → M1**: adding or changing a template updates the registry, index doc, per-template doc and preview in one PR —
  a missing piece is sent back by CI or by a reviewer.
- **M2 → M3**: code changes come with local verification commands and output; green CI is the precondition for merge.
- **M1 → M3**: documentation changes pass the word-list gate; after editing a rule, check that the authoritative file
  and the summaries still agree.
- **M3 → all**: CI is the alignment mechanism, so machine-decidable parts stay out of human review.

### 4.3 Information sync mechanisms

- **Registry consistency**: every push / PR, CI checks that registry ↔ filesystem ↔ index docs ↔ version ↔ README
  badges agree;
- **Triple version agreement**: `VERSION` == release tag == `CHANGELOG` section, enforced by `release.yml`;
- **No double-writing of rules**: each rule keeps one authoritative copy, and other documents carry a mandatory-item
  summary plus a link (the main skill and the specialist skills split work this way);
- **Visible change**: every merge adds the matching `CHANGELOG.md` section, and release notes are extracted from the
  changelog at release time.

---

## 5. Environment, layout and code style

### 5.1 Development environment

- Python 3.12+ (CI pins 3.12 as the minimum verified version)
- Python dependencies come from the repo-root `requirements.txt`: `pip install -r requirements.txt` (lower bounds, the
  same file CI uses). It lists only the packages bundled scripts actually import (`matplotlib` / `numpy` / `seaborn` /
  `python-docx` / `PyMuPDF` / `jsonschema`).
- The paper pipeline additionally needs external tools: `xelatex` and `pandoc`.

Please run this locally before submitting:

```bash
python -m compileall -q skills
```

### 5.2 Directory conventions

The seven skills are each self-contained. **Do not place files outside a skill directory** (`docs/` holds
external-facing planning documents only):

```
skills/<skill>/
├── SKILL.md            # skill contract: when to use it, how, and its boundaries
├── code/               # executable scripts (templates/, tools/)
├── docs/               # human-facing docs (guides/, templates/)
└── examples/           # examples and previews
```

Skills come in three kinds (see `skills/manifest.json`): **core** (`SKILL.md` only), **knowledge** (`SKILL.md` +
`README.md` + `docs/`) and **tool** (`SKILL.md` + `README.md` + `code/` + `docs/` + `examples/`). A new skill is
registered first, and CI checks that the registry ↔ directories ↔ README skill table ↔ badge count agree; core-kind
skills are exempt from the `README.md` requirement.

### 5.3 Code style

- Python: 4-space indentation, standard library first; scripts use `argparse` with the existing flag style
  (`-o/--out`, `--check`, `--list`, `--lang`);
- **Exit-code semantics**: `0` success / `1` validation or rendering failure / `2` usage or environment error;
- **CLI contract**: every CLI complies with `0/1/2` today (an unknown template id or a missing input file exits `2`);
  `--lang {zh,en}` is an optional flag on user-facing entry points
  (8 covered today; `word_postprocess.py` and `strip_invisible.py` do not provide it yet — Experimental, so adding it
  is not a breaking change);
- Comments and docstrings are Chinese (matching the repository); user-facing messages are bilingual where
  `--lang {zh,en}` is supported;
- Do not add new formatter/linter toolchains (the repo does not depend on ruff/black/pytest);
- Do not commit generated artifacts (workspace directories, `.aux`, PDF/PNG outputs — see `.gitignore`).

---

## 6. Contributor roles and permissions

Roles accumulate through actual contributions, with permissions matched by responsibility. These **roles** are the
permission dimension and are separate from the L1–L4 contribution tiers in whitepaper §8.

| Role | Who holds it | Permissions | Visible reward |
|---|---|---|---|
| **Reporter** | Anyone | Open issues (bugs / requests) | Accepted feedback lands in `CHANGELOG.md` and the release notes |
| **Contributor** | Anyone with a merged PR | Submit PRs (docs, examples, code, templates) | Template authors are permanently credited in the registry `author` field |
| **Reviewer** | Sustained reviewers invited by a maintainer | Review PRs, give a verdict, request changes | Review history is recorded in `CHANGELOG.md` |
| **Maintainer** | Long-term participants who know the rules | Merge, release, change CI and version numbers, decide Stable contract changes | Listed as co-maintainers in the whitepaper roadmap |

**Permission boundaries** (matching the "Open by design" interface tiers):

| Change | Decided by | Notes |
|---|---|---|
| Docs, examples, word-list additions, templates and scripts | Contributor PRs, reviewer approval | The regular path |
| Registry field semantics, required content-contract fields, theme-contract fields, CLI parameters and exit codes | Maintainers | Stable contract; breaking changes require a `MAJOR` bump and a `CHANGELOG.md` entry |
| `VERSION`, `CHANGELOG` sections, CI workflows, releases | Maintainers | Releases are tag-triggered, and `release.yml` checks the triple agreement |
| Issue triage and labels | Reviewers / maintainers | Decide the owning module and push it forward |

Responsibility: reviewers answer only for what machines cannot judge (semantics, faithful sourcing, measured budgets,
whether it is worth it); maintainers own contract stability and version governance, and never substitute personal
preference for reproducible evidence.

---

## 7. Commits and pull requests

Follow the existing commit style: `<type>(<scope>): <summary>`, with `type` in
`feat` / `fix` / `docs` / `refactor` / `chore`; the body explains **why**, not what.

Please use the repository's PR template, tick each item, and declare the owning module (M1 docs and examples /
M2 code and templates / M3 testing and verification). CI must be fully green; the gate list is in M3.

---

## 8. Review criteria

What machines can decide (syntax, consistency, schemas, successful rendering) goes to CI. **Humans review only what
machines cannot:**

- whether slot **semantics** are right (misplaced parallel/convergent/comparative meaning is far worse than overflow);
- whether the copy is faithful to the source (**fabricating data or references is forbidden**);
- whether character budgets were **measured** (estimates are not accepted);
- whether it deserves to be a template.

Rejected: fabricated data or references; wrong semantic labelling; appearance-only changes that break existing
contracts (CLI parameters, registry fields, artifact paths).

---

## 9. Attribution and licence

The project is distributed under [Apache-2.0](LICENSE); contributing means agreeing to the same licence.

Template authors are credited **permanently** in the corresponding registry's `author` field and listed alongside
official templates; fixes and documentation contributions are recorded in [CHANGELOG.md](CHANGELOG.md) and thanked
in the release notes.

---

## 10. Code of conduct

Critique ideas, not people. Technical disagreements are settled by **reproducible evidence** (command, input, output),
not by seniority or volume. Plagiarism, data fabrication and invented references are never acceptable.
