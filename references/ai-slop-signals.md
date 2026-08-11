# AI slop signal catalog

The forensics list for D4 (AI slop & wishful-thinking residue). Each signal gives identification, counter/positive examples, and scoring linkage. **Penalty lenses and measurement-table definitions (M1-M15) follow scoring-rubric.md** — this file only decides "recognized as what, filed where".

**Judgment principle**: not "smells like AI ⇒ penalize", but "does it obstruct human maintenance". Stray residue is normal development debris; scaled, concentrated residue that obstructs reading and changing is slop.

**Core distinction**:
- **Human-normal debt** (light penalty; never alone drops a project out of the 90s) = copy-paste, dead code, a few big files, a few dead exports, **semantic debt (SC/CV signals 12/13/15/16/17)** — universal in human projects.
- **AI process fingerprints** (heavy penalty; can trigger hard gates) = AI-coding-process markers inlined in source, AI debugging residue in hot paths, systemic god-files/god-functions.

**Semantic signals are source-agnostic**: never ask whether AI or a human wrote them — ask only whether they mislead a maintainer or force call-site archaeology. They never trigger hard gates and are never auto-classified as AI fingerprints.

---

## Wish-detection protocol (MUST, run before scoring)

1. **List promises**: read README/docs/key docstrings; list every promise (performance/capability/architecture/extensibility) with `file:line`.
2. **Verify one by one**: "performance optimization" ⇒ does it really cut complexity/overhead, or does it add overhead (extra abstraction layers, full copies, cold-path caching) and end up slower; "extensible" ⇒ real second implementation / extension points?; "supports X" ⇒ really implemented, or placeholder/TODO. **Claiming speed while being slower = the prototypical wish signal.**
3. **Record evidence**: every conclusion carries `file:line`; failures enter the "AI-slop findings" section.

---

## Signal 1: promise-implementation betrayal (wishful thinking, most severe)

**Identify**: a claimed capability/performance/architecture fails code verification, or verifies inverted.

**Counter-example**: README claims "multi-level cache + batching, 10× faster"; the code rebuilds the whole pipeline on every call, processes items synchronously one by one, and re-sums everything — slower than a plain loop.
**Positive example**: `# measured: below 10k rows a plain loop is fastest; optimize when a real bottleneck appears` — a measured conclusion with reasons.

**Linkage**: P_fail counts into D1; a major wish (performance promise actually adds overhead) ⇒ D4 straight to the 45 tier.

---

## Signal 2: AI process markers inlined in source

**Identify**: AI coding-process markers/traces **inside source files** (.py/.ts/.cpp): `"Codex P1/P2"` review tags, `@anchor.probe` probe references, `"第N轮"` fix retrospectives, `"review round N on PR #xxx"`. Human maintainers must filter them out one by one to read.

**Test**: does a human maintainer need this comment — or only an AI coding agent?

**Counter-example**: `# (Codex P2) fix #2841: after changing this function, sync the monkeypatch binding in main_routers` — what a human sees is AI review-round metadata.
**Positive example**: `# keep only value: callers don't need keys; dropping them saves memory; return early on empty` — explains why.

**Exclusions (not signals)**: AGENTS.md / CLAUDE.md / .github/instructions / copilot-instructions and other **top-level convention and documentation files** (normal engineering practice); AI toolchains (CI, agent configs) don't count. **Only traces inlined in source files count.**

**Linkage**: counted per M8 (narrowed wordlist); M≥3 in core ⇒ D4 45 tier; M≥5 spread across core/hot paths and obstructing reading ⇒ G3, cap 45.

---

## Signal 3: AI debugging residue in hot paths

**Identify**: the AI's bug-hunting loop left uncleaned in core code — opaque, dependent on external debugging context, unsafe for humans to remove:
- coordinate-specific debug blocks embedded in hot sampling functions (`if (debug && pos.x==728 && pos.y==-8) fprintf(...)`);
- magic-offset memory checks (`IsBadReadPtr(baseM + 0x34001)`) executed on every chunk production path;
- a source file header embedding a whole debugging retrospective ("round 1: 0xC0000005… round 2: …");
- unconditional `print("[DEBUG] ...")` in hot paths (no context, no discernible purpose).

**NOT this signal (E_debug, ordinary debug output)**: simple bare println/eprintln/console.log — even bypassing the logging system — as long as a human understands it at a glance and can fix it in one line (e.g. `println!("natives is None")`): an omission, not debugging residue.

**How**: inspect debug instrumentation in the hottest sampling functions; grep `getenv|fprintf|debug|IsBadReadPtr|print(`; count env switches; `.artifacts/`, `.investigations/`-style process directories are material evidence of repeated AI flailing.

**Linkage**: M9 splits two classes — **E_ai (coordinate/offset/narrative/probe residue) net ≥5 ⇒ G4, cap 45**; E_debug (ordinary bare prints) ≥8 = 1 D4 signal (human-normal debt), never G4.

---

## Signal 4: structural god-function / god-file (big AND mixed)

**Identify**: core business logic concentrated in a single oversized function/file **that is also responsibility-mixed and hard to trace** — big but single-responsibility and clear doesn't count (don't force-split honest long flows). Candidacy: **functions ≥400 lines / files ≥1800 lines** ⇒ RM protocol (see scoring-rubric.md); R_func ≥3 or R_file ≥3 ⇒ mixed.

**Counter-example**: 3,000-line `main.py` holding config parsing, global state, HTTP routes, DB operations, and UI rendering; a 400-line core function mutating global variables midway.
**Positive example**: responsibilities live in their own modules, file boundaries = logic boundaries, functions <100 lines; or 4,000 lines but single-responsibility with clean method extraction (grok-build dispatch, HMCL settings page).

**Linkage**: mixed ⇒ G1 cap 60 (pass-line edge) + D2 ≤45 + D1 ≤70 (structure veto); big but single ⇒ no gate, D2 not demoted.

---

## Signal 5: hallucinated comments

**Identify**: comments referencing functions/files/parameters/behaviors that don't exist or contradict the code (AI generated the comment, the code changed but the comment didn't, or the API was fabricated).

**Counter-example**: `# uses get_cached_data for speed (config in redis_client)` + `data = fetch_from_db()` — neither the function nor the config object exists.
**Positive example**: `# no cache here: this endpoint is called a few times a day — a cache layer isn't worth it`.

**Linkage**: counts as H; H≥3 ⇒ D4 45 tier; each H also feeds D3's H count.

---

## Signal 6: restatement comments (describe operations, not reasons)

**Identify**: comments translating code into natural language with zero new information; high per-line comment frequency where every line is self-evident from the code.

**Counter-example**: `# loop over each item in the list` / `# if x is greater than 10, perform addition` — every line translated.
**Positive example**: `# threshold is 10: below this is noise data, excluded from the sum` — explains why.

**Linkage**: counted as R in D3 (fixed sampling frame + decision tree); **R-share >40% ⇒ 45 tier**.

---

## Signal 7: dead code & unused imports

**Identify**: unused imports (grep each imported name across the project); functions/classes defined but never called; commented-out code blocks left in shipped source (M12).

**Counter-example**: `import os, sys, json, random, hashlib` (sys/random/hashlib never used) + a "deprecated" function nothing calls.
**Positive example**: no unused imports; deprecated logic deleted — git history preserves it.

**Linkage**: human-normal-debt signal (DZ); commented-out code blocks ≥3 ⇒ D4 45 tier.

---

## Signal 8: over-engineering (patterns for trivial problems)

**Identify**: a 10-line problem wrapped in factories/abstract base classes/observers/multi-layer interfaces with no callers and no extension expectation — just to "look proper".

**Counter-example**: one `print` hidden behind `Protocol` + `ConsoleSender` + `SenderFactory`, with a single call site in the whole project.
**Positive example**: `def send_message(msg): print(msg)  # console is the only impl for now; abstract when a second arrives`.

**Linkage**: D1's decorative-abstraction count D (with the rubric's exemptions: test doubles, polymorphic call sites, documented layer boundaries); D≥5 ⇒ 45 tier.

---

## Signal 9: void abstractions & needless indirection

**Identify**: functions/classes that merely forward the call unchanged — no logic, validation, or transformation in between; deep forwarding chains (A→B→C→D, each layer empty) are the hot zone.

**Counter-example**: `get_user_name(user_id)` only calls `_fetch_user(user_id).name`, which only calls `database.query_user` — three pure forwarding layers.
**Positive example**: a wrapper with real responsibility (caching/validation/conversion) is legitimate indirection. A fallback wrapper converting `throws` into a default value has real responsibility.

---

## Signal 10: vacuous defenses (swallowed exceptions, impossible conditions)

**Identify**: empty `except`/`catch` blocks, `pass`, `print` — errors swallowed silently (M4); null checks on never-null variables; `if x != None and x is not None`-style redundant checks; try/catch everywhere hiding bugs.

**Counter-example**: `except Exception: pass  # fail silently; the caller never knows it failed`.
**Positive example**: `except TimeoutError:  # timeouts are expected: retry; if still failing, re-raise so the caller decides`.

**Linkage**: error-swallowing empty catches ≥5 ⇒ D4 45 tier; empty catches wrapping key business logic = concentrated pollution.

---

## Signal 11: copy-paste variants (DRY bankruptcy)

**Identify**: multiple near-identical logic blocks differing only in params/naming, repeated across functions/files. Every variant is live and correct — but a bugfix must land in N places.

**Counter-example**: `calc_price_a` vs `compute_price_b` — same logic, different names.
**Positive example**: `def calc_price(items, tax_rate): return sum(item.price for item in items) * (1 + tax_rate)` — one reuse point.

**Linkage**: counted per M5's fixed procedure and group definition (SIG ≥6-line Type-1 clones; all instances of one template = 1 group). **Systemic** (≥3 groups AND every change must sync ≥2 call sites) ⇒ D4 45 tier; below the "needs syncing" qualifier ⇒ human-normal debt, 70-85 tier only.

---

## Signal 12: name-behavior mismatch (SI-1 name⇆denotation)

**Identify**: a symbol's name promises content/behavior the implementation doesn't deliver — directly misleading readers. Covers type name vs its fields, function name vs its body, test name vs what it asserts.

**Fixed procedure (M14 SI-1 — never impressionistic spot-checks)**: run `references/semantic-surface.py` → take the **top-15 most-referenced exported symbols** (types + public functions; sampled test names included); adjudicate each name against its actual content/behavior, one by one, with `file:line` evidence; record every verdict. Confirmed mismatches count as `SI1_viol`.

**Counter-example**: `LyricData` holding only track metadata while the actual lyrics live in `LyricInput` — the authoritative "lyric data" name sits on the wrong type; `def get_total(items): return sum(items) / len(items)` — named "total", actually "average".
**Positive example**: `TrackMetadata` holding metadata, `LyricLine` holding lyric lines — the name says what's inside; or a deliberate rename with zero stale references left.

**Linkage**: `SI1_viol` ≥2 = 1 SC signal (D4), ≥5 ⇒ D4 45 tier; D3: ≥2 ⇒ 45 tier, ≥4 ⇒ 20 tier.

---

## Signal 13: patchwork feel & convention entropy (CV)

**Identify**: one recurring concern solved with multiple mutually exclusive idioms across the project — naming styles mixed (`fetch_data`/`FetchData`/`fetchData`), errors thrown in one module, Result-boxed in another, silently nil-ed in a third; state via singleton here, DI there, raw global elsewhere. Seams of multiple unshepherded generation rounds.

**Fixed procedure (convention census, M14 CV)**: pick ONE recurring concern (error handling / async pattern / state access / naming style); sample **20 sites** of that concern at even intervals across the source tree; count distinct idioms; **≥3 idioms for the same concern = 1 CV violation**. Repeat per concern; record sampled sites and idiom counts.

**Counter-example**: async via completion handlers at 8 sites, async/await at 8, reactive publishers at 4 — three idioms for one concern.
**Positive example**: one dominant idiom with occasional justified, documented deviations.
**Exclusions (not signals)**: language-mandated duality (e.g. Swift `throws` + `Result` at API boundaries), framework-required patterns, a documented migration in progress.

**Linkage**: CV ≥1 concern = 1 D4 signal; CV ≥2 concerns ⇒ D4 45 tier. **≥2 mutually exclusive naming conventions within ONE file ⇒ confirmed even without the census.**

---

## Signal 14: README promises unfulfilled

**Identify**: features/performance/architecture claimed in the README are missing or inconsistent in code — signal 1 on the documentation side.

**Counter-example**: README says "supports user registration and login"; the code has no authentication at all.
**NOT signals**: README ads/marketing/sponsor/donation blocks; missing or minimal README; untidy README — none of these count.

**Linkage**: unfulfilled README promises join P_fail in D1/D4; no separate "documentation quality" penalty.

---

## Signal 15: broken contract (SI-2 declaration⇆consumption closure)

**Identify**: a declared contract element — field, parameter, config key, enum branch, event name — that no code path consumes; or a consumed element that was never declared. Nastiest variant — **selective-consumption trap**: the same element declared at ≥2 levels but honored at only one, so a switch that looks live is silently ignored somewhere.

**Fixed procedure (M14 SI-2)**: `references/semantic-surface.py` lists exported fields with zero read sites as candidates; adjudicate each against the exclusions; count `SI2_unconsumed` (dead contract elements) and `SI2_trap` (selective-consumption instances, each recorded as an honored-level + ignored-level `file:line` pair).

**Counter-example**: a menu-item `show: Bool` honored by the top-level filter but ignored when the item nests inside `children` — setting `show = false` on a child compiles, looks supported, and does nothing; the maintainer discovers the lie only by testing or archaeology.
**Positive example**: every declared field has at least one reader; an intentionally reserved field carries a doc saying so (`/// reserved for v2; not yet consumed`).

**Exclusions (not signals)**: serialization/API payloads mirroring a wire format, dynamic key access, framework-mandated members, documented public API surface consumed by downstream clients.

**Linkage**: `SI2_unconsumed` ≥3 = 1 SC signal, ≥5 ⇒ D4 45 tier; `SI2_trap` ≥1 = 1 SC signal (every trap misleads someone), ≥3 ⇒ 45 tier; half-implemented switches also feed D1's `P_placeholder` — a capability the contract advertises but the code doesn't deliver.

---

## Signal 16: concept ghosting (SI-3 concept single-source)

**Identify**: one domain concept materialized as ≥2 parallel representations with no declared authority — two type names sharing a domain token, two enums for the same axis, two competing "sources of truth". Maintainers can't tell which one to read, extend, or trust.

**Fixed procedure (M14 SI-3)**: the script lists type-name clusters sharing a ≥4-character domain token (tokens appearing in 2–8 type names — big homogeneous naming families are not ghosting); adjudicate each cluster pair-wise — is one member clearly authoritative (the others unmistakable views/DTOs/projections referencing it)? A cluster with no authoritative member ⇒ 1 `SI3_pairs` (count clusters, not pair permutations).

**Counter-example**: `LyricData` and `LyricInput` coexisting — both look like "the lyric type"; any lyric-handling fix must first answer "which one is real?" before touching code.
**Positive example**: `LyricDocument` as the single authority, with `LyricLineView` unmistakably its view projection (named and documented as such, holding a reference to the authority).

**Exclusions (legitimate affix pairs, not signals)**: Request/Response, Input/Output, Query/Command, Create/Update, Read/Write, Get/Set, Add/Remove, Start/Stop, Open/Close — paired roles of ONE operation, not competing authorities.

**Linkage**: `SI3_pairs` ≥2 = 1 SC signal, ≥4 ⇒ D4 45 tier; ≥2 ⇒ D2 ext_doc yellow evidence (tracing a concept first requires discovering which representation is authoritative).

---

## Signal 17: rootless vocabulary (SI-4 self-evident vocabulary)

**Identify**: a symbol / enum value / config key whose meaning cannot be derived from the code itself — name and nearby docs say nothing; understanding requires grepping every call site or runtime experiments (call-site archaeology).

**Fixed procedure (M14 SI-4)**: the script lists enum values (and exported symbols) outside common vocabulary carrying no comment within ±5 lines; adjudicate each — can a maintainer state what it means from the code alone? No ⇒ 1 `SI4_unrooted`.

**Counter-example**: enum case `"cloud"` in a lyrics-source enum with no doc — cloud what? remote service? placeholder? Discoverable only by tracing every switch over it.
**Positive example**: `case cloud // lyrics fetched from the network-disk share` — one line roots it; self-evident values (`case local`, `case embedded`) need nothing.

**Exclusions (not signals)**: standard vocabulary of the project's field (`vertex` in a graphics project), framework-conventional names, values documented at the declaration site.

**Linkage**: `SI4_unrooted` ≥3 = 1 SC signal, ≥5 ⇒ D4 45 tier; D3: ≥3 ⇒ 45 tier; ≥1 at a core symbol ⇒ D2 ext_doc yellow evidence.

---

## Aggregate judgment

| Signal density | D4 reference | Total impact (weight 30) |
|---|---|---|
| Almost none (≤1 stray) | 85-95 | upward room |
| A few (2-4, human-normal debt) | 75-85 | neutral |
| At scale (≥5, or one major wish / AI fingerprint) | 45-60 | heavy drag, possible gates |
| Flood (AI fingerprints everywhere) | ≤40 | gates trigger, total under 50 |

**Note**: D4 weighs 30. One major wish or AI fingerprint can cost a whole tier; hard gates cap the total directly (G1→60, G3→45, G4→45, G1+G3/G4→40) — G3/G4/combo sit below the 60 line, G1 at the pass-line edge — making "AI fingerprints at scale = fail = unfit for human maintenance" hold as the 60-split. **Surface-neat but absurdly designed projects: don't be fooled by comments/docs/naming/test volume — return to signal 1 (wishes), signals 2/3 (AI fingerprints), signal 4 (structural gods) and punish there.** **Semantic debt (signals 12/13/15/16/17) is source-agnostic and never gate-triggering** — at scale it drags the total through D4's 45 tier (SC ≥3 signals / CV ≥2 concerns). Detailed tiers: scoring-rubric.md D4.

**Evidence format**: every finding in the report follows `file:line — signal N (<signal name>): <description>`.
