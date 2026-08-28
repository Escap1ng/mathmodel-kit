# mathmodel-kit

> A one-stop skill kit for mathematical modeling competitions — from problem analysis, model building and algorithm implementation to publication-quality figures and paper production.
>
> [中文 →](README.md)

## Overview

The kit ships four coordinated agent skills: one orchestrator governs the whole pipeline, while three specialists cover data figures, academic diagrams and paper output. Each works standalone; together they close the loop.

| Skill | Role |
|---|---|
| [`math-modeling-helper`](skills/math-modeling-helper/SKILL.md) | Orchestrator · problem analysis, algorithm selection, code implementation, paper writing & grading |
| [`mathmodel-figure`](skills/mathmodel-figure/SKILL.md) | Data figures · 20 matplotlib templates plus a Nature figure standard for hand-drawn chart types, one command to PNG / PDF / SVG |
| [`mathmodel-diagram`](skills/mathmodel-diagram/SKILL.md) | Academic diagrams · 5 JSON-driven templates (roadmap / framework / flow / problem analysis) |
| [`mathmodel-paper`](skills/mathmodel-paper/SKILL.md) | Paper output · LaTeX skeleton → PDF → Word, plus layout fine-tuning |

## Highlights

- **Full-pipeline coverage** — a single entry point runs "problem understanding → model building → algorithm implementation → paper output" end to end; specialist skills remain independently callable.
- **Publication-grade by default** — data figures at 300 DPI, vector-first, with a unified Nature-style palette (identity / direction / hierarchy roles) and Arial sans-serif typography; diagrams validate CJK text width slot by slot and fail loudly on overflow.
- **Deterministic & reproducible** — figure templates ship seeded simulation data; diagrams are driven by content JSON, so every artifact can be re-rendered and revised at any time.
- **Machine-checked quality gates** — non-zero-exit capacity checks, nine-zone inspection, red-team review and a self-scoring card jointly constrain delivery quality.

## Repository Layout

```
mathmodel-kit/
├── README.md                   # Chinese docs (see README_EN.md for English)
├── LICENSE                     # Apache License 2.0
└── skills/
    ├── math-modeling-helper/   # Orchestrator: full-pipeline rules & grading criteria
    ├── mathmodel-figure/       # code/ templates & style · docs/ figure rules · examples/ previews
    ├── mathmodel-diagram/      # code/ renderers · docs/ methodology · examples/ reproducible samples
    └── mathmodel-paper/        # LaTeX skeleton · Word fine-tuning script · abstract template
```

## Quick Start

**Install** — copy the desired skill directories under `skills/` into your agent's skill directory (e.g. `~/.claude/skills/`):

```bash
cp -r skills/mathmodel-figure ~/.claude/skills/
```

**Data figures**

```bash
cd skills/mathmodel-figure
python3 code/tools/render_template.py --list             # list all 20 template ids
python3 code/tools/render_template.py paired-raincloud   # accepts id / English alias / Chinese title
```

**Academic diagrams**

```bash
cd skills/mathmodel-diagram
python3 code/templates/roadmap_5band.py content.json -o out.png   # PNG 300dpi + matching vector PDF
python3 code/templates/roadmap_5band.py content.json --check      # capacity check only, writes nothing
```

**Paper** — copy `templates/paper.tex` into your workspace and fill in the placeholders, compile twice with `xelatex`, convert to Word with `pandoc`, then fine-tune the layout with `code/word_postprocess.py`; abstract writing guide in `templates/abstract-template.md`.

## Dependencies

- Python 3 with `matplotlib` / `seaborn` / `numpy` / `pandas`
- Paper output additionally requires `xelatex` (with CJK font support) and `pandoc`; Word layout fine-tuning requires `python-docx`

## License

[Apache License 2.0](LICENSE)
