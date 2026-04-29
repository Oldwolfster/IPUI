# SQL.py  Update: open-or-create DB picker + schema-aware table click + column tooltips

import os
import sqlite3
import time
import tkinter as tk
from tkinter import filedialog
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

    def ip_setup(self, ip):
        self.current_query  = PRESET_QUERIES[0][1]
        self.db_path        = DB_PATH
        self.last_db_folder = os.path.dirname(os.path.abspath(self.db_path))

    # ══════════════════════════════════════════════════════════════
    # LEFT PANE — table browser + presets
    # ══════════════════════════════════════════════════════════════

    def tables(self, parent):
        Title(parent, "Database", glow=True)

        row = Row(parent)
        self.private_btn_db = Button(
            row,
            os.path.basename(self.db_path),
            color_bg   = Style.COLOR_TAB_BG,
            width_flex = 1,
            on_click   = self.handle_pick_db_clicked
        )
        self.private_btn_db.tooltip = self.db_path

        sub = CardCol(parent, name="card_sql_tables", height_flex=True)
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
            tables = self.get_table_names()
        except Exception as e:
            Body  (parent, "Could not connect to database.")
            Detail(parent, str(e))
            Detail(parent, self.db_path)
            return

        if not tables:
            Body  (parent, "No tables found.")
            Detail(parent, self.db_path)
            return

        for t in tables:
            btn = Button(parent, t,
                         color_bg   = Style.COLOR_PANEL_BG,
                         width_flex = 1)
            btn.on_click = self.make_table_click(t)
            btn.tooltip  = self.build_table_tooltip(t)

    def build_table_tooltip(self, table_name):
        try:
            cols = self.get_table_columns(table_name)
        except Exception as e:
            return f"Could not read schema:\n{e}"
        if not cols:
            return f"{table_name} (no columns)"
        return f"{table_name}\n" + "\n".join(f"  • {c}" for c in cols)

    def refresh_table_list(self):
        card = self.form.widgets.get("card_sql_tables")
        if not card:
            return

        card.clear_children()
        Heading(card, "Tables")
        self.build_table_list(card)

    def get_table_names(self):
        conn   = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_table_columns(self, table_name):
        conn   = sqlite3.connect(self.db_path)
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        cols   = [row[1] for row in cursor.fetchall()]
        conn.close()
        return cols

    def make_table_click(self, table_name):
        def clicked():
            try:
                cols = self.get_table_columns(table_name)
            except Exception:
                cols = []
            col_list = ", ".join(cols) if cols else "*"
            sql = f"SELECT {col_list}\nFROM {table_name}\nLIMIT 100"
            self.current_query = sql
            self.update_query_box(sql)
            self.set_status(f"Preview ready for {table_name}")
        return clicked

    def make_preset_click(self, sql):
        def clicked():
            self.run_query(sql)
        return clicked

    def handle_pick_db_clicked(self):
        root = tk.Tk()
        root.withdraw()

        picked = filedialog.asksaveasfilename(
            title            = "Open or create SQLite database",
            initialdir       = self.last_db_folder,
            defaultextension = ".db",
            confirmoverwrite = False,
            filetypes        = [("SQLite DB", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")]
        )

        root.destroy()

        if not picked:
            return

        created = not os.path.exists(picked)
        if created:
            sqlite3.connect(picked).close()    # creates an empty SQLite file

        self.db_path        = picked
        self.last_db_folder = os.path.dirname(picked)
        self.update_db_button()
        self.refresh_table_list()
        verb = "Created new database" if created else "Loaded database"
        self.set_status(f"{verb}: {os.path.basename(picked)}")

    def update_db_button(self):
        if hasattr(self, "private_btn_db") and self.private_btn_db:
            self.private_btn_db.set_text(os.path.basename(self.db_path))
            self.private_btn_db.tooltip = self.db_path

    # ══════════════════════════════════════════════════════════════
    # MIDDLE PANE — query display
    # ══════════════════════════════════════════════════════════════

    def query(self, parent):
        row=Row(parent)

        Title(row, "Query", glow=True)

        Body(row, "", name="lbl_sql_status",text_align=RIGHT)
        TextArea(parent, name="code_sql", height_flex=1)

        row = Row(parent)
        Button(row, "Run Query",
               color_bg=Style.COLOR_BUTTON_CTA,
               on_click=self.handle_run_clicked)

        Button(row, "Open SQL",
               color_bg=Style.COLOR_BUTTON_SECONDARY,
               on_click=self.handle_open_sql_clicked)

        Button(row, "Save SQL",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.handle_save_sql_clicked)



    def handle_run_clicked(self):
        cb = self.form.widgets.get("code_sql")
        if cb:
            self.run_query(cb.text)

    def handle_open_sql_clicked(self):
        root = tk.Tk()
        root.withdraw()

        picked = filedialog.askopenfilename(
            title      = "Open SQL file",
            initialdir = self.last_db_folder,
            filetypes  = [("SQL files", "*.sql *.txt"), ("All files", "*.*")]
        )

        root.destroy()

        if not picked:
            return

        with open(picked, "r", encoding="utf-8") as private_file:
            sql = private_file.read()

        self.current_query = sql
        self.update_query_box(sql)
        self.set_status(f"Loaded SQL from {os.path.basename(picked)}")

    def handle_save_sql_clicked(self):
        cb = self.form.widgets.get("code_sql")
        if not cb:
            return

        root = tk.Tk()
        root.withdraw()

        picked = filedialog.asksaveasfilename(
            title            = "Save SQL file",
            initialdir       = self.last_db_folder,
            defaultextension = ".sql",
            filetypes        = [("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        root.destroy()

        if not picked:
            return

        with open(picked, "w", encoding="utf-8") as private_file:
            private_file.write(cb.text)

        self.set_status(f"Saved SQL to {os.path.basename(picked)}")

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE — results grid
    # ══════════════════════════════════════════════════════════════

    def results(self, parent):
        Title(parent, "Results", glow=True)
        card = CardCol(parent, height_flex=True,pad=0)
        PowerGrid(card, name="grid_sql_results")

    # ══════════════════════════════════════════════════════════════
    # QUERY EXECUTION
    # ══════════════════════════════════════════════════════════════

    def run_query(self, sql):
        self.current_query = sql
        self.update_query_box(sql)

        started = time.perf_counter()

        try:
            conn   = sqlite3.connect(self.db_path)
            cursor = conn.execute(sql)

            if cursor.description is None:
                conn.commit()
                conn.close()
                elapsed_ms = (time.perf_counter() - started) * 1000
                self.populate_grid(["status"], [["Statement executed successfully"]])
                self.set_status(f"Statement executed in {elapsed_ms:.1f} ms")
                return

            cols   = [desc[0] for desc in cursor.description]
            rows   = [list(r) for r in cursor.fetchall()]
            conn.close()

            elapsed_ms = (time.perf_counter() - started) * 1000
            self.populate_grid(cols, rows)
            self.set_status(f"{len(rows)} rows returned in {elapsed_ms:.1f} ms")

        except Exception as e:
            self.set_status(f"Error: {e}")
            self.populate_grid(["error"], [[str(e)]])

    def update_query_box(self, sql):
        cb = self.form.widgets.get("code_sql")
        if cb:
            cb.set_text(sql)

    def populate_grid(self, cols, rows):
        grid = self.form.widgets.get("grid_sql_results")
        if not grid:
            return

        if not rows:
            grid.set_data([["No results"]], columns=["status"])
            return

        grid.set_data(rows, columns=cols)

    def set_status(self, msg):
        lbl = self.form.widgets.get("lbl_sql_status")
        if lbl:
            lbl.set_text(msg)