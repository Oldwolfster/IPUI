# The Composer — Registration CSR, Target State

*Planning spec for the next-tab CSR. Registry stays frozen as a working POC; this describes the tab we build alongside it. Concise on purpose — decisions and principles, not the reasoning trail.*

---

## 1. Purpose

The Composer is the CSR of Registry's primitive builders into a new tab — but **elevated from imperative to declarative**. It does not replace the primitives (field / table / pull-query builders). It becomes a **declarative front-end that emits them**. You declare *intent*; the system derives compliant primitives.

The reason this matters: a primitive only knows *what it is*, not *what it's for*. That's why an auto-stubbed pull query writes `1.0 as b_ba` — at the primitive level it has no idea where `b_ba` comes from. The declaration carries the missing context, so the emitted primitive can be correct (`(h / ab) as b_ba`).

---

## 2. Two doors (both stay open)

- **Composer — the compliance lane.** Guarantees everything created conforms to the grammar and conventions. Its product isn't tables; it's *compliance*. A malformed name is structurally impossible.
- **Paste-into-`_SchemaTbl` — the fast lane.** Raw paste stays as the escape hatch: for speed, and for cases the grammar doesn't cover yet. The composer is never the *only* way in.

Speed is the paste lane's job. The composer's job is guaranteeing correctness.

---

## 3. Tables: keys & grain

- A **grain *is* a set of keys.** "Pick a grain" and "pick keys" are the same selection viewed from two ends.
- **Grain is a named preset that seeds an editable key multiselect.** Pick a grain → conventional keys pre-checked → adjust if needed.
- The preset **enforces the non-negotiables**: `GD` always auto-injected and first; forest grain always includes `game_pk` (doubleheaders). Everything else stays editable.
- Net effect: compliance-by-construction — you can't omit a required key.

---

## 4. Metrics: two tiers

The composer branches by layer.

### 4a. Feet / ETL tier — *build first*

A metric is `{entity}_{metric}` chosen from registry lists, with **context** as a multiselect. Flat, finite, fully covered by the grammar we already have. This is the original composer design.

### 4b. Forest tier — *build second*

Forest metrics are richer. The unit of declaration is **(dimension, shape)**: a metric projected over a dimension's values, combined with the game's actual exposure to those values.

---

## 5. Forest field types

Every forest field is exactly one of:

1. **Carried measure** — pulled from feet (`b_ba`, `b_ba_vsL`).
2. **Carried context** — joined and grabbed (`starter_hand`).
3. **Computed projection** — an *expression* over atomic measures, evaluated per row (e.g. `b_ba_pitchmix = Σ (b_ba_vs_type × starter_pct_type)`). This is the new and powerful kind: it bakes domain knowledge into the pipe instead of leaving the tree to rediscover it badly.

---

## 6. The shape catalog

A dimension is factored via one of two shapes. **Do not design the catalog in the abstract — let each new shape be earned by a real second use.**

- **Context-only (default, cheap, additive).** The dimension rides as a column the tree splits on against the *overall* metric. N dimensions = N columns. Scales indefinitely. This is the default for most dimensions (home/away, rest, park).
- **Crossed / dot-product (rationed).** The metric is split across the dimension's values and recombined by the game's exposure. Use **only** when the split is strong and well-sampled. This is the door to combinatorial explosion — keep crossing a deliberate, rare choice.

Hand and pitch type are the *same operation* at different cardinality:
- **Hand** = the degenerate dot-product: 2 values, one-hot exposure → pick the live split.
- **Pitch type** = the general dot-product: N values, frequency-distribution exposure → weighted sum.

---

## 7. The forest declaration (full parameter set)

A forest table declares:

- **Prediction / deliverable grain** — **fixed** at batter/game (one prediction per batter-game).
- **Training grain** — **free** (batter/game, PA, …). XGB predicts at the grain it trains at; the two are welded. *Consequence:* choosing a finer training grain commits you to building inference rows at that same grain (e.g. expected-PA rows for tonight's slate).
- **Aggregation rule** — bridges training grain → deliverable grain. Legal **iff** the deliverable is a **weighted-linear** combination of per-unit predictions *and* the weights are suppliable. (Uniform sum is PA's special case; weighted sum covers pitch type. Nonlinear targets — e.g. "multi-hit game" — break it.)
- **Weight source** (when aggregation is weighted, or for type-3 dot products) — starter / PA-weighted / team. A declared choice, never a silent assumption.
- **Dimensions × shapes** — which dimensions are factored, and how (context-only vs crossed).

Why this set matters: the *same declaration with one parameter changed* yields **forest vs forest_pa** (training grain) and **champion vs challenger** (one added dimension). That is what makes an honest A/B possible — the two arms differ *only* by the declared delta, with no hand-maintained drift.

---

## 8. Worked example — factor "hand"

- `hand` lives as a **dimension in atomic `feet_batter`** (Kimball-atomic: game / batter / + dimensions).
- Forest projects it, at batter/game grain, into four fields:
  - `b_ba` — overall (always kept)
  - `b_ba_vsL`, `b_ba_vsR` — crossed metrics
  - `starter_hand` — context flag (the tree picks the live split)
- Grain stays batter/game → one prediction per start.
- **Still to pin in the declaration:** does "hand" mean batter-platoon only, or also pitcher-side (`p_ba` × batter hand)? And *what is* "hand" — the starter's, or PA-weighted exposure across the staff?

---

## 9. The architecture that makes it possible

**Atomic feet, free-grain forest.** Skills and frequencies live as plain measures at the finest grain; the forest projection combines them *per game, at build time*, in the pull query. The "infinite distribution possibilities" are never stored — only the finite set of actual matchups is ever evaluated. This is the load-bearing decision the whole composer rests on; everything in §5–§7 depends on it.

---

## 10. Build sequence (anchors)

1. **Feet-tier composer.** Proves the architecture — declarative front-end → primitive emitter, paste coexists, grammar does real work — on easy ground.
2. **Forest-tier composer.** Build the `(dimension, shape)` machinery, driven onto working code with **hand as its first real use**.
3. **Pitch type.** Proves the shape generalizes (degenerate → general dot-product). The abstraction is earned by the second use, not forecast.
4. **Training-grain + aggregation parameter.** `forest_pa` retroactively becomes its proof-of-concept.

---

## 11. Non-goals / deferred

- Don't pre-design the shape catalog; let the second real dimension earn each shape.
- Nonlinear deliverable targets are outside the weighted-linear aggregation model.
- *Where* a dot product lives — feature-time (XGB learns it) / ETL-time (precomputed column) / aggregation-time (train per-value, weight at rollup) — is a per-field empirical choice. Sparse per-cell counts decide it; it is not a global commitment.
- Evaluation honesty (walk-forward, out-of-fold per-row scoring) is a *separate* concern from the composer and is not specified here.