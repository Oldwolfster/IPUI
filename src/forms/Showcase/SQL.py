# SQL.py  NEW: SQL showcase tab — demonstrates PowerGrid with SQLDataSource

import sqlite3
from ipui import *

DB_PATH = r"src\ipui\assets\sample_db\rock_on_forever_claude.db"

PRESET_QUERIES = [
    ("All Runs",
     "SELECT run_id, batch_id, epoch_count, best_mae,\n"
     "       accuracy, runtime_seconds\n"
     "FROM batch_history\n"
     "WHERE epoch_count is not null\n"
     "ORDER BY best_mae ASC"),
    ("Top 20 by MAE",
     "SELECT run_id, batch_id, best_mae, accuracy,\n"
     "       optimizer, architecture\n"
     "FROM batch_history\n"
     "WHERE best_mae IS NOT NULL\n"
     "ORDER BY best_mae ASC LIMIT 20"),
    ("Optimizer Showdown",
     "SELECT optimizer,\n"
     "       COUNT(*) AS runs,\n"
     "       ROUND(MIN(best_mae),4) AS best,\n"
     "       ROUND(AVG(best_mae),4) AS avg_mae\n"
     "FROM batch_history\n"
     "GROUP BY optimizer\n"
     "ORDER BY avg_mae ASC"),
    ("Batch Summary",
     "SELECT s.batch_id, s.created_at,\n"
     "  (SELECT COUNT(*) FROM batch_history h\n"
     "   WHERE h.batch_id = s.batch_id) AS runs,\n"
     "  (SELECT ROUND(MIN(best_mae),4) FROM batch_history h\n"
     "   WHERE h.batch_id = s.batch_id) AS best_mae\n"
     "FROM batch_specs s\n"
     "ORDER BY s.created_at DESC"),
]


class SQL(_BaseTab):
    """Showcase tab demonstrating PowerGrid SQL capabilities."""

    def ip_setup_pane(self):
        self.current_query = PRESET_QUERIES[0][1]

    # ══════════════════════════════════════════════════════════════
    # LEFT PANE — table browser + presets
    # ══════════════════════════════════════════════════════════════

    def tables(self, parent):
        Title(parent, "Database", glow=True)

        sub = CardCol(parent)
        Heading(sub, "Tables")
        self.build_table_list(sub)

        Spacer(parent)
        sub = CardCol(parent)
        Heading(sub, "Preset Queries")
        for name, sql in PRESET_QUERIES:
            btn = Button(sub, name,
                         color_bg=Style.COLOR_TAB_BG,
                         width_flex=1)
            btn.on_click = self.make_preset_click(sql)

    def build_table_list(self, parent):
        try:
            conn   = sqlite3.connect(DB_PATH)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception:
            Body(parent, "Could not connect to database.")
            Detail(parent, DB_PATH)
            return
        for t in tables:
            btn = Button(parent, t,
                         color_bg=Style.COLOR_PANEL_BG,
                         width_flex=1)
            btn.on_click = self.make_table_click(t)

    def make_table_click(self, table_name):
        def clicked():
            sql = f"SELECT * FROM {table_name}"
            self.run_query(sql)
        return clicked

    def make_preset_click(self, sql):
        def clicked():
            self.run_query(sql)
        return clicked

    # ══════════════════════════════════════════════════════════════
    # MIDDLE PANE — query display
    # ══════════════════════════════════════════════════════════════

    def query(self, parent):
        Title(parent, "Query", glow=True)

        #CodeBox(parent,                data=self.current_query,                name="code_sql",                height_flex=1)
        TextArea(parent,name="code_sql",                height_flex=1)

        row = Row(parent)
        Button(row, "Run Query",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=self.on_run_clicked)

        Body(parent, "", name="lbl_sql_status")

    def on_run_clicked(self):
        if self.current_query:
            self.run_query(self.current_query)

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE — results grid
    # ══════════════════════════════════════════════════════════════

    def results(self, parent):
        Title(parent, "Results", glow=True)
        card = CardCol(parent, height_flex=True)
        PowerGrid(card, name="grid_sql_results")

    # ══════════════════════════════════════════════════════════════
    # QUERY EXECUTION
    # ══════════════════════════════════════════════════════════════

    def run_query(self, sql):
        self.current_query = sql
        self.update_query_box(sql)
        lbl = self.form.widgets.get("lbl_sql_status")
        try:
            conn   = sqlite3.connect(DB_PATH)
            cursor = conn.execute(sql)
            cols   = [desc[0] for desc in cursor.description]
            rows   = [list(r) for r in cursor.fetchall()]
            conn.close()
            self.populate_grid(cols, rows)
            if lbl:
                lbl.set_text(f"{len(rows)} rows returned")
        except Exception as e:
            if lbl:
                lbl.set_text(f"Error: {e}")

    def update_query_box(self, sql):
        cb = self.form.widgets.get("code_sql")
        if cb:
            cb.set_text(sql)

    def populate_grid(self, cols, rows):
        grid = self.form.widgets.get("grid_sql_results")
        if not grid:
            return
        if not rows:
            grid.set_data([["No results"]])
            return
        grid.set_data(rows, columns=cols)