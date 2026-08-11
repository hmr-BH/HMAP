# Golden example — a full scoring walkthrough

A synthetic worked example showing the mandatory S1-S6 flow: filled measurement sheet → per-dimension table lookups → boundary records → gates → 60-split → total. **Use it to calibrate how the tables are applied, especially at boundaries.** The project is fictional; the reasoning patterns are normative.

Subject: `quill`, a Python CLI static-site generator. 64 source files / 8,120 LOC; 12 test files / 1,900 LOC. Depth: medium (22 files read).

## S2 — measurement sheet

| # | Value | Notes |
|---|---|---|
| M1 | 64 files / 8,120 LOC | tests kept separate |
| M2 | max 1,940 (`quill/pipeline.py`); >1000: 1; 500-1000: 2 | one RM candidate |
| M3 | max function 210 lines; ≥400: 0 | no function candidates |
| M4 | 2 empty `except` | both commented `# best-effort: cache cleanup` |
| M5 | `cp-detect.py` → 1 group | 3 instances across `exporters/html.py`, `exporters/rss.py` (same template) |
| M6 | 12% | |
| M7 | 210 asserts / 12 files = 17.5; placeholders 0 | |
| M8 | 0 | |
| M9 | E_ai = 0; E_debug = 3 | bare `print()` in `quill/cli.py` bypassing the logger |
| M10 | 1.2‰ | |
| M11 | 3 TODOs, all with issue refs | |
| M12 | 0 | |
| M13 | none | |

**RM on the only candidate** — `quill/pipeline.py` (1,940 lines): blocks = config load → stage registry → stage dispatch → result aggregation → error mapping. One dataflow (input → stages → output); config/IO/error handling are chained support steps ⇒ R_file = 1 ⇒ **single responsibility** ⇒ no G1, never enters D2 yellow/red (HMCL/grok-build precedent).

## S3 — dimension scoring

### D1 (design & honesty): raw 95

- Promises: "plugin architecture" — verified: 2 real plugins registered (`quill/plugins/`); "fast rebuilds" — no benchmark claim in code, phrased as "rebuilds only what changed" — verified: incremental builder exists (`quill/incremental.py`). P_fail = 0, P_placeholder = 0.
- Decorative abstractions: 1 single-implementation interface (`ExporterBase`) with no test double, no polymorphic call site, no documented boundary ⇒ D = 1.
- Tests: T_placeholder = 0; T_assert/T_file = 17.5 ≥3; CI runs tests on every push.
- Table: P_fail=0 AND D≤1 AND T_placeholder≤2 AND real assertions ⇒ **90 tier, base 90**.
- Adjustments: P_placeholder=0 → +2; T_assert/T_file≥3 with core coverage → +2; CI routine → +1 ⇒ **95**.

### D2 (traceability & mental load): raw 84

- N_mixed = 0 (RM above). Cycles: none. ext_doc: no.
- **T_trace**: 3 journeys probed — `quill build`: `cli.py` → `engine.py` → `stages.py` → disk = 3 hops; `quill serve`: 3 hops; `quill deploy`: 2 hops ⇒ max 3 ⇒ **yellow**.
- **T_impact**: most-called business functions: `render_page` 4 call sites, `load_config` 5, `register_stage` 3 (logger/error-helper fan-out excluded per lens) ⇒ 5; a typical feature change (new stage type) touches 3 files ⇒ max(5,3) = 5 ⇒ **yellow**.
- **ND_max**: deepest control-flow chain = 3 (`stages.py:dispatch`), closures restart per lens ⇒ green.
- **Params**: 1 function with 8 required params (`engine.render(...)`) ⇒ **yellow** (≤2).
- Tier: 3 yellows ⇒ 90 − 3×2.5 = 82.5 → round half up ⇒ **83**. Adjustment: core hard spots carry why-comments → +1 ⇒ **84**.
- **Boundary record #1**: journey `quill build` — whether `engine.py`'s internal helper module counts as a hop was disputed (3 vs 4). Decision: the helper only reformats data in transit, same dataflow ⇒ not a hop ⇒ 3 hops. Either way yellow (4 still ≤5) — no tier straddle, no midpoint needed. Evidence: `quill/engine.py:88-140`.

### D3 (readability): raw 87

- Sampling frame: 5 largest files' body comments + 10 interval files ×2 = 28 comments.
- Classification: I=7, R=5, S=0 (file headers excluded), H=0 ⇒ R-share = 5/28 ≈ 18% ⇒ 15%~40% ⇒ **70-85 tier, base 85**.
- G(M10) = 1.2 <3; names fully semantic.
- Adjustments: G<3 + semantic names → +1; core hard spots have why-comments → +1 ⇒ **87**.
- **Boundary record #2**: `pipeline.py:410` — `# stages run in registration order: users depend on it for override semantics`. Disputed R vs I. Decision: **I** — the ordering guarantee is a contract the code doesn't state. Had it been R, R-share = 6/28 ≈ 21% — same tier (15%~40%), so no midpoint needed; recorded per rule 8 anyway.

### D4 (slop, reverse): raw 90

- Signals: CP 1 group (non-systemic, 3 instances, one template — fixing means editing one file cluster, not syncing call sites) = 1 human-normal-debt signal. E_debug = 3 <8 ⇒ no signal. Empty catches both best-effort ⇒ not C. M=0, E_ai=0, W=0, H=0, CD=0, DZ=0, TODOs=3 <5.
- Total signals = 1, all human-normal debt, zero fingerprints ⇒ **90 tier, base 90**. Zero-signal +1 n/a ⇒ **90**.

## S4 — gates

G1: RM single ⇒ no. G3: M=0 ⇒ no. G4: E_ai=0 ⇒ no. **No caps.**

## S5 — total

0.25×95 + 0.30×84 + 0.15×87 + 0.30×90 = 23.75 + 25.20 + 13.05 + 27.00 = **89.0 → 89**. Tier: 80-90, **"smooth"**.

## S6 — checks

- 60-split: clearly ≥60 side; total 89 agrees. ✓
- Core question: "would you maintain quill yourself?" — yes: traceable, tested, one big-but-clean pipeline file. Total agrees. ✓
- Calibration: profile ≈ "big but well-organized, slightly weaker" (~84) to "lovingly maintained" (90-93); 89 sits between, deviation ≤3 from the nearer band ⇒ no recheck needed.

## What this example demonstrates

1. **Big file ≠ penalty**: 1,940-line `pipeline.py` goes through RM, comes out single-responsibility, and never enters D2's yellow/red — line counts alone would have wrongly triggered G1.
2. **Boundary records beat gut rounding**: two disputed classifications recorded with evidence; neither straddled a tier after inspection — but had one straddled (e.g. R-share exactly at 40%), rule 8's midpoint applies, not systematic down-rounding.
3. **Lenses matter**: excluding logger fan-out from T_impact and counting only required params are what keep D2 reproducible.
4. **D4 stays mechanical**: 1 signal, human-debt class, zero fingerprints ⇒ 90 — no negotiation.
