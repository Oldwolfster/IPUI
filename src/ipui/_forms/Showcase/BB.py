from datetime import date, timedelta, datetime
import sqlite3
from pathlib import Path
from pybaseball import statcast
from ipui import *




DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")


class EZ_Pane(_BaseTab):


    # ══════════════════════════════════════════════════════════════
    # PITCH BUCKETS
    # Statcast pitch_type codes grouped into 4 families.
    # Anything unknown falls into "other".
    # ══════════════════════════════════════════════════════════════

    PITCH_BUCKETS = {
        "FF": "fastball", "SI": "fastball", "FC": "fastball", "FA": "fastball",
        "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking", "SV": "breaking", "CS": "breaking",
        "CH": "offspeed", "FS": "offspeed", "SP": "offspeed", "FO": "offspeed",
    }
    BUCKETS = ["fastball", "breaking", "offspeed", "other"]

    # ══════════════════════════════════════════════════════════════
    # PANES
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

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
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(DB_PATH)

    def create_indexes(self, conn):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_game_date ON pitches(game_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_batter    ON pitches(batter)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pitcher   ON pitches(pitcher)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events    ON pitches(events)")
        conn.commit()

    def distinct_game_dates(self, conn):
        rows = conn.execute("""
            SELECT DISTINCT game_date
            FROM   plate_appearances
            ORDER  BY game_date
        """).fetchall()
        return [r[0] for r in rows]

    def commands(self, parent):
        card = CardCol(parent)
        Title(card, "Build Vault", glow=True)
        Body(card, "Pull Statcast pitch data day-by-day into SQLite")

        row = Row(card)
        Body(row, "Start Date:")
        TextBox(row, initial_value="2026-03-18", name="txt_start_date")

        row = Row(card)
        Body(row, "End Date:")
        TextBox(row, initial_value="2026-03-20", name="txt_end_date")
        #TextBox(row, initial_value=self.yesterday(), name="txt_end_date")

        row = Row(card)
        Button(row, "Build Vault",  color_bg=Style.COLOR_BUTTON_CTA, on_click=self.run_vault)
        Button(row, "Harvest Batters", on_click=self.harvest_batters)  # NEW
        Button(row, "Build Training", on_click=self.build_training)
        Button(row, "Build Pitch Mix", color_bg=Style.COLOR_BUTTON_CTA, on_click=self.build_pitcher_pitch_mix)
        Button(row, "Build Batter vs Pitch", color_bg=Style.COLOR_BUTTON_CTA, on_click=self.build_batter_vs_pitch)

        #Button(row, "Build PlateAppearance", on_click=self.build_pa)
        Button(row, "All Features",
               color_bg=Style.COLOR_BUTTON_CTA,
               on_click=self.build_all)



    def info(self, parent):
        card = CardCol(parent, scroll_v=True)
        Title(card, "Status", glow=True)
        self.lbl_status= Body(card, "Ready.")

    def status(self,str_status: str):
        print(f"status: {str_status}")
        self.lbl_status.set_text( f"{self.lbl_status.text}\n{str_status}")

    # ══════════════════════════════════════════════════════════════
    # VAULT BUILDER
    # ══════════════════════════════════════════════════════════════

    def run_vault(self):

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
                df.to_sql("pitches", conn, if_exists="append", index=False)
                total_rows += len(df)

        self.create_indexes(conn)
        conn.close()
        self.status(
            f"Done! {total_rows:,} pitches across {total_days} days.\n"
            f"Range: {start_str} → {end_str}\n"
            f"DB: {DB_PATH}"
        )

    def delete_day(self, conn, day_str):
        exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pitches'").fetchone()
        if not exists:            return
        cur = conn.execute("DELETE FROM pitches WHERE game_date = ?", (day_str,))
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


    # BB.py method: build_training  NEW: Build batter_games training table
    def build_training(self):
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS batter_games")
        conn.execute("""
                CREATE TABLE batter_games (
                    batter      INTEGER,
                    game_date   TEXT,
                    hits        INTEGER,
                    at_bats     INTEGER,
                    home        INTEGER,
                    stand       TEXT,
                    p_throws    TEXT,
                    PRIMARY KEY (batter, game_date)
                )
            """)
        conn.execute("""
                INSERT INTO batter_games
                SELECT
                    batter,
                    game_date,
                    SUM(CASE WHEN events IN ('single','double','triple','home_run') THEN 1 ELSE 0 END) as hits,
                    SUM(CASE WHEN events IS NOT NULL THEN 1 ELSE 0 END) as at_bats,
                    MAX(CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END) as home,
                    MAX(stand) as stand,
                    MAX(p_throws) as p_throws
                FROM pitches
                GROUP BY batter, game_date
            """)
        count = conn.execute("SELECT COUNT(*) FROM batter_games").fetchone()[0]
        conn.commit()
        conn.close()
        self.status(f"Built {count:,} batter-game training rows.")


   

    # ══════════════════════════════════════════════════════════════
    # BUILD ALL FEATURES
    # ══════════════════════════════════════════════════════════════

    def build_all(self):
        #self.reset_status()
        self.build_pa_features()
        self.build_batter_features()
        self.build_pitcher_features()
        self.status("")
        self.status("All feature tables built. ✓")

    # ══════════════════════════════════════════════════════════════
    # PA-LEVEL ENRICHED TABLE
    # Pulls everything we need from pitches at PA grain.
    # One row per PA, with all signals known *before* the pitch.
    # ══════════════════════════════════════════════════════════════

    def build_pa_features(self):
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS plate_appearances")
        conn.execute("""
            CREATE TABLE plate_appearances AS
            SELECT
                batter,
                pitcher,
                game_date,
                game_pk,
                at_bat_number,
                stand,
                p_throws,
                CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END         AS home,
                CASE WHEN inning_topbot = 'Bot' THEN home_team ELSE away_team END AS bat_team,
                CASE WHEN inning_topbot = 'Bot' THEN away_team ELSE home_team END AS pit_team,
                home_team                                                 AS park,
                MAX(events)                                               AS events,
                MAX(CASE WHEN events IN ('single','double','triple','home_run') THEN 1 ELSE 0 END) AS is_hit,
                MAX(CASE WHEN events IS NOT NULL AND events NOT IN
                    ('walk','hit_by_pitch','sac_bunt','sac_fly','catcher_interf')
                    THEN 1 ELSE 0 END)                                    AS is_ab,
                MAX(CASE WHEN events IN ('strikeout','strikeout_double_play')
                    THEN 1 ELSE 0 END)                                    AS is_k,
                MAX(CASE WHEN events IN ('walk','hit_by_pitch') THEN 1 ELSE 0 END) AS is_bb,
                MAX(launch_speed)                                         AS launch_speed,
                MAX(launch_angle)                                         AS launch_angle,
                MAX(estimated_ba_using_speedangle)                        AS xba,
                MAX(woba_value)                                           AS woba_value,
                MAX(woba_denom)                                           AS woba_denom,
                MAX(babip_value)                                          AS babip_value,
                MAX(iso_value)                                            AS iso_value,
                MAX(n_thruorder_pitcher)                                  AS thru_order,
                MAX(batter_days_since_prev_game)                          AS bat_rest,
                MAX(pitcher_days_since_prev_game)                         AS pit_rest,
                MAX(age_bat)                                              AS age_bat,
                MAX(age_pit)                                              AS age_pit,
                MAX(if_fielding_alignment)                                AS if_align,
                MAX(of_fielding_alignment)                                AS of_align
            FROM   pitches
            WHERE  events IS NOT NULL
            GROUP  BY batter, game_pk, at_bat_number
        """)
        conn.execute("CREATE INDEX if not exists idx_pae_batter_date  ON plate_appearances(batter, game_date)")
        conn.execute("CREATE INDEX if not exists  idx_pae_pitcher_date ON plate_appearances(pitcher, game_date)")
        conn.execute("CREATE INDEX if not exists idx_pae_date         ON plate_appearances(game_date)")
        count = conn.execute("SELECT COUNT(*) FROM plate_appearances").fetchone()[0]
        conn.commit()
        conn.close()
        self.status(f"plate_appearances:        {count:,} rows")

    # ══════════════════════════════════════════════════════════════
    # BATTER AS-OF FEATURES
    # For each (batter, game_date) compute rolling stats using
    # ONLY PAs from game_date < that date. Leak-free.
    # ══════════════════════════════════════════════════════════════

    def build_batter_features(self):
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS batter_features")
        conn.execute("""
            CREATE TABLE batter_features (
                batter          INTEGER,
                as_of_date      TEXT,
                pa_season       INTEGER,
                ab_season       INTEGER,
                hits_season     INTEGER,
                ba_season       REAL,
                k_pct_season    REAL,
                bb_pct_season   REAL,
                xba_season      REAL,
                hard_hit_pct    REAL,
                avg_ls          REAL,
                ba_vs_lhp       REAL,
                ba_vs_rhp       REAL,
                PRIMARY KEY (batter, as_of_date)
            )
        """)
        dates = self.distinct_game_dates(conn)
        self.status(f"Building batter features over {len(dates)} dates...")
        for i, d in enumerate(dates):
            self.build_batter_features_for_date(conn, d)
            if (i + 1) % 10 == 0:
                self.status(f"  ...{i+1}/{len(dates)} dates")
        count = conn.execute("SELECT COUNT(*) FROM batter_features").fetchone()[0]
        conn.execute("CREATE INDEX idx_bf_batter_date ON batter_features(batter, as_of_date)")
        conn.commit()
        conn.close()
        self.status(f"batter_features:    {count:,} rows")

    def build_batter_features_for_date(self, conn, as_of):
        conn.execute("""
            INSERT INTO batter_features
            SELECT
                batter,
                ? AS as_of_date,
                COUNT(*)                                                AS pa_season,
                SUM(is_ab)                                              AS ab_season,
                SUM(is_hit)                                             AS hits_season,
                CASE WHEN SUM(is_ab) > 0
                     THEN SUM(is_hit) * 1.0 / SUM(is_ab) END            AS ba_season,
                SUM(is_k)  * 1.0 / COUNT(*)                             AS k_pct_season,
                SUM(is_bb) * 1.0 / COUNT(*)                             AS bb_pct_season,
                AVG(xba)                                                AS xba_season,
                SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END), 0) AS hard_hit_pct,
                AVG(launch_speed)                                       AS avg_ls,
                CASE WHEN SUM(CASE WHEN p_throws = 'L' AND is_ab = 1 THEN 1 ELSE 0 END) > 0
                     THEN SUM(CASE WHEN p_throws = 'L' THEN is_hit ELSE 0 END) * 1.0 /
                          SUM(CASE WHEN p_throws = 'L' AND is_ab = 1 THEN 1 ELSE 0 END) END AS ba_vs_lhp,
                CASE WHEN SUM(CASE WHEN p_throws = 'R' AND is_ab = 1 THEN 1 ELSE 0 END) > 0
                     THEN SUM(CASE WHEN p_throws = 'R' THEN is_hit ELSE 0 END) * 1.0 /
                          SUM(CASE WHEN p_throws = 'R' AND is_ab = 1 THEN 1 ELSE 0 END) END AS ba_vs_rhp
            FROM   plate_appearances
            WHERE  game_date < ?
            GROUP  BY batter
        """, (as_of, as_of))

    # ══════════════════════════════════════════════════════════════
    # PITCHER AS-OF FEATURES
    # Same idea, pitcher-side.
    # ══════════════════════════════════════════════════════════════

    def build_pitcher_features(self):
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS pitcher_features")
        conn.execute("""
            CREATE TABLE pitcher_features (
                pitcher             INTEGER,
                as_of_date          TEXT,
                pa_season           INTEGER,
                ab_season           INTEGER,
                hits_allowed        INTEGER,
                ba_against          REAL,
                k_pct_season        REAL,
                bb_pct_season       REAL,
                xba_allowed         REAL,
                hard_hit_pct        REAL,
                ba_against_lhb      REAL,
                ba_against_rhb      REAL,
                PRIMARY KEY (pitcher, as_of_date)
            )
        """)
        dates = self.distinct_game_dates(conn)
        self.status(f"Building pitcher features over {len(dates)} dates...")
        for i, d in enumerate(dates):
            self.build_pitcher_features_for_date(conn, d)
            if (i + 1) % 10 == 0:
                self.status(f"  ...{i+1}/{len(dates)} dates")
        count = conn.execute("SELECT COUNT(*) FROM pitcher_features").fetchone()[0]
        conn.execute("CREATE INDEX idx_pf_pitcher_date ON pitcher_features(pitcher, as_of_date)")
        conn.commit()
        conn.close()
        self.status(f"pitcher_features:   {count:,} rows")

    def build_pitcher_features_for_date(self, conn, as_of):
        conn.execute("""
            INSERT INTO pitcher_features
            SELECT
                pitcher,
                ? AS as_of_date,
                COUNT(*)                                                AS pa_season,
                SUM(is_ab)                                              AS ab_season,
                SUM(is_hit)                                             AS hits_allowed,
                CASE WHEN SUM(is_ab) > 0
                     THEN SUM(is_hit) * 1.0 / SUM(is_ab) END            AS ba_against,
                SUM(is_k)  * 1.0 / COUNT(*)                             AS k_pct_season,
                SUM(is_bb) * 1.0 / COUNT(*)                             AS bb_pct_season,
                AVG(xba)                                                AS xba_allowed,
                SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END) * 1.0 /
                    NULLIF(SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END), 0) AS hard_hit_pct,
                CASE WHEN SUM(CASE WHEN stand = 'L' AND is_ab = 1 THEN 1 ELSE 0 END) > 0
                     THEN SUM(CASE WHEN stand = 'L' THEN is_hit ELSE 0 END) * 1.0 /
                          SUM(CASE WHEN stand = 'L' AND is_ab = 1 THEN 1 ELSE 0 END) END AS ba_against_lhb,
                CASE WHEN SUM(CASE WHEN stand = 'R' AND is_ab = 1 THEN 1 ELSE 0 END) > 0
                     THEN SUM(CASE WHEN stand = 'R' THEN is_hit ELSE 0 END) * 1.0 /
                          SUM(CASE WHEN stand = 'R' AND is_ab = 1 THEN 1 ELSE 0 END) END AS ba_against_rhb
            FROM   plate_appearances
            WHERE  game_date < ?
            GROUP  BY pitcher
        """, (as_of, as_of))




    # ══════════════════════════════════════════════════════════════
    # PITCH BUCKET VIEW
    # One-shot: tag every pitch with its bucket via a view (or
    # materialized helper table). Used by the next two builds.
    # ══════════════════════════════════════════════════════════════



    def build_pitch_bucket_view(self):
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS pitch_bucketed")
        case_expr = self.bucket_case_expression()
        conn.execute(f"""
            CREATE TABLE pitch_bucketed AS
            SELECT
                game_date,
                game_pk,
                at_bat_number,
                batter,
                pitcher,
                pitch_type,
                {case_expr} AS bucket,
                CASE WHEN events IS NOT NULL THEN 1 ELSE 0 END                                  AS ends_pa,
                CASE WHEN events IN ('single','double','triple','home_run') THEN 1 ELSE 0 END   AS is_hit,
                CASE WHEN events IS NOT NULL AND events NOT IN
                    ('walk','hit_by_pitch','sac_bunt','sac_fly','catcher_interf')
                    THEN 1 ELSE 0 END                                                            AS is_ab
            FROM   pitches
        """)
        conn.execute("CREATE INDEX idx_pb_pitcher_date ON pitch_bucketed(pitcher, game_date)")
        conn.execute("CREATE INDEX idx_pb_batter_date  ON pitch_bucketed(batter,  game_date)")
        conn.execute("CREATE INDEX idx_pb_date         ON pitch_bucketed(game_date)")
        count = conn.execute("SELECT COUNT(*) FROM pitch_bucketed").fetchone()[0]
        conn.commit()
        conn.close()
        self.status(f"pitch_bucketed:     {count:,} rows")

    def bucket_case_expression(self):
        clauses = [f"WHEN pitch_type = '{code}' THEN '{bucket}'"
                   for code, bucket in self.PITCH_BUCKETS.items()]
        return "CASE " + " ".join(clauses) + " ELSE 'other' END"

    # ══════════════════════════════════════════════════════════════
    # PITCHER PITCH MIX
    # For each (pitcher, as_of_date): % of each bucket thrown season-to-date.
    # Leak-free: only pitches from game_date < as_of_date.
    # ══════════════════════════════════════════════════════════════

    def build_pitcher_pitch_mix(self):
        self.build_pitch_bucket_view()
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS pitcher_pitch_mix")
        conn.execute("""
            CREATE TABLE pitcher_pitch_mix (
                pitcher        INTEGER,
                as_of_date     TEXT,
                pitches_total  INTEGER,
                pct_fastball   REAL,
                pct_breaking   REAL,
                pct_offspeed   REAL,
                pct_other      REAL,
                PRIMARY KEY (pitcher, as_of_date)
            )
        """)
        dates = self.distinct_game_dates(conn)
        self.status(f"Building pitcher pitch mix over {len(dates)} dates...")
        for i, d in enumerate(dates):
            self.insert_pitcher_pitch_mix_for_date(conn, d)
            if (i + 1) % 20 == 0:
                self.status(f"  ...{i+1}/{len(dates)} dates")
        count = conn.execute("SELECT COUNT(*) FROM pitcher_pitch_mix").fetchone()[0]
        conn.execute("CREATE INDEX idx_ppm_pitcher_date ON pitcher_pitch_mix(pitcher, as_of_date)")
        conn.commit()
        conn.close()
        self.status(f"pitcher_pitch_mix:  {count:,} rows")

    def insert_pitcher_pitch_mix_for_date(self, conn, as_of):
        conn.execute("""
            INSERT INTO pitcher_pitch_mix
            SELECT
                pitcher,
                ? AS as_of_date,
                COUNT(*)                                                              AS pitches_total,
                SUM(CASE WHEN bucket = 'fastball' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS pct_fastball,
                SUM(CASE WHEN bucket = 'breaking' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS pct_breaking,
                SUM(CASE WHEN bucket = 'offspeed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS pct_offspeed,
                SUM(CASE WHEN bucket = 'other'    THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS pct_other
            FROM   pitch_bucketed
            WHERE  game_date < ?
            GROUP  BY pitcher
        """, (as_of, as_of))

    # ══════════════════════════════════════════════════════════════
    # BATTER vs PITCH BUCKET
    # For each (batter, as_of_date, bucket): BA against that bucket
    # AND the AB count so the model can weight by reliability.
    # Counts only the PA-ENDING pitch (the putaway pitch).
    # Leak-free: only PAs from game_date < as_of_date.
    # ══════════════════════════════════════════════════════════════

    def build_batter_vs_pitch(self):
        conn = self.open_db()
        conn.execute("DROP TABLE IF EXISTS batter_vs_pitch")
        conn.execute("""
            CREATE TABLE batter_vs_pitch (
                batter      INTEGER,
                as_of_date  TEXT,
                bucket      TEXT,
                abs         INTEGER,
                hits        INTEGER,
                ba          REAL,
                PRIMARY KEY (batter, as_of_date, bucket)
            )
        """)
        dates = self.distinct_game_dates(conn)
        self.status(f"Building batter vs pitch over {len(dates)} dates...")
        for i, d in enumerate(dates):
            self.insert_batter_vs_pitch_for_date(conn, d)
            if (i + 1) % 20 == 0:
                self.status(f"  ...{i+1}/{len(dates)} dates")
        count = conn.execute("SELECT COUNT(*) FROM batter_vs_pitch").fetchone()[0]
        conn.execute("CREATE INDEX idx_bvp_batter_date ON batter_vs_pitch(batter, as_of_date)")
        conn.commit()
        conn.close()
        self.status(f"batter_vs_pitch:    {count:,} rows")

    def insert_batter_vs_pitch_for_date(self, conn, as_of):
        conn.execute("""
            INSERT INTO batter_vs_pitch
            SELECT
                batter,
                ? AS as_of_date,
                bucket,
                SUM(is_ab)                                              AS abs,
                SUM(is_hit)                                             AS hits,
                CASE WHEN SUM(is_ab) > 0
                     THEN SUM(is_hit) * 1.0 / SUM(is_ab) END            AS ba
            FROM   pitch_bucketed
            WHERE  ends_pa = 1
              AND  game_date < ?
            GROUP  BY batter, bucket
        """, (as_of, as_of))