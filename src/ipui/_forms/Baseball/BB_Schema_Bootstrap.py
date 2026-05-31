# BB_Schema_Bootstrap.py  class: BB_Schema_Bootstrap  FULL REPLACEMENT
# Reverted to pre-position state. Only addition vs your original: rebuild_table().

import re
import sqlite3
from pathlib import Path

from ipui._forms.Baseball.BB import BB
from ipui.utils.MgrDT import MgrDT


class BB_Schema_Bootstrap:

    DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")


    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — pure dispatch. Each step independently re-runnable.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def bootstrap(cls, db):
        cls.check_tables_table              (db)
        cls.sync_hardcoded_SCHEMA           (db)
        cls.materialize_tables_from_metadata(db)


    # ══════════════════════════════════════════════════════════════
    # STEP 1 — ensure _tables exists.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def check_tables_table(cls, db):
        Path(db).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _tables (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                tbl     TEXT,
                layer   TEXT,
                col     TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _run_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                DS          TEXT,
                target      TEXT,
                level       TEXT,
                rows        INTEGER,
                elapsed_ms  INTEGER,
                message     TEXT
            )
        """)
        conn.commit()
        conn.close()


    # ══════════════════════════════════════════════════════════════
    # STEP 2 — insert SCHEMA rows that aren't already in _tables.
    # Idempotent at row level: existing (tbl, col) pairs are untouched.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def sync_hardcoded_SCHEMA(cls, db):
        conn     = sqlite3.connect(db)
        existing = cls.fetch_existing_pairs(conn)
        missing  = [(tbl, col) for (tbl, col) in cls.SCHEMA if (tbl, col) not in existing]
        for tbl, col in missing:
            layer = tbl.split('_')[0]
            conn.execute("INSERT INTO _tables (tbl, layer, col) VALUES (?, ?, ?)", (tbl, layer, col))
        conn.commit()
        conn.close()


    # ══════════════════════════════════════════════════════════════
    # STEP 3 — materialize physical tables from _tables metadata.
    # GD auto-injected as PK col 1. TS auto-injected as PK col 2 on feet_*.
    # PK columns flagged by 'PK' prefix (case/whitespace/underscore tolerant).
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def materialize_tables_from_metadata(cls, db):
        conn = sqlite3.connect(db)
        for tbl in cls.fetch_distinct_tables(conn):
            cls.materialize_one_table(conn, tbl)
        conn.commit()
        conn.close()


    @classmethod
    def materialize_one_table(cls, conn, tbl):
        rows         = conn.execute("SELECT col FROM _tables WHERE tbl=? ORDER BY id", (tbl,)).fetchall()
        layer        = tbl.split('_')[0]
        col_decls    = ["GD              INTEGER"]
        pk_cols      = ["GD"]
        if layer == 'feet':
            col_decls.append("TS              INTEGER")
            pk_cols  .append("TS")
        for (raw_col,) in rows:
            is_pk, decl = cls.parse_col_row(raw_col)
            col_name    = decl.split()[0]
            col_decls.append(decl)
            if is_pk:
                pk_cols.append(col_name)
        pk_clause    = f"PRIMARY KEY ({', '.join(pk_cols)})"
        body         = ",\n    ".join(col_decls + [pk_clause])
        sql          = f"CREATE TABLE IF NOT EXISTS {tbl} (\n    {body}\n) WITHOUT ROWID"
        conn.execute(sql)


    # ══════════════════════════════════════════════════════════════
    # REBUILD ONE TABLE — drop physical, recreate from _tables metadata.
    # Delegates to materialize_one_table. Used by Workbench Add/Delete Column.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def rebuild_table(cls, tbl):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute(f"DROP TABLE IF EXISTS {tbl}")
        cls.materialize_one_table(conn, tbl)
        conn.commit()
        conn.close()
        BB.log(tbl, "INFO", "rebuilt from _tables")


    # ══════════════════════════════════════════════════════════════
    # PARSER — tolerant of pk/Pk/PK/pK, leading whitespace, underscore-or-space after marker.
    # Returns (is_pk: bool, cleaned_decl: str).
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def parse_col_row(cls, raw):
        stripped = raw.strip()
        match    = re.match(r'^(pk)([\s_]+)(.+)$', stripped, flags=re.IGNORECASE)
        if match:
            return True,  match.group(3).strip()
        return     False, stripped


    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def fetch_existing_pairs(cls, conn):
        rows = conn.execute("SELECT tbl, col FROM _tables").fetchall()
        return set((tbl, col) for (tbl, col) in rows)

    @classmethod
    def fetch_distinct_tables(cls, conn):
        rows = conn.execute("SELECT tbl, MIN(id) AS first_id FROM _tables GROUP BY tbl ORDER BY first_id").fetchall()
        return [tbl for (tbl, _) in rows]


    # ══════════════════════════════════════════════════════════════
    # SCHEMA — the seed. (tbl, col_declaration) per row.
    # GD and TS are NEVER in SCHEMA — materializer injects them.
    # ══════════════════════════════════════════════════════════════

    SCHEMA = [

        # ═══ raw_pitches ═══ Full Statcast pitch shape. PK = (GD, game_pk, at_bat_number, pitch_number).
        # GD is auto-injected as PK col 1 by the materializer; the rest of the PK is flagged here.
        ('raw_pitches',  '   pitch_type                                  TEXT'   ),
        ('raw_pitches',  '   release_speed                               REAL'   ),
        ('raw_pitches',  '   release_pos_x                               REAL'   ),
        ('raw_pitches',  '   release_pos_z                               REAL'   ),
        ('raw_pitches',  '   player_name                                 TEXT'   ),
        ('raw_pitches',  '   batter                                      INTEGER'),
        ('raw_pitches',  '   pitcher                                     INTEGER'),
        ('raw_pitches',  '   events                                      TEXT'   ),
        ('raw_pitches',  '   description                                 TEXT'   ),
        ('raw_pitches',  '   spin_dir                                    INTEGER'),
        ('raw_pitches',  '   spin_rate_deprecated                        INTEGER'),
        ('raw_pitches',  '   break_angle_deprecated                      INTEGER'),
        ('raw_pitches',  '   break_length_deprecated                     INTEGER'),
        ('raw_pitches',  '   zone                                        INTEGER'),
        ('raw_pitches',  '   des                                         TEXT'   ),
        ('raw_pitches',  '   game_type                                   TEXT'   ),
        ('raw_pitches',  '   stand                                       TEXT'   ),
        ('raw_pitches',  '   p_throws                                    TEXT'   ),
        ('raw_pitches',  '   home_team                                   TEXT'   ),
        ('raw_pitches',  '   away_team                                   TEXT'   ),
        ('raw_pitches',  '   type                                        TEXT'   ),
        ('raw_pitches',  '   hit_location                                INTEGER'),
        ('raw_pitches',  '   bb_type                                     TEXT'   ),
        ('raw_pitches',  '   balls                                       INTEGER'),
        ('raw_pitches',  '   strikes                                     INTEGER'),
        ('raw_pitches',  '   game_year                                   INTEGER'),
        ('raw_pitches',  '   pfx_x                                       REAL'   ),
        ('raw_pitches',  '   pfx_z                                       REAL'   ),
        ('raw_pitches',  '   plate_x                                     REAL'   ),
        ('raw_pitches',  '   plate_z                                     REAL'   ),
        ('raw_pitches',  '   on_3b                                       INTEGER'),
        ('raw_pitches',  '   on_2b                                       INTEGER'),
        ('raw_pitches',  '   on_1b                                       INTEGER'),
        ('raw_pitches',  '   outs_when_up                                INTEGER'),
        ('raw_pitches',  '   inning                                      INTEGER'),
        ('raw_pitches',  '   inning_topbot                               TEXT'   ),
        ('raw_pitches',  '   hc_x                                        REAL'   ),
        ('raw_pitches',  '   hc_y                                        REAL'   ),
        ('raw_pitches',  '   tfs_deprecated                              INTEGER'),
        ('raw_pitches',  '   tfs_zulu_deprecated                         INTEGER'),
        ('raw_pitches',  '   umpire                                      INTEGER'),
        ('raw_pitches',  '   sv_id                                       INTEGER'),
        ('raw_pitches',  '   vx0                                         REAL'   ),
        ('raw_pitches',  '   vy0                                         REAL'   ),
        ('raw_pitches',  '   vz0                                         REAL'   ),
        ('raw_pitches',  '   ax                                          REAL'   ),
        ('raw_pitches',  '   ay                                          REAL'   ),
        ('raw_pitches',  '   az                                          REAL'   ),
        ('raw_pitches',  '   sz_top                                      REAL'   ),
        ('raw_pitches',  '   sz_bot                                      REAL'   ),
        ('raw_pitches',  '   hit_distance_sc                             INTEGER'),
        ('raw_pitches',  '   launch_speed                                REAL'   ),
        ('raw_pitches',  '   launch_angle                                REAL'   ),  # was INT in dump (NULL-heavy sample)
        ('raw_pitches',  '   effective_speed                             REAL'   ),
        ('raw_pitches',  '   release_spin_rate                           INTEGER'),
        ('raw_pitches',  '   release_extension                           REAL'   ),
        ('raw_pitches',  'PK game_pk                                     INTEGER'),
        ('raw_pitches',  '   fielder_2                                   INTEGER'),
        ('raw_pitches',  '   fielder_3                                   INTEGER'),
        ('raw_pitches',  '   fielder_4                                   INTEGER'),
        ('raw_pitches',  '   fielder_5                                   INTEGER'),
        ('raw_pitches',  '   fielder_6                                   INTEGER'),
        ('raw_pitches',  '   fielder_7                                   INTEGER'),
        ('raw_pitches',  '   fielder_8                                   INTEGER'),
        ('raw_pitches',  '   fielder_9                                   INTEGER'),
        ('raw_pitches',  '   release_pos_y                               REAL'   ),
        ('raw_pitches',  '   estimated_ba_using_speedangle               REAL'   ),  # xBA — was INT in dump
        ('raw_pitches',  '   estimated_woba_using_speedangle             REAL'   ),  # xwOBA — was INT in dump
        ('raw_pitches',  '   woba_value                                  REAL'   ),
        ('raw_pitches',  '   woba_denom                                  INTEGER'),
        ('raw_pitches',  '   babip_value                                 REAL'   ),  # was INT in dump
        ('raw_pitches',  '   iso_value                                   REAL'   ),  # was INT in dump
        ('raw_pitches',  '   launch_speed_angle                          INTEGER'),  # 1-6 bucket, int correct
        ('raw_pitches',  'PK at_bat_number                               INTEGER'),
        ('raw_pitches',  'PK pitch_number                                INTEGER'),
        ('raw_pitches',  '   pitch_name                                  TEXT'   ),
        ('raw_pitches',  '   home_score                                  INTEGER'),
        ('raw_pitches',  '   away_score                                  INTEGER'),
        ('raw_pitches',  '   bat_score                                   INTEGER'),
        ('raw_pitches',  '   fld_score                                   INTEGER'),
        ('raw_pitches',  '   post_away_score                             INTEGER'),
        ('raw_pitches',  '   post_home_score                             INTEGER'),
        ('raw_pitches',  '   post_bat_score                              INTEGER'),
        ('raw_pitches',  '   post_fld_score                              INTEGER'),
        ('raw_pitches',  '   if_fielding_alignment                       TEXT'   ),
        ('raw_pitches',  '   of_fielding_alignment                       TEXT'   ),
        ('raw_pitches',  '   spin_axis                                   INTEGER'),
        ('raw_pitches',  '   delta_home_win_exp                          REAL'   ),
        ('raw_pitches',  '   delta_run_exp                               REAL'   ),
        ('raw_pitches',  '   bat_speed                                   REAL'   ),  # was INT in dump
        ('raw_pitches',  '   swing_length                                REAL'   ),  # was INT in dump
        ('raw_pitches',  '   estimated_slg_using_speedangle              REAL'   ),  # xSLG — was INT in dump
        ('raw_pitches',  '   delta_pitcher_run_exp                       REAL'   ),
        ('raw_pitches',  '   hyper_speed                                 REAL'   ),
        ('raw_pitches',  '   home_score_diff                             INTEGER'),
        ('raw_pitches',  '   bat_score_diff                              INTEGER'),
        ('raw_pitches',  '   home_win_exp                                REAL'   ),
        ('raw_pitches',  '   bat_win_exp                                 REAL'   ),
        ('raw_pitches',  '   age_pit_legacy                              INTEGER'),
        ('raw_pitches',  '   age_bat_legacy                              INTEGER'),
        ('raw_pitches',  '   age_pit                                     INTEGER'),
        ('raw_pitches',  '   age_bat                                     INTEGER'),
        ('raw_pitches',  '   n_thruorder_pitcher                         INTEGER'),
        ('raw_pitches',  '   n_priorpa_thisgame_player_at_bat            INTEGER'),
        ('raw_pitches',  '   pitcher_days_since_prev_game                INTEGER'),
        ('raw_pitches',  '   batter_days_since_prev_game                 INTEGER'),
        ('raw_pitches',  '   pitcher_days_until_next_game                INTEGER'),
        ('raw_pitches',  '   batter_days_until_next_game                 INTEGER'),
        ('raw_pitches',  '   api_break_z_with_gravity                    REAL'   ),
        ('raw_pitches',  '   api_break_x_arm                             REAL'   ),
        ('raw_pitches',  '   api_break_x_batter_in                       REAL'   ),
        ('raw_pitches',  '   arm_angle                                   REAL'   ),  # was INT in dump
        ('raw_pitches',  '   attack_angle                                REAL'   ),  # was INT in dump
        ('raw_pitches',  '   attack_direction                            REAL'   ),  # was INT in dump
        ('raw_pitches',  '   swing_path_tilt                             REAL'   ),  # was INT in dump
        ('raw_pitches',  '   intercept_ball_minus_batter_pos_x_inches    REAL'   ),  # was INT in dump
        ('raw_pitches',  '   intercept_ball_minus_batter_pos_y_inches    REAL'   ),  # was INT in dump

        # ═══ raw_schedule ═══ Game-level facts.
        ('raw_schedule',  'PK game_pk                                    INTEGER'),
        ('raw_schedule',  '   game_datetime                              TEXT'   ),
        ('raw_schedule',  '   status                                     TEXT'   ),
        ('raw_schedule',  '   home_team_id                               INTEGER'),
        ('raw_schedule',  '   away_team_id                               INTEGER'),
        ('raw_schedule',  '   home_starter_id                            INTEGER'),
        ('raw_schedule',  '   away_starter_id                            INTEGER'),
        ('raw_schedule',  '   venue                                      TEXT'   ),
        ('raw_schedule',  '   game_type                                  TEXT'   ),

        # ═══ etl_pa ═══ One row per plate appearance. Cleaned event grain.
        ('etl_pa',        'PK batter                                     INTEGER'),
        ('etl_pa',        'PK game_pk                                    INTEGER'),
        ('etl_pa',        'PK at_bat_number                              INTEGER'),
        ('etl_pa',        '   pitcher                                    INTEGER'),
        ('etl_pa',        '   stand                                      TEXT'   ),
        ('etl_pa',        '   p_throws                                   TEXT'   ),
        ('etl_pa',        '   home                                       INTEGER'),
        ('etl_pa',        '   bat_team                                   TEXT'   ),
        ('etl_pa',        '   pit_team                                   TEXT'   ),
        ('etl_pa',        '   park                                       TEXT'   ),
        ('etl_pa',        '   events                                     TEXT'   ),
        ('etl_pa',        '   is_hit                                     INTEGER'),
        ('etl_pa',        '   is_ab                                      INTEGER'),
        ('etl_pa',        '   is_k                                       INTEGER'),
        ('etl_pa',        '   is_bb                                      INTEGER'),
        ('etl_pa',        '   is_hr                                      INTEGER'),
        ('etl_pa',        '   total_bases                                INTEGER'),
        ('etl_pa',        '   launch_speed                               REAL'   ),
        ('etl_pa',        '   launch_angle                               REAL'   ),
        ('etl_pa',        '   xba                                        REAL'   ),
        ('etl_pa',        '   woba_value                                 REAL'   ),
        ('etl_pa',        '   woba_denom                                 INTEGER'),

        # ═══ feet_batter ═══ Per-batter, per-timeslice aggregates. SUMABLE METRICS ONLY.
        ('feet_batter',   'PK batter                                     INTEGER'),
        ('feet_batter',   '   pa                                         INTEGER'),
        ('feet_batter',   '   ab                                         INTEGER'),
        ('feet_batter',   '   hits                                       INTEGER'),
        ('feet_batter',   '   hr                                         INTEGER'),
        ('feet_batter',   '   bb                                         INTEGER'),
        ('feet_batter',   '   k                                          INTEGER'),
        ('feet_batter',   '   total_bases                                INTEGER'),
        ('feet_batter',   '   sum_launch_speed                           REAL'   ),
        ('feet_batter',   '   sum_xba                                    REAL'   ),
        ('feet_batter',   '   sum_woba_value                             REAL'   ),
        ('feet_batter',   '   sum_woba_denom                             INTEGER'),
        ('feet_batter',   '   hard_hit_count                             INTEGER'),
        ('feet_batter',   '   barrel_count                               INTEGER'),

        # ═══ feet_pitcher ═══ Mirror of feet_batter, pitcher perspective. SUMABLE ONLY.
        ('feet_pitcher',  'PK pitcher                                    INTEGER'),
        ('feet_pitcher',  '   bf                                         INTEGER'),
        ('feet_pitcher',  '   ab_against                                 INTEGER'),
        ('feet_pitcher',  '   hits_allowed                               INTEGER'),
        ('feet_pitcher',  '   hr_allowed                                 INTEGER'),
        ('feet_pitcher',  '   bb_allowed                                 INTEGER'),
        ('feet_pitcher',  '   k_pitcher                                  INTEGER'),
        ('feet_pitcher',  '   total_bases_allowed                        INTEGER'),
        ('feet_pitcher',  '   sum_launch_speed                           REAL'   ),
        ('feet_pitcher',  '   sum_xba_allowed                            REAL'   ),
        ('feet_pitcher',  '   sum_woba_value                             REAL'   ),
        ('feet_pitcher',  '   sum_woba_denom                             INTEGER'),
        ('feet_pitcher',  '   hard_hit_allowed                           INTEGER'),
        ('feet_pitcher',  '   barrel_allowed                             INTEGER'),

        # ═══ forest ═══ Wide flat training matrix. Skeleton; many versions will live here.
        #                Forest is its own "layer" via prefix-split semantics ('forest'.split('_')[0] == 'forest').
        ('forest',        'PK batter                                     INTEGER'),
        ('forest',        'PK game_pk                                    INTEGER'),
        ('forest',        '   bat_pa_season                              INTEGER'),
        ('forest',        '   bat_ba_season                              REAL'   ),
        ('forest',        '   bat_xwoba_season                           REAL'   ),
        ('forest',        '   pit_xwoba_30                               REAL'   ),
        ('forest',        '   target_fantasy_pts                         REAL'   ),

    ]