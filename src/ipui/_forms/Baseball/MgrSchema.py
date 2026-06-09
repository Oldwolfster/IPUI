# MgrSchema.py  NEW FILE — single authority for _SchemaTbl.py and _SchemaViews.py

from pathlib import Path
import shutil
from ipui._forms.Baseball.BbDB import BbDB
from ipui.utils.EZ import EZ

class MgrSchema:
    """Manages schema files and DB sync. Stateless — the files ARE the state."""
    VIEWS_FILE  = Path(__file__).parent / "_SchemaViews.py"
    TABLES_FILE = Path(__file__).parent / "_SchemaTbl.py"
    BACKUP_DIR  = Path(__file__).parent / "docs" / "backup"

    # ══════════════════════════════════════════════════════════════
    # CREATE TABLE — dispatcher
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def create_table(table_name, columns):
        table_name    = MgrSchema.validate_name(table_name)
        MgrSchema     . insert_table_schema(table_name, columns)
        stub_sql      = MgrSchema.build_stub_select(table_name, columns)
        MgrSchema     . save_view(f"pull_{table_name}", stub_sql)
        MgrSchema     . drop_and_rebuild_table(table_name)

        BbDB.log      ( table_name, "table created")

    @staticmethod
    def create_table(table_name, columns):
        table_name    = MgrSchema.validate_name(table_name)
        MgrSchema     . replace_table_schema(table_name, columns)
        stub_sql      = MgrSchema.build_stub_select(table_name, columns)
        MgrSchema     . save_view(f"pull_{table_name}", stub_sql)
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
    def replace_table_schema(table_name, columns):
        """Replace a table's block in _SchemaTbl.py, rebuild DB, update summary."""
        MgrSchema     . backup_file(MgrSchema.TABLES_FILE)
        original      = MgrSchema.read_file(MgrSchema.TABLES_FILE)
        new_block     = MgrSchema.generate_table_block(table_name, columns)
        final         = MgrSchema.swap_table_block(original, table_name, new_block)
        MgrSchema     . validate_no_tables_lost(original, final, table_name)
        MgrSchema     . write_file(MgrSchema.TABLES_FILE, final)
        BbDB          . rebuild_table(table_name)
        BbDB          . update_summary(table_name)
        BbDB          . log(table_name, "replaced in _SchemaTbl.py")

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
    def build_stub_select(table_name, columns):
        parts = ["0 AS GD"]
        if BbDB.layer_of(table_name) == "feet":
            parts.append("0 AS TS")
        for col in columns:
            val   = "''" if col['type'] == 'TEXT' else "0.0" if col['type'] == 'REAL' else "0"
            parts.append(f"{val:<45s}AS {col['name']}")
        return "SELECT\n    " + ",\n    ".join(parts)
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
        indented_sql = "\n".join("            " + line for line in sql_lines)
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