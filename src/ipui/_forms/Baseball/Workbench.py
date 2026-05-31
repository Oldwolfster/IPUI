# ════════════════════════════════════════════════════════════════════════════════
# Workbench.py  NEW FILE  —  Per-table command center.
# Phase 1: read-only column grid + source viewer. Controls are placeholders.
# Pipe's Workbench button calls load_table() to focus this tab on one table.
# ════════════════════════════════════════════════════════════════════════════════

import inspect
from ipui import *
from ipui._forms.Baseball.BB import BB


class Workbench(_BaseTab):
    """Per-table command center — inspect columns, see source, (later) add/delete."""


    # ══════════════════════════════════════════════════════════════
    # SETUP
    # ══════════════════════════════════════════════════════════════

    def ip_setup_early(self, ip):
        self.current_table  = None

        self.analysis_cache = {}                                             # {col_name: (min, max, avg, nulls)} — populated by Analyze in Phase 2
        self.private_form_type = "TEXT"                                      # NEW
        self.private_form_pk   = False                                       # NEW


    # ══════════════════════════════════════════════════════════════
    # PUBLIC ENTRY — Pipe calls this. Sets the focus table and rebuilds.
    # ══════════════════════════════════════════════════════════════

    def load_table(self, tbl):
        self.current_table  = tbl
        self.analysis_cache = {}                                             # fresh table → fresh cache
        self.refresh_all_panes()


    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS — three panes per TAB_LAYOUT in FormBaseball.
    # ══════════════════════════════════════════════════════════════

    def columns(self, parent):
        Title(parent, "Columns", glow=True)
        self.build_table_header(parent)
        self.build_columns_grid(parent)

    def controls(self, parent):
        Title(parent, "Actions", glow=True)
        self.build_action_buttons(parent)

    def source(self, parent):
        Title(parent, "Source", glow=True)
        self.build_source_box(parent)


    # ══════════════════════════════════════════════════════════════
    # COLUMNS PANE — header + PRAGMA-driven grid
    # ══════════════════════════════════════════════════════════════

    def build_table_header(self, parent):
        tbl   = self.current_table
        layer = BB.layer_of(tbl) if tbl else None
        rows  = BB.row_count(tbl) if tbl else 0
        text  = f"Table: {tbl or '—'}    Layer: {layer or '—'}    Rows: {rows:,}"
        Detail(parent, text, name="lbl_wb_header")

    def build_columns_grid(self, parent):
        card = CardCol(parent, name="card_wb_columns_grid", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_wb_columns")
        self.populate_columns_grid()

    def populate_columns_grid(self):
        grid = self.form.widgets.get("grid_wb_columns")
        if not grid: return
        if not self.current_table:
            grid.set_data([["—"]], columns=["No table selected"])
            return
        rows = self.scan_columns(self.current_table)
        cols = ["#", "Name", "Type", "PK", "Min", "Max", "Avg", "Nulls"]
        grid.set_data(rows, columns=cols)

    def scan_columns(self, tbl):
        info = BB.query(f"PRAGMA table_info({tbl})")
        out  = []
        for cid, name, ctype, _notnull, _dflt, pk in info:
            stats = self.analysis_cache.get(name, ("—", "—", "—", "—"))
            out.append([cid + 1, name, ctype or "—", "✓" if pk else "", *stats])
        return out


    # ══════════════════════════════════════════════════════════════
    # CONTROLS PANE — placeholder buttons wired to passme (Phase 2+)
    # ══════════════════════════════════════════════════════════════

    def build_action_buttons(self, parent):
        Button(parent, "Add Column",     on_click=self.passme, flex_width=1)
        Button(parent, "Delete Selected",on_click=self.passme, flex_width=1)
        Button(parent, "Analyze",        on_click=self.passme, flex_width=1, color_bg=Style.COLOR_BUTTON_ACCENT)
        Button(parent, "Refresh",        on_click=self.handle_refresh_clicked, flex_width=1)

    def handle_refresh_clicked(self):
        self.refresh_all_panes()                                             # only one wired today; others land in later phases

    def passme(self): pass


    # ══════════════════════════════════════════════════════════════
    # SOURCE PANE — Python method (raw) OR view DDL (etl/feet/forest)
    # ══════════════════════════════════════════════════════════════

    def build_source_box(self, parent):
        card = CardCol(parent, name="card_wb_source", flex_height=1, pad=0)
        text = self.fetch_source_text()
        CodeBox(card, text, name="code_wb_source")

    def build_source_box(self, parent):
        card = CardCol(parent, scroll_v=True, flex_height=1, pad=0)
        CodeBox(card, data=self.fetch_source_text(), name="code_wb_source")

    def fetch_source_text(self):
        tbl = self.current_table
        if not tbl: return "-- No table selected\n"
        layer = BB.layer_of(tbl)
        body  = self.fetch_raw_source(tbl) if layer == "raw" else self.fetch_view_source(tbl)
        return body if body.endswith("\n") else body + "\n"

    def fetch_raw_source(self, tbl):
        pipe   = self.form.get_tab("Pipe")                                   # raw pull methods live on Pipe
        method = getattr(pipe, f"pull_{tbl}", None) if pipe else None
        if not method: return f"-- No pull_{tbl}() method found on Pipe"
        try:               return inspect.getsource(method)
        except Exception as e: return f"-- Could not read source: {e}"

    def fetch_view_source(self, tbl):
        rows = BB.query(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type='view' AND name LIKE ? ORDER BY name",
            (f"pull_{tbl}%",),
        )
        if not rows:
            return (f"-- No views found matching 'pull_{tbl}%'\n"
                    f"-- Create one with:\n"
                    f"-- CREATE VIEW pull_{tbl}_01 AS\n"
                    f"--     SELECT ... FROM ...")
        return ";\n\n".join(r[1] for r in rows if r[1]) + ";"


    # ══════════════════════════════════════════════════════════════
    # REFRESH ALL — rebuild all three panes via set_pane
    # ══════════════════════════════════════════════════════════════

    def refresh_all_panes(self):
        self.set_pane(0, self.columns)
        self.set_pane(1, self.controls)
        self.set_pane(2, self.source)


# ════════════════════════════════════════════════════════════════════════════════
# Workbench.py  —  Add Column form (UI only, all submits/toggles are passme stubs)
# All four existing buttons stay as-is. New form appears BELOW them.
# Type buttons use the Documentation.py toggle pattern (active = CTA color).
# ════════════════════════════════════════════════════════════════════════════════

class deleteme:

    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: ip_setup_early  Update: seed form state
    # Add the three private_form_* lines after the existing two.
    # Anchor + insertion:
    #
    #     self.current_table  = None                                           # REFERENCE
    #     self.analysis_cache = {}                                             # REFERENCE
    #     self.private_form_type = "TEXT"                                      # NEW
    #     self.private_form_pk   = False                                       # NEW


    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: build_action_buttons  Update: append Add Column form
    # Existing 4 buttons untouched. New form follows.
    # ════════════════════════════════════════════════════════════════════════════

    def build_action_buttons(self, parent):
        Button(parent, "Add Column",     on_click=self.passme, flex_width=1)
        Button(parent, "Delete Selected",on_click=self.passme, flex_width=1)
        Button(parent, "Analyze",        on_click=self.passme, flex_width=1, color_bg=Style.COLOR_BUTTON_ACCENT)
        Button(parent, "Refresh",        on_click=self.handle_refresh_clicked, flex_width=1)
        Spacer(parent, height=16)
        self.build_add_column_form(parent)


    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: build_add_column_form  NEW: bottom-of-pane form
    # Name TextBox · Type button stack · # TextBox · PK toggle · Add submit.
    # ════════════════════════════════════════════════════════════════════════════

    def build_add_column_form(self, parent):
        Title(parent, "Add Column", glow=False)
        Detail(parent, "Name")
        TextBox(parent, name="txt_wb_new_col_name", flex_width=1)
        Detail(parent, "Type")
        self.build_type_buttons(parent)
        Detail(parent, "#  (optional position)")
        TextBox(parent, name="txt_wb_new_col_pos", flex_width=1)
        Spacer(parent, height=8)
        self.build_pk_toggle(parent)
        Spacer(parent, height=8)
        Button(parent, "Add", on_click=self.passme, flex_width=1, color_bg=Style.COLOR_BUTTON_CTA)


    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: build_type_buttons  NEW: 5-button mutually-exclusive stack
    # Active type uses CTA color; others use TAB_BG. Click → set state, rebuild pane.
    # Pattern mirrors Documentation.py's build_menu.
    # ════════════════════════════════════════════════════════════════════════════

    def build_type_buttons(self, parent):
        types = ["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"]
        for t in types:
            is_active = (t == self.private_form_type)
            color     = Style.COLOR_BUTTON_CTA if is_active else Style.COLOR_TAB_BG
            Button(parent, t, color_bg=color, flex_width=1,
                   on_click=lambda chosen=t: self.set_form_type(chosen))


    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: build_pk_toggle  NEW: single toggle button, label flips
    # ════════════════════════════════════════════════════════════════════════════

    def build_pk_toggle(self, parent):
        label = "✓ Primary Key" if self.private_form_pk else "☐ Primary Key"
        color = Style.COLOR_BUTTON_CTA if self.private_form_pk else Style.COLOR_TAB_BG
        Button(parent, label, color_bg=color, flex_width=1, on_click=self.toggle_form_pk)


    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: set_form_type  NEW: update state, rebuild controls pane
    # ════════════════════════════════════════════════════════════════════════════

    def set_form_type(self, chosen):
        self.private_form_type = chosen
        self.set_pane(1, self.controls)


    # ════════════════════════════════════════════════════════════════════════════
    # Workbench.py  method: toggle_form_pk  NEW: flip PK state, rebuild controls pane
    # ════════════════════════════════════════════════════════════════════════════

    def toggle_form_pk(self):
        self.private_form_pk = not self.private_form_pk
        self.set_pane(1, self.controls)