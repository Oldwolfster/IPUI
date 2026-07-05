# MgrSchema.py  NEW FILE — single authority for _SchemaTbl.py and _SchemaViews.py

from pathlib import Path
import shutil
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrDT import MgrDT
from ipui.utils.EZ import EZ


class MgrSchema:
    DEFAULT_SEQ = {"Key": 50, "Entity": 500, "Metric": 1000, "Context": 5000}

    """Manages schema files and DB sync. Stateless — the files ARE the state."""
    VIEWS_FILE                  = Path(__file__).parent / "_SchemaViews.py"
    TABLES_FILE                 = Path(__file__).parent / "_SchemaTbl.py"
    BACKUP_DIR                  = Path(__file__).parent / "docs" / "backup"
    FIELDS_FILE                 = Path(__file__).parent / "_SchemaFlds.py"
    CLONE_VERBATIM_PREFIXES     = ["update"]
    # ══════════════════════════════════════════════════════════════
    # CREATE TABLE — dispatcher
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def create_table(table_name, columns):
        table_name    = MgrSchema.validate_name(table_name)
        raw_cols      = MgrSchema.to_raw_cols(columns)
        MgrSchema     . update_tbl_schema(table_name, columns)
        BbDB          . rebuild_table(table_name, raw_cols)
        BbDB          . update_summary(table_name)
        MgrSchema     . build_stub_select(table_name, columns)
        BbDB.log      ( table_name, "table created")

    # ══════════════════════════════════════════════════════════════
    # SAVE VIEW — dispatcher
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def save_view(view_name, select_sql):
        MgrSchema     .validate_name(view_name)
        MgrSchema     . validate_sql(view_name, select_sql)
        MgrSchema     . backup_file(MgrSchema.VIEWS_FILE)
        method_text   = MgrSchema.format_method(view_name, select_sql)
        file_text     = MgrSchema.read_file(MgrSchema.VIEWS_FILE)
        split_text    = MgrSchema.remove_existing(file_text, view_name)
        final_text    = MgrSchema.insert_method(split_text, method_text)
        MgrSchema     . write_file(MgrSchema.VIEWS_FILE, final_text)
        MgrSchema     . drop_and_rebuild_view(view_name)
        BbDB.log      ( view_name, "saved to _SchemaViews.py")

    # ══════════════════════════════════════════════════════════════
    # SYNC DB — idempotent reload + rebuild
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def drop_and_rebuild_table(object_name):
        """Drop one object, then re-run configure so missing schema objects are recreated without altering existing ones."""
        BbDB.execute(f"DROP TABLE IF EXISTS {object_name}")
        MgrSchema.rebuild()

    @staticmethod
    def drop_and_rebuild_view(object_name):
        """Drop one object, then re-run configure so missing schema objects are recreated without altering existing ones."""
        BbDB.execute(f"DROP VIEW IF EXISTS {object_name}")
        MgrSchema.rebuild()

    @staticmethod
    def rebuild():
        """Drop one object, then re-run configure so missing schema objects are recreated without altering existing ones."""
        import importlib
        from ipui._forms.Baseball import _SchemaTbl, _SchemaViews
        importlib.reload(_SchemaTbl)
        importlib.reload(_SchemaViews)
        BbDB.configure() #Idiomatic  Won't alter existing but creates if absent... from a view to thw hole db.
    # ══════════════════════════════════════════════════════════════
    # TABLE SCHEMA — insert block into _SchemaTbl.py
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def insert_table_schema(table_name, columns):
        MgrSchema.backup_file(MgrSchema.TABLES_FILE)
        file_text = MgrSchema.read_file(MgrSchema.TABLES_FILE)
        lines     = file_text.splitlines(keepends=True)
        insert_at = MgrSchema.find_table_insert_line(lines, BbDB.layer_of(table_name))
        block     = MgrSchema.generate_table_block(table_name, columns)
        final     = ''.join(lines[:insert_at] + block + lines[insert_at:])
        MgrSchema.write_file(MgrSchema.TABLES_FILE, final)
        BbDB.log(table_name, "added to _SchemaTbl.py")

    @staticmethod
    def find_table_insert_line(lines, layer):
        last_match = None
        for i, line in enumerate(lines):
            if f"('{layer}_" in line or f"('{layer}'," in line:
                last_match = i
        if last_match is None:
            for i in range(len(lines) - 1, -1, -1):
                if ']' in lines[i]: return i
            return len(lines)
        idx = last_match + 1
        while idx < len(lines) and lines[idx].strip() == '':
            idx += 1
        return idx

    @staticmethod
    def generate_table_block(table_name, columns):
        lines = [f"        # ═══ {table_name} ═══\n"]
        for col in columns:
            pk = 'PK' if col['pk'] else '  '
            lines.append(f"        ('{table_name}', '{pk} {col['name']:<40s}{col['type']}'),\n")
        lines.append("\n\n")
        return lines
    # ══════════════════════════════════════════════════════════════
    # TABLE SCHEMA — part 2
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def update_tbl_schema(table_name, columns):
        """Write this table's block to _SchemaTbl.py. Predict tables skip — they're ephemeral."""
        if BbDB.layer_of(table_name) == "predict":
            return
        MgrSchema     . backup_file(MgrSchema.TABLES_FILE)
        original      = MgrSchema.read_file(MgrSchema.TABLES_FILE)
        new_block     = MgrSchema.generate_table_block(table_name, columns)
        final         = MgrSchema.swap_table_block(original, table_name, new_block)
        MgrSchema     . validate_no_tables_lost(original, final, table_name)
        MgrSchema     . write_file(MgrSchema.TABLES_FILE, final)


    @staticmethod
    def to_raw_cols(columns):
        raw_cols = []
        for col in columns:
            pk = 'PK' if col['pk'] else '  '
            raw_cols.append(f"{pk} {col['name']:<40s}{col['type']}")
        return raw_cols


    @staticmethod
    def find_table_block_lines(file_text, table_name):
        """Return (set of line indices, first_idx) for this table's block."""
        lines          = file_text.splitlines(keepends=True)
        comment_marker = f"# ═══ {table_name}"
        entry_marker   = f"('{table_name}',"
        remove         = set()
        first_idx      = None
        for i, line in enumerate(lines):
            if comment_marker in line or entry_marker in line:
                remove.add(i)
                if first_idx is None: first_idx = i
        return remove, first_idx

    @staticmethod
    def swap_table_block(file_text, table_name, new_block):
        """Remove existing table block and insert new_block at same position."""
        lines              = file_text.splitlines(keepends=True)
        remove, first_idx  = MgrSchema.find_table_block_lines(file_text, table_name)
        if first_idx is None:
            for i in range(len(lines) - 1, -1, -1):
                if ']' in lines[i]: return ''.join(lines[:i] + new_block + lines[i:])
        result   = []
        inserted = False
        for i, line in enumerate(lines):
            if i in remove:
                if not inserted:
                    result.extend(new_block)
                    inserted = True
                continue
            result.append(line)
        return ''.join(result)

    @staticmethod
    def validate_no_tables_lost(original, final, table_name):
        """Verify every table from original still has entries in final text."""
        import re
        original_tables = set(re.findall(r"\('(\w+)',", original))
        final_tables    = set(re.findall(r"\('(\w+)',", final))
        missing         = original_tables - final_tables
        if missing: EZ.err(f"Schema replace would lose tables: {missing}")
    # ══════════════════════════════════════════════════════════════
    # STUB SELECT — clean SQL for new pull views
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def build_stub_selectOld(table_name, columns):
        if BbDB.layer_of(table_name) == "raw": return
        if BbDB.layer_of(table_name) == "predict": return
            #MgrSchema.build_predict_view(table_name)

        parts = ["0 AS GD"]
        if BbDB.layer_of(table_name) == "feet":
            parts.append("0 AS TS")
        for col in columns:
            val   = "''" if col['type'] == 'TEXT' else "0.0" if col['type'] == 'REAL' else "0"
            parts.append(f"{val:<45s}AS {col['name']}")
        final =  "SELECT\n    " + ",\n    ".join(parts)
        MgrSchema.save_view(f"pull_{table_name}", final)


    def build_stub_select(table_name, columns):
        if BbDB.layer_of(table_name) == "raw": return
        if BbDB.layer_of(table_name) == "predict": return       # REPLACE old build_predict_view call
        parts = ["0 AS GD"]
        if BbDB.layer_of(table_name) == "feet":
            parts.append("0 AS TS")
        for col in columns:
            val   = "''" if col['type'] == 'TEXT' else "0.0" if col['type'] == 'REAL' else "0"
            parts.append(f"{val:<45s}AS {col['name']}")
        final =  "SELECT\n    " + ",\n    ".join(parts)
        MgrSchema.save_view(f"pull_{table_name}", final)

    # ══════════════════════════════════════════════════════════════
    # VIEW HELPERS
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def validate_sql(view_name, select_sql):
        error = MgrSchema.test_sql(view_name, select_sql)
        if error is not None: EZ.err(error)

    @staticmethod
    def test_sql(view_name, select_sql):
        """Returns error string or None if valid."""
        try:
            BbDB.query(f"EXPLAIN {select_sql}")
            return None
        except Exception as e:
            msg = f"SQL invalid: {e}"
            BbDB.log(view_name, msg)
            return msg

    @staticmethod
    def format_method(view_name, select_sql):
        sql_lines    = select_sql.strip().splitlines()
        indented_sql = "\n".join("    " + line for line in sql_lines)
        return (
            "\n    @classmethod\n"
            f"    def view_{view_name}(cls):\n"
            '        return """\n'
            f"{indented_sql}\n"
            '        """\n'
        )

    @staticmethod
    def remove_existing(file_text, view_name):
        bounds = MgrSchema.find_method_bounds(file_text, view_name)
        lines  = file_text.splitlines(keepends=True)
        if bounds is None:
            return (file_text, '')
        start, end = bounds
        return (''.join(lines[:start]), ''.join(lines[end:]))

    @staticmethod
    def find_method_bounds(file_text, view_name):
        """Return (start, end) line indices for @classmethod + method, or None."""
        marker  = f"def view_{view_name}("
        lines   = file_text.splitlines(keepends=True)
        def_idx = None
        for i, line in enumerate(lines):
            if marker in line:
                def_idx = i
                break
        if def_idx is None:
            return None
        start = def_idx - 1 if def_idx > 0 and "@classmethod" in lines[def_idx - 1] else def_idx
        end   = len(lines)
        for i in range(def_idx + 1, len(lines)):
            if "@classmethod" in lines[i] or "class " in lines[i]:
                end = i
                break
        return (start, end)

    @staticmethod
    def insert_method(split_text, method_text):
        file_before, file_after = split_text
        return file_before.rstrip() + "\n" + method_text + file_after
    # ══════════════════════════════════════════════════════════════
    # FILE I/O
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def backup_file(file_path):
        MgrSchema.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, MgrSchema.BACKUP_DIR / f"{file_path.name}.bak")

    @staticmethod
    def read_file(file_path):
        return file_path.read_text(encoding='utf-8')

    @staticmethod
    def write_file(file_path, file_text):
        tmp = file_path.with_suffix('.py.tmp')
        tmp.write_text(file_text, encoding='utf-8')
        shutil.move(str(tmp), str(file_path))

    @staticmethod
    def validate_name(name):
        if not name:         raise ValueError("Schema name cannot be blank")
        if not name.replace('_', '').isalnum():         raise ValueError(f"Invalid schema name: {name}")
        if name[0].isdigit():   raise ValueError(f"Schema name cannot start with a number: {name}")
        return name




    # ══════════════════════════════════════════════════════════════
    # FIELDS — upsert/delete a _registry vocab row, file stays in sync
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def flds_upsert(kind, token, definition, dtype, seq=None):
        """Save one (kind, token) vocab row: DB, then the file."""
        if not dtype: EZ.err(f"({kind}, {token}) has no dtype — every field needs one.")
        if seq is None: seq = MgrSchema.DEFAULT_SEQ.get(kind, 50)
        MgrSchema.delete_if_exists_in_db(kind, token)
        MgrSchema.insert_to_db(kind, token, definition, dtype, seq)
        MgrSchema.update_SchemaFlds(kind, token, definition, dtype, seq)

    @staticmethod
    def flds_delete(kind, token):
        """Delete one (kind, token) vocab row: DB, then the file."""
        MgrSchema.delete_if_exists_in_db(kind, token)
        MgrSchema.remove_from_SchemaFlds(kind, token)

    @staticmethod
    def delete_if_exists_in_db(kind, token):
        BbDB.execute("DELETE FROM _registry WHERE kind=? AND token=?", (kind, token))

    @staticmethod
    def insert_to_db(kind, token, definition, dtype, seq=None):
        if seq is None: seq = MgrSchema.DEFAULT_SEQ.get(kind, 50)
        BbDB.execute("INSERT INTO _registry (GD, kind, token, definition, dtype, seq) VALUES (?,?,?,?,?,?)",
                     (MgrDT.today_gd(), kind, token, definition, dtype, seq))

    @staticmethod
    def sync_fields_to_db():
        """Startup call: insert every _SchemaFlds.py line missing from _registry."""
        import importlib
        from ipui._forms.Baseball import _SchemaFlds
        importlib.reload(_SchemaFlds)
        for line in _SchemaFlds._SchemaFlds.FIELDS:
            kind, token, definition, dtype, seq = MgrSchema.parse_field_line(line)
            exists = BbDB.query("SELECT 1 FROM _registry WHERE kind=? AND token=?", (kind, token))
            if not exists:
                MgrSchema.insert_to_db(kind, token, definition, dtype, seq)

    # ── _SchemaFlds.py — find/sandwich/remove a single line by (kind, token) ───
    @staticmethod
    def update_SchemaFlds(kind, token, definition, dtype, seq=None):
        """Replace this (kind, token)'s line in place if it exists, else append it."""
        MgrSchema.backup_file(MgrSchema.FIELDS_FILE)
        new_line       = MgrSchema.format_field_line(kind, token, dtype, definition, seq)
        top, _, bottom = MgrSchema.split_around_field_line(kind, token)
        final          = MgrSchema.splice_fields_list(top, new_line, bottom)
        MgrSchema.write_file(MgrSchema.FIELDS_FILE, final)

    @staticmethod
    def remove_from_SchemaFlds(kind, token):
        """Drop this (kind, token)'s line from _SchemaFlds.py entirely — no replacement."""
        MgrSchema.backup_file(MgrSchema.FIELDS_FILE)
        top, old_line, bottom = MgrSchema.split_around_field_line(kind, token)
        final = MgrSchema.splice_fields_list(top, None, bottom)
        MgrSchema.write_file(MgrSchema.FIELDS_FILE, final)

    @staticmethod
    def split_around_field_lineOLD(kind, token):
        """(top_lines, matched_line_or_None, bottom_lines) split on this (kind, token)'s
           line. top/bottom are everything above/below it; matched line is excluded from both."""
        file_text = MgrSchema.read_file(MgrSchema.FIELDS_FILE)
        lines     = file_text.splitlines(keepends=True)
        needle    = f"{kind:<9s}{token:<10s}"
        for i, line in enumerate(lines):
            if needle in line: return lines[:i], line, lines[i + 1:]
        return lines, None, []


    @staticmethod
    def split_around_field_line(kind, token):
        """(top_lines, matched_line_or_None, bottom_lines) split on this (kind, token)'s
           line. top/bottom are everything above/below it; matched line is excluded from both."""
        file_text = MgrSchema.read_file(MgrSchema.FIELDS_FILE)
        lines     = file_text.splitlines(keepends=True)
        needle    = f"{kind:<9s}{token:<10s}"
        for i, line in enumerate(lines):
            if needle in line: return lines[:i], line, lines[i + 1:]
        end = MgrSchema.find_schema_list_end(lines, MgrSchema.find_schema_list_start(lines, "FIELDS"))    # NEW
        return lines[:end], None, lines[end:]

    @staticmethod
    def splice_fields_list(top, new_line, bottom):
        """Rejoin top + [new_line] + bottom (new_line=None means just drop it),
           inserting before the closing ']' when there's no bottom to anchor on."""
        entry = [] if new_line is None else [f"        {new_line!r},\n"]
        if bottom: return ''.join(top + entry + bottom)
        for i in range(len(top) - 1, -1, -1):
            if ']' in top[i]: return ''.join(top[:i] + entry + top[i:])
        return ''.join(top + entry)

    def format_field_line(kind, token, dtype, definition, seq=None):
        """'kind  token  dtype  seq  definition', tightly padded."""
        if seq is None: seq = MgrSchema.DEFAULT_SEQ.get(kind, 50)
        return f"{kind:<9s}{token:<10s}{dtype:<9s}{str(seq):<6s}{definition}"

    @staticmethod
    def parse_field_line(line):
        """'kind  token  dtype  [seq]  definition' → (kind, token, definition, dtype, seq).
           If 4th token is numeric it's seq; otherwise it's the start of definition."""
        parts = line.split(maxsplit=4)
        kind, token, dtype = parts[0], parts[1], parts[2]
        if len(parts) >= 4 and parts[3].isdigit():
            seq        = int(parts[3])
            definition = parts[4].strip() if len(parts) > 4 else ""
        else:
            seq        = MgrSchema.DEFAULT_SEQ.get(kind, 50)
            definition = parts[3].strip() if len(parts) > 3 else ""
            if len(parts) > 4: definition = (parts[3] + " " + parts[4]).strip()
        return kind, token, definition, dtype, seq

    @staticmethod
    def seq_for(kind, token):
        """Seq from _registry, or default for the kind if not found."""
        rows = BbDB.query("SELECT seq FROM _registry WHERE kind=? AND token=?", (kind, token))
        if rows and rows[0][0] is not None: return rows[0][0]
        return MgrSchema.DEFAULT_SEQ.get(kind, 50)


    @staticmethod
    def key_tokens():
        """All _registry tokens with kind='Key', plus GD (auto-injected, never a _registry row)."""
        rows = BbDB.query("SELECT token FROM _registry WHERE kind='Key'")
        return frozenset(r[0] for r in rows) | {"GD"}

    @staticmethod
    def sync_tracks_to_db():
        import importlib
        from ipui._forms.Baseball import _SchemaFlds
        importlib.reload(_SchemaFlds)
        for gd, track, tbl in getattr(_SchemaFlds._SchemaFlds, "TRACKS", []):
            BbDB.execute("INSERT OR IGNORE INTO _track_tables (GD, track, tbl) VALUES (?,?,?)",
                         (gd, track, tbl))

    # MgrSchema.py method: tracks_replace_table  NEW: full replace table's track assignments, then mirror file
    @staticmethod
    def tracks_replace_table(tbl, tracks):
        BbDB.execute("DELETE FROM _track_tables WHERE tbl=?", (tbl,))
        for track in tracks or []:
            BbDB.execute("INSERT OR IGNORE INTO _track_tables (GD, track, tbl) VALUES (?,?,?)",
                         (MgrDT.today_gd(), track, tbl))
        MgrSchema.write_tracks_from_db()

    @staticmethod
    def track_add_table(track, tbl):
        if not track or not tbl: return
        BbDB.execute("INSERT OR IGNORE INTO _track_tables (GD, track, tbl) VALUES (?,?,?)",
                     (MgrDT.today_gd(), track, tbl))
        MgrSchema.write_tracks_from_db()

    @staticmethod
    def write_tracks_from_db():
        rows = BbDB.query("SELECT GD, track, tbl FROM _track_tables ORDER BY track, tbl")
        MgrSchema.backup_file(MgrSchema.FIELDS_FILE)
        body = [f"        ({int(gd)}, {track!r}, {tbl!r}),\n" for gd, track, tbl in rows]
        MgrSchema.write_schema_list("TRACKS", body)

    # MgrSchema.py method: write_schema_list  NEW: replace or append a class-level list in _SchemaFlds.py
    @staticmethod
    def write_schema_list(list_name, body_lines):
        file_text = MgrSchema.read_file(MgrSchema.FIELDS_FILE)
        lines     = file_text.splitlines(keepends=True)
        start     = MgrSchema.find_schema_list_start(lines, list_name)
        block     = [f"\n    {list_name} = [\n"] + body_lines + ["    ]\n"]
        if start is None:
            MgrSchema.write_file(MgrSchema.FIELDS_FILE, file_text.rstrip() + "\n" + ''.join(block))
            return
        end = MgrSchema.find_schema_list_end(lines, start)
        MgrSchema.write_file(MgrSchema.FIELDS_FILE, ''.join(lines[:start] + block + lines[end + 1:]))


    # MgrSchema.py method: find_schema_list_start  NEW: find class-level list assignment
    @staticmethod
    def find_schema_list_start(lines, list_name):
        needle = f"{list_name} = ["
        for i, line in enumerate(lines):
            if line.strip().startswith(needle): return i
        return None


    # MgrSchema.py method: find_schema_list_end  NEW: find matching closing bracket for simple list block
    @staticmethod
    def find_schema_list_end(lines, start):
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("[") - lines[i].count("]")
            if i > start and depth <= 0: return i
        return start

    # ══════════════════════════════════════════════════════════════
    # ETL VIEW CLONING
    # ══════════════════════════════════════════════════════════════
    # MgrSchema.py method: clone_etl_views_entrypoint  New: orchestrate ETL view cloning

    @staticmethod
    def clone_etl_views_ENTRYPOINT(source, new):
        """Clone all ETL views (updates, mixins, pull) from source table to new table."""
        for prefix in MgrSchema.CLONE_VERBATIM_PREFIXES:
            MgrSchema.clone_verbatim_view(prefix, source, new)
        MgrSchema.clone_mixin_views(source, new)
        MgrSchema.clone_pull_view(source, new)


    def clone_verbatim_view(prefix, source, new):
        """Clone {prefix}_{source} → {prefix}_{new}, updating table references."""
        sql = MgrSchema.view_select_sql(f"{prefix}_{source}")
        if not sql: return
        sql = sql.replace(source, new)                                                # NEW
        MgrSchema.save_view(f"{prefix}_{new}", sql)

    # MgrSchema.py method: clone_mixin_views  New: copy all mixin views for a table
    @staticmethod
    def clone_mixin_views(source, new):
        """Clone every pull_{source}_mixin_{desc} → pull_{new}_mixin_{desc}."""
        prefix = f"pull_{source}_mixin_"
        rows   = BbDB.query("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE ?", (f"{prefix}%",))
        for (name,) in rows:
            desc = name[len(prefix):]
            sql  = MgrSchema.view_select_sql(name)
            if sql: MgrSchema.save_view(f"pull_{new}_mixin_{desc}", sql)

    # MgrSchema.py method: clone_pull_view  New: copy pull view, updating mixin references
    @staticmethod
    def clone_pull_view(source, new):
        """Clone pull_{source} → pull_{new}, updating mixin references in SQL."""
        sql = MgrSchema.view_select_sql(f"pull_{source}")
        if not sql: return
        sql = sql.replace(f"pull_{source}_mixin_", f"pull_{new}_mixin_")
        MgrSchema.save_view(f"pull_{new}", sql)

    # MgrSchema.py method: view_select_sql  New: extract bare SELECT from sqlite_master
    @staticmethod
    def view_select_sql(view_name):
        """Bare SELECT from sqlite_master, or None if view doesn't exist."""
        import re
        rows = BbDB.query("SELECT sql FROM sqlite_master WHERE type='view' AND name=?", (view_name,))
        if not rows or not rows[0][0]: return None
        match = re.search(r'\bAS\b\s+', rows[0][0], re.IGNORECASE)
        if not match: return None
        return rows[0][0][match.end():]


    @staticmethod
    def delete_table_entrypointOLD(table_name):
        """Delete a table: drop views, remove from _SchemaTbl.py, drop from DB."""
        MgrSchema.delete_table_views(table_name)
        MgrSchema.remove_from_tbl_schema(table_name)
        BbDB.drop_table(table_name)
        BbDB.execute("DELETE FROM _summary WHERE tbl = ?", (table_name,))
        BbDB.execute("DELETE FROM _track_tables WHERE tbl = ?", (table_name,))
        MgrSchema.write_tracks_from_db()
        BbDB.log(table_name, "deleted (table + views + schema)")

    def delete_table_entrypoint(table_name):
        """Delete a table: drop views, remove from _SchemaTbl.py, drop from DB."""
        MgrSchema.delete_table_views(table_name)
        MgrSchema.remove_from_tbl_schema(table_name)
        import importlib                                                          # NEW
        from ipui._forms.Baseball import _SchemaTbl                               # NEW
        importlib.reload(_SchemaTbl)                                              # NEW
        BbDB.drop_table(table_name)
        BbDB.execute("DELETE FROM _summary WHERE tbl = ?", (table_name,))
        BbDB.execute("DELETE FROM _track_tables WHERE tbl = ?", (table_name,))
        MgrSchema.write_tracks_from_db()
        BbDB.log(table_name, "deleted (table + views + schema)")
    # MgrSchema.py method: delete_table_views  New: find and delete all associated views
    @staticmethod
    def delete_table_views(table_name):
        """Delete all pull, mixin, and update views associated with this table."""
        for prefix in MgrSchema.CLONE_VERBATIM_PREFIXES:
            MgrSchema.delete_one_view(f"{prefix}_{table_name}")
        rows = BbDB.query("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE ?",
                          (f"pull_{table_name}_mixin_%",))
        for (name,) in rows:
            MgrSchema.delete_one_view(name)
        MgrSchema.delete_one_view(f"pull_{table_name}")

    # MgrSchema.py method: delete_one_view  New: drop from DB + remove from _SchemaViews.py
    @staticmethod
    def delete_one_view(view_name):
        """Drop a view from the DB and remove its method from _SchemaViews.py."""
        BbDB.execute(f"DROP VIEW IF EXISTS {view_name}")
        bounds = MgrSchema.find_method_bounds(MgrSchema.read_file(MgrSchema.VIEWS_FILE), view_name)
        if bounds is None: return
        MgrSchema.backup_file(MgrSchema.VIEWS_FILE)
        lines      = MgrSchema.read_file(MgrSchema.VIEWS_FILE).splitlines(keepends=True)
        start, end = bounds
        MgrSchema.write_file(MgrSchema.VIEWS_FILE, ''.join(lines[:start] + lines[end:]))

    # MgrSchema.py method: remove_from_tbl_schema  New: strip table block from _SchemaTbl.py
    @staticmethod
    def remove_from_tbl_schema(table_name):
        """Remove this table's block from _SchemaTbl.py."""
        file_text         = MgrSchema.read_file(MgrSchema.TABLES_FILE)
        remove, first_idx = MgrSchema.find_table_block_lines(file_text, table_name)
        if not remove: return
        MgrSchema.backup_file(MgrSchema.TABLES_FILE)
        lines = file_text.splitlines(keepends=True)
        MgrSchema.write_file(MgrSchema.TABLES_FILE,
                             ''.join(line for i, line in enumerate(lines) if i not in remove))