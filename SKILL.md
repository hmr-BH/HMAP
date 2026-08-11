---
name: human-maintainability
version: 1.0.2
description: "Assess a programming project's HUMAN maintainability (HMAP): 0-100 score, nine-tier verdict, per-dimension scores, and file:line evidence — built to catch vibe-coding / AI-generated slop. Triggers: assess maintainability / rate this project / code quality score / readability score / AI slop detection / vibe coding check / HMAP / human maintainability / 评估项目可维护性 / 给项目打分 / 代码质量评估 / 可读性评分 / AI屎山检测 / vibe coding 体检 / 是否适合人类维护. Anti-trigger: the user asks to fix, refactor, optimize, or write code — that is a different task; this skill only assesses, never modifies."
---

# human-maintainability (HMAP)

Human Maintainability Assessment of Programming Projects — scores whether a project is maintainable by **human programmers** (0-100, nine tiers), with dedicated forensics for vibe-coding / AI-generated slop.

**Core principle: assess only, never modify.** No refactoring, no bug fixes, no touching source files; findings go into the report, period.

## Trigger / anti-trigger

- **Trigger**: the user asks to "assess maintainability / score this project / check for AI slop / rate code quality / is it human-maintainable" for any path, with the target given or inferable.
- **Anti-trigger**: the user wants bugs fixed, refactoring, features, or performance work — do NOT apply this skill. If asked to "assess then fix", finish the assessment first; handle fixes only under a new instruction.

## Scoring model (4 weighted dimensions, 100 max)

> **Read before scoring**: this is a **human readability & maintainability** assessment, not a style-compliance review — comment coverage, naming consistency, DRY and similar "standards" earn no points by themselves, only when they serve human understanding and maintenance. **Core question**: after reading the code, ask yourself "if this project were handed to you, would you maintain it yourself? Why?" The total score must agree with the answer.
>
> **Black cat, white cat — equal treatment**: AI authorship, project size, and maintainer count are NEVER scoring criteria — only whether the artifact obstructs human maintenance. READMEs are checked only for promise fulfillment (tidiness/ads/marketing/absence are not penalized).

| Dimension | Weight | Key question |
|---|---|---|
| D1 Design soundness & technical honesty | 25 | Does the architecture match the problem's complexity? Do promises survive code verification? Real engineering thinking (measurement/trade-offs) or wishful thinking? Do tests give maintainers safety? |
| D2 Traceability & mental load | 30 | Can a human trace request → code? Clear responsibilities or everything fused together? Change one thing — how many places must you know? Must the structure be memorized via external docs? |
| D3 Human readability & self-explanation | 15 | Does the code explain itself? Do names/comments convey "why", or are they decorative / written for AI? |
| D4 AI slop & wishful-thinking residue (reverse) | 30 | Promise betrayal, over-engineering, source-inlined AI process markers, structural gods (big AND mixed), systemic copy-paste, debug residue, hallucinated comments — more residue, lower score |

Score each dimension 0-100, weight-sum, then apply structural hard gates. **Detailed rules (M1-M13 measurement table, tier mapping, RM responsibility-mixing protocol, tie-breaks): [`references/scoring-rubric.md`](references/scoring-rubric.md); signal catalog: [`references/ai-slop-signals.md`](references/ai-slop-signals.md); worked scoring example: [`references/golden-example.md`](references/golden-example.md).**

> **Structural hard gates (pass-line verdicts)**: structural facts that make human maintenance impossible or infeasible hard-cap the total — core god-function/god-file that is also responsibility-mixed → **60** (pass-line edge); source-inlined AI process markers at scale → **45**; AI debugging residue in hot paths ≥5 (coordinate/offset special-cases, magic offsets, embedded debugging narratives, probe residue; **ordinary bare printlns excluded**) → **45**; **G1 together with G3/G4 → 40**. Dimension scores may not lift the total above a cap. **Gates judge structure only — never size, headcount, or AI authorship**; top-level convention files (AGENTS.md/CLAUDE.md etc.) are not AI process markers.

## Nine tiers (60 is the split: ≥60 pass = human-maintainable; <60 fail = unfit for direct human maintenance)

| Range | Verdict |
|---|---|
| 90-100 | **Ideal**: clear responsibility boundaries, request→code traceable, comments explain "why", all promises kept |
| 80-90 | **Smooth**: generally fluent, only acceptable debt; **no structural mixing, no AI fingerprints at scale** |
| 70-80 | **Burdened**: cross-file tracing costs, a few bloated spots, or minor AI traces |
| 60-70 | **Pass-line edge**: visible AI-slop traces or structural bloat emerging (god-file/bloated functions); takeover is hard but humans can still maintain it |
| 50-60 | **Fail — unfit for direct human maintenance**: severe responsibility mixing, poor readability; takeover cost disproportionate |
| 40-50 | **Unfit**: core bloated, structure untraceable; external docs/AI required to understand |
| 30-40 | **Unfit (heavier)**: structural gods rampant; humans cannot change code safely |
| 20-30 | **Extremely unfit**: structural gods + AI process fingerprints everywhere |
| 0-20 | **AI-agent-only**: total slop, beyond rescue |

Boundary semantics: `>=90` lands in the 90 tier; and so on; `<20` in the 0 tier.
**The 60 split is this skill's anchor**: ≥60 = pass = a human programmer can maintain it (matching cent exam intuition); <60 = fail = unfit for direct human maintenance. Tier descriptions encode the "can humans maintain it" judgment, not surface quality — structural mixing lands below 60; AI fingerprints at scale land below 60.

## Assessment workflow

**Before starting you MUST read** [`references/scoring-rubric.md`](references/scoring-rubric.md), [`references/ai-slop-signals.md`](references/ai-slop-signals.md), and [`references/golden-example.md`](references/golden-example.md) to align scoring lenses and calibration.

### Step 1: parse arguments

- **Target path** (required): the project directory, relative or absolute; defaults to the current working directory.
- `--depth=light|medium|deep` (optional): sampling intensity. Default medium.
- `--output=path` (optional): write the full report to the given markdown file.
- `--focus=dimension` (optional): assess only the named dimension (D1 design / D2 traceability / D3 readability / D4 slop); no total score.

### Step 2: inventory

Glob / Grep / Bash: total file count and file tree (exclude dependency & build dirs: `node_modules`, `.git`, `dist`, `build`, `venv`, `target`, `__pycache__`, `.next`, `bin/Release`, `obj`, etc.); language mix and estimated total LOC; locate README, build/package entry, entry file, test directories.

### Step 3: sampling protocol

Sample and **declare the sampling scope and confidence**. Unread files must not be scored as if read.

| Project size | Sampling strategy | Default reads |
|---|---|---|
| ≤50 source files | read all | all |
| 50-500 | entry + core modules + per-layer representatives + largest files + most-commented files | 15-30 files |
| >500 | stratified sampling: entry, business core, boundary/infra | 30-60 files |

Must-read regardless of size: README, build/package entry, entry file, largest source file, most recently modified files. `--depth=deep` doubles the read count; `--depth=light` halves it. **Repeated evaluations must fix the same sampling depth.**

### Step 4: per-dimension forensics

- **Measure first (mandatory before scoring)**: run M1-M13 from the rubric's global measurement table and fill the sheet. **Measured values decide tiers — before impressions.**
- **Promise verification (mandatory)**: list README/doc promises → verify each in code (claiming "performance gains" while only adding abstraction layers, claiming "extensible" with no extension points ⇒ major wish evidence). README: promises only; tidiness/ads/absence not penalized.
- **Responsibility mixing via the RM protocol**: every ≥400-line function / ≥1800-line file goes through RM (enumerate domains → count → precedents → arbiter) for "single responsibility vs mixed". Big-but-single is not penalized; bloat is.
- **Boundary decisions**: when a measurement lands on a boundary or signals conflict, record a boundary decision per rubric rule 8 (object / both-side reasoning / final choice / evidence) — no systematic rounding to either side.
- Every scoring judgment must land on `file:line` evidence; impressions without evidence may not be used.

### Step 5: weighted scoring & structural gates

- Per the rubric's measurement→anchor tables: tier per dimension → enumerated adjustments → four raw scores.
- Weighted total = 0.25×D1 + 0.30×D2 + 0.15×D3 + 0.30×D4; apply hard gates (G1/G3/G4; multiple hits → lowest cap).
- **Forced judgment**: honestly answer "would you maintain it yourself? Why?" — "no" ⇒ total ≤60, "absolutely not" ⇒ ≤40. If the answer says so but the total hasn't reached the cap, you were dazzled by surface discipline (tests/CI/docs) — lower it.
- **60-split check (mandatory, the anchor)**: answer "which side of the 60 line — ≥60 pass (human-maintainable) or <60 fail (unfit)?" A <60-side answer with total ≥60 ⇒ the mechanical score was fooled by surface quality — **force it below 60**; a ≥60-side answer with total <60 ⇒ recheck measurements. **On conflict, the answer wins.**
- Map the total to the nine tiers; round to integer.
- **Scoring discipline**: evidence-based, neither inflated nor soft; declare low confidence when evidence is thin; totals differing by >3 across two evaluations ⇒ run the rubric's consistency self-check — no bargaining.

### Step 6: report

- **Output language rule (mandatory): the final report MUST be written in the same language as the user's input** (user writes Chinese ⇒ report in Chinese; English ⇒ English; and so on). The skill text itself is English; this rule governs only the delivered report.
- Default: full report in the conversation. With `--output`: a condensed version in the conversation, the full report written to the file — state the path.

## Report template

```markdown
## HMAP Report: <project name> (<target path>)

**Total: XX/100 — <tier verdict>**

Scope: N source files, M read (depth: light/medium/deep), confidence: high/medium/low. Measurement sheet: key M1-M13 values (≤5 lines).

### Dimension scores

| Dimension | Raw | Weight | Weighted | One-line rationale |
|---|---|---|---|---|
| D1 Design soundness & honesty |  | 25 |  |  |
| D2 Traceability & mental load |  | 30 |  |  |
| D3 Readability & self-explanation |  | 15 |  |  |
| D4 AI slop & wishful residue |  | 30 |  |  |

### Overall assessment

(3-5 sentences: overall impression and main tensions)

### Strengths (evidenced)

- `file:line` — strength

### Key problems (evidenced, most severe first)

- `file:line` — problem

### AI-slop findings

- `file:line` — slop signal (cite the signal number/name from `references/ai-slop-signals.md`)

### Evidence appendix (mandatory)

- Comment sample classification: every sampled comment → I/R/S/H with its classification reason
- T_trace hop lists for the 3 probed journeys; T_impact probe result; D (decorative abstraction) enumeration
- All boundary decisions (object / both-side reasoning / final choice / evidence)

### Conclusion & recommendations

- Fit for human maintenance? (nine-tier verdict)
- If <60: the 1-3 worst concentrations, and whether a human or an AI agent should fix them
- Hard gates hit (if any) + forced-judgment answer
- Optional improvements (suggest only, never implement)
```

## Boundary discipline

1. **Assess only, never modify**: no refactoring, no bug fixes, no touching any source file.
2. **No fabricated evidence**: judgments without `file:line` evidence may not enter the report; verify the cited line exists before citing.
3. **Honest scoring**: the score must be derivable from the measurement sheet and tier tables; declare thin sampling; prefer low confidence over inflation.
4. **Stay in scope**: with `--focus`, assess only that dimension.
