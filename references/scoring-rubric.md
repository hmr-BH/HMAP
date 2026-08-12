# Scoring rubric (per-dimension)

> **Measurement-driven**: measure → look up the tier → adjust ±5 within the tier. Goal: two independent evaluations of the same project differ by ≤3 total points. Thresholds anchor to public research (cited by author/org: SIG, SonarSource, NASA/JPL). **Measurements decide tiers; qualitative judgment may only adjust within a tier — never jump tiers by impression.**

## General rules (read before scoring)

1. **This is a human readability & maintainability assessment, not a style-compliance review.** Naming consistency, comment coverage, DRY, documentation completeness earn no points by themselves — only when they genuinely help humans understand and maintain.
2. **Core question (enforced)**: anchor everything to "if this project were handed to you, would you maintain it yourself? Why?" The total must match the answer. An answer of "no"/"never" with a high total ⇒ you were dazzled by surface discipline (tests/CI/docs) — apply gates and lower the score.
3. **Black cat, white cat — equal treatment**: AI authorship, project size, and maintainer count are NEVER criteria; judge only whether the artifact obstructs human maintenance. READMEs are checked for promise fulfillment only (tidiness/ads/marketing/absence are not penalized). Top-calibration: a lovingly human-maintained project with why-comments, honest docs, and clear boundaries lands in the 90 tier (90-95); thin tests, a few big files, or occasional copy-paste are acceptable debt and do NOT justify dropping to the 80s unless they genuinely obstruct understanding or change.
4. **Human-normal debt vs AI process fingerprints**:
   - **Human-normal debt**: copy-paste, dead code, a few big files, a few dead exports, semantic debt (SC/CV signals) — no heavy penalty while they don't significantly obstruct understanding or change. Copy-paste is heavily penalized only when **systemic** (≥3 groups AND every change must be synced across ≥2 call sites). **Parallel-architecture exemption**: families organized one-variant-per plugin/provider/platform/loader, each variant carrying real differences (URLs, manifests, vendor quirks), are idiomatic symmetry — NOT systemic even when the sync condition holds.
   - **AI process fingerprints**: AI-coding-process markers inlined **in source files**, AI debugging residue in hot paths, systemic god-files/god-functions, **flood-scale copy-paste (≥6 template families, each with sync evidence)** — heavily penalized, can trigger hard gates. Top-level convention/doc files (AGENTS.md / CLAUDE.md / .github/instructions / copilot-instructions) are NOT fingerprints. **A fingerprint needs positive artifact evidence; ambiguous classification defaults to human-normal debt** — the conservative default survives ONLY in hard-gate judgments (rule 8's exception).
5. Weights fixed: D1 design 25 / D2 traceability 30 / D3 readability 15 / D4 slop (reverse) 30.
6. Anchors at 90/70/45/20; tiers come from the measurement→anchor tables; within a tier, base score + enumerated adjustments only.
7. **Objective measurement first**: anything Glob/Grep/Bash can count must be counted and tabled. After measuring, check the counting lens (comments miscounted? a big file actually single-responsibility — settled by RM, never by line count; grep hits polluted by comments or log-string prose?) — wrong lens ⇒ re-measure.
8. **Boundary records (no systematic rounding)**: when a measurement lands on a boundary or signals conflict, do NOT mechanically round to either side. Record a **boundary decision** — object, both-side reasoning, final choice, `file:line` evidence — and when the result straddles two adjacent tiers take their **midpoint** (rounded down). Claims without evidence count as "signal absent". **Exception: hard-gate judgments (G1/G3/G4) and RM mixing verdicts stay conservative** (ambiguous ⇒ mixed / larger R) — gates are a safety floor, not a score.
9. Insufficient evidence ⇒ 70 baseline with declared low confidence; never inflate.

## Scoring procedure (mandatory order)

| Step | Action | Output |
|---|---|---|
| S1 | Parse args; inventory per SKILL.md Step 2/3; fix sampling scope (same depth across runs) | file list, sampling declaration |
| S2 | Run the global measurement table M1-M15 | reproducible numbers |
| S3 | Per dimension: measurements → tier table → base + adjustments | four raw scores |
| S4 | Check hard gates G1/G3/G4 (multiple hits → lowest cap) | gate list |
| S5 | Weighted = 0.25×D1 + 0.30×D2 + 0.15×D3 + 0.30×D4; total = min(weighted, cap); round to nine tiers | total + tier |
| S6 | **60-split check (the anchor)** + core-question review: first answer "which side of 60 (≥60 pass = human-maintainable / <60 fail = unfit)", then "would you maintain it". Conflicts resolve to the answer (<60 side with total ≥60 ⇒ force below 60) | consistency confirmation |
| S7 | Calibration: profile-similar projects deviating >3 ⇒ recheck S2/S3 | drift check |

---

## Global measurement table (mandatory in S2)

Measure before any scoring. Record `file:line` evidence along the way.

| # | Item | How | Used by |
|---|---|---|---|
| M1 | Source file count, total LOC | Glob source extensions (exclude dependency/build dirs) → Bash `wc -l` | denominator |
| M2 | File-size distribution (max; counts >2000/1000/500) | `wc -l \| sort -rn \| head`; awk buckets | D2/G1 (distribution reference) |
| M3 | Function-size distribution (max; counts >500/200/60) | awk on function boundaries; record `file:line` for each >500. 60 lines ≈ one reviewable page (NASA/JPL), psychological reference only | D2/G1 (RM candidacy: ≥400) |
| M4 | Empty catch/except | Grep `except...pass`, `catch{}` (multiline) | D4 |
| M5 | Copy-paste groups (CP) | **Fixed procedure**: ① run `references/cp-detect.py` (6-line sliding-window exact-duplication detector; ignores blank lines, comment-only lines, indentation) for candidates; ② **merge near-duplicates (mandatory, two passes)**: first merge exact clones into template families, then merge structural twins — same control flow/statements, only identifiers/literals/type names differ — into the same family (all instances of one template = 1 group; instance count noted); ③ **reverse spot-check (mandatory)**: even when cp-detect returns 0, sample the 10 largest files plus filenames sharing a stem (`*CacheManager`, `*View`, `*Store`, numbered twins like `_v2`/`_v3`/`1`) for ≥6-line structural twins; ④ if the script can't run, manually enumerate in the 10 largest files. **Output to record per family**: instance count, files touched, and **sync evidence** (do bug fixes/features have to land in N places — check git history or call-site structure). A group needs ≥6-line clones at ≥2 locations (SIG Type-1) | D4 |
| M6 | Comment density | comment lines / (code+comment) ×100% | D3 extreme signal |
| M7 | Test assertion density | `assert\|expect\|Assert.` count ÷ test files; also placeholder asserts `assertTrue(true)`. **A vacuous assert does NOT count as a placeholder when its test body contains a compile-time check (e.g. `let _: any P.Type = T.self`) or another real assertion** | D1 |
| M8 | AI process markers | **Source files only** (exclude top-level convention files): explicit AI coding-round/tool artifacts — `Codex P\d\|CodeRabbit\|anchor.probe\|@anchor\|探针引用\|agent 复盘\|审查留痕\|修复轮次\|第X轮.*(修复\|复盘\|审查)\|review round`. (CJK pattern strings are detection targets — keep verbatim.) Bare "排查/修复/fix" does NOT count (normal engineering vocabulary) | D4/G3 |
| M9 | Debug residue in hot paths | Two steps: ① grep candidates `getenv\|fprintf\|console.log\|debugger;\|System.out.print\|IsBadReadPtr\|debug &&\|print(`; ② after excluding product-intent output (CLI stdout, structured logger, documented env config), count two classes: **E_ai — true AI debugging residue** (coordinate/offset-specific debug blocks `if (debug && pos.x==...)`, magic-offset memory checks `IsBadReadPtr(base+0xNNN)`, embedded debugging narratives such as a file-header "round N 0xC0000005…" retrospective, probe residue) — feeds G4; **E_debug — ordinary debug output** (bare println/eprintln/console.log bypassing the logger but readable and one-line-fixable) — D4 signal only, never G4 | D4/G4 |
| M10 | Junk-name density | `\b(tmp\|temp\|foo\|bar\|xxx\|thing\|handle\d*\|var\d*\|data\d\|result\d)\b` occurrences ÷ source lines ×1000 (exclude comments/examples). **`data/result/item/value/list/info/res` not counted** (domain idioms; spot-check name-behavior consistency instead). Also exclude method calls (e.g. `.handle(error)`) and prose inside log strings | D3 |
| M11 | TODO/FIXME count & quality | Grep; spot-check for issue IDs / trigger conditions (Google Java style). Empty TODOs: ≥5 = 1 signal | D1/D4 |
| M12 | Commented-out code blocks | Comment blocks containing executable statements (`;`, `if\|for\|return\|=`). **Doc comments and explanatory prose that merely mention code keywords do NOT count** (SonarSource S125) | D4 |
| M13 | Circular dependencies | import/require graph; core-module cycles count (S7091/S7027; manually review JPA/polymorphism false positives) | D2 |
| M14 | Semantic Coherence Audit (SCA) | **Fixed protocol — see the SCA section below**: run `references/semantic-surface.py` for extraction & candidates; adjudicate the top-15 most-referenced symbols (SI-1); review candidates (SI-2/3/4); convention census (CV). Outputs: `SI1_viol` / `SI2_unconsumed` / `SI2_trap` / `SI3_pairs` / `SI4_unrooted` / `CV` | D1/D2/D3/D4 |
| M15 | Mutable global state census | Count module-level mutable variables, singletons with mutable fields, and init-order flags (`isInitialized`-style patterns). Exclude DI containers and immutable constants | D2 |

> **RM candidacy**: functions ≥400 lines / files ≥1800 lines. The other M2/M3 buckets are distribution reference only, not penalty lines.
> Measurement discipline: same commands and same sampling across runs; numbers recorded before impressions; the sheet ships with the report.

---

## Semantic Coherence Audit (SCA) — the M14 protocol

Code communicates with humans through three channels: **names, contracts, and documentation**. Semantic coherence = four invariants; a violation of any of them misleads maintainers or forces call-site archaeology. This is the third evaluation axis alongside structure and residue. **All four invariants share ONE audit protocol — script-generated candidates, fixed-sample human adjudication, recorded verdicts. Never adjudicate by impression.**

### The four invariants

| Invariant | Definition | Typical violation |
|---|---|---|
| **SI-1 Name⇆Denotation** | A symbol's promised content/behavior must actually be inside it. Covers: type name vs its fields, function name vs its body, test name vs what it asserts | `LyricData` holding only metadata while the lyrics live in `LyricInput`; `get_total` returning an average |
| **SI-2 Declaration⇆Consumption closure** | Declared contract elements (fields / params / config keys / enum branches / event names) must be consumed; consumed elements must be declared. Nasty variant — **selective consumption**: the same element declared at ≥2 levels but consumed at only one — a switch that looks live but is silently ignored | a `show` flag filtered at the top menu level but ignored inside `children` |
| **SI-3 Concept single-source** | One domain concept has exactly one authoritative representation (one type / one name / one source of truth). Detector: type-name pairs sharing a domain token | `LyricData` vs `LyricInput` — which one is the authoritative lyric type? |
| **SI-4 Self-evident vocabulary** | A symbol/enum value's meaning must be derivable from the code itself (name + nearby docs), without call-site archaeology | enum value `"cloud"` with no doc — discoverable only by grepping usages |

**Convention census (CV)** — the fixed procedure for signal 13: sample 20 sites of one recurring concern (error handling / async pattern / state access); count distinct idioms; ≥3 idioms for the same concern = 1 CV violation.

### Protocol (fixed — identical across runs)

1. **Extract**: run `references/semantic-surface.py <root>` → semantic-surface inventory (exported types/enums + fields/values + reference counts) and candidate lists for SI-2/SI-3/SI-4. No runtime ⇒ manual extraction in the 10 largest files.
2. **Adjudicate SI-1**: take the **top-15 most-referenced exported symbols** (types + public functions); judge each name against its content/behavior with `file:line` evidence. Tests included: sampled test names vs asserted behavior.
3. **Review candidates**: SI-2/SI-3/SI-4 candidates adjudicated with exclusions — serialization/API payloads, dynamic key access, framework-mandated members, and documented public API surface do NOT count; SI-3 legitimate affix pairs (Request/Response, Input/Output, Query/Command, Create/Update, Read/Write...) do NOT count.
4. **Count** into the measurement sheet: `SI1_viol` (of 15) / `SI2_unconsumed` / `SI2_trap` (selective-consumption instances) / `SI3_pairs` / `SI4_unrooted` / `CV`.

### Thresholds (conservative; boundary calls follow rule 8)

| Count | 1 D4 signal when | Enters D4 45-tier list when |
|---|---|---|
| SI1_viol | ≥2 | — (debt only; D3 carries the tier impact) |
| SI2_unconsumed | ≥3 | — (debt only) |
| SI2_trap | ≥1 (every trap misleads a maintainer) | ≥3 (live-looking dead switches at scale actively betray maintainers) |
| SI3_pairs | ≥2 | — (debt only) |
| SI4_unrooted | ≥3 | — (debt only; D3 carries the tier impact) |
| CV | ≥1 concern | — (debt only) |

Dimension linkages: D1 (P_placeholder extension), D2 (yellow-zone evidence), D3 (misleading-name tier rows), D4 (SC/CV signal rows). **SC/CV violations never trigger hard gates** — they are locally fixable; they pull the total down through D4's signal counting, and only SI2_trap at scale (≥3) reaches the 45 tier. SC/CV signals are **semantic debt**: counted as ordinary signals regardless of authorship — never auto-classified as AI fingerprints.

---

## Structural hard gates (total caps)

Any established fact caps the total; multiple hits → lowest cap; each hit carries `file:line` evidence.

| Gate | Condition | Cap |
|---|---|---|
| G1 core god-function/god-file | Core business concentrated in a single oversized function/file **AND responsibility-mixed, hard to trace**. Candidacy by size (func ≥400 lines / file ≥1800 lines); mixing is decided ONLY by the RM protocol, never by line count | 60 |
| G3 inlined AI process markers at scale | ≥5 M8 markers in source files, spread across core/hot paths, visibly obstructing reading | 45 |
| G4 AI debugging residue in hot paths | ≥5 E_ai items (M9 net count). **Ordinary debug output (E_debug — bare println/eprintln/console.log, readable, one-line-fixable) never triggers G4**, only the D4 signal | 45 |

**Combination rule**: G1 plus any of G3/G4 → cap **40** (structural god + AI fingerprints = structural disaster).

**G1 three steps**: ① find the largest units (M2/M3); ② run RM on every ≥400-line function / ≥1800-line file; ③ RM "mixed" ⇒ hit; "single responsibility" ⇒ no gate (protects HMCL/grok-build-style "big but well-organized"). God-class statics (WMC≥47 / ATFD>5 / TCC<1/3, Lanza & Marinescu / PMD GodClass) may corroborate, never decide alone.

**Boundaries**: gates judge structure only — never size, headcount, or AI authorship; AGENTS.md/CLAUDE.md-style top-level convention files are not AI markers; when the project itself IS an AI tool, its prompt/agent code is product (no G3); "core/hot path" = entry → main business → persistence; ambiguous RM ⇒ mixed (conservative per rule 8's gate exception); **caps are ceilings not targets** (total = min(weighted, cap); when the pre-cap weighted score is lower, the weighted score stands).

**Judgment cross-check**: "won't maintain" ⇒ ≤60, "impossible" ⇒ ≤40; on conflict the stricter wins.

---

## Responsibility-Mixing protocol (RM) — shared arbiter for G1 and D2

The sole execution judge of "big but single-responsibility (no penalty) vs big and mixed (heavy penalty)" — the arbiter separating HMCL/grok-build (big, clear) from PCL/N.E.K.O (big, mixed). **Line counts never substitute for this protocol.**

**Steps (per candidate: function ≥400 lines / file ≥1800 lines)**:
1. **List functional blocks**: every inner block (sub-function, code section, class member) with a one-line description.
2. **Assign domains**: standard set — `config parsing` / `state management` / `UI rendering` / `business logic` / `I/O & serialization` / `network` / `platform syscalls` / `data structure defs` / `test stubs` / `error handling`. Custom domains allowed if explicitly enumerated.
   - **Domain-association rule**: `config parsing` / `I/O & serialization` / `network` / `platform syscalls` / `error handling` are **support domains**. A support domain on the **same dataflow** as the business domain (request-response / producer-consumer / input-process-output), serving a chained adjacent step, does **not** count separately. Domains count separately only when they **coexist in parallel without a shared dataflow** (login + downloads + theming stuffed into one file, mutually unconnected). Record a "non-related reason" for every unrelated domain pair; a same-dataflow exemption must be statable in one sentence with a clear flow boundary — otherwise no exemption.
3. **Count**: R_func = domains touched by one function (after support-domain folding); R_file = independent sub-domains with substantial logic (≥30 lines).
4. **Verdict**: R_func ≥3 or R_file ≥3 (each with substantial logic) ⇒ **mixed**; all blocks in one domain or one dataflow ⇒ **single responsibility**, regardless of size.
5. **Evidence**: record each sub-domain's `file:line` and assignment rationale (including non-related reasons and dataflow boundaries).

**Ties**: R=2 (borderline) ⇒ not mixed; record "borderline", D2 adjusts −1~−2. Ambiguous R ⇒ larger value (conservative, per rule 8's gate exception). No skipping candidates.

**Final arbiter (non-overridable)**: if the RM result conflicts with "could an ordinary human maintainer read this and change it safely WITHOUT external docs", the human answer wins and the domain assignment must be redone: RM says single but humans need external docs to remember it ⇒ assignment too loose, re-judge as mixed; RM says mixed but humans can read and change it directly ⇒ support domains were over-split, recount.

**Binding precedents** (a conflicting assignment is an error — reassign per precedent):
- **HMCL 2,881-line settings page → single responsibility**: config load → form render → edit → save-back — consecutive steps of one UI dataflow → R=1, no G1.
- **grok-build 4,376-line dispatch → single responsibility**: input → dispatch → output, one dataflow, network/IO chained step by step → R=1.
- **PCL god-file → mixed**: login auth, theme config, page rendering, download management, version update, network, error popups coexist in parallel with no shared dataflow → R≥3, G1 hit.
- **N.E.K.O god-file → mixed**: config + state + UI + business + IO stacked in parallel, no single dataflow → R≥3.

---

## D1: design soundness & technical honesty (weight 25)

**Definition**: is the design actually reasonable and do promises actually hold — engineering thinking (measurement/trade-offs/real implementations) vs wishful thinking (claims/placeholders/decoration).

**Anchors**: 90 = architecture matches complexity, core promises all verified, decisions have technical reasons, real tests (even if thin); 70 = mostly holds, a few decorative abstractions or slightly exaggerated promises; 45 = architecture mismatched to the problem, multiple promises unfulfillable (especially "performance optimizations" that are actually slower), decisions feel like wishes; 20 = absurd design, promises comprehensively fail.

**Measurement**:
1. **Promise verification (core)**: list every promise; count `P_fail` (major promises verified false or inverted — e.g. "performance gain" that adds overhead; each with claim-site + code-site `file:line` pairs), `P_placeholder` (placeholder/TODO/throwing stub; **also: declared-but-never-consumed contract elements that advertise a capability — half-implemented switches from M14's SI2_unconsumed/SI2_trap**), verification rate P/C.
2. **Decorative abstractions (D)**: grep `interface|abstract class|Factory|Provider|Strategy|Protocol|Abstract[A-Z]`; judge each — "single implementation project-wide, no extension expectation" ⇒ D+1. **Exemptions (any one suffices ⇒ do NOT count): a test double/mock exists; ≥2 call sites use it polymorphically (`any P` / generic constraints); it guards a documented cross-layer boundary.**
3. **Test safety**: from M7 — `T_placeholder` (per M7's definition), `T_ignore` (@Ignore/skip), `T_assert/T_file`.
4. **Build/CI**: try building or read the CI config — "every commit auto-builds + tests with visible results"?
5. **Performance-promise recheck**: for claimed optimizations, check whether caches/batching/indexes really cut cost or add it.

**Measurement → tier**:

| Condition | Tier | Base |
|---|---|---|
| P_fail=0 AND D≤1 AND T_placeholder≤2 AND real assertions exist | 90 | 90 |
| P_fail=0 AND (D=2~3 OR T_placeholder=3~5 OR T_assert/T_file<1) | 70-85 | 85 |
| P_fail=0 AND D=4 | 70-85 | 80 |
| P_fail=1 (minor) AND D≤3 | 70-80 | 78 |
| P_fail=1 AND D=4 | 70-80 | 72 |
| P_fail≥2 OR one performance promise actually adds overhead OR D≥5 OR tests all placeholder | 45 | 50 |
| P_fail≥4 OR promises comprehensively fail OR absurd design | 20 | 25 |

**Adjustments** (cap 95, floor 20): P_fail=0 AND P_placeholder=0 (all promises evidenced) → +2; T_assert/T_file≥3 with core coverage → +2; build works or CI routine → +1; T_placeholder≥3 → −3; tests all placeholder → −5; zero automated tests (T_file=0) → −5; not buildable and no CI → −3; D≥4 → −3.

**Tie-breaks**: P_fail between 1~2 ⇒ count as major (lower tier); pick table values, never invent intermediates; disputed "major" ⇒ major unless rebutted with evidence; undecidable performance claims ⇒ "unverified", lower tier (claimant bears the burden of proof); strong tests + absurd design ⇒ absurdity wins (lower tier), and recheck D4 for wishful thinking; **structure veto (anti-inflation): if G1 hits (structural god) or D2 lands in the red zone, D1 ≤70** — full promise-keeping earns no 80+.

---

## D2: traceability & mental load (weight 30)

**Definition**: can a human maintainer trace request→code and change code safely? Human working memory is ~4±1 chunks (Miller 1956 / Cowan 2001) — mixed, bloated logic can't be held in a human head and forces reliance on external docs. **File size itself is neutral**: big but RM-single-responsibility, clear, well-commented ⇒ no penalty; bloat is penalized.

**Anchors**: 90 = request→code traceable, changes touch 1-2 places, logic boundaries match file boundaries (large files/functions allowed when RM-single); 70 = mostly traceable, occasional cross-file hops; 45 = **bloated logic** (one file/function runs many jobs, no clear architecture, tracing interrupted, changes ripple, **needs external docs to remember structure**); 20 = completely untraceable, humans refuse to touch it.

**Measurement (fixed counting lenses — follow them exactly)**:
- M2 file distribution; M3 function distribution; **RM results** (`N_mixed` = mixed candidates).
- **T_trace**: pick the 3 main user journeys identifiable from the README/entry point; for each, count hops from the event entry (UI action / CLI command) to data landing (disk / network / subprocess) — entering a new file = 1 hop, same-file jumps don't count; take the maximum across the 3 journeys. *Worked example*: modpack install sheet → sheet view model → install coordinator → download service → disk = 4 hops ⇒ yellow.
- **T_impact (single lens — lockstep change surface)**: pick 2-3 **representative changes** — ones a maintainer performs in normal weekly work (add a setting, add a resource source, fix a bug across the stack, adjust a behavior); count the files that must be edited in the same commit; take the max. **Low-frequency architectural extensions (a new mod loader, a new protocol, a new platform backend) are NOT representative — record them as an observation, never as the red**. Raw call-site counts may only **corroborate, never decide**; when counted, first exclude same-file calls, test code, **stable-contract consumers** (getters / state stores / DI registries / logging / i18n / path-constant fan-out, plugin implementations invoked through their interface), and edits already priced as systemic CP in D4. **API popularity is not a change surface** — a getter called from 30 files costs nothing until its contract changes.
- M13 circular dependencies.
- **ND_max** max nesting depth — *lens*: count only control-flow keywords (`if/guard/for/while/switch/catch`); a closure body counts as a fresh function boundary (restart from 0); declarative UI-builder nesting (SwiftUI ViewBuilder and similar) and chained modifiers NEVER count (Linux: >3 refactor; SonarSource S134/ESLint default 4; >5 red zone).
- **Long parameter lists** — *lens*: only `func`/method signatures; constructors/initializers and declarative view builders excluded; count only **required parameters (no default value)**; commas inside closure/tuple types don't count (SIG ≤4 target, >7 watch).
- With tooling: cyclomatic >10 / cognitive >15 unit counts (McCabe/Sonar — red flags for splitting only, combine with RM).
- **ext_doc (two levels)**: ① dataflow level — can the core dataflow be reconstructed from code alone? ② symbol level — can core symbols' semantics be understood without call-site archaeology? **Yellow evidence**: M14's SI4_unrooted ≥1 at a core symbol, or SI3_pairs ≥2 (tracing a concept first requires discovering which representation is authoritative), or M15 mutable-global-state hubs ≥3 (hidden coupling through shared mutable state).

**Measurement → tier** (big-but-single never enters yellow/red):

| Signal | Green | Yellow | Red |
|---|---|---|---|
| N_mixed (core) | 0 | — | ≥1 (→G1); reds from mixing = min(N_mixed, 3) |
| T_trace hops | ≤2 | 3-5 | ≥6 |
| T_impact change surface (lockstep lens) | ≤2 | 3-5 | ≥6 |
| ND_max nesting | ≤3 | 4-5; also ≥6 when confined to exactly 1 function | max ≥8, or ≥7 in ≥2 functions |
| Functions with >7 required params | 0 | 1-14 | ≥15 |
| Circular deps (core) | none | 1-2 core cycles, or non-core | ≥3 core cycles (manual review first) |
| ext_doc needed (dataflow OR symbol level) | no | some modules / some core symbols | core unreconstructable from code, spans ≥3 files |

**Tier counting**: no reds ⇒ 90 − 2.5 per yellow, rounded half up (1 yellow=88, 2=85, 3=83, 4=80), **floor 70** — accumulated yellows alone never fail D2. Any red ⇒ the red count sets the score: **1 red ⇒ 45, 2 reds ⇒ 40, ≥3 reds ⇒ 30**; yellows do NOT subtract further. If the red is N_mixed ⇒ G1: D2=45 and the total is separately capped at 60.

**Cognitive-load compound**: ND yellow (4-5) AND the same function branch-heavy (branches ≥6 or cyclomatic ≥10) ⇒ that function counts as **2 yellows**; deep nesting AND mixed responsibilities ⇒ straight to 45.

**Adjustments** (any tier, total adjustment within ±2; cap 95, floor 20): T_trace≤1 → +1; T_impact≤1 → +1; M15 = 0 (no mutable global state) → +1; core hard spots carry why-comments → +1; RM "borderline" (R=2) → −2.

**Tie-breaks**: big files/long functions always go through RM before any tiering (single-responsibility never yellow/red, even at 3,000 lines); "big-but-clear vs big-and-mixed" disputes settle by the human arbiter (read & safely change without external docs); boundary values follow rule 8 (record + midpoint where tiers straddle); suspected false-positive cycles ⇒ manual review first; pick table values within a tier; core path unreadable ⇒ 70 with declared low confidence.

---

## D3: human readability & self-explanation (weight 15)

**Definition**: can the code itself be understood, and do comments/docs help or hinder? Comments are judged only by "does the information go beyond what the code shows, and is it stale" — **count, density, and compliance earn nothing** (Ousterhout and Clean Code disagree; this dimension takes no side, only "does it obstruct understanding").

**Anchors**: 90 = names convey intent directly, code self-explains, comments explain "why"; 70 = mostly readable, some spots need context lookup; 45 = names carry no semantics (junk names rampant, or proven meaningless by name-behavior spot-checks), comments restate operations or address AI/checklists; 20 = nearly unreadable, AI-dependent.

**Measurement**:
1. **Junk-name density (M10)** — with its exclusion rules.
2. **Comment intent classification (core)** — **fixed sampling frame**: all body comments of the 5 largest source files + the first 2 body comments of 10 files picked at even intervals in filename order (N≤30). **File headers / license headers are excluded from the sample entirely and never count as S.** Repeated runs must use the same frame.
   **Classification decision tree** (apply per comment, in order):
   ① references nonexistent symbols or contradicts the code → **H** (hallucinated);
   ② adds information the code cannot show — rationale, external constraints, domain knowledge, trade-offs, magic-value meaning, threading/performance reasons → **I** (intent);
   ③ merely translates the declaration into prose — the name already says it (`/// The x`, `- Parameter x: The x`, `/// Whether the toggle is visible`) → **R** (restatement). **Contract docstrings that add constraints, side-effects, exceptions, or override semantics are I, not R**;
   ④ rule boxes / separators / decorative banners in the body → **S** (decorative). **Exception — NAV (navigation aid)**: section labels / region markers inside files >300 lines (`// ===== Downloads =====`, `// MARK: Settings`) substitute for the method extraction the file skipped; they help orientation more than they pollute. Count NAV separately — they never enter S, R-share, or any tier trigger; NAV ≥10 ⇒ only a −2 adjustment (they hint at missing extraction).
   **Labeled examples** (from real disputes — calibrate against these):
   - `/// The Microsoft OAuth authorization endpoint.` on `static let authorize` nested in `enum Authentication` → **R** (name + nesting already say it)
   - `// CurseForge sort field: 6 = Last Updated` → **I** (magic value explained)
   - `/// fallback for logging / debugging` → **I** (reason for existence)
   - `- Parameter version: The version.` → **R** (signature translation)
   - `// keep only value: callers don't need keys; dropping them saves memory` → **I** (why)
   - `/// Checks which save types are available on disk, performing I/O off the main thread.` → **I** (threading rationale)
   - `/// Whether the resource is currently disabled.` → **R**
   - `// ======== 下载 ========`-style section banner inside a 700-line constructor → **NAV** (navigation in a long file, not decoration)
   - Copyright/license file-header block → **excluded from the sample**
   Record per-comment classifications in the report's evidence appendix.
3. **Name-behavior consistency (fixed procedure, not impression)**: adjudicate the M14 SI-1 sample — the top-15 most-referenced exported symbols (types + public functions), name vs content/behavior, each with `file:line` evidence; `SI1_viol` and `SI4_unrooted` feed the tier table below.
4. **Public API contract docs**: sample 10 public functions for contract docstrings (what / preconditions / side-effects / exceptions, Effective Java Item 56); penalize only when missing docs FORCE callers to read implementations.
5. TODO quality (M11); line width (>120 physical columns; CJK by logical width).

**Measurement → tier** (R-share = R ÷ sampled comments N):

| Condition | Tier | Base |
|---|---|---|
| G<5 AND R-share <15% AND S≤3 AND H=0 AND I≥5 AND SI1_viol ≤1 (fewer than 10 comments total ⇒ "core hard spots all have why-comments AND R/H=0") | 90 | 90 |
| G=5~15 OR R-share ≥15% OR H≤2 — the default tier when no 90/45 condition holds | 70-85 | 85 |
| G≥15 OR H≥3 OR **SI1_viol ≥2** OR **SI4_unrooted ≥3** OR (R-share >60% AND I<5 — restatement flood with zero why-payoff) OR missing API contract docs force reading implementations (≥3 of sampled) | 45 | 50 |
| R overwhelming majority AND H≥5, OR misleading names (**SI1_viol ≥4**), OR readable only via AI | 20 | 25 |

**Adjustments** (cap 95, floor 20): G<3 with fully semantic names → +1; core hard spots all carry why-comments → +1; zero restatements → +1; R-share 40-60% → −3; R-share >60% → −5; NAV ≥10 → −2; S ≥8 → −2; comment density <5% with high complexity → −2; density >40% dominated by short comments (AI-template tone) → −2; CJK projects: double-check comment-code consistency → feeds the H count.

**Tie-breaks**: sparse comments never penalized, abundant comments never rewarded (density is an extreme signal only); a single stale comment doesn't drop the tier — ≥3 do; name-vs-comment conflicts ⇒ names rule (lower tier), comments adjust ±2 only; a comment-free file with excellent names ⇒ no penalty; H=1~2 ambiguous with "individual typo" ⇒ counts as H.

---

## D4: AI slop & wishful-thinking residue (weight 30, reverse scoring)

**Definition**: how much **AI-produced residue that obstructs human maintenance** the project contains — NOT "AI-written code" itself. AI generation/assistance/toolchains are never penalized; only artifacts humans can't accept (structural gods, hot-path debug residue, promise betrayal, systemic copy-paste, inlined AI process markers, hallucinated comments, semantic incoherence). Higher raw score = less slop.

**Signals (all from the measurement table + D1/D3 by-products; no new measurement)**:

| Signal | Definition / source | Threshold |
|---|---|---|
| M AI process markers | M8 (excluding top-level convention files) | counted separately in core; M≥3 → 45 |
| E_ai AI debugging residue | M9's E_ai (coordinate/offset special-cases, magic offsets, narratives, probes) | ≥5 → G4 |
| E_debug ordinary debug output | M9's E_debug (bare prints bypassing the logger, readable, fixable) | ≥8 = 1 signal (human-normal debt; never G4) |
| W wishful betrayal | D1's P_fail | ≥2 major → 45 |
| CP copy-paste groups | M5 (SIG ≥6-line clones; fixed procedure + group definition, incl. mandatory near-duplicate merge and reverse spot-check) | **Three levels**: non-systemic (<3 families, or no sync evidence) = 1 debt signal; **systemic** (≥3 families AND each change syncs ≥2 sites) = **2 debt signals ("heavy debt", never a 45-tier trigger by itself)**; **flood-scale** (≥6 families, each with sync evidence) = **fingerprint → 45 tier**. **Single-family mega-cloning (one template with many instances — e.g. a 50-copy toast/UI template) is systemic, NOT flood: instance count alone never reaches the 45 tier** — it is real debt, not AI-process residue. **Parallel-architecture exemption** (rule 4): one-variant-per plugin/provider/platform/loader families with real per-variant differences are NOT systemic — 1 debt signal regardless of family size |
| C error-swallowing empty catches | M4 classified: best-effort (commented as such / cache cleanup / offline fallback) = human-normal debt, no heavy penalty; **error-swallowing** (no log, no fallback, wraps key business logic) = C | ≥5 swallowing → 45 |
| H hallucinated comments | D3's H | ≥3 → 45 |
| CD commented-out code blocks | M12 | ≥3 = 1 signal (debt; never a 45-tier trigger by itself) |
| DZ dead code / unused exports | per-symbol reference checks | human-normal debt; ≥1 = 1 signal |
| TODO empty/stale | M11 | ≥5 = 1 signal |
| SC semantic-coherence violations | M14's SI1/SI2/SI3/SI4 | per-invariant thresholds in the SCA section (each crossed invariant = 1 signal, max 4); debt — only **SI2_trap ≥3 → 45** |
| CV convention entropy | M14's convention census (signal 13's procedure) | ≥1 concern = 1 signal (debt; never a 45-tier trigger by itself) |

**Counting**: each category with ≥1 hit = 1 signal (multiple hits in one category still 1 signal, but over-threshold fingerprint hits trigger the 45 tier directly; systemic CP counts as 2 signals per the table). **Human-normal debt** = non-systemic CP, systemic CP (2 signals), best-effort catches, E_debug, CD, DZ, TODOs, occasional big files, **SC/CV semantic debt** (source-agnostic: counted as ordinary signals, never auto-fingerprints). **AI process fingerprints** = M, E_ai, W, **flood-scale CP**, G1 hits, H, error-swallowing catches. **Ambiguous classification ⇒ human-normal debt** (rule 4): a fingerprint needs positive artifact evidence; conservative defaults survive only in hard-gate judgments.

**Measurement → tier**:

| Condition | Tier | Base |
|---|---|---|
| ≤2 signals, all human-normal debt, zero fingerprints | 90 | 90 |
| ≥3 signals, all human-normal debt, zero fingerprints | 70-85 | 88 − signals×2, **floor 70** |
| 1 isolated fingerprint (no other signals) | 70-85 | 80 |
| Any fingerprint over threshold: M≥3 / E_ai≥3 / W≥2 / **CP at flood scale** / C≥5 / H≥3 / SI2_trap≥3 — or 1 fingerprint + ≥1 other signal — or G1 hit | 45 | 50 |
| Flood: M across the core / E_ai≥5 (→G4) / W≥4 / H≥5 / ≥3 fingerprint categories | 20 | 25 |

**Human-normal debt alone never leaves the 70-85 band** — no fail-by-debt. The 45 tier requires at least one fingerprint; the 20 tier requires flood.

**Adjustments** (cap 95, floor 20): zero signals → +1; signals concentrated in one file (≥2 categories) → −3; comments all AI-template tone → −3; each fingerprint category beyond the first → −3 (not applied when already flood); one major wishful betrayal ⇒ straight to the 45 tier, no stacking.

**Tie-breaks**: human-normal debt ⇒ yellow zone, fingerprints ⇒ red zone, **ambiguous ⇒ human-normal debt**; ≥2 signal categories in one file = "concentrated pollution" (−3 per adjustments); CP at the 2~3 family boundary without sync evidence ⇒ non-systemic (debt); systemic CP (≥3 families, or a single mega-family of any instance count) stays in the 70-85 band as 2 signals — only flood-scale CP (≥6 families) is a fingerprint; one major betrayal + one other signal ⇒ straight 45; **when G1 triggers, D4 ≤55; when G3 or G4 triggers, D4 ≤45** and the total is gate-capped (G1→60, G3→45, G4→45, G1+G3/G4→40); **unverifiable AI authorship ⇒ neither penalized nor rewarded** (only verifiable artifacts count); signal definitions follow this file and ai-slop-signals.md — no personal lenses.

---

## Calibration check (S7 drift check, not a scoring rule)

When the subject's profile resembles a row below, the score should land in the reference range. Deviation >3 ⇒ recheck S2/S3 — **never adjust the score to fit**. Systematic multi-project drift ⇒ the rubric needs rework (maintainer's call).

| Reference profile | Reference range |
|---|---|
| Lovingly human-maintained, clear boundaries, why-comments | 90-95 |
| Big but well-organized, mature OSS (many "big but single-responsibility" files) | 80-90 |
| Well-organized but carrying one systemic design smell at scale (param-list epidemic, systemic CP, zero tests) | 70-80 |
| Mixed god-file (G1 hit), otherwise disciplined | 55-60 (pass-line edge) |
| Mixed gods + accumulated debt | 45-56 |
| AI fingerprints at scale (G3 or G4 hit) | 40-45 |
| Structural gods + AI fingerprints (G1+G3/G4) | 35-42 |
| Slop pile: gods + fingerprints + broken promises + unreadable | 20-35 |
| Beyond rescue | <20 |

> **60-line semantics**: profiles at ≥60 = human-maintainable (if painful); <60 = not fit for direct human maintenance. This is the skill's anchor — the evaluator must state which side their judgment lands on; conflicts resolve to the judgment.
> **Use the full 0-100 range**: 0-40 are real landing zones — a project whose dimensions land in the flood/20 tiers SHOULD total 20-40; do not park bad projects at 45-55 by default. Symmetrically, do not park good projects below 80 for human-normal debt alone (debt floors D2/D4 at 70).
> Key distinction anchor: HMCL/grok-build-style "big but organized" vs PCL/N.E.K.O-style "big and mixed" — the difference comes from the RM protocol alone, never from line counts.
> Precedent constraint: RM assignments conflicting with the binding precedents are errors — reassign per precedent.
> **G1 cap semantics**: total = min(pre-cap weighted, cap); when the pre-cap weighted score is below the cap, the weighted score stands (e.g. PCL-like projects with low D1/D3 land below the 60 line).

---

## Consistency self-check (two runs converge within ≤3)

Totals differing by >3 ⇒ check in order (**no bargaining over totals**):
1. Compare M1-M15 sheets (especially M8/M9 exclusion lenses, M10 wordlist, M14 adjudication sample) ⇒ rerun commands on mismatch.
2. Compare sampling scopes ⇒ the deeper one wins.
3. Compare RM domain assignments ⇒ per-sub-domain evidence + binding precedents.
4. Compare red/yellow/green counts and tiers ⇒ **compare both sides' boundary records item by item and re-verify the evidence** (rule 8).
5. For D3 divergence: first confirm both runs used the **same comment sampling frame and the same decision tree**; then compare per-comment classifications. For SC divergence: confirm both ran the same SCA protocol (same tool version, same top-15 sample, same exclusions).
6. Compare adjustment triggers (enumerated, reproducible).
7. Still divergent ⇒ take the **midpoint** (rounded down) and declare the disagreement — hard-gate verdicts excepted (they stay conservative).
8. **60-split review**: if two evaluators land on opposite sides of 60, return to the core question "would you maintain it yourself" to arbitrate the side — the answer decides the side, mechanical scores follow.

**Main variance sources and their seals**: responsibility mixing ⇒ RM protocol (enumeration + counting + precedents + arbiter); comment quality ⇒ fixed sampling frame + decision tree + I/R/S/H/NAV counts; copy-paste/wishes/AI markers ⇒ fixed definitions (M5 procedure + group definition, systemic "needs syncing" lens + parallel-architecture exemption, P_fail, M8 narrowed list, M9 exclusion lens); change-surface ⇒ T_impact lockstep lens (API popularity excluded); semantic coherence ⇒ SCA fixed protocol (script candidates + top-15 adjudication sample + recorded verdicts + exclusion rules); big-file penalties ⇒ "big but single-responsibility never yellow/red"; qualitative judgments ⇒ within-tier ±5 with evidence and boundary records only.
