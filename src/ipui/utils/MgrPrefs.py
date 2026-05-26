# ═══════════════════════════════════════════════════════════════════════════
# MgrPrefs.py  NEW   Generic per-app JSON prefs store for IPUI/NeuroForge tabs.
# ═══════════════════════════════════════════════════════════════════════════
# Usage:
#     prefs = MgrPrefs("neuroforge")          # → ~/.neuroforge/prefs.json
#     data  = prefs.load("sql")               # → {} if missing/corrupt
#     prefs.save("sql", {"db_path": "..."})   # writes immediately
#
# Design notes:
#   - One file per app folder, nested by section key, so multiple tabs can
#     share without colliding.  prefs.json = {"sql": {...}, "forge": {...}}
#   - Corruption is silent → reset to {}.  Prefs aren't user-authored content.
#   - Write-on-change, no lifecycle hook to wire up.
#   - Pure stdlib; no framework coupling.  Lives outside _BaseWidget on purpose
#     so any module (or non-IPUI code) can use it.
# ═══════════════════════════════════════════════════════════════════════════

import os
import json


class MgrPrefs:

    def __init__(self, app_folder_name):
        # app_folder_name is the name *without* the dot, e.g. "neuroforge".
        # We add the dot ourselves so callers can't accidentally pass "/etc"
        # or similar and clobber something real.
        self.folder = os.path.join(os.path.expanduser("~"), f".{app_folder_name}")
        self.path   = os.path.join(self.folder, "prefs.json")

    def load(self, section):
        # Returns dict for the requested section, or {} on any failure.
        # Never raises — the whole point is silent fallback to defaults.
        data = self.read_all()
        return data.get(section, {}) if isinstance(data, dict) else {}

    def save(self, section, values):
        # Merges `values` into the named section and writes the full file.
        # Other sections (e.g. another tab's prefs) are preserved untouched.
        data           = self.read_all() or {}
        data[section]  = values
        self.write_all(data)

    def read_all(self):
        # Internal — full-file read.  Returns {} if file missing or unparseable.
        if not os.path.exists(self.path): return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def write_all(self, data):
        # Internal — full-file write.  Creates the app folder on demand.
        # Swallows OSError (read-only disk, permission denied, etc.) since
        # a failed pref-save should never crash the app.
        try:
            os.makedirs(self.folder, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass
