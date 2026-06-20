# Lists of shit - ToDoBB.md

## Project Summary — 
### The shit this project does.

**Baseball Workshop** is IPUI's guinea pig app — a baseball analytics pipeline predicting player stats using XGBoost.

**Pipeline:** RAW → ETL → FEET → FOREST → PREDICT. Each layer feeds the next via pull views. Data flows one game-day (GD) at a time.

**Convention over scaffolding — naming IS wiring:**
- Table prefix = layer: raw_, etl_, feet_, forest_, predict_. `BbDB.layer_of()` derives layer from name.
- `pull_{table}` view feeds a table. 
  - `pull_{table}_mixin_{suffix}` views are composable building blocks for `pull_{table}`. Auto-discovered and editable from a table's Workshop. 
  - `update_{table}*` views are auto-discovered and applied.
- `sync_{table}` methods handle raw layer pulls. Discovered via `getattr`.
- `t_` prefix on a column = XGBoost target. Keys are stripped for training, reattached for output.
- `predict_{forest}` and `model_{forest}` are auto-named from the forest table.
- GD (game date integer YYYYMMDD) auto-injected into every table by MgrSchema.
- TS (timeslice) auto-added when present in feet layer: 1=game, 7/15/28=rolling, 200=season. Controlled by list in pipe.
- Schema-defined table order = pipeline execution order


### App specific shit to know.
- All schema changes must be done via MgrSchema to ensure no drift, for example...
  - adding GD.
  - We automatically update source files adding new tables to _SchemaTbl or views to _SchemaViews.
  - Predict tables are ephemeral — NOT stored in _SchemaTbl. Model views are auto-created by MgrSchema.build_predict_view.
- If we need to raise an error, let's use the IPUI custom EZ.err
- tables_for_layer returns schema-defined order first (pipeline dependency order), then DB-only tables. Order matters.
- Forest tables MUST include game_pk in their keys — batter + GD is not unique (doubleheaders).
- TextBox: .text is read-only. Use .set_text(value) to update.




## List of shit that is done

6/10
ctrl/home ctrl/end ctrl/shift/home ctrl/shift/end added to textarea/textbox
shift/tab and ctrl-shift-tab added to textarea/textbox
Autoformat SQL when saving


## List of shit that needs to be done
Not refreshing pipe when clone table
Struggling to change PK on UI
vertical scroll works but only via mousewheel - not via keyboard 

2.2) Building DB Tab

2) DONE move name preview value to the BannerPlate of pane 3.  "Building ... " or Editing ...
3) Done when clicking 'keys' on inspector it should select the keys that the table has.
4) DONE:when in clone or edit mode.  no longer allow the db explorer(pane 0) change the table in the left grid.  do add doubleclicking a field adds ot the new version(keys up top - metrics at bottom)
5) Done:move up/move down work, but the field is unhighlighted... after it moves field in grid rehighlight the  field 
6) Donenew: Layer should be selected and suffix populated if it has been set when identity is clicked.
7) issue screenshotsare for:  First image: before adding pitcher.  After: Added pitcher but deleted p_throws - removing pitcher does not add deleted field back.  but subsequent toggles of pitcher don't continue deleting fields




## Plan to add metrics.
1) DONE - Build ETL Pipeline. (easily maintainable ETL) from Raw to Forest
2) DONE - Build grain-agnositc XGB Model to Train any Forest table to predict any feature.
3) Fields for "Model Views" are invariant. Automate recording summary results to a table - anytime a "Model" view is created, write the results, dates, and features, total MAE, Guy's line to a summary set of tables.
   A) DONE:Record results to table from C (Actually one table per drill level - for speed at large aggregations)  No rolling up from atomic
   B) Add "Regression Guard / Joy Meter" query from this table - add PROMINENTLY to Pipe page.
   C) Add "Beats the line" nmng Forest table RED if it is negative. (requires new data source) 
   D) Add "Beats GUY's line" number.   Color that fucking Forest table RED if it is negative. (DOES NOT requires new data source - it's the line i draw from log5 + other available baselines.)
4) Build Walk forward process. (new button next to 'Run All')
   A) UI 
   A1) uses same date boxes.
   A2) Allow multi-selection of Forest tables Pull all data... run models serially after.
   B) Processing
   B1) Kick off RAW download in discrete process for full range.  this is the slow part,so let's keep it going while the rest runs.
   B2) Truncate All > Raw
   C2) ETL first 2 days through Forest (one day of training and one day of inference) were are not pussys and this is all the warm up we need(but we will slice by Regime... maybe hot/cold) 
   C3) Run XGB on all selected models using last day as inference
   C4) Store results to a table (step 3)  Include "Count Weighted Total MAE" CWTM!  (is nesting acronyms a capital offense?   I'll risk it)
   C5) If this is day matching "end textbox" then go to c10
   C7) Ensure Raw has completed the next day.  if not wait until it does.
   C8) ETL one additional day from Raw to Forest
   C9) Go to step C3.
   C8) Repeat Using 'filter' approach to test for LEAKAGE. 
5) Build system to compare results. Note: Has dependency on new summary table but does not alter it.
   A) Switch to table from model views.
   B) Add option for single grid (keep existing format as unified grid would be VERY SLOW on Drill down)
   C) Add total MAE to top of pane and unified grid.
6) Create Grammar rules for naming fields.  (if something doesn't fit - OMMIT or amend rules - not 'wing it')
   {Entity}_{Metric}_{Time Slice]}_{Context}
   See below for details:
7) Review existing fields to ensure compliance with grammar rules.

8) Test on full season of data. then back to a few days for fast development
9) Automated Leakage Detection -perhaps replay walk-forward versus filter walk-forward could serve as a free leakage test.
   A) Features for prediction day D must be identical whether produced by replaying history only through D, or by using the full dataset with a strict <= D filter.
   B) feature_date <= prediction_date
   C) stat_window_end < prediction_event_time
   D) train keys do not overlap predict keys
   E) target field not present in feature list
   F_same-game result fields blocked unless explicitly whitelisted 
10) Process to analyze impact of feature.
    Prereq 1:(This is done on full season + current season)
    Prereq 2:(A synthetic matchup is run for validation  (maybe BruteForce vs Wolf)   calibration step using a tiny known-answer fixture to catch bugs in the walk-forward harness itself before they corrupt feature decisions
    OMMISION: "first day ommited from results" we only have if for log5, which is the only one we are not trying to measure 
   A) Lift on Walk forward test.
   B) Leakage
   C) Null test (feature importance through ablation.)
   D) Counterfeit
      D1) does feature only impact when not in presence of another feature that impacts better - probably O(N^2 :< ) 
      D2) Fill rate should be one factor which to keep... accuracy... what else
    E) Score based on
    E2) lift
    E3) sample size
    E4) fill rate
    E5) stability across dates
    E6) stability across regimes
    E7) leakage risk
    E8) compute cost
    E9) redundancy with stronger features
    E10)xgb 'importance number'
 
11) Add statistics
12) Investigate "paid API" to see what they offer... can we do it ourselves?



DETAILS OF STEP 6
[Entity]_[Metric]_[TimeSlice]_[Context]
Component Definitions
1. Entity (parts[0]): Defines the target table and primary keys for automated Workshop wiring.
b = Batter (automates join to feet_batter)
p = Pitcher (automates join to feet_pitcher)

2. Metric (parts[1]): The core baseline statistic or analytical calculation.
Examples: ba (Batting Average), ops (OPS), baa (Batting Average Against).

3. TimeSlice (parts[2]): A strict integer mapping directly to the TS dimension column in the database. Eliminates lookback string theater.
200 = 200 day rolling window.
9999 = Career/All-Time historical aggregate sentinel value.

4. [Context1]_[Context2]... (parts[3+ - Optional): Relational platoon/situational splits. Must use explicit relational tokens to prevent naming collisions (e.g., vsR instead of HR to bypass Home Run brain fog).
vsR = Versus Right-handed opponent.
vsL = Versus Left-handed opponent.
home
away









Connect to weather api


## List of shit that needs to be done later


Add Run status near the buttons: ✓ 484 rows returned or ✗ no such column.
Change query results title to Query Results — 484 rows or Query Results — ERROR.
Change schema save button to include count: Save 1 Schema Change.
When destructive, consider stronger wording: Replace Table: 1 Change.
When no schema changes exist, show No Schema Changes and disable/gray the button.
Show selected column in the table header: Table: forest — selected: b_ba.
For supporting view creation, label textbox Supporting View Suffix.
Show generated name preview: Full name: pull_forest_mixin_batter_season.
Forgive obvious naming mistakes and show cleanup: Using suffix: batter_season.
Add tiny glossary/hover labels: GD = game/as-of date, TS = trailing window.
In ETL cards, visually mark dev/empty tables: EMPTY or TEST