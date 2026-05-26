# ═══════════════════════════════════════════════════════════════════════════
# MgrAccessImport.py  REPLACE WHOLE FILE   Additive importer .accdb → SQLite
# ═══════════════════════════════════════════════════════════════════════════
# Stable public API — never changes:
#     MgrAccessImport.import_from(accdb_path, sqlite_path=None)
#
# Behavior:
#   - Opens .accdb via pyodbc + ACE driver.
#   - For each user table:
#       1. CREATE in SQLite if missing.  Existing schemas untouched (additive).
#       2. Pick id column: first of first 3 cols whose name contains "id"
#          (case-insensitive).  None found → skip with console note.
#       3. If SQLite table empty → INSERT all rows from Access.
#          Else → INSERT only WHERE id > MAX(id) in SQLite.
#   - BLOB columns → NULL.
#   - Progress every 100 rows + final tick.
#
# Column name sanitization (Access → SQLite):
#   <digit><letter> at start (2 chars) → swap     "2B"    → "B2"
#   multiple leading digits           → prefix   "23B"   → "_23B"
#   "/"  → "_"                                   "K/9"   → "K_9"
#   "-"  → "_"                                   "K-BB"  → "K_BB"
#   "%"  → "_pct"                                "K%"    → "K_pct"
#   else case preserved.
#
# Type map (Wolf's data uses these four; unknown → TEXT as safe fallback):
#   VARCHAR → TEXT     INTEGER → INTEGER
#   DOUBLE  → REAL     DATETIME→ TEXT (ISO 8601)
#
# Convention: classmethods only, matches IPUI's Mgr* family.
# ═══════════════════════════════════════════════════════════════════════════

import os
import re
import sqlite3
import pyodbc

from ipui.utils.EZ import EZ


class MgrAccessImport:

    DRIVER = r"{Microsoft Access Driver (*.mdb, *.accdb)}"

    TYPE_MAP = {
        "VARCHAR"  : "TEXT",
        "INTEGER"  : "INTEGER",
        "SMALLINT" : "INTEGER",
        "COUNTER"  : "INTEGER",
        "LONGCHAR" : "TEXT",
        "DOUBLE"   : "REAL",
        "BIT"      : "INTEGER",
        "DATETIME" : "TEXT",
    }

    PROGRESS_EVERY = 100

    # ──────────────────────────────────────────────────────────────────────
    # PUBLIC — frozen signature.  Never changes.
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def import_from(cls, accdb_path, sqlite_path=None):
        sqlite_path = sqlite_path or cls.sibling_db_path(accdb_path)
        a_cursor    = cls.connect_access(accdb_path)
        s_conn      = sqlite3.connect(sqlite_path)
        try:
            cls.run_all_tables(a_cursor, s_conn)
            s_conn.commit()
        finally:
            cls.close_access(a_cursor)
            s_conn.close()

    # ──────────────────────────────────────────────────────────────────────
    # ORCHESTRATION
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def run_all_tables(cls, a_cursor, s_conn):
        tables = cls.list_tables(a_cursor)
        total  = len(tables)
        for idx, table in enumerate(tables, start=1):
            cls.run_one_table(a_cursor, s_conn, table, idx, total)

    @classmethod
    def run_one_table(cls, a_cursor, s_conn, table, idx, total):
        header = f"table {table} ({idx} of {total})"
        cols   = cls.list_columns(a_cursor, table)
        id_col = cls.pick_id_column(cols)
        if not id_col:
            print(f"{header}  [skipped — no id column in first 3]")
            return
        cls.sync_schema(s_conn, table, cols)
        cls.sync_data  (a_cursor, s_conn, table, cols, id_col, header)

    # ──────────────────────────────────────────────────────────────────────
    # CONNECTION
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def connect_access(cls, accdb_path):
        conn_str = f"DRIVER={cls.DRIVER};DBQ={accdb_path};"
        conn     = pyodbc.connect(conn_str)
        conn.setdecoding(pyodbc.SQL_CHAR,  encoding="cp1252")
        conn.setdecoding(pyodbc.SQL_WCHAR, encoding="latin-1")
        conn.setencoding(encoding="utf-8")
        return conn.cursor()

    @classmethod
    def close_access(cls, cursor):
        if not cursor: return
        conn = cursor.connection
        cursor.close()
        if conn: conn.close()

    @classmethod
    def sibling_db_path(cls, accdb_path):
        # foo.accdb → foo.db  (same folder)
        root, _ = os.path.splitext(accdb_path)
        return root + ".db"

    # ──────────────────────────────────────────────────────────────────────
    # SCHEMA DISCOVERY
    # ──────────────────────────────────────────────────────────────────────

    # ═══════════════════════════════════════════════════════════════════════════
    # MgrAccessImport.py  method: list_tables   Update:   skip Access internals
    # ═══════════════════════════════════════════════════════════════════════════
    # Skip names starting with "~" (temp/scratch) or "MSys" (system).
    # tableType="TABLE" is supposed to filter MSys out but some ACE versions
    # leak them through, so we belt-and-suspenders here.

    @classmethod
    def list_tables(cls, cursor):
        return [
            row.table_name
            for row in cursor.tables(tableType="TABLE")
            if not cls.is_internal_table(row.table_name)
        ]

    @classmethod
    def is_internal_table(cls, name):
        return name.startswith("~") or name.startswith("MSys")


    @classmethod
    def list_columns(cls, cursor, table):
        out = []
        for c in cursor.columns(table=table):
            access_name = c.column_name
            # print(f"  [type debug] {table}.{c.column_name} → {c.type_name!r}")
            sqlite_name = cls.sanitize_name(access_name)
            access_type = c.type_name.upper()
            cls.require_known_type(access_type, table, access_name)
            sqlite_type = cls.TYPE_MAP[access_type]
            out.append((access_name, sqlite_name, sqlite_type))
        return out

    @classmethod
    def require_known_type(cls, access_type, table, access_name):
        if access_type in cls.TYPE_MAP: return
        EZ.err(
            f"Unknown Access type {access_type!r} on {table}.{access_name}.\n"
            f"Add it to MgrAccessImport.TYPE_MAP and re-run."
        )


    @classmethod
    def pick_id_column(cls, cols):
        # First of first-3 cols whose sanitized name contains "id" (case-insensitive).
        # Returns (access_name, sqlite_name) or None.
        for access_name, sqlite_name, _ in cols[:3]:
            if "id" in sqlite_name.lower():
                return (access_name, sqlite_name)
        return None

    # ──────────────────────────────────────────────────────────────────────
    # NAME SANITIZATION
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def sanitize_name(cls, name):
        name = cls.fix_leading_digits(name)
        name = name.replace("/", "_")
        name = name.replace("-", "_")
        name = name.replace("%", "_pct")
        return name

    @classmethod
    def fix_leading_digits(cls, name):
        # "2B"   → "B2"    exact <digit><letter>
        # "23B"  → "_23B"  multi-digit prefix
        # "2"    → "_2"    pure number (no letter)
        if re.fullmatch(r"\d[A-Za-z]", name):
            return name[1] + name[0]
        if re.match(r"\d", name):
            return "_" + name
        return name

    # ──────────────────────────────────────────────────────────────────────
    # SCHEMA SYNC  (additive — CREATE missing tables only)
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def sync_schema(cls, s_conn, table, cols):
        if cls.sqlite_table_exists(s_conn, table): return
        cls.create_sqlite_table(s_conn, table, cols)

    @classmethod
    def sqlite_table_exists(cls, s_conn, table):
        row = s_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone()
        return row is not None

    @classmethod
    def create_sqlite_table(cls, s_conn, table, cols):
        col_defs = ", ".join(f'"{sqlite_name}" {sqlite_type}'
                             for _, sqlite_name, sqlite_type in cols)
        s_conn.execute(f'CREATE TABLE "{table}" ({col_defs})')

    # ──────────────────────────────────────────────────────────────────────
    # DATA SYNC  (additive — INSERT only rows with id > MAX(id))
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def sync_data(cls, a_cursor, s_conn, table, cols, id_col, header):
        access_id, sqlite_id = id_col
        max_id = cls.sqlite_max_id(s_conn, table, sqlite_id)
        to_do  = cls.access_pending_count(a_cursor, table, access_id, max_id)
        if to_do == 0:
            print(f"{header}  [up to date]")
            return
        cls.copy_rows(a_cursor, s_conn, table, cols, access_id, max_id, to_do, header)

    @classmethod
    def sqlite_max_id(cls, s_conn, table, sqlite_id):
        row = s_conn.execute(
            f'SELECT MAX("{sqlite_id}") FROM "{table}"'
        ).fetchone()
        return row[0]      # may be None if table empty

    @classmethod
    def access_pending_count(cls, a_cursor, table, access_id, max_id):
        if max_id is None:
            sql = f'SELECT COUNT(*) FROM [{table}]'
            a_cursor.execute(sql)
        else:
            sql = f'SELECT COUNT(*) FROM [{table}] WHERE [{access_id}] > ?'
            a_cursor.execute(sql, max_id)
        return a_cursor.fetchone()[0]

    @classmethod
    def copy_rows(cls, a_cursor, s_conn, table, cols, access_id, max_id, to_do, header):
        select_sql   = cls.build_select(table, cols, access_id, max_id)
        insert_sql   = cls.build_insert(table, cols)
        params       = () if max_id is None else (max_id,)
        a_cursor.execute(select_sql, *params)

        done = 0
        for row in a_cursor:
            s_conn.execute(insert_sql, tuple(row))
            done += 1
            if done % cls.PROGRESS_EVERY == 0 or done == to_do:
                print(f"{header}  record {done} of {to_do}")

    @classmethod
    def build_select(cls, table, cols, access_id, max_id):
        # Pull columns in declared order, using Access's raw names + brackets.
        col_list = ", ".join(f"[{access_name}]" for access_name, _, _ in cols)
        if max_id is None:
            return f'SELECT {col_list} FROM [{table}]'
        return     f'SELECT {col_list} FROM [{table}] WHERE [{access_id}] > ?'

    @classmethod
    def build_insert(cls, table, cols):
        col_list     = ", ".join(f'"{sqlite_name}"' for _, sqlite_name, _ in cols)
        placeholders = ", ".join("?" for _ in cols)
        return f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})'