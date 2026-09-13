# Contributing

Thank you for helping `mathmodel-kit`. The project aims to make the **mechanically correct** parts of mathematical
modeling (figures, diagrams, typesetting, delivery checks) deterministic, reproducible and verifiable, while leaving
**modeling judgement** to the user. Contributions follow the same line.

> 中文版：[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 1. First, should it be a template at all?

**Do not turn one-off figures into templates** — hand-drawing per
`skills/mathmodel-diagram/docs/guides/authoring.md` or `skills/mathmodel-figure/docs/guides/nature-standard.md`
is faster.

A template is worth it only when a figure type is drawn repeatedly. Test: after swapping in new data and copy,
does the figure's **structure** still hold?

---

## 2. Development environment

- Python 3.12+ (CI pins 3.12 as the minimum verified version)
- Figures: `pip install matplotlib numpy seaborn`
- Diagrams: `pip install matplotlib numpy`
- Contract validation: `pip install jsonschema` (optional; the validator falls back to a built-in minimal checker)
- Paper pipeline: `xelatex`, `pandoc`, and `python-docx` for Word post-processing

Please run this locally before submitting:

```bash
python -m compileall -q skills
```

---

## 3. Directory conventions

The four skills are each self-contained. **Do not place files outside a skill directory** (`docs/` holds
external-facing planning documents only):

```
skills/<skill>/
├── SKILL.md            # skill contract: when to use it, how, and its boundaries
├── code/               # executable scripts (templates/, tools/)
├── docs/               # human-facing docs (guides/, templates/)
└── examples/           # examples and previews
```

---

## 4. Adding a template (the most common contribution)

### 4.1 Data-chart templates (`mathmodel-figure`)

1. Write `skills/mathmodel-figure/code/templates/make_<name>.py`
   - ship **seeded** simulated data (`np.random.default_rng(<fixed seed>)`) so results are reproducible;
   - use the shared palette via `from plot_style import ...` when needed (the renderer copies `plot_style.py`
     into the workspace automatically);
   - always emit PNG (300 DPI) + PDF + SVG named `<name>_replica.*`;
2. Register it in `skills/mathmodel-figure/code/tools/manifest.json` (fields as in existing entries:
   `id`, `script`, `title`, `group`, `aliases`, `cjk_hints`, `preview`, `author`);
3. Add a preview at `skills/mathmodel-figure/examples/previews/<name>_replica.png`;
4. Add one row to the catalogue table in `skills/mathmodel-figure/docs/templates/figure-catalog.md`.

### 4.2 Academic diagram templates (`mathmodel-diagram`)

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

---

## 5. Code style

- Python: 4-space indentation, standard library first; scripts use `argparse` with the existing flag style
  (`-o/--out`, `--check`, `--list`, `--lang`);
- **Exit-code semantics**: `0` success / `1` validation or rendering failure / `2` usage or environment error;
- Comments and docstrings are Chinese (matching the repository); user-facing messages are bilingual where
  `--lang {zh,en}` is supported;
- Do not add new formatter/linter toolchains (the repo does not depend on ruff/black/pytest);
- Do not commit generated artifacts (workspace directories, `.aux`, PDF/PNG outputs — see `.gitignore`).

---

## 6. Commits and pull requests

Follow the existing commit style: `<type>(<scope>): <summary>`, with `type` in
`feat` / `fix` / `docs` / `refactor` / `chore`; the body explains **why**, not what.

Please use the repository's PR template and tick each item. CI must be fully green:

| Check | Contents |
|---|---|
| `syntax` | All Python scripts compile |
| `manifest-consistency` | Registry ↔ filesystem ↔ index docs ↔ version ↔ README badges agree |
| `manifest-consistency` | Schemas are valid and all bundled examples pass strict validation |
| `figures` / `diagrams` | Every template renders non-empty artifacts |
| `strip-invisible` | The invisible-character scrubber round-trips correctly |
| `Paper LaTeX build` | The paper skeleton compiles |

---

## 7. Review criteria

What machines can decide (syntax, consistency, schemas, successful rendering) goes to CI. **Humans review only what
machines cannot:**

- whether slot **semantics** are right (misplaced parallel/convergent/comparative meaning is far worse than overflow);
- whether the copy is faithful to the source (**fabricating data or references is forbidden**);
- whether character budgets were **measured** (estimates are not accepted);
- whether it deserves to be a template.

Rejected: fabricated data or references; wrong semantic labelling; appearance-only changes that break existing
contracts (CLI parameters, registry fields, artifact paths).

---

## 8. Attribution and licence

The project is distributed under [Apache-2.0](LICENSE); contributing means agreeing to the same licence.

Template authors are credited **permanently** in the corresponding registry's `author` field and listed alongside
official templates; fixes and documentation contributions are recorded in [CHANGELOG.md](CHANGELOG.md) and thanked
in the release notes.

---

## 9. Code of conduct

Critique ideas, not people. Technical disagreements are settled by **reproducible evidence** (command, input, output),
not by seniority or volume. Plagiarism, data fabrication and invented references are never acceptable.
