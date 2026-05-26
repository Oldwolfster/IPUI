from ipui.utils.MgrDT import MgrDT
from ipui._forms.Baseball.BB_Schema_Bootstrap import BB_Schema_Bootstrap
from datetime import date, timedelta, datetime
from ipui import *
from pathlib import Path
from datetime import datetime
from ipui._forms.Baseball.BB import BB
from ipui._forms.Baseball.Z_NOTWORKINGTooltipBaseballTable import TooltipBaseballTable
from ipui._forms.Baseball.BB import BB
from datetime import date, timedelta
import time as _time
import pybaseball



class Pipe(_BaseTab):

    DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")

    SYNC_DEPS = {
        "staging_batter_features_season":      ["plate_appearances"],
        "staging_batter_features_recent_form": ["batter_games"],            # NEW
        "batter_features":                     ["staging_batter_features_season",
                                                "staging_batter_features_recent_form"],  # UPDATED
        "pitcher_features":                    ["plate_appearances"],
        "batter_games":                        ["plate_appearances"],
        "league_summary":                      ["plate_appearances"],
        "pitcher_pitch_mix":                   ["pitch_bucketed"],
        "batter_vs_pitch":                     ["pitch_bucketed"],
    }

    EVENT_BASES = {
        "single"  : 1,
        "double"  : 2,
        "triple"  : 3,
        "home_run": 4,
    }

    PITCH_BUCKETS = {
        "FF": "fastball", "SI": "fastball", "FC": "fastball", "FA": "fastball",
        "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking", "SV": "breaking", "CS": "breaking",
        "CH": "offspeed", "FS": "offspeed", "SP": "offspeed", "FO": "offspeed",
    }
    BUCKETS = ["fastball", "breaking", "offspeed", "other"]
    # ══════════════════════════════════════════════════════════════
    # IMPERATIVE — manual wiring
    # ══════════════════════════════════════════════════════════════

    def all_in_one(self, parent):
        # pitches_min, pitches_max = self.get_dates("pitches")
        BB_Schema_Bootstrap.bootstrap(self.DB_PATH)
        BB.configure(self.DB_PATH)
        self.top_section(parent)
        self.layers(parent)


    def top_section(self, parent):
        frame = CardCol(parent,  pad =2)
        header = Card(frame, pad =3)
        header = Plate(header, pad =5)
        header = Plate(header, pad =5)
        header = Row(header) #simpler to reuse the reference
        Title(header, "Data Pipeline", glow=True)
        Spacer(header)
        Button(header, "Update all",color_bg=Style.COLOR_BUTTON_CTA,on_click=self.update_all)

        TextBox(header, initial_value="2026-03-18", name="txt_start_date")
        Body(header, "to:")
        TextBox(header, initial_value="2026-03-20", name="txt_end_date")
        Spacer(header)
        Button(header, "blah ", on_click=self.passme)
        Button(header, "blah", on_click=self.passme)
        Button(header, "Phoenix", on_click=self.nuke_clicked, color_bg=Style.COLOR_BUTTON_DANGER)


    def nuke_clicked(self):
        self.form.msgbox(
            "Nuke etl + feet layers?\n\n"
            "All derived tables in etl and feet will be DROPPED.\n"
            "raw and forest are untouched.\n"
            "and then it all gets rebuilt",
            MSG_BTNS_YES_NO + MSG_ICON_QUESTION + MSG_DEFAULT_2,
            "Nuke derived layers",
            on_result=self.nuke_confirmed,
        )

    def nuke_confirmed(self, result):
        if result != MSG_RESULT_YES:
            BB.log("nuke", "INFO", "cancelled by user")
            return
        for tbl in BB.layer_tables("etl") + BB.layer_tables("feet"):
            BB.drop_table(tbl)
        BB.refresh()
        BB.log("nuke", "DONE", "etl + feet layers nuked")
        self.refresh_pane()

    def refresh_table(self, tbl):
        dates = self.get_start_and_end_dates()
        if dates is None: return
        start_gd, end_gd = dates
        layer = BB.layer_of(tbl)
        BB.log(tbl, "INFO", f"refresh requested for GD {start_gd} → {end_gd}  (layer={layer})")
        if   layer == "raw" : self.refresh_raw_table   (tbl, start_gd, end_gd)
        elif layer in ("etl","feet"): self.refresh_derived_table(tbl, start_gd, end_gd)
        else: BB.log(tbl, "WARN", f"refresh not supported for layer '{layer}'")
        self.refresh_pane()

    def refresh_raw_table(self, tbl, start_gd, end_gd):
        method_name = f"pull_{tbl}"
        if not hasattr(self, method_name):
            BB.log(tbl, "WARN", f"no puller method '{method_name}' on Pipe")
            return
        getattr(self, method_name)(start_gd, end_gd)

    def layers(self, parent):
        frame = CardRow(parent, flex_height=1, pad=2)
        for layer in BB.LAYERS:
            self.build_a_layer(frame, layer)

    def refresh_derived_table(self, tbl, start_gd, end_gd):
        rc = BB.execute(f"DELETE FROM {tbl} WHERE GD BETWEEN ? AND ?", (start_gd, end_gd))
        BB.log(tbl, "INFO", f"refresh purge: {rc} rows for GD {start_gd} → {end_gd}", rows=rc)
        self.run_view_into_table(tbl, start_gd, end_gd)




    def build_a_layer(self, parent, layer):
        col = CardCol(parent, flex_width=1, flex_height=1, pad=2)
        header = Plate(col, pad=5)
        Title(header, layer.upper(),  text_align='c')
        body = Plate(col, scroll_v=True, flex_height=1, pad=3)
        self.build_cards_for_layer(body, layer)




    def build_cards_for_layer(self, parent, layer):
        for tbl in BB.LAYERS[layer]:
            self.build_one_card(parent, tbl)


    # Pipe.py  method: build_one_card  NEW: jazzed-up table card with stats + buttons

    def build_one_card(self, parent, tbl):
        card = Card(parent, pad=5)
        head = Row(card)
        Title(head, tbl)
        Spacer(head)
        Body(head, f"{BB.col_count(tbl)}c")
        rows  = BB.row_count(tbl)
        mn, mx = BB.date_range(tbl)
        Body(card, f"Rows:   {rows:,}")
        rng = f"{MgrDT.gd_to_iso(mn)}  to  {MgrDT.gd_to_iso(mx)}"
        Body(card, f"Range:  {rng}")
        btns = Row(card)
        Button(btns, "Refresh"  ,   on_click=lambda: self.refresh_table(tbl))
        Button(btns, "Workbench",   on_click=self.passme)
        Button(btns, "SQL"      ,   on_click=lambda: self.view_in_sql(tbl))


    def view_in_sql(self, tbl):
        dates  = self.get_start_and_end_dates()
        start_gd, end_gd = dates if dates else (None, None)
        self.form.switch_tab("SQL")                                          # construct if first visit
        sql_tab = self.form.get_tab("SQL")
        if sql_tab is None:
            BB.log("view_in_sql", "ERROR", "SQL tab not found after switch")
            return
        sql_tab.load_query_for_table(tbl, BB.db_path, start_gd, end_gd)


    def passme(self):


        pass




    # ══════════════════════════════════════════════════════════════
    # Pitching
    # ══════════════════════════════════════════════════════════════



    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: pull_raw_pitches  NEW: external API → raw_pitches
    # Loops dates, transforms gd → GD as INT in transit, delete-then-insert per day.
    # Drops Statcast columns we don't know about; logs WARN listing them.
    # Logs every step to _run_log via BB.log.
    # ══════════════════════════════════════════════════════════════


    def pull_raw_pitches(self, start_gd, end_gd):
        BB.log("raw_pitches", "INFO", f"pull starting: GD {start_gd} → {end_gd}")
        t_overall  = _time.time()
        total_rows = 0
        known_cols = self.known_raw_pitches_cols()

        for gd_int in MgrDT.gd_range(start_gd, end_gd):
            day_str = MgrDT.gd_to_iso(gd_int)                    # pybaseball wants "YYYY-MM-DD"
            t_day   = _time.time()
            try:
                df = pybaseball.statcast(start_dt=day_str, end_dt=day_str, verbose=False)
            except Exception as e:
                BB.log("raw_pitches", "ERROR", f"{day_str} statcast call failed: {e}")
                continue

            if df is None or len(df) == 0:
                BB.log("raw_pitches", "INFO", f"{day_str} returned 0 rows (off day?)")
                continue

            df = self.conform_pitches_df(df, gd_int, known_cols)
            n  = self.replace_day_pitches(gd_int, df)
            ms = int((_time.time() - t_day) * 1000)
            BB.log("raw_pitches", "INFO", f"{day_str} inserted", rows=n, elapsed_ms=ms)
            total_rows += n

        ms_total = int((_time.time() - t_overall) * 1000)
        BB.log("raw_pitches", "DONE", f"pull complete: GD {start_gd} → {end_gd}",
               rows=total_rows, elapsed_ms=ms_total)




    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: conform_pitches_df  NEW: transform game_date→GD, drop unknowns
    # ══════════════════════════════════════════════════════════════

    def conform_pitches_df(self, df, gd_int, known_cols):
        df['GD'] = gd_int                                             # set GD directly to known int (faster than parsing per row)
        if 'game_date' in df.columns:
            df = df.drop(columns=['game_date'])
        df_cols = set(df.columns)
        extras  = df_cols - known_cols
        missing = known_cols - df_cols
        if extras:
            BB.log("raw_pitches", "WARN", f"Statcast drift: dropping unknown columns: {sorted(extras)}")
        if missing:
            BB.log("raw_pitches", "WARN", f"raw_pitches expects columns Statcast didn't return: {sorted(missing)}")
        keep = [c for c in df.columns if c in known_cols]
        return df[keep]


    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: replace_day_pitches  NEW: delete-then-insert one GD
    # ══════════════════════════════════════════════════════════════

    def replace_day_pitches(self, gd_int, df):
        import sqlite3
        conn = sqlite3.connect(BB.db_path)
        cur  = conn.execute("DELETE FROM raw_pitches WHERE GD = ?", (gd_int,))
        if cur.rowcount > 0:
            BB.log("raw_pitches", "INFO", f"GD {gd_int} replaced {cur.rowcount} existing rows")
        df.to_sql("raw_pitches", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        return len(df)


    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: known_raw_pitches_cols  NEW: column set from materialized table
    # Reads from sqlite_master / PRAGMA. Cached on first call.
    # ══════════════════════════════════════════════════════════════

    def known_raw_pitches_cols(self):
        rows = BB.query("PRAGMA table_info(raw_pitches)")
        return set(r[1] for r in rows)


    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: gd_int_to_date  NEW: 20240715 → date(2024, 7, 15)
    # ══════════════════════════════════════════════════════════════

    def gd_int_to_date(self, gd_int):
        s = str(gd_int)
        return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))


    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: parse_textbox_date_to_gd  NEW: read YYYY-MM-DD textbox, return GD int
    # ══════════════════════════════════════════════════════════════


    def parse_textbox_date_to_gd(self, name):
        raw = self.form.widgets[name].text
        return MgrDT.str_to_gd(raw)


    # ══════════════════════════════════════════════════════════════
    # Pipe.py  method: on_update_all_clicked  NEW: handler for top_section's Update all button
    # Replace `on_click=self.passme` on the "Update all" button with this method.
    # ══════════════════════════════════════════════════════════════

    def update_all(self):
        dates = self.get_start_and_end_dates()
        if dates is None: return
        start_gd, end_gd = dates
        self.purge_all_derived(start_gd, end_gd)                              # Phase 1
        self.run_raw_layer    (start_gd, end_gd)                              # Phase 2
        self.run_layer        ("etl",  start_gd, end_gd)                      # Phase 3a
        self.run_layer        ("feet", start_gd, end_gd)                      # Phase 3b
        self.refresh_pane     ()


    # ════════════════════════════════════════════════════════════════════════════
    # Pipe.py  method: purge_all_derived  NEW: Phase 1 — wipe GD range from etl+feet
    # Logs one line per table. Forest never touched.
    # ════════════════════════════════════════════════════════════════════════════

    def purge_all_derived(self, start_gd, end_gd):
        for tbl in BB.layer_tables("etl") + BB.layer_tables("feet"):
            rc = BB.execute(f"DELETE FROM {tbl} WHERE GD BETWEEN ? AND ?", (start_gd, end_gd))
            BB.log(tbl, "INFO", f"phase1 purge: {rc} rows for GD {start_gd} → {end_gd}", rows=rc)



    def get_start_and_end_dates(self):
        try:
            start_gd = self.parse_textbox_date_to_gd("txt_start_date")
            end_gd   = self.parse_textbox_date_to_gd("txt_end_date")
        except (ValueError, KeyError) as e:
            BB.log("update_all", "ERROR", f"bad date input: {e}")
            return None
        if start_gd > end_gd:
            BB.log("update_all", "ERROR", f"start_gd {start_gd} > end_gd {end_gd}; aborting")
            return None
        return start_gd, end_gd


    def run_raw_layer(self, start_gd, end_gd):
        for tbl in BB.LAYERS.get("raw", []):
            method_name = f"pull_{tbl}"
            if hasattr(self, method_name):
                getattr(self, method_name)(start_gd, end_gd)
            else:
                BB.log(tbl, "WARN", f"no puller method '{method_name}' on Pipe")


    def run_layer(self, layer, start_gd, end_gd):
        for tbl in BB.LAYERS.get(layer, []):
            self.run_view_into_table(tbl, start_gd, end_gd)


    def refresh_pane(self):
        self.form.set_pane(0, self.all_in_one)


    # ══════════════════════════════════════════════════════════════
    # Pipe.py  view→table orchestration — pure dispatch, helpers below
    # ══════════════════════════════════════════════════════════════


    def run_view_into_table(self, tbl, start_gd, end_gd):
        views = self.find_views(tbl)
        if not views: return
        pk_cols = self.target_pk_columns(tbl)
        if not pk_cols:
            BB.log(tbl, "ERROR", f"target has no PK; cannot UPSERT — aborting")
            return
        for view in views:
            columns = self.match_columns(view, tbl)
            if columns is None: continue
            self.execute_upsert(tbl, view, columns, pk_cols, start_gd, end_gd)


    # ════════════════════════════════════════════════════════════════════════════
    # Pipe.py  method: find_views  Update: prefix-match, alphabetical order
    # Returns list of view names sorted ascending.  pull_feet_batter_01_from_pa
    # sorts before pull_feet_batter_02_from_hardhit — controls run order.
    # ════════════════════════════════════════════════════════════════════════════

    def find_views(self, tbl):
        prefix = f"pull_{tbl}"
        rows   = BB.query(
            "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE ? ORDER BY name",
            (prefix + "%",),
        )
        if not rows:
            BB.log(tbl, "WARN", f"no views matching '{prefix}*' found; skipping")
            return []
        return [r[0] for r in rows]


    # ════════════════════════════════════════════════════════════════════════════
    # Pipe.py  method: target_pk_columns  NEW: read PK column names from PRAGMA
    # PRAGMA table_info returns (cid, name, type, notnull, dflt, pk_seq) where
    # pk_seq > 0 means part of PK. Sort by pk_seq to preserve composite order.
    # ════════════════════════════════════════════════════════════════════════════

    def target_pk_columns(self, tbl):
        rows = BB.query(f"PRAGMA table_info({tbl})")
        pks  = [(r[5], r[1]) for r in rows if r[5] > 0]                       # (pk_seq, name)
        pks.sort()
        return [name for _, name in pks]


    # ════════════════════════════════════════════════════════════════════════════
    # Pipe.py  method: execute_upsert  NEW: replaces execute_insert
    # Builds: INSERT INTO tbl (cols) SELECT cols FROM view WHERE GD BETWEEN ? AND ?
    #         ON CONFLICT(pk_cols) DO UPDATE SET <non-pk-col> = excluded.<non-pk-col>, ...
    # If view supplies only PK columns (no payload), the DO UPDATE clause is empty;
    # we degrade to ON CONFLICT DO NOTHING so first-view-with-just-keys still works.
    # ════════════════════════════════════════════════════════════════════════════

    def execute_upsert(self, tbl, view, columns, pk_cols, start_gd, end_gd):
        col_list   = ", ".join(columns)
        pk_list    = ", ".join(pk_cols)
        nonpk      = [c for c in columns if c not in pk_cols]
        set_clause = ", ".join(f"{c}=excluded.{c}" for c in nonpk)
        conflict   = f"DO UPDATE SET {set_clause}" if nonpk else "DO NOTHING"
        sql        = (
            f"INSERT INTO {tbl} ({col_list}) "
            f"SELECT {col_list} FROM {view} WHERE GD BETWEEN ? AND ? "
            f"ON CONFLICT({pk_list}) {conflict}"
        )
        rc = BB.execute(sql, (start_gd, end_gd))
        BB.log(tbl, "INFO", f"upsert from {view}: {rc} rows", rows=rc)


    def match_columns(self, view, tbl):
        view_cols   = set(r[1] for r in BB.query(f"PRAGMA table_info({view})"))
        target_cols = set(r[1] for r in BB.query(f"PRAGMA table_info({tbl})"))
        common      = view_cols & target_cols
        extras      = view_cols - target_cols
        missing     = target_cols - view_cols
        if extras:
            BB.log(tbl, "WARN", f"view '{view}' has extra columns (will drop): {sorted(extras)}")
        if missing:
            BB.log(tbl, "INFO", f"target '{tbl}' has columns view doesn't provide (will be NULL): {sorted(missing)}")
        if not common:
            BB.log(tbl, "ERROR", f"view '{view}' and target '{tbl}' share zero columns; aborting")
            return None
        return sorted(common)
