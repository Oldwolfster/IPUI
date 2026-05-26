# ETL.py  class: ETL  NEW: Self-discovering ETL dashboard — UI scaffolding (no sync logic yet)
from datetime import date, timedelta, datetime
from pybaseball import statcast

from ipui import *
import sqlite3
from pathlib import Path
from datetime import datetime

from ipui._forms.Showcase.ETL_Mixin import ETL_Mixin


class My_Name_Means_NOTHING(_BaseTab, ETL_Mixin):

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
    # PANES
    # ══════════════════════════════════════════════════════════════

    def commands(self, parent):
        self.build_schema()
        pitches_min, pitches_max = self.get_dates("pitches")

        frame = CardCol(parent, flex_height=1)
        header = Row(frame)
        Title(header, "ETL Pipeline", glow=True)
        Button(header, "Build Indexes",color_bg=Style.COLOR_BUTTON_CTA,on_click=self.build_indexes)
        Button(header, "Harvest Batters", on_click=self.harvest_batters)
        Button(header, "Sync Schedule", on_click=self.update_schedule)
        Spacer(header)
        Button(header, "Nuke", on_click=self.on_nuke_clicked,color_bg=Style.COLOR_BUTTON_DANGER)
        self.build_pitches_plate(frame, pitches_min, pitches_max)



        scroller = CardCol(frame, scroll_v=True)
        Title(scroller, "Derived Tables")
        for table_name, sync_method in self.scan_sync_methods():
            self.build_derived_plate(scroller, table_name, sync_method, pitches_max)

    def info(self, parent):
        card = CardCol(parent, scroll_v=True)
        Title(card, "Status", glow=True)
        self.lbl_status = Body(card, "Ready.")



    def status(self, str_status: str):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"etl [{ts}]: {str_status}")
        self.lbl_status.set_text(f"{self.lbl_status.text}\n[{ts}] {str_status}")

    # ══════════════════════════════════════════════════════════════
    # PLATES
    # ══════════════════════════════════════════════════════════════

    def build_pitches_plate(self, parent, pitches_min, pitches_max):
        plate = Plate(parent)
        row=Row(plate)
        Title(row, "pitches  (source)")
        Spacer(row)
        TextBox(row, initial_value="2026-03-18", name="txt_start_date")
        Body(row, "to:")
        TextBox(row, initial_value="2026-03-20", name="txt_end_date")
        Button(row, "Load/Reload", color_bg=Style.COLOR_BUTTON_CTA, on_click=self.update_pitches)

        row_count = self.get_row_count("pitches")

        Body(plate, f"Rows:   {row_count:,}")
        Body(plate, f"Range:  {pitches_min or '—'}  →  {pitches_max or '—'}")
        Body(plate, "Pulled from pybaseball (see BB tab)")


    def update_pitches(self):

        start_str = self.form.widgets["txt_start_date"].text.strip()
        end_str   = self.form.widgets["txt_end_date"].text.strip()
        start     = self.parse_date(start_str)
        end       = self.parse_date(end_str)
        if start is None or end is None:
            self.status("Bad date format. Use YYYY-MM-DD.")
            return
        if start > end:
            self.status("Start date must be before end date.")
            return

        conn        = self.open_db()

        total_days  = (end - start).days + 1
        total_rows  = 0

        for i, d in enumerate(self.date_range(start, end)):
            day_str = d.strftime("%Y-%m-%d")
            self.delete_day(conn,day_str)
            self.status(f"Pulling {day_str}... (day {i+1} of {total_days})")
            df = statcast(start_dt=day_str, end_dt=day_str, verbose=False)
            if df is not None and len(df) > 0:
                df = df.rename(columns={"game_date": "gd"})
                df.to_sql("pitches", conn, if_exists="append", index=False)
                total_rows += len(df)

        conn.close()
        self.set_pane(0, self.commands)
        self.status(
            f"Done! {total_rows:,} pitches across {total_days} days.\n"
            f"Range: {start_str} → {end_str}\n"
            f"DB: {self.DB_PATH}"
        )

    def delete_day(self, conn, day_str):
        exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pitches'").fetchone()
        if not exists:            return
        cur = conn.execute("DELETE FROM pitches WHERE gd = ?", (day_str,))
        if cur.rowcount > 0: self.status(f"Re-pull: deleted {cur.rowcount:,} existing pitches for {day_str}")
        conn.commit()

    def harvest_batters(self):
        conn = self.open_db()
        conn.execute("CREATE TABLE IF NOT EXISTS batters (id INTEGER PRIMARY KEY, name TEXT)")
        rows = conn.execute("""
            SELECT p.batter, p.des
            FROM pitches p
            LEFT JOIN batters b ON p.batter = b.id
            WHERE p.des IS NOT NULL
              AND b.id IS NULL
            GROUP BY p.batter
        """).fetchall()
        for batter_id, des in rows:
            parts = des.split()
            name  = (parts[0] + " " + parts[1]) if len(parts) >= 2 else des
            conn.execute("INSERT INTO batters (id, name) VALUES (?, ?)", (batter_id, name))
        conn.commit()
        conn.close()
        self.status(f"Harvested {len(rows):,} new batters.")

    def stale_dependencies(self, table_name, pitches_max):
        deps = self.SYNC_DEPS.get(table_name, [])
        stale = []
        for dep in deps:
            _, dep_max = self.get_dates(dep)
            if dep_max != pitches_max:
                stale.append(dep)
        return stale



    def build_derived_plate(self, parent, table_name, sync_method, pitches_max):
            plate = Plate(parent)
            row = Row(plate)
            Title(row, table_name)

            row_count            = self.get_row_count(table_name)
            table_min, table_max = self.get_dates(table_name)
            is_built             = row_count > 0
            is_current           = is_built and pitches_max is not None and table_max == pitches_max


            stale_deps           = self.stale_dependencies(table_name, pitches_max)

            if not is_built:
                Body(plate, "Status: not built")
                Body(plate, "Rows:   —")
                Body(plate, "Range:  —")
                if stale_deps:
                    Body(plate, f"⚠ Waiting on: {', '.join(stale_deps)}")
                    return
                Spacer(row)
                Button(row, "Sync", color_bg=Style.COLOR_BUTTON_CTA, on_click=sync_method)
                return

            Body(plate, f"Rows:   {row_count:,}")
            Body(plate, f"Range:  {table_min}  →  {table_max}")

            if is_current:
                Body(plate, "Status: up to date ✓")
                return

            gap = self.days_behind(table_max, pitches_max)
            Body(plate, f"Status: {gap} day(s) behind")
            if stale_deps:
                Body(plate, f"⚠ Waiting on: {', '.join(stale_deps)}")
                return
            Button(row, "Sync", color_bg=Style.COLOR_BUTTON_CTA, on_click=sync_method)

    # ══════════════════════════════════════════════════════════════
    # SCANNER — convention IS the registry
    # Any method named sync_<table_name> auto-registers
    # ══════════════════════════════════════════════════════════════

    def scan_sync_methods(self):
        results = []
        for name in dir(self):
            if not name.startswith("sync_"):  continue
            method = getattr(self, name)
            if not callable(method):          continue
            table_name = name[len("sync_"):]
            results.append((table_name, method))
        return results

    # ══════════════════════════════════════════════════════════════
    # Nuke the whole thing
    # ══════════════════════════════════════════════════════════════

    def on_nuke_clicked(self):
        self.form.msgbox(
            "WIPE EVERYTHING?\n\n"
            "This drops pitches AND all derived tables.\n"
            "You will need to re-pull from the BB tab.",
            MSG_BTNS_YES_NO + MSG_ICON_QUESTION + MSG_DEFAULT_2,
            "Nuke Database",
            on_result=self.on_nuke_confirmed,
        )


    def on_nuke_confirmed(self, result):
        if result != MSG_RESULT_YES:
            self.status("Nuke cancelled.")
            return
        self.nuke_database()

    def nuke_database(self):
        conn = self.open_db()
        self.status("Nuking database...")
        for table_name in self.all_table_names():
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.status(f"  dropped {table_name}")
        conn.commit()
        conn.close()
        self.set_pane(0, self.commands)
        self.status("Database nuked ✓  (use BB tab to re-pull pitches)")

    # ══════════════════════════════════════════════════════════════
    # DB HELPERS
    # ══════════════════════════════════════════════════════════════
    def all_table_names(self):
        conn = self.open_db()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]


    def yesterday(self):
        return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    def parse_date(self, text):
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except:
            return None

    def date_range(self, start, end):
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)

    def open_db(self):
        return sqlite3.connect(self.DB_PATH)

    def table_exists(self, conn, table_name):
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        ).fetchone()
        return row is not None

    def get_row_count(self, table_name):
        conn = self.open_db()
        if not self.table_exists(conn, table_name):
            conn.close()
            return 0
        row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        conn.close()
        return row[0]

    def get_dates(self, table_name):
        conn = self.open_db()
        if not self.table_exists(conn, table_name):
            conn.close()
            return (None, None)
        print(f"checking{table_name}")
        row = conn.execute(
            f"SELECT MIN(gd), MAX(gd) FROM {table_name}"
        ).fetchone()
        conn.close()
        return (row[0], row[1])

    def days_behind(self, table_max, pitches_max):
        fmt = "%Y-%m-%d"
        a   = datetime.strptime(table_max,   fmt).date()
        b   = datetime.strptime(pitches_max, fmt).date()
        return (b - a).days


    # ══════════════════════════════════════════════════════════════
    # SYNC STUBS — wire real logic later
    # ══════════════════════════════════════════════════════════════



    def sync_batter_games(self):
        self.run_sync("batter_games", """
            INSERT INTO batter_games
            SELECT
                gd,
                batter,
                game_pk,
                SUM(is_hit)                                        AS hits,
                SUM(is_ab)                                         AS at_bats,
                MAX(home)                                          AS home,
                MAX(stand)                                         AS stand,
                MAX(p_throws)                                      AS p_throws
            FROM   plate_appearances
            WHERE  gd NOT IN (SELECT DISTINCT gd FROM batter_games)
            GROUP  BY gd, batter, game_pk
        """)

    def sync_plate_appearances(self):
        self.run_sync("plate_appearances", """
            INSERT INTO plate_appearances
            SELECT
                gd,
                batter,
                at_bat_number,
                game_pk,
                pitcher,
                stand,
                p_throws,
                CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END                  AS home,
                CASE WHEN inning_topbot = 'Bot' THEN home_team ELSE away_team END  AS bat_team,
                CASE WHEN inning_topbot = 'Bot' THEN away_team ELSE home_team END  AS pit_team,
                home_team                                                          AS park,
                MAX(events)                                                        AS events,
                MAX(CASE WHEN events IN ('single','double','triple','home_run')
                         THEN 1 ELSE 0 END)                                        AS is_hit,
                MAX(CASE WHEN events IS NOT NULL AND events NOT IN
                         ('walk','hit_by_pitch','sac_bunt','sac_fly','catcher_interf')
                         THEN 1 ELSE 0 END)                                        AS is_ab,
                MAX(CASE WHEN events IN ('strikeout','strikeout_double_play')
                         THEN 1 ELSE 0 END)                                        AS is_k,
                MAX(CASE WHEN events IN ('walk','hit_by_pitch')
                         THEN 1 ELSE 0 END)                                        AS is_bb,
                MAX(launch_speed)                                                  AS launch_speed,
                MAX(launch_angle)                                                  AS launch_angle,
                MAX(estimated_ba_using_speedangle)                                 AS xba,
                MAX(woba_value)                                                    AS woba_value,
                MAX(woba_denom)                                                    AS woba_denom,
                MAX(babip_value)                                                   AS babip_value,
                MAX(iso_value)                                                     AS iso_value,
                MAX(n_thruorder_pitcher)                                           AS thru_order,
                MAX(batter_days_since_prev_game)                                   AS bat_rest,
                MAX(pitcher_days_since_prev_game)                                  AS pit_rest,
                MAX(age_bat)                                                       AS age_bat,
                MAX(age_pit)                                                       AS age_pit,
                MAX(if_fielding_alignment)                                         AS if_align,
                MAX(of_fielding_alignment)                                         AS of_align
            FROM   pitches
            WHERE  events IS NOT NULL
              AND  gd NOT IN (SELECT DISTINCT gd FROM plate_appearances)
            GROUP  BY gd, batter, game_pk, at_bat_number
        """)


    def sync_batter_features(self):
        tb_e  = self.tb_expr()
        slg_e = self.slg_expr()
        iso_e = self.iso_expr()
        obp_e = self.obp_expr()
        ops_e = self.ops_expr()

        self.run_sync("batter_features", f"""
            INSERT INTO batter_features
            SELECT
                src.gd                                                          AS gd,
                prior.batter                                                    AS batter,
                COUNT(*)                                                        AS pa_season,
                SUM(prior.is_ab)                                                AS ab_season,
                SUM(prior.is_hit)                                               AS hits_season,
                {tb_e}                                                          AS tb_season,
                SUM(prior.is_hit) * 1.0 / NULLIF(SUM(prior.is_ab), 0)           AS ba_season,
                {slg_e}                                                         AS slg_season,
                {iso_e}                                                         AS iso_season,
                {obp_e}                                                         AS obp_season,
                {ops_e}                                                         AS ops_season,
                SUM(prior.is_k)   * 1.0 / COUNT(*)                              AS k_pct_season,
                SUM(prior.is_bb)  * 1.0 / COUNT(*)                              AS bb_pct_season,
                AVG(prior.xba)                                                  AS xba_season,
                SUM(CASE WHEN prior.launch_speed >= 95 THEN 1 ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.launch_speed IS NOT NULL
                                    THEN 1 ELSE 0 END), 0)                      AS hard_hit_pct,
                AVG(prior.launch_speed)                                         AS avg_ls,
                SUM(CASE WHEN prior.p_throws = 'L' THEN prior.is_hit ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.p_throws = 'L' AND prior.is_ab = 1
                                    THEN 1 ELSE 0 END), 0)                      AS ba_vs_lhp,
                SUM(CASE WHEN prior.p_throws = 'R' THEN prior.is_hit ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.p_throws = 'R' AND prior.is_ab = 1
                                    THEN 1 ELSE 0 END), 0)                      AS ba_vs_rhp
            FROM       (SELECT DISTINCT gd FROM plate_appearances
                        WHERE  gd NOT IN (SELECT gd FROM batter_features)) src
            INNER JOIN plate_appearances                                       prior
                       ON prior.gd                       <  src.gd
                      AND substr(prior.gd, 1, 4)         =  substr(src.gd, 1, 4)
            GROUP  BY  src.gd, prior.batter
        """)

# ════════════════════════════════════════════════════════════════════════════════
# ETL.py  method: sync_pitcher_features  Update: compose SQL from offensive-stat helpers
# ════════════════════════════════════════════════════════════════════════════════

    def sync_pitcher_features(self):
        tb_e  = self.tb_expr()
        slg_e = self.slg_expr()
        iso_e = self.iso_expr()
        obp_e = self.obp_expr()
        ops_e = self.ops_expr()

        self.run_sync("pitcher_features", f"""
            INSERT INTO pitcher_features
            SELECT
                src.gd                                                          AS gd,
                prior.pitcher                                                   AS pitcher,
                COUNT(*)                                                        AS pa_season,
                SUM(prior.is_ab)                                                AS ab_season,
                SUM(prior.is_hit)                                               AS hits_allowed,
                {tb_e}                                                          AS tb_allowed,
                SUM(prior.is_hit) * 1.0 / NULLIF(SUM(prior.is_ab), 0)           AS ba_against,
                {slg_e}                                                         AS slg_against,
                {iso_e}                                                         AS iso_against,
                {obp_e}                                                         AS obp_against,
                {ops_e}                                                         AS ops_against,
                SUM(prior.is_k)   * 1.0 / COUNT(*)                              AS k_pct_season,
                SUM(prior.is_bb)  * 1.0 / COUNT(*)                              AS bb_pct_season,
                AVG(prior.xba)                                                  AS xba_allowed,
                SUM(CASE WHEN prior.launch_speed >= 95 THEN 1 ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.launch_speed IS NOT NULL
                                    THEN 1 ELSE 0 END), 0)                      AS hard_hit_pct,
                SUM(CASE WHEN prior.stand = 'L' THEN prior.is_hit ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.stand = 'L' AND prior.is_ab = 1
                                    THEN 1 ELSE 0 END), 0)                      AS ba_against_lhb,
                SUM(CASE WHEN prior.stand = 'R' THEN prior.is_hit ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.stand = 'R' AND prior.is_ab = 1
                                    THEN 1 ELSE 0 END), 0)                      AS ba_against_rhb
            FROM       (SELECT DISTINCT gd FROM plate_appearances
                        WHERE  gd NOT IN (SELECT gd FROM pitcher_features)) src
            INNER JOIN plate_appearances                                       prior
                       ON prior.gd                       <  src.gd
                      AND substr(prior.gd, 1, 4)         =  substr(src.gd, 1, 4)
            GROUP  BY  src.gd, prior.pitcher
        """)

    def sync_league_summary(self):
        tb_e  = self.tb_expr()
        slg_e = self.slg_expr()
        iso_e = self.iso_expr()
        obp_e = self.obp_expr()
        ops_e = self.ops_expr()

        self.run_sync("league_summary", f"""
            INSERT INTO league_summary
            SELECT
                src.gd                                                  AS gd,
                COUNT(*)                                                AS pa_count,
                SUM(prior.is_ab)                                        AS ab_count,
                SUM(prior.is_hit)                                       AS hit_count,
                {tb_e}                                                  AS tb_count,
                SUM(prior.is_hit) * 1.0 / NULLIF(SUM(prior.is_ab), 0)   AS league_ba,
                {slg_e}                                                 AS league_slg,
                {iso_e}                                                 AS league_iso,
                {obp_e}                                                 AS league_obp,
                {ops_e}                                                 AS league_ops,
                SUM(prior.is_k)   * 1.0 / COUNT(*)                      AS league_k
            FROM       (SELECT DISTINCT gd FROM plate_appearances
                        WHERE  gd NOT IN (SELECT gd FROM league_summary)) src
            INNER JOIN plate_appearances                                   prior
                       ON  prior.gd                       <  src.gd
                      AND  substr(prior.gd, 1, 4)         =  substr(src.gd, 1, 4)
            GROUP BY   src.gd
        """)
    def sync_pitch_bucketed(self):
        case_expr = self.bucket_case_expression()
        self.run_sync("pitch_bucketed", f"""
            INSERT INTO pitch_bucketed
            SELECT
                gd,
                game_pk,
                at_bat_number,
                batter,
                pitcher,
                pitch_type,
                {case_expr}                                                        AS bucket,
                CASE WHEN events IS NOT NULL THEN 1 ELSE 0 END                     AS ends_pa,
                CASE WHEN events IN ('single','double','triple','home_run')
                     THEN 1 ELSE 0 END                                             AS is_hit,
                CASE WHEN events IS NOT NULL AND events NOT IN
                     ('walk','hit_by_pitch','sac_bunt','sac_fly','catcher_interf')
                     THEN 1 ELSE 0 END                                             AS is_ab
            FROM   pitches
            WHERE  gd NOT IN (SELECT DISTINCT gd FROM pitch_bucketed)
        """)

    def bucket_case_expression(self):
        clauses = [f"WHEN pitch_type = '{code}' THEN '{bucket}'"
                   for code, bucket in self.PITCH_BUCKETS.items()]
        return "CASE " + " ".join(clauses) + " ELSE 'other' END"


    def sync_pitcher_pitch_mix(self):
        self.run_sync("pitcher_pitch_mix", """
            INSERT INTO pitcher_pitch_mix
            SELECT
                src.gd                                                                            AS gd,
                prior.pitcher                                                                     AS pitcher,
                COUNT(*)                                                                          AS pitches_total,
                SUM(CASE WHEN prior.bucket = 'fastball' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)       AS pct_fastball,
                SUM(CASE WHEN prior.bucket = 'breaking' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)       AS pct_breaking,
                SUM(CASE WHEN prior.bucket = 'offspeed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)       AS pct_offspeed,
                SUM(CASE WHEN prior.bucket = 'other'    THEN 1 ELSE 0 END) * 1.0 / COUNT(*)       AS pct_other
            FROM       (SELECT DISTINCT gd FROM pitch_bucketed
                        WHERE  gd NOT IN (SELECT gd FROM pitcher_pitch_mix)) src
            INNER JOIN pitch_bucketed                                          prior
                       ON prior.gd                       <  src.gd
                      AND substr(prior.gd, 1, 4)         =  substr(src.gd, 1, 4)
            GROUP  BY  src.gd, prior.pitcher
        """)

# ETL.py  method: sync_batter_vs_pitch  NEW: BA against each pitch bucket, season-to-date, PA-ending pitches only

    def sync_batter_vs_pitch(self):
        self.run_sync("batter_vs_pitch", """
            INSERT INTO batter_vs_pitch
            SELECT
                src.gd                                                  AS gd,
                prior.batter                                            AS batter,
                prior.bucket                                            AS bucket,
                SUM(prior.is_ab)                                        AS abs,
                SUM(prior.is_hit)                                       AS hits,
                SUM(prior.is_hit) * 1.0 / NULLIF(SUM(prior.is_ab), 0)   AS ba
            FROM       (SELECT DISTINCT gd FROM pitch_bucketed
                        WHERE  gd NOT IN (SELECT gd FROM batter_vs_pitch)) src
            INNER JOIN pitch_bucketed                                          prior
                       ON prior.gd                       <  src.gd
                      AND substr(prior.gd, 1, 4)         =  substr(src.gd, 1, 4)
                      AND prior.ends_pa                  =  1
            GROUP  BY  src.gd, prior.batter, prior.bucket
        """)


    def run_sync(self, table_name, sql):
        conn = self.open_db()
        self.status(f"{table_name}: syncing...")
        conn.execute(sql)
        conn.commit()
        conn.close()
        self.set_pane(0,self.commands)
        self.status(f"{table_name}: synced ✓")



    # ══════════════════════════════════════════════════════════════
    # Schedule
    # ══════════════════════════════════════════════════════════════

    def update_schedule(self):
        import statsapi
        from datetime import date, timedelta

        pitches_min, pitches_max = self.get_dates("pitches")
        if pitches_min is None:
            self.status("No pitches loaded — sync pitches first.")
            return

        start_str = pitches_min
        end_str = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")

        self.status(f"Pulling schedule {start_str} → {end_str}...")
        raw = statsapi.get("schedule", {
            "sportId": 1,
            "startDate": start_str,
            "endDate": end_str,
            "hydrate": "probablePitcher",
        })

        conn = self.open_db()
        conn.execute("DELETE FROM schedule WHERE gd BETWEEN ? AND ?", (start_str, end_str))

        rows_in = 0
        for date_entry in raw.get("dates", []):
            gd = date_entry.get("date")
            for g in date_entry.get("games", []):
                row = self.extract_schedule_row(gd, g)
                conn.execute("""
                    INSERT INTO schedule
                    (gd, game_pk, game_datetime, status,
                     home_team, away_team, home_team_id, away_team_id,
                     home_starter_id, away_starter_id, venue, game_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
                rows_in += 1

        conn.commit()
        conn.close()
        self.set_pane(0, self.commands)
        self.status(f"Schedule synced: {rows_in:,} games ({start_str} → {end_str})")
        self.verify_game_pk_match()

    def extract_schedule_row(self, gd, g):
        home   = g.get("teams", {}).get("home", {})
        away   = g.get("teams", {}).get("away", {})
        home_p = home.get("probablePitcher") or {}
        away_p = away.get("probablePitcher") or {}
        return (
            gd,
            g.get("gamePk"),
            g.get("gameDate"),
            g.get("status", {}).get("detailedState"),
            home.get("team", {}).get("name"),
            away.get("team", {}).get("name"),
            home.get("team", {}).get("id"),
            away.get("team", {}).get("id"),
            home_p.get("id"),
            away_p.get("id"),
            g.get("venue", {}).get("name"),
            g.get("gameType"),
        )

    # ETL.py  method: verify_game_pk_match  NEW: one-shot diagnostic — confirms schedule.game_pk == pitches.game_pk
    def verify_game_pk_match(self):
        conn = self.open_db()
        row = conn.execute("""
            SELECT
                (SELECT COUNT(DISTINCT game_pk) FROM schedule
                  WHERE gd IN (SELECT DISTINCT gd FROM pitches))    AS sched_games,
                (SELECT COUNT(DISTINCT game_pk) FROM pitches)       AS pitch_games,
                (SELECT COUNT(DISTINCT s.game_pk)
                   FROM schedule s
                   JOIN pitches  p ON s.game_pk = p.game_pk)        AS joined_games
        """).fetchone()
        conn.close()
        sched, pitch, joined = row
        self.status(
            f"game_pk verification:\n"
            f"  schedule games (on dates we have pitches): {sched:,}\n"
            f"  pitches games:                              {pitch:,}\n"
            f"  matched on game_pk:                         {joined:,}\n"
            f"  → {'✓ IDS MATCH' if joined == pitch else '⚠ MISMATCH'}"
        )

    # ══════════════════════════════════════════════════════════════
    # OBS HELPERS
    # ══════════════════════════════════════════════════════════════
    def total_bases_expr(self, col="prior.events"):
        clauses = [f"WHEN {col} = '{evt}' THEN {tb}"
                   for evt, tb in self.EVENT_BASES.items()]
        return "CASE " + " ".join(clauses) + " ELSE 0 END"

    # ETL.py  method: tb_expr  NEW: SUM of total bases (e.g. for tb_season column)
    def tb_expr(self):        return f"SUM({self.total_bases_expr()})"

    # ETL.py  method: slg_expr  NEW: SLG = total bases / at-bats
    def slg_expr(self): return f"{self.tb_expr()} * 1.0 / NULLIF(SUM(prior.is_ab), 0)"

    # ETL.py  method: iso_expr  NEW: ISO = SLG - BA = (TB - hits) / AB; pure power
    def iso_expr(self):        return f"({self.tb_expr()} - SUM(prior.is_hit)) * 1.0 / NULLIF(SUM(prior.is_ab), 0)"

    # ETL.py  method: obp_expr  NEW: OBP = (hits + walks) / PA
    def obp_expr(self):   return "(SUM(prior.is_hit) + SUM(prior.is_bb)) * 1.0 / NULLIF(COUNT(*), 0)"

    # ETL.py  method: ops_expr  NEW: OPS = OBP + SLG
    def ops_expr(self):return f"({self.obp_expr()}) + ({self.slg_expr()})"

    # ════════════════════════════════════════════════════════════════════════════════
    # ETL.py  method: sync_staging_batter_features_season  NEW
    # All season-to-date aggregation moved here from sync_batter_features.
    # Year-bounded + gd-< prior pattern, identical math to v2 of sync_batter_features.
    # Existing offensive-stat helpers (tb_expr / slg_expr / iso_expr / obp_expr /
    # ops_expr) compose the SQL exactly as before.
    # ════════════════════════════════════════════════════════════════════════════════

    def sync_staging_batter_features_season(self):
        tb_e  = self.tb_expr()
        slg_e = self.slg_expr()
        iso_e = self.iso_expr()
        obp_e = self.obp_expr()
        ops_e = self.ops_expr()

        self.run_sync("staging_batter_features_season", f"""
            INSERT INTO staging_batter_features_season
            SELECT
                src.gd                                                          AS gd,
                prior.batter                                                    AS batter,
                COUNT(*)                                                        AS pa_season,
                SUM(prior.is_ab)                                                AS ab_season,
                SUM(prior.is_hit)                                               AS hits_season,
                {tb_e}                                                          AS tb_season,
                SUM(prior.is_hit) * 1.0 / NULLIF(SUM(prior.is_ab), 0)           AS ba_season,
                {slg_e}                                                         AS slg_season,
                {iso_e}                                                         AS iso_season,
                {obp_e}                                                         AS obp_season,
                {ops_e}                                                         AS ops_season,
                SUM(prior.is_k)   * 1.0 / COUNT(*)                              AS k_pct_season,
                SUM(prior.is_bb)  * 1.0 / COUNT(*)                              AS bb_pct_season,
                AVG(prior.xba)                                                  AS xba_season,
                SUM(CASE WHEN prior.launch_speed >= 95 THEN 1 ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.launch_speed IS NOT NULL
                                    THEN 1 ELSE 0 END), 0)                      AS hard_hit_pct,
                AVG(prior.launch_speed)                                         AS avg_ls,
                SUM(CASE WHEN prior.p_throws = 'L' THEN prior.is_hit ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.p_throws = 'L' AND prior.is_ab = 1
                                    THEN 1 ELSE 0 END), 0)                      AS ba_vs_lhp,
                SUM(CASE WHEN prior.p_throws = 'R' THEN prior.is_hit ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN prior.p_throws = 'R' AND prior.is_ab = 1
                                    THEN 1 ELSE 0 END), 0)                      AS ba_vs_rhp
            FROM       (SELECT DISTINCT gd FROM plate_appearances
                        WHERE  gd NOT IN (SELECT gd FROM staging_batter_features_season)) src
            INNER JOIN plate_appearances                                       prior
                       ON prior.gd                       <  src.gd
                      AND substr(prior.gd, 1, 4)         =  substr(src.gd, 1, 4)
            GROUP  BY  src.gd, prior.batter
        """)


    # ════════════════════════════════════════════════════════════════════════════════
    # ETL.py  method: sync_batter_features  Update: boring assembly — pure JOIN of
    # staging tables into the final destination. All math lives upstream now.
    # ════════════════════════════════════════════════════════════════════════════════

    def sync_batter_features(self):
        self.run_sync("batter_features", """
            INSERT INTO batter_features
            SELECT
                s.gd,
                s.batter,
                s.pa_season,
                s.ab_season,
                s.hits_season,
                s.tb_season,
                s.ba_season,
                s.slg_season,
                s.iso_season,
                s.obp_season,
                s.ops_season,
                s.k_pct_season,
                s.bb_pct_season,
                s.xba_season,
                s.hard_hit_pct,
                s.avg_ls,
                s.ba_vs_lhp,
                s.ba_vs_rhp
            FROM   staging_batter_features_season s
            WHERE  (s.gd, s.batter) NOT IN (SELECT gd, batter FROM batter_features)
        """)




# ════════════════════════════════════════════════════════════════════════════════
# ETL.py  method: sync_batter_games  Update: +hr, +k, +sf columns
# Same MAX-event pattern as existing fields; same PA-level events source.
# ════════════════════════════════════════════════════════════════════════════════

    def sync_batter_games(self):
        self.run_sync("batter_games", """
            INSERT INTO batter_games
            SELECT
                gd,
                batter,
                game_pk,
                SUM(is_hit)                                                AS hits,
                SUM(is_ab)                                                 AS at_bats,
                SUM(CASE WHEN events = 'home_run'  THEN 1 ELSE 0 END)      AS hr,
                SUM(is_k)                                                  AS k,
                SUM(CASE WHEN events = 'sac_fly'   THEN 1 ELSE 0 END)      AS sf,
                MAX(home)                                                  AS home,
                MAX(stand)                                                 AS stand,
                MAX(p_throws)                                              AS p_throws
            FROM   plate_appearances
            WHERE  gd NOT IN (SELECT DISTINCT gd FROM batter_games)
            GROUP  BY gd, batter, game_pk
        """)


# ════════════════════════════════════════════════════════════════════════════════
# ETL.py  method: sync_staging_batter_features_recent_form  NEW
# The complex one. Six rolling/streak features computed in a single CTE chain.
# Year-bounded: streaks and windows don't cross seasons.
# "As of" semantics: for game on `gd`, look at games STRICTLY before `gd`.
    # ════════════════════════════════════════════════════════════════════════════════
    # CTE breakdown:
    #   per_batter_game        — one row per (year, batter, game), with had_hit flag
    #                            and a game ordinal so we can do windowed lookbacks.
    #   streak_breakers        — the most recent prior game where the batter went
    #                            hitless (for streak_with_hit) or got a hit
    #                            (for streak_without_hit). NULL = no breaker exists,
    #                            streak is the full season game count.
    #   src_gds                — all (gd, batter) targets needing a recent_form row.
    # Final SELECT joins src_gds back to per_batter_game (looking up the batter's
    # most-recent game STRICTLY before src.gd) and computes the 6 features from
    # the windowed views.
    # ════════════════════════════════════════════════════════════════════════════════

    def sync_staging_batter_features_recent_form(self):
        self.run_sync("staging_batter_features_recent_form", """
            INSERT INTO staging_batter_features_recent_form
            WITH per_batter_game AS (
                SELECT
                    bg.gd                                                  AS gd,
                    bg.batter                                              AS batter,
                    substr(bg.gd, 1, 4)                                    AS yr,
                    bg.hits                                                AS hits,
                    bg.at_bats                                             AS at_bats,
                    bg.hr                                                  AS hr,
                    bg.k                                                   AS k,
                    bg.sf                                                  AS sf,
                    CASE WHEN bg.hits >  0 THEN 1 ELSE 0 END               AS had_hit,
                    CASE WHEN bg.hits >= 2 THEN 1 ELSE 0 END               AS multi_hit,
                    ROW_NUMBER() OVER (
                        PARTITION BY bg.batter, substr(bg.gd, 1, 4)
                        ORDER BY bg.gd
                    )                                                      AS game_num_in_year
                FROM batter_games bg
            ),
            src_gds AS (
                SELECT DISTINCT
                    bg.gd                                                  AS gd,
                    bg.batter                                              AS batter,
                    substr(bg.gd, 1, 4)                                    AS yr
                FROM   batter_games bg
                WHERE  (bg.gd, bg.batter) NOT IN
                       (SELECT gd, batter FROM staging_batter_features_recent_form)
            )
            SELECT
                src.gd                                                     AS gd,
                src.batter                                                 AS batter,

                -- streak_with_hit: count of consecutive most-recent prior
                -- games (this season) with had_hit = 1, ending at the last
                -- prior game. Total prior games minus the game_num_in_year
                -- of the most recent hitless game.
                COALESCE(
                    (SELECT COUNT(*)
                       FROM per_batter_game p
                      WHERE p.batter = src.batter
                        AND p.yr     = src.yr
                        AND p.gd     < src.gd)
                  - COALESCE(
                       (SELECT MAX(p.game_num_in_year)
                          FROM per_batter_game p
                         WHERE p.batter   = src.batter
                           AND p.yr       = src.yr
                           AND p.gd       < src.gd
                           AND p.had_hit  = 0),
                       0),
                    0)                                                     AS streak_with_hit,

                -- streak_without_hit: mirror, ending in 0-hit games.
                COALESCE(
                    (SELECT COUNT(*)
                       FROM per_batter_game p
                      WHERE p.batter = src.batter
                        AND p.yr     = src.yr
                        AND p.gd     < src.gd)
                  - COALESCE(
                       (SELECT MAX(p.game_num_in_year)
                          FROM per_batter_game p
                         WHERE p.batter   = src.batter
                           AND p.yr       = src.yr
                           AND p.gd       < src.gd
                           AND p.had_hit  = 1),
                       0),
                    0)                                                     AS streak_without_hit,

                -- hits_last_5: sum hits in 5 most-recent prior games this season.
                COALESCE(
                    (SELECT SUM(p.hits) FROM (
                        SELECT hits FROM per_batter_game
                         WHERE batter = src.batter
                           AND yr     = src.yr
                           AND gd     < src.gd
                         ORDER BY gd DESC
                         LIMIT 5
                    ) p),
                    0)                                                     AS hits_last_5,

                -- hits_last_10: same, longer window.
                COALESCE(
                    (SELECT SUM(p.hits) FROM (
                        SELECT hits FROM per_batter_game
                         WHERE batter = src.batter
                           AND yr     = src.yr
                           AND gd     < src.gd
                         ORDER BY gd DESC
                         LIMIT 10
                    ) p),
                    0)                                                     AS hits_last_10,

                -- games_since_multi_hit: prior games this season minus
                -- game_num_in_year of last multi-hit game. NULL if none.
                CASE
                    WHEN (SELECT MAX(p.game_num_in_year)
                            FROM per_batter_game p
                           WHERE p.batter    = src.batter
                             AND p.yr        = src.yr
                             AND p.gd        < src.gd
                             AND p.multi_hit = 1) IS NULL
                    THEN NULL
                    ELSE (SELECT COUNT(*)
                            FROM per_batter_game p
                           WHERE p.batter = src.batter
                             AND p.yr     = src.yr
                             AND p.gd     < src.gd)
                       - (SELECT MAX(p.game_num_in_year)
                            FROM per_batter_game p
                           WHERE p.batter    = src.batter
                             AND p.yr        = src.yr
                             AND p.gd        < src.gd
                             AND p.multi_hit = 1)
                END                                                        AS games_since_multi_hit,

                -- babip_last_10: (hits - hr) / (ab - k - hr + sf) over 10 most-recent
                -- prior games. NULL if denominator is 0 (rare; e.g., walked every PA).
                (SELECT
                    (SUM(p.hits) - SUM(p.hr)) * 1.0
                    / NULLIF(SUM(p.at_bats) - SUM(p.k) - SUM(p.hr) + SUM(p.sf), 0)
                 FROM (
                    SELECT hits, hr, at_bats, k, sf FROM per_batter_game
                     WHERE batter = src.batter
                       AND yr     = src.yr
                       AND gd     < src.gd
                     ORDER BY gd DESC
                     LIMIT 10
                 ) p)                                                       AS babip_last_10

            FROM src_gds src
        """)


# ════════════════════════════════════════════════════════════════════════════════
# ETL.py  method: sync_batter_features  Update: LEFT JOIN both staging tables
# Boring assembly. All math lives upstream. Two LEFT JOINs, one INSERT.
# ════════════════════════════════════════════════════════════════════════════════

    def sync_batter_features(self):
        self.run_sync("batter_features", """
            INSERT INTO batter_features
            SELECT
                s.gd,
                s.batter,
                s.pa_season,
                s.ab_season,
                s.hits_season,
                s.tb_season,
                s.ba_season,
                s.slg_season,
                s.iso_season,
                s.obp_season,
                s.ops_season,
                s.k_pct_season,
                s.bb_pct_season,
                s.xba_season,
                s.hard_hit_pct,
                s.avg_ls,
                s.ba_vs_lhp,
                s.ba_vs_rhp,
                r.streak_with_hit,
                r.streak_without_hit,
                r.hits_last_5,
                r.hits_last_10,
                r.games_since_multi_hit,
                r.babip_last_10
            FROM       staging_batter_features_season           s
            LEFT  JOIN staging_batter_features_recent_form      r
                       ON  r.gd     = s.gd
                      AND  r.batter = s.batter
            WHERE      (s.gd, s.batter) NOT IN
                       (SELECT gd, batter FROM batter_features)
        """)