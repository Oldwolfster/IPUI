# Baseball Pipeline — State of the Union
*Generated from source review, May 2026*

---

## Architecture at a Glance

```
FormBaseball (host form)
│
├── Pipe       (tab)   — ETL orchestration + layer browser
├── Workbench  (tab)   — Table explorer / column editor
├── Predict    (tab)   — Model comparison UI
├── SQL        (tab)   — Ad-hoc query runner
├── Docs       (tab)   — (same layout as SQL, TBD content)
├── Tree       (tab)   — (TBD)
├── Kanban     (tab)   — Todo/Doing/Done
└── Breakout   (tab)   — Game embed
```

**Key service classes (not tabs):**
- `BB` — configured-once DB service (`BB.configure(path)` once at startup; all other code just calls `BB.query()`, `BB.execute()`, etc.)
- `BB_Schema_Bootstrap` — idempotent startup: creates `_tables` + `_run_log`, syncs `_Schema_tbl.SCHEMA`, materializes physical tables, then calls `_Schema_views.create_all()`
- `_Schema_tbl` — the hardcoded column registry (source of truth for table shapes)
- `_Schema_views` — all `pull_*` views defined as `view_pull_xxx()` methods; discovered and registered by convention at bootstrap

---

## Data Layer Map

| Layer     | Tables                          | Notes |
|-----------|---------------------------------|-------|
| `raw`     | `raw_pitches`, `raw_schedule`   | Append-only; pulled from Statcast via `pybaseball` |
| `etl`     | `etl_pa`                        | One row per plate appearance; cleaned event grain |
| `feet`    | `feet_batter`, `feet_pitcher`   | Daily per-entity summable metrics; PK = `(GD, TS, batter/pitcher)` |
| `forest`  | `forest`                        | Flat training matrix; skeleton only |
| `_tables` | (meta)                          | Column registry; drives `BB.LAYERS` cache |
| `_run_log`| (meta)                          | Execution log; `BB.log()` writes here (currently stdout-only — INSERT commented out) |

### Naming conventions enforced
- `GD` = game date as `INTEGER YYYYMMDD` — first column and first PK column on every table
- `TS` = timeslice integer — auto-injected as PK col 2 on `feet_*` tables
- `WITHOUT ROWID` on every table
- `pull_<target>` views feed the upsert engine (multiple views per target supported, sorted alphabetically for run order)

---

## Pipeline Engine (Pipe.py)

### Startup flow
```
all_in_one()
  ├── BB_Schema_Bootstrap.bootstrap()   ← tables + views guaranteed to exist
  ├── BB.configure()                    ← LAYERS cache loaded
  ├── top_section()                     ← header + date range + action buttons
  └── layers()                          ← one column card per layer
```

### Update flow (Update All button)
```
update_all()
  ├── Phase 1: purge_all_derived()      ← DELETE from etl + feet for GD range
  ├── Phase 2: run_raw_layer()          ← pull_raw_pitches() via pybaseball/statcast
  ├── Phase 3a: run_layer("etl")        ← run_view_into_table() for each etl table
  ├── Phase 3b: run_layer("feet")       ← run_view_into_table() for each feet table
  └── refresh_pane()
```

### View → table upsert engine
- `find_views(tbl)` — prefix match on `pull_<tbl>*`, alphabetical (controls run order via naming)
- `match_columns()` — intersection of view cols and target cols; extras warned, missing allowed (NULL fill)
- `execute_upsert()` — `INSERT ... ON CONFLICT DO UPDATE SET ...` (degrades to DO NOTHING if view is PK-only)
- `target_pk_columns()` — reads PK from `PRAGMA table_info`

### Per-table refresh
Individual "Refresh" button on each card calls `refresh_table(tbl)`:
- `raw` layer → dispatches to `pull_<tbl>(start_gd, end_gd)`
- `etl`/`feet` layers → delete-range + re-upsert from views

### Nuke operation
Drops all `etl`, `feet`, `forest` tables + their `pull_*` views, deletes from `_tables`, refreshes `BB.LAYERS`. `raw` and `_tables`/`_run_log` are untouched.

---

## Views (_Schema_views.py)

| View name          | Target    | Notes |
|--------------------|-----------|-------|
| `pull_etl_pa`      | `etl_pa`  | Selects last pitch per AB from `raw_pitches`; computes `is_hit`, `is_ab`, `is_k`, `is_bb`, `is_hr`, `total_bases`, `home`, `bat_team`, `pit_team`, `xba` |
| `pull_feet_batter` | `feet_batter` | **Defined twice** — second definition wins (Python method override). The winning version groups by `(GD, batter, p_throws)` and includes `launch_speed_cnt`, `xba_cnt` for safe averaging later |

### ⚠️ Known issue: duplicate `view_pull_feet_batter`
Two `@classmethod` definitions of `view_pull_feet_batter` exist in `_Schema_views`. Python silently uses the second one. The first (no `p_throws` split) is dead code. Needs cleanup.

---

## Predict Tab (Predict.py)

### Layout
```
TAB_LAYOUT = [("controls", 0.2), ("by_model", 0.75)]
```
Pane 0 is always the controls sidebar. Panes 1-N are dynamically managed.

### Pane state machine (per pane index)
```
by_model  →  (user picks model)  →  by_day  →  (user clicks a day)  →  by_dude
   ↑                                   ↑                                    |
   └───────────── ← Back ─────────────┘◄──────────────── ← Back ───────────┘
```

### Queries
- `query_daily_summary()` — joins model view to `batter_games` (⚠️ `batter_games` table not in current schema — see issues)
- `query_predictions_for()` — same join, per-GD, left joins `batters` for names (⚠️ `batters` table also not in schema)

### Model convention
Any SQLite view named `model_*` is auto-discovered. Contract: `SELECT gd, batter, game_pk, predicted FROM ...`

---

## Known Issues / Gaps

### 🔴 Breaking
1. **`batter_games` table missing** — `Predict` queries join against it, but it's not in `_Schema_tbl.SCHEMA` or `_Schema_views`. The old system had this; the refactor appears to have dropped it.
2. **`batters` lookup table missing** — `query_predictions_for` left-joins `batters` for player names. Not in schema.
3. **Duplicate `view_pull_feet_batter`** — second definition silently shadows the first. Dead code + confusing.

### 🟡 Logged / deferred
4. **`BB.log()` INSERT commented out** — runs fine (stdout), but `_run_log` table is never written.
5. **`raw_schedule` puller missing** — schema defines the table; no `pull_raw_schedule()` method on `Pipe`.
6. **`forest` table is a skeleton** — defined in schema, no views populate it yet.
7. **Two `blah` buttons** in `top_section()` are `on_click=self.passme` placeholders.
8. **`Predict.open_db()`** — bypasses `BB`; opens its own connection directly. Should use `BB.query()`.
9. **`Predict` uses `batter_games` date format** — queries pass `start_str`/`end_str` as `YYYY-MM-DD` strings but the rest of the pipeline uses `GD` integers.
10. **`SCHEMAOLD`** in `BB_Schema_Bootstrap` — dead array still in file; should be removed.
11. **`ip_setup` defined twice** in `FormBaseball` — second one (atest cleanup) shadows the first (`print("from form")`).

### 🟢 Opportunities
12. **No models yet** — only the bootstrap `model_001_bootstrap` (4 × ba_season, MAE ~0.761) if it was ever created. `feet_batter` data is the raw material to build better ones.
13. **Weather API** — on the ToDo list; would feed into `forest` as a feature.
14. **`forest` → training matrix** — the full pipeline from `feet_batter` + `feet_pitcher` through feature engineering into the `forest` table is unbuilt.

---

## File Inventory

| File | Role |
|------|------|
| `FormBaseball.py` | Host form; TAB_LAYOUT; header bar |
| `Pipe.py` | ETL tab; pipeline orchestration; pybaseball pull |
| `BB.py` | DB service singleton; configure/query/execute/log |
| `BB_Schema_Bootstrap.py` | Idempotent startup; table materialization |
| `_Schema_tbl.py` | Column registry (SCHEMA list) |
| `_Schema_views.py` | pull_* view definitions |
| `Predict.py` | Model comparison UI |
| `ToDoBaseball.md` | "Connect to weather api" |

---

## Suggested Next Steps (prioritized)

1. **Fix `batter_games`** — either add it back to schema + a view, or rewrite `Predict` queries to join against `etl_pa` directly (cleaner)
2. **Fix duplicate view** — remove the dead first `view_pull_feet_batter`
3. **Wire `BB.log()` INSERT** — one-liner uncomment; `_run_log` table is already there
4. **Build first real model** — `feet_batter` + `feet_pitcher` data is available; a pitcher-matchup model would immediately beat the bootstrap
5. **`forest` ETL** — views to populate the training matrix