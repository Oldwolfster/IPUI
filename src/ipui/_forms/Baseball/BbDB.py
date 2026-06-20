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
    LOG_TO_FILE = True

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — one call at startup, everything exists after.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def configure(cls):
        Path(cls.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        cls.materialize_all_tables()

        from ipui._forms.Baseball.MgrSchema import MgrSchema
        MgrSchema.sync_fields_to_db()
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
    def has_rows_on_or_past(cls, tbl, gd=None):
        if gd is None: sql, params = f"SELECT 1 FROM {tbl} LIMIT 1",               ()
        else:          sql, params = f"SELECT 1 FROM {tbl} WHERE GD >= ? LIMIT 1", (gd,)
        return bool(cls.query(sql, params))

    @classmethod
    def execute(cls, sql, params=()):
        conn = sqlite3.connect(cls.DB_PATH)
        cur  = conn.execute(sql, params)
        rc   = cur.rowcount
        conn.commit()
        conn.close()
        return rc

    @classmethod
    def execute_many(cls, sql, params_list):
        conn = sqlite3.connect(cls.DB_PATH)
        conn.executemany(sql, params_list)
        conn.commit()
        conn.close()
    # ══════════════════════════════════════════════════════════════
    # TABLE HELPERS
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def drop_table(cls, tbl):
        cls.execute(f"DROP TABLE IF EXISTS {tbl}")
        cls.log(tbl, "dropped")



    @classmethod
    def tables_for_layer(cls, layer):
        layer = layer.lower()                                                # NEW
        rows = cls.query("""
            SELECT name FROM sqlite_master
            WHERE  type='table' AND (name = ? OR name LIKE ?)
            ORDER BY name
        """, (layer, f"{layer}_%"))
        return [r[0] for r in rows]

    @classmethod                                                                # NEW
    def tables_for_layerDELEETEMEE(cls, layer):                                           # NEW
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl                  # NEW
        seen = []                                                               # NEW
        for tbl, _ in _SchemaTbl.SCHEMA:                                        # NEW
            if tbl not in seen and tbl.split('_')[0] == layer.lower():
                seen.append(tbl)                                                # NEW
        return seen


    @classmethod
    def tables_for_layer(cls, layer):
        schema_tbls = cls.tables_for_layer_schema(layer)
        return        cls.tables_for_layer_add_db_only(layer, schema_tbls)

    # BbDB.py method: tables_for_layer_schema  New: tables from _SchemaTbl in defined order
    @classmethod
    def tables_for_layer_schema(cls, layer):
        layer = layer.lower()
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl
        seen = []
        for tbl, _ in _SchemaTbl.SCHEMA:
            if tbl not in seen and tbl.split('_')[0] == layer:  seen.append(tbl)
        return seen

    # BbDB.py method: tables_for_layer_add_db_only  New: append DB tables not already in list
    @classmethod
    def tables_for_layer_add_db_only(cls, layer, seen):
        layer = layer.lower()
        rows = cls.query("""
            SELECT name FROM sqlite_master
            WHERE  type='table' AND (name = ? OR name LIKE ?)
            ORDER BY name
        """, (layer, f"{layer}_%"))
        for r in rows:
            if r[0] not in seen:                seen.append(r[0])
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
    def rebuild_table(cls, tbl, raw_cols=None):
        if raw_cols is None:
            import importlib
            from ipui._forms.Baseball import _SchemaTbl
            importlib.reload(_SchemaTbl)
            from ipui._forms.Baseball._SchemaTbl import _SchemaTbl as fresh
            raw_cols = [col for (t, col) in fresh.SCHEMA if t == tbl]
        conn = sqlite3.connect(cls.DB_PATH)
        conn.execute(f"DROP TABLE IF EXISTS {tbl}")
        cls.materialize_one_table(conn, tbl, raw_cols)
        conn.commit()
        conn.close()
        cls.log(tbl, "rebuilt from schema")


    # ══════════════════════════════════════════════════════════════
    # LOG — timestamped print.  No DB.
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def log_path(cls, now=None):
        if now is None: now = datetime.now()
        return Path(cls.DB_PATH).parent / f"baseball_{now.strftime('%Y%m%d')}.log"

    @classmethod
    def log(cls, target, msg):
        now  = datetime.now()
        ts   = now.strftime("%H:%M:%S")
        line = f"[{ts}] {target:20s} {msg}"
        print(line)

        if cls.LOG_TO_FILE:
            try:
                Path(cls.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
                with open(cls.log_path(now), "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception as e:
                print(f"[{ts}] {'log_file':20s} failed: {e}")

        cls.pipe_log_text=f"{line}\n{cls.pipe_log_text}"

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
        print(f"tbl={tbl}")
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
    def upsert_from_view(cls, tbl, gd):
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
            f"SELECT {col_list} FROM {view} WHERE GD = ?"
            f"ON CONFLICT({pk_list}) {conflict}"
        )
        cls.execute(sql, (gd,))
        #cls.log(tbl, f"upserted from {view}")

    @classmethod
    def has_ts(cls,tbl):
        """check for TS in primary key  - c[1] is name and c[5] is part of PK"""
        cols = cls.query(f"PRAGMA table_info({tbl})")
        return any(c[1] == "TS" and c[5] > 0 for c in cols)

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

    @classmethod
    def phoenix(cls):
        cls.delete_db_files()                                          # ashes
        cls.configure()                                               # rise
        day  = cls.phoenix_count_today()    + 1                       # includes this rise
        life = cls.phoenix_count_lifetime() + 1                       # includes this rise
        cls.log("Phoenix", f"🔥 Phoenix #{day} - {'':32s}lifetime #{life}")

    # BbDB.py method: phoenix_count_lifetime  NEW: sum 🔥 across every daily log (survives nuke)
    @classmethod
    def phoenix_count_lifetime(cls):
        folder = cls.log_path().parent
        total  = 0
        for f in folder.glob("baseball_*.log"):
            total += f.read_text(encoding="utf-8").count("🔥")
        return total

    # BbDB.py method: delete_db_files  NEW: remove db + sqlite sidecars (wal/shm/journal)
    @classmethod
    def delete_db_files(cls):
        p     = Path(cls.DB_PATH)
        kill  = [p, p.with_suffix(".db-wal"), p.with_suffix(".db-shm"), p.with_suffix(".db-journal")]
        for f in kill:
            f.unlink(missing_ok=True)

    # BbDB.py method: phoenix_count_today  NEW: count prior rises in today's log (survives nuke)
    @classmethod
    def phoenix_count_today(cls):
        path = cls.log_path()
        if not path.exists(): return 0
        return path.read_text(encoding="utf-8").count("🔥")