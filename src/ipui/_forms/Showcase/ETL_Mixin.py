# ETL_Mixin.py  class: ETL_Mixin  NEW: Schema + indexes mixin for ETL tab (paired naming with ETL.py)

import sqlite3


class ETL_Mixin:

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINTS — auto-discover schema_* and index_* methods
    # ══════════════════════════════════════════════════════════════

    def build_schema(self):
        conn = self.open_db()
        for name, method in self.scan_methods("schema_"):
            method(conn)
        conn.commit()
        conn.close()

    def build_indexes(self):
        conn = self.open_db()
        count = 0
        for name, method in self.scan_methods("index_"):
            method(conn)
            count += 1
        conn.commit()
        conn.close()
        self.status(f"Built indexes for {count} tables. ✓")

    def scan_methods(self, prefix):
        results = []
        for name in dir(self):
            if not name.startswith(prefix):  continue
            method = getattr(self, name)
            if not callable(method):         continue
            results.append((name[len(prefix):], method))
        return results

    # ══════════════════════════════════════════════════════════════
    # SCHEMAS — one method per table, all idempotent
    # PKs lead with gd (snapshots) or game_pk (events) for append-only inserts
    # `pitches` excluded — pandas owns its schema on first to_sql
    # ══════════════════════════════════════════════════════════════

# ETL_Mixin.py  method: schema_plate_appearances  Update: gd, subject — subject is (batter, at_bat_number)

    def schema_plate_appearances(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plate_appearances (
                gd              TEXT,
                batter          INTEGER,
                at_bat_number   INTEGER,
                game_pk         INTEGER,
                pitcher         INTEGER,
                stand           TEXT,
                p_throws        TEXT,
                home            INTEGER,
                bat_team        TEXT,
                pit_team        TEXT,
                park            TEXT,
                events          TEXT,
                is_hit          INTEGER,
                is_ab           INTEGER,
                is_k            INTEGER,
                is_bb           INTEGER,
                launch_speed    REAL,
                launch_angle    INTEGER,
                xba             REAL,
                woba_value      REAL,
                woba_denom      INTEGER,
                babip_value     INTEGER,
                iso_value       INTEGER,
                thru_order      INTEGER,
                bat_rest        INTEGER,
                pit_rest        INTEGER,
                age_bat         INTEGER,
                age_pit         INTEGER,
                if_align        TEXT,
                of_align        TEXT,
                PRIMARY KEY (gd, batter,game_pk, at_bat_number)
            ) WITHOUT ROWID
        """)

    def schema_schedule(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                gd              TEXT,
                game_pk         INTEGER,
                game_datetime   TEXT,
                status          TEXT,
                home_team       TEXT,
                away_team       TEXT,
                home_team_id    INTEGER,
                away_team_id    INTEGER,
                home_starter_id INTEGER,
                away_starter_id INTEGER,
                venue           TEXT,
                game_type       TEXT,
                PRIMARY KEY (gd, game_pk)
            ) WITHOUT ROWID
        """)



    def schema_batter_features(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batter_features (
                gd              TEXT,
                batter          INTEGER,
                pa_season       INTEGER,
                ab_season       INTEGER,
                hits_season     INTEGER,
                tb_season       INTEGER,
                ba_season       REAL,
                slg_season      REAL,
                iso_season      REAL,
                obp_season      REAL,
                ops_season      REAL,
                k_pct_season    REAL,
                bb_pct_season   REAL,
                xba_season      REAL,
                hard_hit_pct    REAL,
                avg_ls          REAL,
                ba_vs_lhp       REAL,
                ba_vs_rhp       REAL,
                PRIMARY KEY (gd, batter)
            ) WITHOUT ROWID
        """)

    def schema_pitcher_features(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pitcher_features (
                gd                  TEXT,
                pitcher             INTEGER,
                pa_season           INTEGER,
                ab_season           INTEGER,
                hits_allowed        INTEGER,
                tb_allowed          INTEGER,
                ba_against          REAL,
                slg_against         REAL,
                iso_against         REAL,
                obp_against         REAL,
                ops_against         REAL,
                k_pct_season        REAL,
                bb_pct_season       REAL,
                xba_allowed         REAL,
                hard_hit_pct        REAL,
                ba_against_lhb      REAL,
                ba_against_rhb      REAL,
                PRIMARY KEY (gd, pitcher)
            ) WITHOUT ROWID
        """)

    def schema_pitch_bucketed(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pitch_bucketed (
                gd              TEXT,
                game_pk         INTEGER,
                at_bat_number   INTEGER,
                batter          INTEGER,
                pitcher         INTEGER,
                pitch_type      TEXT,
                bucket          TEXT,
                ends_pa         INTEGER,
                is_hit          INTEGER,
                is_ab           INTEGER
            )
        """)

    def schema_pitcher_pitch_mix(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pitcher_pitch_mix (
                gd             TEXT,
                pitcher        INTEGER,
                pitches_total  INTEGER,
                pct_fastball   REAL,
                pct_breaking   REAL,
                pct_offspeed   REAL,
                pct_other      REAL,
                PRIMARY KEY (gd, pitcher)
            ) WITHOUT ROWID
        """)

    def schema_batter_vs_pitch(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batter_vs_pitch (
                gd          TEXT,
                batter      INTEGER,
                bucket      TEXT,
                abs         INTEGER,
                hits        INTEGER,
                ba          REAL,
                PRIMARY KEY (gd, batter, bucket)
            ) WITHOUT ROWID
        """)

    def schema_league_summary(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS league_summary (
                gd          TEXT PRIMARY KEY,
                pa_count    INTEGER,
                ab_count    INTEGER,
                hit_count   INTEGER,
                tb_count    INTEGER,
                league_ba   REAL,
                league_slg  REAL,
                league_iso  REAL,
                league_obp  REAL,
                league_ops  REAL,
                league_k    REAL
            ) WITHOUT ROWID
        """)



    def schema_batter_games(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batter_games (
                gd          TEXT,
                batter      INTEGER,
                game_pk     INTEGER,
                hits        INTEGER,
                at_bats     INTEGER,
                home        INTEGER,
                stand       TEXT,
                p_throws    TEXT,
                PRIMARY KEY (gd, batter, game_pk)
            ) WITHOUT ROWID
        """)
    def schema_batters(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batters (
                id    INTEGER PRIMARY KEY,
                name  TEXT
            )
        """)


    def schema_staging_batter_features_season(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS staging_batter_features_season (
                gd              TEXT,
                batter          INTEGER,
                pa_season       INTEGER,
                ab_season       INTEGER,
                hits_season     INTEGER,
                tb_season       INTEGER,
                ba_season       REAL,
                slg_season      REAL,
                iso_season      REAL,
                obp_season      REAL,
                ops_season      REAL,
                k_pct_season    REAL,
                bb_pct_season   REAL,
                xba_season      REAL,
                hard_hit_pct    REAL,
                avg_ls          REAL,
                ba_vs_lhp       REAL,
                ba_vs_rhp       REAL,
                PRIMARY KEY (gd, batter)
            ) WITHOUT ROWID
        """)









    # ══════════════════════════════════════════════════════════════
    # INDEXES — secondary indexes only where the PK doesn't cover access
    # PK clustering handles the dominant patterns; these add support
    # for less-common but still-useful query shapes
    # ══════════════════════════════════════════════════════════════

    def index_pitches(self, conn):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pitches_gd       ON pitches(gd)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pitches_batter   ON pitches(batter)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pitches_pitcher  ON pitches(pitcher)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pitches_events   ON pitches(events)")

    def index_plate_appearances(self, conn):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pa_gd       ON plate_appearances(gd)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pa_batter   ON plate_appearances(batter)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pa_pitcher  ON plate_appearances(pitcher)")

    def index_pitch_bucketed(self, conn):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pb_gd       ON pitch_bucketed(gd)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pb_pitcher  ON pitch_bucketed(pitcher)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pb_batter   ON pitch_bucketed(batter)")

    def index_batter_games(self, conn):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bg_gd       ON batter_games(gd)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bg_batter   ON batter_games(batter)")

    def index_schedule(self, conn):
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sch_gd          ON schedule(gd)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sch_home_start  ON schedule(home_starter_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sch_away_start  ON schedule(away_starter_id)")




# ════════════════════════════════════════════════════════════════════════════════
# ETL_Mixin.py  method: schema_batter_games  Update: +hr, +k, +sf columns
# Source data already in plate_appearances.events; just exposing at game level.
# ════════════════════════════════════════════════════════════════════════════════

    def schema_batter_games(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batter_games (
                gd          TEXT,
                batter      INTEGER,
                game_pk     INTEGER,
                hits        INTEGER,
                at_bats     INTEGER,
                hr          INTEGER,
                k           INTEGER,
                sf          INTEGER,
                home        INTEGER,
                stand       TEXT,
                p_throws    TEXT,
                PRIMARY KEY (gd, batter, game_pk)
            ) WITHOUT ROWID
        """)


# ════════════════════════════════════════════════════════════════════════════════
# ETL_Mixin.py  method: schema_staging_batter_features_recent_form  NEW
# Window-function-derived rolling features. Same PK as batter_features so the
# final assembly join is trivial.
# ════════════════════════════════════════════════════════════════════════════════

    def schema_staging_batter_features_recent_form(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS staging_batter_features_recent_form (
                gd                      TEXT,
                batter                  INTEGER,
                streak_with_hit         INTEGER,
                streak_without_hit      INTEGER,
                hits_last_5             INTEGER,
                hits_last_10            INTEGER,
                games_since_multi_hit   INTEGER,
                babip_last_10           REAL,
                PRIMARY KEY (gd, batter)
            ) WITHOUT ROWID
        """)


# ════════════════════════════════════════════════════════════════════════════════
# ETL_Mixin.py  method: schema_batter_features  Update: +6 recent-form columns
# Mirrors the new staging_batter_features_recent_form output. Existing
# season-feature columns unchanged.
# ════════════════════════════════════════════════════════════════════════════════

    def schema_batter_features(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batter_features (
                gd                      TEXT,
                batter                  INTEGER,
                pa_season               INTEGER,
                ab_season               INTEGER,
                hits_season             INTEGER,
                tb_season               INTEGER,
                ba_season               REAL,
                slg_season              REAL,
                iso_season              REAL,
                obp_season              REAL,
                ops_season              REAL,
                k_pct_season            REAL,
                bb_pct_season           REAL,
                xba_season              REAL,
                hard_hit_pct            REAL,
                avg_ls                  REAL,
                ba_vs_lhp               REAL,
                ba_vs_rhp               REAL,
                streak_with_hit         INTEGER,
                streak_without_hit      INTEGER,
                hits_last_5             INTEGER,
                hits_last_10            INTEGER,
                games_since_multi_hit   INTEGER,
                babip_last_10           REAL,
                PRIMARY KEY (gd, batter)
            ) WITHOUT ROWID
        """)


