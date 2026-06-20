# MgrBackup.py  Update — _SchemaFlds.py is now a true two-way mirror of _registry's vocab rows,
#   same relationship _SchemaTbl.py has with every table's SHAPE. Either side can add a field:
#   the DB tab's Save/Delete write straight to _registry AND keep _SchemaFlds.py in sync; a
#   hand-typed line in _SchemaFlds.py gets pulled into _registry on the next sync_fields_to_db().
#   The (kind, token) PK makes "create if missing, never touch if present" free — INSERT OR IGNORE.
#   _SchemaFlds.py always exists, even empty, exactly like _SchemaTbl.py — dropping the DB never
#   touches it.
import re
import shutil
from pathlib import Path
from ipui._forms.Baseball.BbDB import BbDB
from ipui.utils.EZ import EZ


class MgrBackup:

    FIELDS_FILE = Path(__file__).parent / "_SchemaFlds.py"
    BACKUP_DIR  = Path(__file__).parent / "docs" / "backup"

    # ── DB tab → file: keep _SchemaFlds.py in sync with a Save / Delete ────────
    @classmethod
    def save_field(cls, kind, token, definition, dtype):
        """Write/update this (kind, token)'s line in _SchemaFlds.py. Called right after
           DB.py's save_entry writes the same row to _registry, so the file stays a true mirror."""
        if not dtype: EZ.err(f"({kind}, {token}) has no dtype — every field needs one.")
        cls.backup_file(cls.FIELDS_FILE)
        original = cls.read_file(cls.FIELDS_FILE)
        new_line = cls.format_field_line(kind, token, dtype, definition)
        final    = cls.replace_field_line(original, kind, token, new_line)
        cls.write_file(cls.FIELDS_FILE, final)

    @classmethod
    def delete_field(cls, kind, token):
        """Remove this (kind, token)'s line from _SchemaFlds.py. Called right after DB.py's
           delete_entry removes the same row from _registry — otherwise the next sync brings it back."""
        original = cls.read_file(cls.FIELDS_FILE)
        final    = cls.replace_field_line(original, kind, token, None)
        cls.write_file(cls.FIELDS_FILE, final)

    # ── file → DB: call once at startup, after _registry exists ────────────────
    @classmethod
    def sync_fields_to_db(cls):
        """Insert every _SchemaFlds.py line into _registry that isn't already there, in one
           batch. The (kind, token) PK does the "create if missing" work — OR IGNORE silently
           skips any row that already exists, so live DB edits are never overwritten."""
        import importlib
        from ipui._forms.Baseball import _SchemaFlds
        importlib.reload(_SchemaFlds)
        rows = [cls.parse_field_line(line) for line in _SchemaFlds._SchemaFlds.FIELDS]
        if not rows: return
        sql = "INSERT OR IGNORE INTO _registry (kind, token, definition, dtype) VALUES (?,?,?,?)"
        BbDB.execute_many(sql, rows)

    # ══════════════════════════════════════════════════════════════
    # _SchemaFlds.py LINE BUILD / FIND / REPLACE
    # ══════════════════════════════════════════════════════════════
    @classmethod
    def format_field_line(cls, kind, token, dtype, definition):
        """'kind  token  dtype  definition', tightly padded — kind/token/dtype never contain
           a space, so they're always readable as the line's first 3 whitespace tokens."""
        return f"{kind:<9s}{token:<10s}{dtype:<9s}{definition}"

    @classmethod
    def find_field_line(cls, file_text, kind, token):
        """Index of the FIELDS-list line whose (kind, token) matches, or None if absent."""
        needle = f"{kind:<9s}{token:<10s}"
        for i, line in enumerate(file_text.splitlines()):
            if needle in line: return i
        return None

    @classmethod
    def replace_field_line(cls, file_text, kind, token, new_line):
        """Swap this (kind, token)'s line for new_line (append if new), or drop it if
           new_line is None. Every other line is left exactly as it is."""
        lines = file_text.splitlines(keepends=True)
        idx   = cls.find_field_line(file_text, kind, token)
        if new_line is None:
            if idx is not None: lines.pop(idx)
            return ''.join(lines)
        entry = f"        {new_line!r},\n"
        if idx is not None:
            lines[idx] = entry
            return ''.join(lines)
        for i in range(len(lines) - 1, -1, -1):
            if ']' in lines[i]: return ''.join(lines[:i] + [entry] + lines[i:])
        return file_text

    @classmethod
    def parse_field_line(cls, line):
        """'kind  token  dtype  definition' → (kind, token, definition, dtype). kind/token/dtype
           can never contain a space, so they're always the line's first 3 whitespace tokens;
           the definition is everything after, free text, spaces and all."""
        kind, token, dtype, definition = line.split(maxsplit=3)
        return kind, token, definition.strip(), dtype

    # ══════════════════════════════════════════════════════════════
    # FILE I/O — same pattern as MgrSchema
    # ══════════════════════════════════════════════════════════════
    @classmethod
    def backup_file(cls, file_path):
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if file_path.exists(): shutil.copy2(file_path, cls.BACKUP_DIR / f"{file_path.name}.bak")

    @classmethod
    def read_file(cls, file_path):
        if not file_path.exists():
            cls.write_file(file_path, "\nclass _SchemaFlds:\n\n    FIELDS = [\n\n    ]\n")
        return file_path.read_text(encoding='utf-8')

    @classmethod
    def write_file(cls, file_path, file_text):
        tmp = file_path.with_suffix('.py.tmp')
        tmp.write_text(file_text, encoding='utf-8')
        shutil.move(str(tmp), str(file_path))