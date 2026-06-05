# BB.py  class: BB  NEW: configured-once service for baseball DB (path, query, layers cache)
import datetime
import sqlite3
from ipui.utils.MgrDT import MgrDT
from datetime import date, timedelta, datetime


class BB:

    db_path = None                                                       # set by configure() from Pipe
    LAYERS  = {}                                                         # cached: { layer_name: [tbl, ...] } in insertion order


    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — Pipe calls this once at startup with its DB_PATH.
    # After this, every other call on BB just works.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def configure(cls, db_path):
        cls.db_path = db_path
        cls.refresh()

    @classmethod
    def drop_table(cls, tbl):
        cls.execute(f"DROP TABLE IF EXISTS {tbl}")
        BB.log(tbl, "INFO", "dropped")


    @classmethod
    def layer_tables(cls, layer):
        return cls.LAYERS.get(layer, [])


    @classmethod
    def layer_of(cls, tbl):
        for layer, tables in cls.LAYERS.items():
            if tbl in tables:
                return layer
        return None

    # ══════════════════════════════════════════════════════════════
    # CORE QUERY — params optional. ALWAYS use params for any value that
    # came from user input or string interpolation. Default empty tuple
    # makes parameterless calls clean.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def query(cls, sql, params=()):
        conn = sqlite3.connect(cls.db_path)
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return rows



    # ══════════════════════════════════════════════════════════════
    # BB.py  method: execute  NEW: for INSERT/UPDATE/DELETE — returns rowcount.
    # query() stays for SELECT (returns rows). Two clean lanes.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def execute(cls, sql, params=()):
        conn = sqlite3.connect(cls.db_path)
        cur  = conn.execute(sql, params)
        rc   = cur.rowcount
        conn.commit()
        conn.close()
        return rc

    # ══════════════════════════════════════════════════════════════
    # REFRESH — rebuild the LAYERS cache from _tables.
    # Call after Schema_Bootstrap or after any direct edit to _tables.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def refresh(cls):
        rows  = cls.query("""
            SELECT layer, tbl, MIN(id) AS first_id
            FROM   _tables
            GROUP BY layer, tbl
            ORDER BY first_id
        """)
        cls.LAYERS = {}
        for layer, tbl, _ in rows:
            cls.LAYERS.setdefault(layer, []).append(tbl)


    # ══════════════════════════════════════════════════════════════
    # CHEAP STATS — used heavily by the Pipe layer view.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def row_count(cls, tbl):
        return cls.query(f"SELECT COUNT(*) FROM {tbl}")[0][0]

    @classmethod
    def col_count(cls, tbl):
        return len(cls.query(f"PRAGMA table_info({tbl})"))

    @classmethod
    def date_range(cls, tbl):
        rows = cls.query(f"SELECT MIN(GD), MAX(GD) FROM {tbl}")
        return rows[0]                                                   # (min_gd, max_gd) — either may be None when empty

    def date_relative_to_today(self,days_back):
        return (date.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")


    # ══════════════════════════════════════════════════════════════
    # BB.py  method: log  NEW: append a row to _run_log with timestamp.
    # Add this method to BB class. Also add `import datetime` at top of BB.py.
    # Call from anywhere: BB.log("raw_pitches", "INFO", "pulled 587 rows", rows=587, elapsed_ms=1234)
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def log(cls, target, level, message, rows=None, elapsed_ms=None):
        ds = MgrDT.today_ds()
        #cls.query(
        #    "INSERT INTO _run_log (DS, target, level, rows, elapsed_ms, message) VALUES (?, ?, ?, ?, ?, ?)",
        #    (ds, target, level, rows, elapsed_ms, message),
        #)
        print(f"[{ds}] {target:20s} {level:5s} {message}")       # mirror to stdout for live visibility