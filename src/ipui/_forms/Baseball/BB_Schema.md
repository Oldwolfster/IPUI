# Baseball Schema

**Status:** target state, skeleton. Tables shown are the seed — we will fatten by layer once the bones are right.

---

## 1. Conventions

These rules are universal. Violations are bugs, not style choices.

### 1.1 `GD` — Game Date

- Stored as **`INTEGER`** in **`YYYYMMDD`** format. July 15, 2024 → `20240715`.
- **First column of every table.**
- **First column of every primary key**, with rare exceptions for true dimension tables (a player lookup keyed on player_id alone is acceptable).
- All ETL/query code calls **`gd_today()`**, **`gd_prior(gd)`**, **`gd_from(date)`** — never hand-formats dates. One function family, one definition, zero drift.

**Why INT not TEXT:** ~4 bytes vs ~10+ bytes per cell, faster compares, smaller indexes, identical sort behavior. The one cost — month-boundary math — is handled in the helper functions.

### 1.2 `WITHOUT ROWID`

Every table. No exceptions in the skeleton. SQLite's rowid is dead weight when `(gd, ...)` is already the natural clustered key.

### 1.3 Table naming

Layer prefix + descriptive name. No numbers in the table name.

| Layer | Prefix | Example |
|---|---|---|
| Raw source | `raw_` | `raw_pitches` |
| ETL / cleaned | `etl_` | `etl_plate_appearances` |
| Feature store | `feat_` | `feat_batter_daily` |
| Training matrix | (none) | `forest` |

The prefix tells you which layer a table lives in. The UI's left-to-right column layout gives the visual map.

### 1.4 Idempotent rebuild

- `CREATE TABLE IF NOT EXISTS` everywhere.
- The schema **is** the build script. Edit the CREATE statement, delete the DB file, rerun.
- No `ALTER TABLE`. No migrations. The file is the version.

### 1.5 PK clustering, not separate indexing

Because every table is `WITHOUT ROWID` and PK leads with `GD`, the dominant access pattern (date-bounded scans) is already covered. Secondary indexes only when a different access path is genuinely common.

### 1.6 Append-only by layer

| Layer | Mutation policy |
|---|---|
| `raw_` | Append-only. Never UPDATE. New `GD` = new rows. |
| `etl_` | Append-only. Idempotent rebuild of one `GD` is allowed (delete + insert). |
| `feat_` | Append-only. Each row is a point-in-time snapshot. Never UPDATE. |
| `forest` | Drop-and-rebuild. Cheap. Iterate fast on feature subsets. |

---

## 2. Architecture

```
   raw_*           etl_*           feat_*           forest
   ─────           ─────           ──────           ──────
   Source          Cleaned         Per-entity       Wide flat
   truth           conformed       daily            training
   pitches    ──►  plate_apps ──►  batter_daily ──► matrix
   schedule        batter_game     pitcher_daily    (one row
   players                         pitchtype_daily   per
   parks                                             prediction)
```



```
   raw_*           etl_*                 feat_*           forest
   ─────           ─────                   ──────           ──────
   raw_pitches     etl_pa                 feet_batter      Wide flat
   raw_schedule    etl_batter_moonphase       feet_pitcher     Many version trying different shit       
   raw_players  
   raw_parks  
  
```
                        
                                 slugging    moonphases.

5/26    1   Babe Ruth   .354    .355
5/26    3   Babe Ruth   .364    .365




GD     TS batter       avg      slg    
5/25    1   Babe Ruth   .350    .355
5/25    7   Babe Ruth   .360     .689
5/25    30   B R        .375     .
5/25   14   BR .405
5/25   999  


## Inventory
 
| Layer | Table | Grain (one row per...) | Purpose |
|---|---|---|---|
| `raw_` | `raw_pitches` | pitch | Statcast pitch-level source of truth |
| `raw_` | `raw_schedule` | scheduled game | Game-level facts, starters, venue |
| `raw_` | `raw_players` | player snapshot | Player dimension (handedness, name) |
| `raw_` | `raw_parks` | park snapshot | Park dimension (factors, roof) |
| `etl_` | `etl_pa` | plate appearance | Cleaned PA-level events, batter + pitcher refs |
| `feet_` | `feet_batter` | (batter, timeslice) | All sumable batter metrics, every window, one table |
| `feet_` | `feet_pitcher` | (pitcher, timeslice) | Mirror of `feet_batter` |
| (none) | `forest` | prediction target | Wide flat training matrix, pivoted from `feet_*` |


**Each layer's job, one sentence:**

- **`raw_*`** — exactly what the source gave us, structurally clean, semantically untouched.
- **`etl_*`** — conformed, deduplicated, enriched with derived per-event flags. One row per real-world event.
- **`feet_*`** — per-entity rolling aggregates indexed by `(GD, entity_id)`. The point-in-time feature store.
- **`forest`** — the wide flat table fed to XGBoost. One row per prediction target. Every feature joined.

**The leakage guard** (the whole reason this architecture exists):

When building `forest` for a game on `game_gd`, feature joins use **`feat.gd = gd_prior(game_gd)`**. Features are always as-of the day *before* the game. The framework enforces this; the user can't accidentally cheat.

**What each layer is NOT:**

- `raw_*` is **not** where you fix typos, normalize units, or add derived columns. Those belong in `etl_*`.
- `etl_*` is **not** where you compute season-to-date or rolling stats. Those belong in `feat_*`.
- `feat_*` is **not** where game-specific context lives (opposing pitcher, park, weather). That joins in at `forest`.
- `forest` is **not** where model predictions or evaluation metrics live. Those belong in a separate model-artifacts layer (out of scope for this doc).

---

## 3. Layer `raw_` — Source of Truth

Append-only. One row per source event. No transformations.

### `raw_pitches`

One row per pitch thrown. Statcast grain.

- **Schema owner:** pandas via `to_sql` on first import. This table is the one exception to the manual CREATE pattern — we accept whatever shape Statcast hands us and conform downstream in `etl_`.
- **PK leading:** `gd`, then game/pitch identifiers (set after first import).

### `raw_schedule`

One row per scheduled game.

```sql
CREATE TABLE IF NOT EXISTS raw_schedule (
    gd                  INTEGER,
    game_pk             INTEGER,
    game_datetime       TEXT,
    status              TEXT,
    home_team_id        INTEGER,
    away_team_id        INTEGER,
    home_starter_id     INTEGER,
    away_starter_id     INTEGER,
    venue               TEXT,
    game_type           TEXT,
    PRIMARY KEY (gd, game_pk)
) WITHOUT ROWID;
```

### `raw_players`

Static-ish player dimension. Updated when rosters change.

```sql
CREATE TABLE IF NOT EXISTS raw_players (
    gd                  INTEGER,
    player_id           INTEGER,
    name                TEXT,
    bats                TEXT,
    throws              TEXT,
    PRIMARY KEY (gd, player_id)
) WITHOUT ROWID;
```

*Note:* `gd` here is "as-of this snapshot date" rather than "this player was active this day." Player metadata that changes (team, handedness corrections) gets a new row.

### `raw_parks`

Park dimension. Rarely changes.

```sql
CREATE TABLE IF NOT EXISTS raw_parks (
    gd                  INTEGER,
    venue               TEXT,
    park_factor         REAL,
    roof                TEXT,
    PRIMARY KEY (gd, venue)
) WITHOUT ROWID;
```

---

## 4. Layer `etl_` — Cleaned, Conformed, Per-Event

Per-event grain, but derived flags are computed once here so downstream feature code stays clean.

### `etl_plate_appearances`

One row per PA. Distilled from `raw_pitches`.

```sql
CREATE TABLE IF NOT EXISTS etl_plate_appearances (
    gd                  INTEGER,
    batter              INTEGER,
    game_pk             INTEGER,
    at_bat_number       INTEGER,
    pitcher             INTEGER,
    stand               TEXT,
    p_throws            TEXT,
    home                INTEGER,
    park                TEXT,
    events              TEXT,
    is_hit              INTEGER,
    is_ab               INTEGER,
    is_k                INTEGER,
    is_bb               INTEGER,
    launch_speed        REAL,
    launch_angle        INTEGER,
    xba                 REAL,
    woba_value          REAL,
    woba_denom          INTEGER,
    PRIMARY KEY (gd, batter, game_pk, at_bat_number)
) WITHOUT ROWID;
```

### `etl_batter_game`

One row per batter per game. Aggregated from `etl_plate_appearances`.

```sql
CREATE TABLE IF NOT EXISTS etl_batter_game (
    gd                  INTEGER,
    batter              INTEGER,
    game_pk             INTEGER,
    pa                  INTEGER,
    ab                  INTEGER,
    hits                INTEGER,
    hr                  INTEGER,
    bb                  INTEGER,
    k                   INTEGER,
    tb                  INTEGER,
    home                INTEGER,
    PRIMARY KEY (gd, batter, game_pk)
) WITHOUT ROWID;
```

---

## 5. Layer `feat_` — Per-Entity Daily Snapshots

One row per `(gd, entity_id)`. The row contains **everything known about that entity through end of day `gd`**.

The training-matrix join rule: `feat.gd = gd_prior(game_gd)`.

### `feat_batter_daily`

```sql
CREATE TABLE IF NOT EXISTS feat_batter_daily (
    gd                  INTEGER,
    batter              INTEGER,
    pa_season           INTEGER,
    ab_season           INTEGER,
    hits_season         INTEGER,
    ba_season           REAL,
    obp_season          REAL,
    slg_season          REAL,
    ops_season          REAL,
    xwoba_season        REAL,
    hard_hit_pct_30d    REAL,
    hits_last_10        INTEGER,
    pa_last_30d         INTEGER,
    PRIMARY KEY (gd, batter)
) WITHOUT ROWID;
```

### `feat_pitcher_daily`

```sql
CREATE TABLE IF NOT EXISTS feat_pitcher_daily (
    gd                  INTEGER,
    pitcher             INTEGER,
    bf_season           INTEGER,
    k_season            INTEGER,
    bb_season           INTEGER,
    xwoba_allowed_30d   REAL,
    hard_hit_pct_allowed_30d REAL,
    PRIMARY KEY (gd, pitcher)
) WITHOUT ROWID;
```

### `feat_batter_pitchtype_daily`

Per-batter, per-pitch-type snapshots. The matchup-signal table.

```sql
CREATE TABLE IF NOT EXISTS feat_batter_pitchtype_daily (
    gd                  INTEGER,
    batter              INTEGER,
    pitch_type          TEXT,
    pa                  INTEGER,
    xwoba               REAL,
    whiff_pct           REAL,
    hard_hit_pct        REAL,
    PRIMARY KEY (gd, batter, pitch_type)
) WITHOUT ROWID;
```

---

## 6. `forest` — Training Matrix

The wide flat table XGBoost actually trains on. One row per `(batter, game_pk)`.

Drop-and-rebuild every time. Iteration is cheap; this is where feature subset experimentation happens.

```sql
CREATE TABLE IF NOT EXISTS forest (
    gd                          INTEGER,
    batter                      INTEGER,
    game_pk                     INTEGER,
    -- batter features as of gd_prior(gd)
    bat_pa_season               INTEGER,
    bat_ba_season               REAL,
    bat_xwoba_season            REAL,
    bat_hard_hit_pct_30d        REAL,
    -- opposing pitcher features as of gd_prior(gd)
    pit_xwoba_allowed_30d       REAL,
    pit_hard_hit_pct_allowed_30d REAL,
    -- matchup
    platoon_advantage           INTEGER,
    -- park / environment
    park_factor                 REAL,
    -- target
    target_fantasy_pts          REAL,
    PRIMARY KEY (gd, batter, game_pk)
) WITHOUT ROWID;
```

Column-naming convention inside `forest`:

- `bat_*` — batter features
- `pit_*` — pitcher features
- `bvp_*` — batter-vs-pitch-type aggregated features
- `int_*` — interaction features (log5-style, weighted matchup, etc.)
- `park_*`, `wx_*` — environment
- `target_*` — what we're predicting

This convention is what lets feature-importance plots stay readable when the column count climbs.

---

## 7. Open Questions / TBDs

Explicit list. We don't pretend any of this is decided.

- **`raw_pitches` schema control.** Currently pandas owns it. Do we want to take it over with an explicit CREATE for consistency, or keep pandas managing it and conform in `etl_`?
- **Player dimension `GD` semantics.** "Snapshot date of player metadata" feels right but we haven't tested how lookups work when a player's `bats` corrects mid-season.
- **Park factors as time-varying.** Park factor is computed retrospectively. Should `raw_parks` carry season-end factors, or current rolling estimates? Affects leakage if we use full-season factors during in-season training.
- **Target definition.** `target_fantasy_pts` is a placeholder. Real definition depends on the scoring rules of the league the friend plays in. Needs to be confirmed and locked.
- **Class-per-table declarative pattern.** Sketched in conversation, not adopted yet. Reconsider after skeleton is running.
- **Index policy.** Skeleton has none beyond PKs. We'll add `feat_*` secondary indexes if/when feature-build queries get slow.
- **`gd_prior` across month/year boundaries.** Helper must handle this correctly. Implementation deferred but called out in §1.1.
- **Pitch-type universe.** How many distinct `pitch_type` values do we keep? Statcast occasionally reclassifies (e.g., sweeper). Need a canonical list.
- **Real-time prediction path.** This doc covers training. Inference (predict tonight's slate) reuses the same `feat_*` joins but the build sequence is different. Out of scope for v1.