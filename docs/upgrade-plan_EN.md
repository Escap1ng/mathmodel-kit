# Upgrading mathmodel-kit: From a Skill Set to an Open Modeling Toolbox

> Version: v1.1.0 ｜ Status: Phase 1 delivered ｜ Chinese original: [upgrade-plan.md](upgrade-plan.md)

This document answers one question: **how does mathmodel-kit move from "a prompt-centric agent skill set" to "an open,
collaborative mathematical-modeling toolbox"?** Claims are tied to real files and line numbers in the repository;
anything inferred rather than verified is marked as such.

---

## 1. Positioning Diagnosis: Where the Gaps Are

The current form is a **prompt-centric skill set with a small number of CLI tools**: `math-modeling-helper` is a pure
specification orchestrator (no code), `mathmodel-figure` (20 data-chart templates), `mathmodel-diagram` (5 JSON-driven
diagram templates) and `mathmodel-paper` (LaTeX/Word pipeline plus invisible-character scrubbing) are the three
executable landing points.

A "toolbox" does not require more features; it requires **contracts other people can depend on**. The gaps by layer:

| Layer | "Skill set" today | "Toolbox" requirement | Phase 1 response |
|---|---|---|---|
| Contract | Template info lives in hardcoded dicts, docstrings and hand-written docs; no machine-readable schema | Single source of truth + machine-readable data contract | Done: two `manifest.json` + 5 JSON Schemas |
| Style | Colours hardcoded in `plot_style.py` constants and in the other templates' script headers; editing source was the only route | Colour becomes declared, swappable, validatable data | Done: `themes/theme.schema.json` + default theme + `--theme` / `validate_theme.py` |
| Interface | 8 CLIs with divergent styles; diagrams had no unified entry point and no `--list` | Stable CLI contract + enumerable, validatable, exit-code-driven interfaces | Done: unified CLI, `--list --json`, `validate_content.py` |
| Governance | No CONTRIBUTING, no version number, no CHANGELOG, no release flow | Contribution process, review criteria, semantic versioning, release automation | Done: CONTRIBUTING ×2, PR/Issue templates, `VERSION`, `CHANGELOG.md`, `release.yml` |
| Ecosystem | Installation documented only for Claude Code; no public index | Multi-host distribution, discoverable and citable by third parties | Partial: see §11 Phase 2 |

Core judgement: **the bottleneck is not missing features but missing "things others can depend on"**. Phase 1 therefore
added zero modeling capability and spent everything on contracts and governance.

---

## 2. Feasibility

### 2.1 Technical: incremental, non-breaking

Every Phase 1 change is **additive**, not a rewrite, and is machine-verified:

- After moving the figure renderer's three hardcoded dicts into `skills/mathmodel-figure/code/tools/manifest.json`,
  `--list` output and alias/CJK resolution are **identical** to the pre-migration behaviour
  (81 resolution cases + 20 ids, 0 mismatches);
- The original per-template invocation `python3 code/templates/problem_flow.py content.json -o out.png` **still works**;
  the unified entry point only adds enumeration and resolution on top;
- Template scripts, output paths and output formats (PNG 300 DPI + vector PDF/SVG) are unchanged.

Opening up the project does **not** break existing users — that is the precondition for feasibility.

### 2.2 Ecosystem

- Licensing is ready: Apache-2.0 ([LICENSE](../../LICENSE)) permits commercial use and redistribution, a prerequisite
  for third parties to depend on the project;
- Quality gates are ready: CI covers syntax, template rendering, schema validation, registry consistency and LaTeX
  compilation, so contributors can verify their own work;
- Discovery channels already exist: the community has produced public directories of such projects (32 projects,
  pinned commits, SHA-256 verification), and their evaluation dimensions are exactly *reproducibility, license clarity
  and a clear human/machine boundary* — which match this project's existing stance;
- Demand is real: AI assistance for modeling contests is an active field (§10), so no market education is needed.

### 2.3 Cost

There is **no server, database, operations burden or API quota**: all artifacts are files and CLIs, running inside the
user's own agent host and local TeX/Python environment. The marginal cost is review effort, which §7 and §8 amortise.

### 2.4 What we deliberately will not do

| Item | Verdict | Reason |
|---|---|---|
| pip packaging / PyPI | **Not now** | Skills ship as directories; packaging would break relative-path invocation (`python3 code/...`), and skill directory names contain hyphens, so they cannot be imported as packages |
| Online API service | **Not now** | Conflicts with local-first and "no operations"; sending user contest data off-device raises privacy/compliance concerns |
| Building our own agent framework | **No** | Hosts (Claude Code / Codex / Trae, …) already provide the runtime; rebuilding it only adds porting burden |
| Fully automatic "paper in one hour" | **No** | See the compliance and positioning analysis in §10 |

---

## 3. Risks and Challenges

| # | Risk | Manifestation | Mitigation |
|---|---|---|---|
| 1 | **Crowded field** | Existing 5000+ star peer projects and 32 catalogued open-source projects; heavy homogenisation | Do not join the "fully automatic" arms race; press the differentiation on **determinism, reproducibility, verifiability** (§10) |
| 2 | **Contest compliance** | Contest rules on AI use vary and are tightening | Hold the line on "mechanical correctness to the tools, modeling judgement stays with the human"; position as an efficiency and verification tool, never promise ghostwriting |
| 3 | **Specification duplication drift** | The main `SKILL.md` and `mathmodel-paper/SKILL.md` share wording and can fall out of sync | Establish one authority (specialised skills defer to the main skill); index-like content is validated from the registry by CI |
| 4 | **Registry drift** | Adding a template used to require editing several lists | Reduced to "one registry line + one index row"; CI `manifest-consistency` checks registry ↔ filesystem ↔ index docs ↔ version ↔ README badges |
| 5 | **Schema vs docstring duplication** | Both describe the same contract | Clear division: the Schema is the **machine authority**, docstrings stay human-readable; CI verifies examples against the Schema |
| 6 | **Chinese coupling** | Default directory names, error messages and in-figure text are Chinese | `--lang {zh,en}` at the code layer; content (template copy, specifications) is not translated, avoiding half-baked localisation |
| 7 | **Host fragmentation** | Only Claude Code installation is documented | Document the general rule (copy the skill directory into the host's skills directory); add host notes as feedback arrives |
| 8 | **Single-maintainer bandwidth** | Limited review and merge capacity | Push everything machine-decidable to CI and reserve human review for **semantics and originality** (§7) |
| 9 | **Variable contribution quality** | Third-party templates may be semantically wrong (far worse than overflowing text) | The submission checklist requires measured character budgets and explicit semantic conventions; the PR template confirms each item |
| 10 | **Over-engineering** | Toolbox-ification easily slides into abstraction-first design | Every facility must have a **present consumer** (CI, contributor or user); packaging and online services were explicitly rejected |

---

## 4. Modular Component Architecture

Three layers, coupled only through files and CLIs:

```
┌─ Contract layer (machine-readable) ───────────────────────────┐
│  code/tools/manifest.json (figures)                           │
│  code/templates/manifest.json (diagrams)                      │
│  code/templates/schema/*.schema.json (5 content contracts)    │
│  themes/theme.schema.json + themes/*.theme.json (palette)     │
└───────────────────────────────────────────────────────────────┘
              ▲ read registry, validate
┌─ Implementation layer (deterministic rendering) ──────────────┐
│  Figures: code/templates/make_*.py (20)  code/style/plot_style.py │
│  Diagrams: code/templates/*.py (5)       code/common.py        │
│  Tools: render_template.py  validate_content.py                │
│  Tools: validate_theme.py                                      │
│  Paper: paper.tex  word_postprocess.py  strip_invisible.py     │
└───────────────────────────────────────────────────────────────┘
              ▲ invoked by
┌─ Orchestration layer (judgement and process) ─────────────────┐
│  math-modeling-helper: six stages + writing rules + self-check │
│  + scoring                                                     │
└───────────────────────────────────────────────────────────────┘
```

**Inviolable constraint: skill directories are self-contained.** Each `skills/<name>/` must work after being copied
alone into a host's skills directory. This rules out a shared cross-skill Python package and explains why cross-skill
consistency is enforced by **CI checks** rather than by `import`.

**Interface boundary**: inter-layer communication has exactly three forms — (1) read the registry and Schemas;
(2) invoke a CLI and judge by exit code; (3) read/write files at agreed paths. Direct cross-layer imports of
implementation details are forbidden.

**Phase 3 candidate (conditional)**: only if a real need emerges for third-party programs to call the renderer as a
library — not a hypothetical one — will we evaluate extracting an installable namespace package (with a compatibility
layer for in-directory relative paths). Current evidence is insufficient; not doing it now.

---

## 5. Data Model Standardisation

### 5.1 Naming and versions

| Item | Rule |
|---|---|
| Template id | kebab-case (e.g. `problem-flow`, `grouped-bar`), mapping one-to-one onto snake_case script names |
| Contract version | Each registry carries `schema_version` (currently `1.0`); Schemas declare Draft 2020-12 via `$schema` |
| Project version | Root `VERSION` is the single source; `CHANGELOG.md` must contain that version's section (CI-enforced) |

### 5.2 Path resolution (removing ambiguity)

An ambiguity about "relative to what is `script`?" surfaced during Phase 1 and was resolved with an **explicit field**:

- `script_dir`: the directory holding template scripts, relative to the **registry's own directory**;
- all other path fields (`example`/`preview`/`schema`/`doc`): relative to the **registry's own directory**.

The rule is stated in each registry's `description` and applied identically by the CLI and by CI.

### 5.3 How strict should a content contract be?

- **Required fields** come from the code's actual behaviour: only fields accessed via `need()` or `c['key']` are required;
  fields read with `.get(default)` are optional. The contract must not be stricter than the code, or it would reject
  valid input.
- **Exception**: the five-band roadmap requires `band1..band5`. The code defaults missing bands, but a roadmap without
  bands is a broken figure, so the Schema promotes them to required and explains why in `description`.
- **`additionalProperties: true`**: permits `_comment` and future extension fields, so that "adding a comment" does not
  break validation. The contract constrains **structure and values**, not a closed field set.

### 5.4 Compatibility rules

- `MINOR`: new optional fields, new templates, new Schemas;
- `MAJOR`: removing CLI parameters, removing registry fields, **expanding** the required set, tightening enums;
- `PATCH`: documentation, examples, error messages and implementation fixes.

---

## 6. Open API Design

For a skill set, "open API" means **three interface surfaces others can depend on**, not an HTTP service.

### 6.1 Surface 1: CLI contract (for users and agent hosts)

| Command | Key flags | Purpose |
|---|---|---|
| `code/tools/render_template.py <id\|alias\|Chinese fragment>` | `--list`, `--list --json`, `--theme`, `--list-themes`, `--project`, `--overwrite`, `--lang` | Figure rendering (`--theme` swaps the palette; the default theme can be omitted) |
| `code/tools/render_template.py <id> <content.json>` | `-o/--out`, `--check`, `--list`, `--lang` | Unified diagram entry point |
| `code/tools/validate_content.py <id> <content.json>` | `--all`, `--schemas`, `--lang` | Content-contract validation |
| `code/tools/validate_theme.py [<theme files>...]` | `--all`, `--list`, `--lang` | Theme-contract validation |
| `code/word_postprocess.py [paper.docx]` | — | Word layout fine-tuning |
| `code/strip_invisible.py <files...>` | `--clean`, `--no-backup` | Invisible-character scrubbing |

**Unified exit-code semantics**: `0` success / `1` validation or rendering failure / `2` usage or environment error.
This is what lets other programs orchestrate the scripts — machines only read exit codes.

### 6.2 Surface 2: registries and Schemas (for programs and third parties)

`manifest.json` is the equivalent of `--list --json`: id, script, title, group/canvas, aliases and CJK hints, example and
preview paths, authorship. Third parties can **enumerate capabilities and generate documentation or their own front ends**
without reading source code.

`themes/theme.schema.json` is a second kind of data contract: colour is declared against four roles (identity /
baseline / direction / hierarchy). The renderer writes the chosen theme into the workspace as `scripts/theme.json`,
and the style module resolves it as "same directory → bundled default → built-in fallback". Colour therefore becomes
**replaceable data**: third parties can publish their own themes, programs can switch them in bulk, and CI can validate
their structure. Known boundary: themes cover the 9 figure templates that share the style module plus figures drawn with
that module; the other 11 templates and the 5 diagrams keep their palettes in their script headers (an implementation
detail — editable in the workspace copy, but not part of the contract layer).

### 6.3 Surface 3: importable Python functions (for scripts in the same repo)

`resolve_template()`, `load_manifest()`, `validate()`, `script_path()` and friends are exposed as module functions for
reuse inside the same skill (`validate_content.py` reuses the unified entry point's resolution logic via `sys.path`).
They are **not premised on being pip-installable**, so no package-level API stability is promised.

### 6.4 Stability tiers

| Tier | Scope | Commitment |
|---|---|---|
| **Stable** | The CLI parameters and exit codes above, registry fields, theme-contract fields (the `roles`/`cmaps` structure and field names), `schema_version` semantics | Breaking changes require a `MAJOR` bump and a CHANGELOG entry |
| **Experimental** | Exact wording of `--lang`, field order in `--json` output, error message phrasing, the default theme's specific colour values (content) | May change at any time; not treated as breaking |
| **Internal** | Geometry constants inside template scripts, primitive signatures in `common.py` / `plot_style.py` | No commitment; in-repo use only |

---

## 7. Third-Party Contribution Mechanism

### 7.1 Contribution paths (lowest to highest cost)

1. **New template**: write the script → add `docs/templates/<id>.md` (per-slot character budgets and semantic
   conventions) → add `example.json` and `preview.png` → **add one line to the registry**. CI validates all other
   consistency; **no changes to the CLI, CI or index docs are needed**;
2. **Improve an existing template**: edit the script → re-render the preview → update the budgets;
3. **Docs and examples**: corrections and additional scenarios;
4. **Bug reports**: with a minimal reproduction (content JSON + command + expectation).

### 7.2 What machines check vs what humans review (the key split)

| Decided automatically by CI | Human review only |
|---|---|
| Syntax, successful rendering, non-empty artifacts | Whether slot **semantics** are right (misplaced parallel/convergent/comparative meaning is far worse than overflowing text) |
| Registry ↔ filesystem ↔ index docs consistency | Whether the copy is faithful to the source material (fabrication forbidden) |
| Schema validity, example compliance | Whether character budgets were measured (guessing is not allowed) |
| Version ↔ CHANGELOG ↔ README badges | Whether it deserves to be a template (one-off figures are faster hand-drawn) |

This split is what makes **single-maintainer operation** possible: machines absorb mechanical checking, humans spend time
on judgement.

### 7.3 Review criteria

- Mandatory: green CI; `example.json` filled with real content (no placeholders); docs include budgets and semantics;
- Bonus: the template covers a recurring figure type; a stress configuration at the boundary counts is provided;
- Rejected: fabricated data or references; wrong semantic labelling; appearance-only changes that break existing contracts.

### 7.4 Attribution and licence

Contributing implies agreement to distribute under Apache-2.0; template authors are permanently credited in the
registry's `author` field (§8).

---

## 8. Contributor Incentive System

Open-source incentives need not be monetary — **the scarce goods are visibility and attribution**. Design principle:
**no empty promises, no empty files**.

| Tier | Behaviour | Visible reward (already or newly delivered) |
|---|---|---|
| L1 Bug report | With minimal reproduction | CHANGELOG "Fixed" entry + release-notes thanks |
| L2 Docs and examples | Corrections, extra examples | As above |
| L3 Template contribution | A reusable new template | Permanent credit in the registry `author` field; listed alongside official templates in the catalogue |
| L4 Long-term maintenance | Sustained review and governance | Listed as co-maintainer in the §11 roadmap |

Supporting mechanisms: `CHANGELOG.md` groups changes by type (Added/Changed/Fixed/Docs) so contributions are searchable
in history; `release.yml` generates release notes from the CHANGELOG, so publishing doubles as acknowledgement.

**Explicitly not done**: no empty `CONTRIBUTORS.md` (no content means no incentive, and it looks perfunctory);
no points, tokens or rankings (we cannot honour them).

---

## 9. Release and Versioning Strategy

### 9.1 Cadence and version

- Semantic versioning; `VERSION` is the single source;
- This plan corresponds to **`1.1.0`** (backward-compatible capability additions);
- Release action: push a `v*` tag → `release.yml` verifies "tag == VERSION == CHANGELOG section" → generates release notes.

### 9.2 Compatibility commitments

| Surface | Commitment |
|---|---|
| CLI parameters and exit codes | Removal or semantic change requires `MAJOR` |
| Registry fields | Field removal requires `MAJOR`; new optional fields are `MINOR` |
| Content Schema | Expanding the required set or tightening enums is `MAJOR` |
| Artifact formats and paths | Treated as Stable (user scripts may depend on them) |

### 9.3 Environment and dependencies

- Python: CI pins 3.12 as the **minimum verified version**; documentation now matches it (a previous 3.12 vs 3.14
  inconsistency was fixed);
- Optional dependencies: `jsonschema` (strict validation; falls back to a built-in minimal validator), `pymupdf`
  (PDF scrubbing mode only);
- External tools: `xelatex`, `pandoc`. The paper skeleton's Latin font now uses a **fallback probe**
  (Times New Roman → TeX Gyre Termes), so CI no longer patches the source.

---

## 10. Competitive Landscape and Differentiation

### 10.1 State of the field (external information, sources cited)

| Project / platform | Form | Key capabilities | Positioning |
|---|---|---|---|
| MathModelAgent | Open source (~5000 stars) | SKILLS-based pipeline, 17 Chinese/English Typst contest templates, built-in modeling knowledge base (model-selection decision tree, common pitfalls, scoring criteria), multi-LLM via litellm, local Jupyter or cloud sandbox, human-in-the-loop approvals; desktop app and hosted version | End-to-end "paper in an hour" |
| math-modeling-skill | Open-source skill | Three-stage collaboration (modeling/coding/writing), 60+ algorithms in 7 categories, integrates pdf/xlsx/docx/paper_search sub-skills | Three-stage full pipeline |
| MM-Agent (HKUST-GZ) | Paper + code | MM-Bench (111 MCM/ICM problems), four-stage modeling; reported 15 minutes and ~$0.88 per task, and assisted two teams to a Finalist award at MCM/ICM 2025 (top 2.0% of 27,456) | Academic benchmark + modeling copilot |
| ModelingAgent (UIUC) | Paper | ModelingBench plus ModelingJudge (expert-in-the-loop review), multi-agent self-refinement | Academic benchmark |
| LabAgent | Open-source multi-agent | Fully automated paper production (incl. modeling contests), arXiv/Semantic Scholar retrieval, sandboxed execution, four-dimensional peer review, fact checking | General academic production |
| Modex / MH-Agent v2.0 | Platform | 53+ skills, 12+ contests, four rounds of automated review, ≤6h average delivery | Commercial academic automation |
| MathModel Agent Resources | Open-source index | 32 catalogued projects, pinned commits, SHA-256 verification, machine-readable JSON/CSV; evaluated on task coverage, human/machine boundary, evidence chain, reproducibility, security, licence and contest compliance | Ecosystem discovery layer |

### 10.2 Reading the landscape

- **The field is crowded and homogenised**: the dominant route is "multi-agent + LLM, fully automated", competing on
  template counts, supported contests and delivery speed;
- **The hidden cost is widely underrated**: fully automated routes struggle to prove **numeric traceability** (can every
  number in the paper be traced back to a script artifact?), which is precisely what reviewers and compliance care about;
- **An evaluation layer has already appeared** (last row above) whose dimensions — evidence chain, reproducibility,
  licence, human/machine boundary — overlap heavily with the weak spots of the automated route.

### 10.3 Our differentiation (four verifiable advantages)

1. **Determinism and reproducibility**: diagrams are driven by content JSON and figure templates ship with seeded data,
   so any artifact can be re-rendered and re-edited — against the pain point that "LLM output differs every run";
2. **Machine-enforced quality gates**: overflowing text exits non-zero, CJK text width is measured per slot before
   rendering, registry/document consistency is checked in CI, and the paper has a self-check list and a 100-point scoring
   rubric — turning as much as possible from "eyeballed" into "decidable";
3. **Anti-fabrication constraints**: no invented references or data, simulated data may not be presented as reproducing
   real results, and every number in the paper must be traceable;
4. **Delivery consistency**: PDF and Word outputs with layout parity checks plus **zero-width / invisible character
   scrubbing** (including PDF-level ToUnicode reverse lookup) — the last mile most peers do not cover.

**Ecological niche**: instead of competing head-on as a ghostwriting platform, be the **deterministic toolbox layer callable
by any host or pipeline** — making figures, tables, diagrams, typesetting and delivery checks into components others dare
to depend on.

### 10.4 Compliance stance

Contest rules on AI vary and are tightening. This project positions itself explicitly as an **efficiency and verification
tool**: mechanical correctness (reproducibility, no clipping, traceable numbers, format compliance) goes to the tools, while
**model selection, result interpretation and statements of originality remain with the human**. This is not a concession
to limited capability but a **durable position**: it does not depend on how tolerant contest rules are of ghostwriting.

---

## 11. Roadmap and Expected-Outcome Criteria

### 11.1 Three phases

| Phase | Goal | Content | Status |
|---|---|---|---|
| **Phase 1** | Contracts and governance | Registries, JSON Schemas, unified CLI, validator, palette theme contract, CONTRIBUTING, VERSION/CHANGELOG, release flow, font fallback and `--lang`, de-hardcoding CI | **Delivered** |
| **Phase 2** | Ecosystem and distribution | Multi-host installation notes; registration with community index directories; contributor case studies; English documentation and Schema field descriptions aligned; extend theme control to the remaining 11 figure templates (removing the dual palette path) | Not started |
| **Phase 3** | Open components | Evaluate on real demand: an installable namespace package / a stable Python API for third-party embedding. **Trigger**: a concrete third-party programmatic need | Conditional |

### 11.2 Phase 1 outcome criteria (KPI)

| Metric | Baseline | Phase 1 target | Measured | How it is measured |
|---|---|---|---|---|
| Manual edit points to add a template (excluding the new script and example themselves) | 4 (registry/index doc/SKILL/CI count) | **2** (one registry line + one index row) | 2 (CLI, CI and version files need no changes) | Count while following CONTRIBUTING |
| Machine-readable contract coverage | 0 / 25 | 25/25 registered + 5/5 content Schemas | 25/25 + 5/5 | CI `manifest-consistency` |
| Hardcoded template-count assertions in CI | 4 | **0** | 0 | Search for `-ne 20` and the fixed tuple |
| Resolution-behaviour regression | — | Migration changes no resolution result | 81 cases, 0 mismatches | Case-by-case comparison with the pre-migration dicts |
| Governance documentation | None | CONTRIBUTING ×2, PR/Issue templates, VERSION, CHANGELOG, release flow | All present | File existence + CI checks |
| Environment patch dependency | CI `sed` for fonts | **0 patches** | 0 | `paper.yml` contains no `sed` |
| Content-contract validity | No Schemas | 100% of examples pass strict validation | 5/5 (including strict jsonschema mode) | `validate_content.py --all` |
| Palette swappability | 0 (hardcoded in code constants and script headers; source edits only) | Declared theme + CLI switch + Schema validation + CI rejects invalid themes | Delivered: 1 default theme covering the 9 module-based templates and hand-drawn figures; colour equivalence confirmed by point-by-point comparison at 101 samples | `--theme` / `validate_theme.py --all` / CI `Theme contract validation` |

### 11.3 Review cadence

- Every merge: CI checks machine metrics (rows 2, 3, 5, 7 above) automatically;
- Every release: `release.yml` verifies the version agrees in three places (`VERSION`, tag, CHANGELOG);
- Every phase end: humans re-check rows 1 and 4, which require hands-on practice and comparison and cannot be automated.

---

## Sources

- [MathModelAgent, a ~5000-star open-source project (article)](http://m.toutiao.com/group/7684810630658638399/)
- [Math Modeling Skill: a skill for mathematical modeling contests](https://juejin.cn/post/7616936839875395618)
- [MM-Agent: LLM as Agents for Real-world Mathematical Modeling Problem (arXiv:2505.14148)](https://arxiv.org/pdf/2505.14148v1)
- [ModelingAgent: Bridging LLMs and Mathematical Modeling for Real-World Challenges (arXiv:2505.15068)](https://arxiv.org/pdf/2505.15068)
- [LabAgent-MutiAgentSystem project description](https://www.proginn.com/w/1585562)
- [Modex / MH-Agent v2.0 platform](https://www.mingheng.xin/)
- [32 math-modeling AI agents and skills, catalogued](https://agent.csdn.net/6a9d1f3e48977663a5dd6a46.html)
- [A practical math-modeling competition toolbox (CSDN)](https://adg.csdn.net/6a31169110ee7a33f27dde42.html)
