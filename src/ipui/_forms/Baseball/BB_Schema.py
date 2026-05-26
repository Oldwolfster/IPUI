# BB_Schema.py  class: BB_Schema  Update: + materialize_tables, tolerant PK parsing, full SCHEMA through forest

import re
import sqlite3
from pathlib import Path


class BB_Schema:

    DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")  # canonical location


    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — pure dispatch. Each step independently re-runnable.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def bootstrap(cls, db):
        cls.check_tables_table              (db)
        cls.sync_hardcoded_SCHEMA           (db)
        cls.materialize_tables_from_metadata(db)
        # more steps to come


    # ══════════════════════════════════════════════════════════════
    # STEP 1 — ensure _tables exists. The one ROWID exception (metadata table).
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def check_tables_table(cls, db):
        Path(db).parent.mkdir(parents=True, exist_ok=True)               # ensure dir
        conn = sqlite3.connect(db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _tables (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                tbl     TEXT,
                layer   TEXT,
                col     TEXT
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
            layer = tbl.split('_')[0]                                    # derive layer from prefix
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
        layer        = tbl.split('_')[0]                                 # derive layer
        col_decls    = ["GD              INTEGER"]                       # auto-injected, always PK col 1
        pk_cols      = ["GD"]
        if layer == 'feet':                                              # auto-inject TS on feet_*
            col_decls.append("TS              INTEGER")
            pk_cols  .append("TS")
        for (raw_col,) in rows:
            is_pk, decl = cls.parse_col_row(raw_col)
            col_name    = decl.split()[0]                                # first token = column name
            col_decls.append(decl)
            if is_pk:
                pk_cols.append(col_name)
        pk_clause    = f"PRIMARY KEY ({', '.join(pk_cols)})"
        body         = ",\n    ".join(col_decls + [pk_clause])
        sql          = f"CREATE TABLE IF NOT EXISTS {tbl} (\n    {body}\n) WITHOUT ROWID"
        conn.execute(sql)


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

    @classmethod
    def export_table_to_csv(cls, db, tbl, csv_path):
        import pandas as pd
        conn = sqlite3.connect(db)
        df   = pd.read_sql(f"SELECT * FROM {tbl}", conn)
        df.to_csv(csv_path, index=False)
        conn.close()
        return len(df)


    @classmethod
    def import_table_from_csv(cls, db, tbl, csv_path):
        import pandas as pd
        conn = sqlite3.connect(db)
        df   = pd.read_csv(csv_path)
        df.to_sql(tbl, conn, if_exists='replace', index=False)   # or 'append'
        conn.close()
        return len(df)
    # ══════════════════════════════════════════════════════════════
    # SCHEMA — the seed. (tbl, col_declaration) per row.
    # GD and TS are NEVER in SCHEMA — materializer injects them.
    # PK columns flagged by 'PK' prefix (parser is tolerant of case/spacing).
    # Layer derived from tbl prefix at insert. Order in list = column order.
    # ══════════════════════════════════════════════════════════════

    SCHEMA = [

        # ── raw_pitches ── Statcast source of truth. Pandas owns real shape on first import;
        #                   these rows are documentary placeholders until then.
        ('raw_pitches',   'PK game_pk             INTEGER'),
        ('raw_pitches',   'PK at_bat_number       INTEGER'),
        ('raw_pitches',   'PK pitch_number        INTEGER'),
        ('raw_pitches',   '   pitcher             INTEGER'),
        ('raw_pitches',   '   batter              INTEGER'),
        ('raw_pitches',   '   pitch_type          TEXT'   ),
        ('raw_pitches',   '   events              TEXT'   ),
        ('raw_pitches',   '   description         TEXT'   ),
        ('raw_pitches',   '   release_speed       REAL'   ),
        ('raw_pitches',   '   release_spin_rate   REAL'   ),
        ('raw_pitches',   '   plate_x             REAL'   ),
        ('raw_pitches',   '   plate_z             REAL'   ),
        ('raw_pitches',   '   launch_speed        REAL'   ),
        ('raw_pitches',   '   launch_angle        REAL'   ),

        # ── raw_schedule ── Game-level facts.
        ('raw_schedule',  'PK game_pk             INTEGER'),
        ('raw_schedule',  '   game_datetime       TEXT'   ),
        ('raw_schedule',  '   status              TEXT'   ),
        ('raw_schedule',  '   home_team_id        INTEGER'),
        ('raw_schedule',  '   away_team_id        INTEGER'),
        ('raw_schedule',  '   home_starter_id     INTEGER'),
        ('raw_schedule',  '   away_starter_id     INTEGER'),
        ('raw_schedule',  '   venue               TEXT'   ),
        ('raw_schedule',  '   game_type           TEXT'   ),

        # ── etl_pa ── One row per plate appearance. Cleaned event grain.
        ('etl_pa',        'PK batter              INTEGER'),
        ('etl_pa',        'PK game_pk             INTEGER'),
        ('etl_pa',        'PK at_bat_number       INTEGER'),
        ('etl_pa',        '   pitcher             INTEGER'),
        ('etl_pa',        '   stand               TEXT'   ),
        ('etl_pa',        '   p_throws            TEXT'   ),
        ('etl_pa',        '   home                INTEGER'),
        ('etl_pa',        '   bat_team            TEXT'   ),
        ('etl_pa',        '   pit_team            TEXT'   ),
        ('etl_pa',        '   park                TEXT'   ),
        ('etl_pa',        '   events              TEXT'   ),
        ('etl_pa',        '   is_hit              INTEGER'),
        ('etl_pa',        '   is_ab               INTEGER'),
        ('etl_pa',        '   is_k                INTEGER'),
        ('etl_pa',        '   is_bb               INTEGER'),
        ('etl_pa',        '   is_hr               INTEGER'),
        ('etl_pa',        '   total_bases         INTEGER'),
        ('etl_pa',        '   launch_speed        REAL'   ),
        ('etl_pa',        '   launch_angle        REAL'   ),
        ('etl_pa',        '   xba                 REAL'   ),
        ('etl_pa',        '   woba_value          REAL'   ),
        ('etl_pa',        '   woba_denom          INTEGER'),

        # ── feet_batter ── Per-batter, per-timeslice aggregates. SUMABLE METRICS ONLY.
        #                   Rates derived downstream from these sums.
        ('feet_batter',   'PK batter              INTEGER'),
        ('feet_batter',   '   pa                  INTEGER'),
        ('feet_batter',   '   ab                  INTEGER'),
        ('feet_batter',   '   hits                INTEGER'),
        ('feet_batter',   '   hr                  INTEGER'),
        ('feet_batter',   '   bb                  INTEGER'),
        ('feet_batter',   '   k                   INTEGER'),
        ('feet_batter',   '   total_bases         INTEGER'),
        ('feet_batter',   '   sum_launch_speed    REAL'   ),
        ('feet_batter',   '   sum_xba             REAL'   ),
        ('feet_batter',   '   sum_woba_value      REAL'   ),
        ('feet_batter',   '   sum_woba_denom      INTEGER'),
        ('feet_batter',   '   hard_hit_count      INTEGER'),
        ('feet_batter',   '   barrel_count        INTEGER'),

        # ── feet_pitcher ── Mirror of feet_batter, pitcher perspective. SUMABLE ONLY.
        ('feet_pitcher',  'PK pitcher             INTEGER'),
        ('feet_pitcher',  '   bf                  INTEGER'),
        ('feet_pitcher',  '   ab_against          INTEGER'),
        ('feet_pitcher',  '   hits_allowed        INTEGER'),
        ('feet_pitcher',  '   hr_allowed          INTEGER'),
        ('feet_pitcher',  '   bb_allowed          INTEGER'),
        ('feet_pitcher',  '   k_pitcher           INTEGER'),
        ('feet_pitcher',  '   total_bases_allowed INTEGER'),
        ('feet_pitcher',  '   sum_launch_speed    REAL'   ),
        ('feet_pitcher',  '   sum_xba_allowed     REAL'   ),
        ('feet_pitcher',  '   sum_woba_value      REAL'   ),
        ('feet_pitcher',  '   sum_woba_denom      INTEGER'),
        ('feet_pitcher',  '   hard_hit_allowed    INTEGER'),
        ('feet_pitcher',  '   barrel_allowed      INTEGER'),

        # ── forest ── Wide flat training matrix. Skeleton; many versions will live here.
        #              Note: forest is its own "layer" via prefix-split semantics.
        ('forest',        'PK batter              INTEGER'),
        ('forest',        'PK game_pk             INTEGER'),
        ('forest',        '   bat_pa_season       INTEGER'),
        ('forest',        '   bat_ba_season       REAL'   ),
        ('forest',        '   bat_xwoba_season    REAL'   ),
        ('forest',        '   pit_xwoba_30        REAL'   ),
        ('forest',        '   target_fantasy_pts  REAL'   ),

    ]