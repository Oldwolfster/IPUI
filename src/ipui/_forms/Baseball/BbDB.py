import re
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import namedtuple

class BbDB:

    DB_PATH = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")
    Summary = namedtuple('Summary', 'gd rows cols min_gd max_gd')
    pipe_log_display = None
    pipe_log_text = ""

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — one call at startup, everything exists after.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def configure(cls):
        Path(cls.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        cls.materialize_all_tables()
        from ipui._forms.Baseball._SchemaViews import _SchemaViews
        _SchemaViews.create_all(cls.DB_PATH)
        if not cls.query("SELECT 1 FROM _summary LIMIT 1"): cls.update_summary_all()
    # ══════════════════════════════════════════════════════════════
    # QUERY → rows.   EXECUTE → rowcount.   Two clean lanes.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def query(cls, sql, params=()):
        conn = sqlite3.connect(cls.DB_PATH)
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return rows

    @classmethod
    def execute(cls, sql, params=()):
        conn = sqlite3.connect(cls.DB_PATH)
        cur  = conn.execute(sql, params)
        rc   = cur.rowcount
        conn.commit()
        conn.close()
        return rc

    # ══════════════════════════════════════════════════════════════
    # TABLE HELPERS
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def drop_table(cls, tbl):
        cls.execute(f"DROP TABLE IF EXISTS {tbl}")
        cls.log(tbl, "dropped")

    @classmethod
    def tables_for_layer(cls, layer):
        rows = cls.query("""
            SELECT name FROM sqlite_master
            WHERE  type='table' AND (name = ? OR name LIKE ?)
            ORDER BY name
        """, (layer, f"{layer}_%"))
        return [r[0] for r in rows]

    @classmethod                                                                # NEW
    def tables_for_layer(cls, layer):                                           # NEW
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl                  # NEW
        seen = []                                                               # NEW
        for tbl, _ in _SchemaTbl.SCHEMA:                                        # NEW
            if tbl not in seen and tbl.split('_')[0] == layer.lower():
                seen.append(tbl)                                                # NEW
        return seen

    @classmethod
    def layer_of(cls, tbl):
        return tbl.split('_')[0]

    # ══════════════════════════════════════════════════════════════
    # SUMMARY — call after pipeline ops.  Cards read _summary.
    # ══════════════════════════════════════════════════════════════
    @classmethod
    def get_summary(cls, tbl):
        row = cls.query("SELECT GD, rows, cols, min_gd, max_gd FROM _summary WHERE tbl = ?", (tbl,))
        if row: return cls.Summary(*row[0])
        return  cls.Summary(None, 0, 0, None, None)

    @classmethod
    def update_summary(cls, tbl):
        from ipui._forms.Baseball.MgrDT import MgrDT
        gd     = MgrDT.today_gd()
        rows   = cls.query(f"SELECT COUNT(*) FROM {tbl}")[0][0]
        cols   = len(cls.query(f"PRAGMA table_info({tbl})"))
        mn, mx = cls.query(f"SELECT MIN(GD), MAX(GD) FROM {tbl}")[0]
        cls.execute("DELETE FROM _summary WHERE tbl = ?", (tbl,))
        cls.execute("""
            INSERT INTO _summary (GD, tbl, rows, cols, min_gd, max_gd)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (gd, tbl, rows, cols, mn, mx))

    @classmethod
    def update_summary_all(cls):
        for layer in cls.all_layers():
            for tbl in cls.tables_for_layer(layer):
                cls.update_summary(tbl)

    @classmethod
    def all_layers(cls):
        rows = cls.query("""
            SELECT DISTINCT name FROM sqlite_master
            WHERE  type='table' AND name NOT LIKE '\\_%' ESCAPE '\\'
        """)
        return sorted(set(r[0].split('_')[0] for r in rows))

    # ══════════════════════════════════════════════════════════════
    # REBUILD — drop + recreate one table from SCHEMA.
    # Used by Workbench after editing _SchemaTbl.py.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def rebuild_table(cls, tbl):
        import importlib
        from ipui._forms.Baseball import _SchemaTbl
        importlib.reload(_SchemaTbl)
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl as fresh
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute(f"DROP TABLE IF EXISTS {tbl}")
        cols = [col for (t, col) in fresh.SCHEMA if t == tbl]
        cls.materialize_one_table(conn, tbl, cols)
        conn.commit()
        conn.close()
        cls.log(tbl, "rebuilt from schema")

    # ══════════════════════════════════════════════════════════════
    # LOG — timestamped print.  No DB.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def log(cls, target, msg):
        ts   = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {target:20s} {msg}"
        print(line)
        cls.pipe_log_text=f"{line}\n{cls.pipe_log_text}"
        if cls.pipe_log_display: cls.pipe_log_display.text = cls.pipe_log_text

    # ══════════════════════════════════════════════════════════════
    # MATERIALIZATION — _SchemaTbl.SCHEMA → physical tables.
    #   Data tables  : GD injected as PK col 1.  WITHOUT ROWID.
    #   feet_ tables : TS injected as PK col 2.
    #   _prefix      : metadata — no injection, standard ROWID.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def materialize_all_tables(cls):
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl
        conn    = sqlite3.connect(cls.DB_PATH)
        grouped = {}
        order   = []
        for tbl, col_decl in _SchemaTbl.SCHEMA:
            if tbl not in grouped:
                grouped[tbl] = []
                order.append(tbl)
            grouped[tbl].append(col_decl)
        for tbl in order:
            cls.materialize_one_table(conn, tbl, grouped[tbl])
        conn.commit()
        conn.close()

    @classmethod
    def materialize_one_table(cls, conn, tbl, raw_cols):
        layer   = cls.layer_of(tbl)
        columns = []
        pk_cols = []
        columns.append("GD INTEGER")
        pk_cols.append("GD")

        if layer == "feet":
            columns.append("TS INTEGER")
            pk_cols.append("TS")
        for raw_col in raw_cols:
            is_pk, column = cls.parse_col(raw_col)
            columns.append(column)
            if is_pk: pk_cols.append(column.split()[0])
            #max_len = max(len(c.split()[0]) for c in columns)
            #columns = [f"{c.split()[0]:<{max_len}}  {' '.join(c.split()[1:])}" for c in columns]

        pk_clause = f"PRIMARY KEY ({', '.join(pk_cols)})"
        body      = ",\n    ".join(columns + [pk_clause])
        suffix    = " WITHOUT ROWID"
        conn.execute(f"CREATE TABLE IF NOT EXISTS {tbl} (\n    {body}\n){suffix}")

    @classmethod
    def parse_col(cls, raw):
        stripped = raw.strip()
        match    = re.match(r'^(pk)([\s_]+)(.+)$', stripped, flags=re.IGNORECASE)
        if match:
            return True,  match.group(3).strip()
        return     False, stripped


    # ════════════════════════════════════════════════
    # Update tables from view                      ═══
    # ════════════════════════════════════════════════
    @classmethod
    def field_names(cls, tbl):
        return [r[1] for r in cls.query(f"PRAGMA table_info({tbl})")]


    @classmethod
    def upsert_from_view(cls, tbl, start_gd, end_gd):
        """
        generic view→table upsert with column matching
        :param tbl:
        :param start_gd:
        :param end_gd:
        :return:
        """
        view = f"pull_{tbl}"
        if not cls.query("SELECT 1 FROM sqlite_master WHERE type='view' AND name = ?", (view,)):
            cls.log(tbl, f"no view {view}")
            return
        tbl_cols  = [r[1] for r in cls.query(f"PRAGMA table_info({tbl})")]
        view_cols = [r[1] for r in cls.query(f"PRAGMA table_info({view})")]
        common    = sorted(set(tbl_cols) & set(view_cols))
        if not common:
            cls.log(tbl, "no common columns")
            return
        pk_cols   = [r[1] for r in cls.query(f"PRAGMA table_info({tbl})") if r[5] > 0]
        col_list  = ", ".join(common)
        pk_list   = ", ".join(pk_cols)
        set_cols  = sorted(set(common) - set(pk_cols))
        conflict  = "DO NOTHING" if not set_cols else \
                    "DO UPDATE SET " + ", ".join(f"{c} = excluded.{c}" for c in set_cols)
        sql = (
            f"INSERT INTO {tbl} ({col_list}) "
            f"SELECT {col_list} FROM {view} WHERE GD BETWEEN ? AND ? "
            f"ON CONFLICT({pk_list}) {conflict}"
        )
        cls.execute(sql, (start_gd, end_gd))
        cls.log(tbl, f"upserted from {view}")



    @classmethod
    def list_objects(cls, kind):
        where_type = "type IN ('table','view')" if kind == "all" else f"type = '{kind}'"
        rows = cls.query(f"""
            SELECT type, name FROM sqlite_master
            WHERE  {where_type}
            AND    name NOT LIKE 'sqlite_%'
            AND    name NOT LIKE '\\_%' ESCAPE '\\'
            ORDER BY type, name
        """)
        return [list(r) for r in rows]

    # BbDB.py method: field_names  NEW: unified field list for tables AND views
    @classmethod
    def field_names(cls, obj):
        conn  = sqlite3.connect(cls.DB_PATH)
        cur   = conn.execute(f"SELECT * FROM {obj} LIMIT 0")
        names = [d[0] for d in cur.description]
        conn.close()
        return names

