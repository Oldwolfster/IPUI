# FileManager.py  NEW FILE — Safe file operations for the Designer

import shutil
from pathlib import Path
from datetime import datetime


class FileManager:

    # ══════════════════════════════════════════════════════════════
    # BACKUP
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def backup(file_path):
        path = Path(file_path)
        if not path.exists():
            return None
        stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_path = path.with_suffix(f".{stamp}.bak")
        shutil.copy2(path, bak_path)
        return bak_path

    # ══════════════════════════════════════════════════════════════
    # TAB LAYOUT — rewrite the dict in the form file
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def save_TAB_LAYOUT(form_file_path, TAB_LAYOUT):
        path  = Path(form_file_path)
        text  = path.read_text(encoding="utf-8")
        start = text.find("TAB_LAYOUT")
        if start < 0:
            return False
        brace = text.find("{", start)
        if brace < 0:
            return False
        end   = FileManager.find_matching_brace(text, brace)
        if end < 0:
            return False
        indent   = FileManager.detect_indent(text, start)
        new_dict = FileManager.serialize_TAB_LAYOUT(TAB_LAYOUT, indent)
        FileManager.backup(path)
        updated  = text[:start] + f"TAB_LAYOUT = {new_dict}" + text[end + 1:]
        path.write_text(updated, encoding="utf-8")
        return True

    @staticmethod
    def find_matching_brace(text, open_pos):
        depth = 0
        for i in range(open_pos, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return i
        return -1

    @staticmethod
    def detect_indent(text, pos):
        line_start = text.rfind("\n", 0, pos) + 1
        indent     = ""
        for ch in text[line_start:]:
            if ch in " \t":
                indent += ch
            else:
                break
        return indent

    @staticmethod
    def serialize_TAB_LAYOUT(TAB_LAYOUT, indent):
        inner = indent + "    "
        lines = ["{"]
        items = list(TAB_LAYOUT.items())
        for i, (tab_name, entries) in enumerate(items):
            parts = []
            for entry in entries:
                if isinstance(entry, tuple):
                    name, weight = entry
                    parts.append(f'("{name}", {weight})')
                else:
                    parts.append(f'"{entry}"')
            joined = ", ".join(parts)
            comma  = "," if i < len(items) - 1 else ","
            lines.append(f'{inner}"{tab_name}"{" " * max(1, 16 - len(tab_name))}: [{joined}]{comma}')
        lines.append(f"{indent}}}")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # PANE FILE — generate, append, deprecate
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def generate_pane_file(file_path, tab_name, methods):
        path  = Path(file_path)
        lines = [
            "from ipui import *\n\n\n",
            f"class {tab_name}(_BaseTab):\n",
        ]
        for entry in methods:
            m = entry[0] if isinstance(entry, tuple) else entry
            lines.append(f"\n    def {m}(self, parent):\n")
            lines.append(f"        Body(parent, \"Pane: {m}\")\n")
            lines.append(f"        Body(parent, \"Add content here!\")\n")
        path.write_text("".join(lines), encoding="utf-8")

    @staticmethod
    def append_method(file_path, method_name):
        path     = Path(file_path)
        FileManager.backup(path)
        existing = path.read_text(encoding="utf-8")
        stub = (
            f"\n\n    def {method_name}(self, parent):\n"
            f"        Body(parent, \"Pane: {method_name}\")\n"
            f"        Body(parent, \"Add content here!\")\n"
        )
        path.write_text(existing + stub, encoding="utf-8")

    @staticmethod
    def deprecate_method(file_path, method_name):
        path = Path(file_path)
        if not path.exists():
            return False
        FileManager.backup(path)
        text    = path.read_text(encoding="utf-8")
        old     = f"def {method_name}("
        new     = f"def IPUI_DEPRECATED_{method_name}("
        if old not in text:
            return False
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return True


    @staticmethod
    def inject_into_method(file_path, method_name, snippet):
        path  = Path(file_path)
        FileManager.backup(path)
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

        method_line = None
        insert_at   = None
        indent      = None

        for i, line in enumerate(lines):
            if f"def {method_name}(" in line:
                method_line = i
                indent = len(line) - len(line.lstrip())
                continue
            if method_line is not None and i > method_line:
                stripped = line.strip()
                if stripped == "":
                    insert_at = i
                    continue
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= indent and stripped != "":
                    insert_at = i
                    break
                insert_at = i + 1

        if insert_at is None and method_line is not None:
            insert_at = len(lines)

        if insert_at is not None:
            lines.insert(insert_at, snippet + "\n")
            path.write_text("".join(lines), encoding="utf-8")
            return True
        return False