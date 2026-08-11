# HMAP
> Human Maintainability Assessment of Programming Projects

**A 60-point passing line: judging whether a project is worth handing over to human maintenance.**

`HMAP` is a skill that assesses the **human maintainability** of a programming project, targeting Vibe Coding and AI-generated code. It outputs a 0–100 quantitative score with a nine-tier qualitative verdict. **Scores above 60 mean humans can participate in maintenance; below 60 suggests refactoring or handing it to AI.**

[English](README.md) | [中文](README.zh-CN.md)

---

## Why this Skill

AI generates code far faster than humans can understand it. A human-written project may be fully comprehensible today, but after two weeks of AI iteration, even the original author struggles to understand it.

HMAP evaluates project code in depth from multiple angles:
- Oversized files with mixed responsibilities make a single-point change ripple everywhere
- Over-encapsulation disconnected from actual business needs
- Copy-pasted similar logic makes maintenance a struggle
- README promises that don't match actual implementation
- Temporary AI-generation markers and debug code left in production
- ...

The assessment is built on **13 objective metrics** and **hard structural gates** — it rejects vague "overall it's fine" judgments. If a project scores below 60, human programmers will find maintaining it confusing and painful.

## Scoring Guide

| Score | Tier |
|-------|------|
| 90-100 | **Suitable, excellent experience**: clear responsibility boundaries, traceable request→code, comments explain "why", promises fully delivered |
| 80-90 | **Suitable, smooth**: overall fluent, only a few acceptable debts; **no structural mixing, no large-scale AI process fingerprints** |
| 70-80 | **Suitable, with burden**: some cross-file tracing cost, a few mixed points or small AI traces |
| 60-70 | **Passing-line edge: barely maintainable**: obvious AI slop traces or structural mixing signs (god-file/messy functions), humans can still take over with effort |
| 50-60 | **Failing: not suitable for direct human maintenance**: severe responsibility mixing, poor readability, disproportionate handover cost |
| 40-50 | **Unsuitable**: core complexity, untraceable structure, must rely on external docs/AI to understand |
| 30-40 | **Unsuitable (worse)**: pervasive structural god objects, humans cannot safely modify |
| 20-30 | **Extremely unsuitable**: structural god + AI process fingerprints everywhere |
| 0-20 | **AI-agent-only maintenance**: complete slop, beyond saving |

---

## Installation

This skill follows the **Agent Skills standard** (`SKILL.md` + `references/`) and works with **any code agent that supports skills** — not limited to Claude Code (Cursor, Windsurf, Zed, Trae, etc.).

The install method is the same everywhere: copy this repo's `SKILL.md` and `references/` into your agent's skills directory, under a subdirectory named `human-maintainability/`.

Using **Claude Code** as an example (global install, available to all projects):

macOS / Linux:

```bash
mkdir -p ~/.claude/skills/human-maintainability
cp SKILL.md ~/.claude/skills/human-maintainability/
cp -r references ~/.claude/skills/human-maintainability/
```

Windows (PowerShell):

```powershell
$dst = "$HOME\.claude\skills\human-maintainability"
New-Item -ItemType Directory -Force "$dst\references" | Out-Null
Copy-Item SKILL.md $dst -Force
Copy-Item references\*.md "$dst\references\" -Force
```

**Other agents**: place the files in the skills directory specified by your agent's docs — e.g. Cursor's project-level `.cursor/skills/`, Windsurf's `.windsurf/skills/`, or the generic user-level `~/.skills/`. The directory must be named `human-maintainability/`, and `SKILL.md` and `references/` must stay in the same directory.

Project-level install (single project only): put both files in `<your-project>/.claude/skills/human-maintainability/` (or your agent's project-level skills directory).

---

## Usage

Trigger an assessment in a project directory:

- `/human-maintainability score this project`
- `assess the human maintainability of this project`
- `run an HMAP assessment`

Optional parameters:
- `--depth=light|medium|deep` — controls file sampling intensity (deeper = more thorough, shallower = fewer tokens). Default: `medium`
- `--output=<path>` — report file output path (none by default)
- `--focus=<dimension>` — focus on one dimension (`design` / `traceability` / `readability` / `ai-slop`); no total score is produced

---

## Project Structure

```
HMAP/
├── SKILL.md               # Workflow & report template
├── references/
│   ├── scoring-rubric.md  # M1-M13 metrics table & hard gates
│   └── ai-slop-signals.md # 14 AI low-quality signals
├── LICENSE
└── README.md
```

## License

[MIT License](./LICENSE)
