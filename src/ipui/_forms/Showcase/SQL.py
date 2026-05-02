# SQL.py  Update: PowerGrid-driven tables browser w/ drill-down, analyze, script/index buttons
# Replaces button-list with sortable grid; adds DB size readout, filter dropdown,
# action buttons (Preview/Script/Index/Analyze/Refresh), and double-click drill-down to fields.

import os
import sqlite3
import time
import tkinter as tk
from tkinter import filedialog
from ipui import *

#DB_PATH = r"src\ipui\assets\sample_db\rock_on_forever_claude.db"
DB_PATH = r"src\ipui\assets\sample_db\OptimizerShowdown.nf"


class SQL(_BaseTab):
    """Showcase tab demonstrating PowerGrid SQL capabilities."""

    # ══════════════════════════════════════════════════════════════
    # SETUP
    # ══════════════════════════════════════════════════════════════

    def ip_setup(self, ip):

        self.db_path         = DB_PATH
        self.last_db_folder  = os.path.dirname(os.path.abspath(self.db_path))
        self.view_mode       = "tables"        # "tables" | "fields"
        self.selected_table  = None
        self.filter_mode     = "All"           # "All" | "Tables" | "Views"
        self.analysis_cache  = {}              # {table_name: (rows, payload_bytes)}

    # ══════════════════════════════════════════════════════════════
    # LEFT PANE — table browser
    # ══════════════════════════════════════════════════════════════

    def tables(self, parent):
        Title(parent, "Database", glow=True)
        self.build_db_header(parent)
        self.build_filter_row(parent)
        self.build_grid_card(parent)
        self.build_action_row(parent)
        #self.build_preset_card(parent)

    def build_db_header(self, parent):
        row = Row(parent)
        self.private_btn_db = Button(
            row,
            os.path.basename(self.db_path),
            color_bg   = Style.COLOR_TAB_BG,
            width_flex = 1,
            on_click   = self.handle_pick_db_clicked,
        )
        self.private_btn_db.tooltip = self.db_path

        Detail(parent, self.format_db_size(), name="lbl_sql_db_size", text_align=RIGHT)


    def build_filter_row(self, parent):
        row = Row(parent, name="row_sql_filter")
        Detail(row, "View:", width_flex=0, fit_content=True)
        self.build_filter_buttons(row)

    def build_filter_buttons(self, parent):
        for mode in ("All", "Tables", "Views"):
            is_active = (mode == self.filter_mode)
            color = Style.COLOR_BUTTON_CTA if is_active else Style.COLOR_TAB_BG
            Button(parent, mode,
                   color_bg=color,
                   width_flex=1,
                   on_click=self.make_filter_click(mode))

    def make_filter_click(self, mode):
        def clicked(): self.handle_filter_changed(mode)

        return clicked
    def build_grid_card(self, parent):
        card = CardCol(parent, name="card_sql_tables_grid", height_flex=1, pad=0)
        grid = PowerGrid(card, name="grid_sql_tables")
        grid.on_row_click       (self.handle_table_row_clicked,   "Name")
        grid.on_row_double_click(self.handle_table_row_dbl_click, "Name")
        self.refresh_grid()

    def build_action_row(self, parent):
        row = Row(parent, name="row_sql_actions")
        self.build_table_mode_buttons(row)

    def build_table_mode_buttons(self, parent):
        Button(parent, "Preview",  color_bg=Style.COLOR_TAB_BG,         width_flex=1, on_click=self.handle_preview_clicked, tooltip="testing")
        Button(parent, "Script",   color_bg=Style.COLOR_TAB_BG,         width_flex=1, on_click=self.handle_script_clicked)
        Button(parent, "Index",    color_bg=Style.COLOR_TAB_BG,         width_flex=1, on_click=self.handle_index_clicked)
        Button(parent, "Analyze",  color_bg=Style.COLOR_BUTTON_ACCENT,  width_flex=1, on_click=self.handle_analyze_clicked)
        Button(parent, "Refresh",  color_bg=Style.COLOR_TAB_BG,         width_flex=1, on_click=self.handle_refresh_clicked)

    def build_field_mode_buttons(self, parent):
        Button(parent, "← Back",   color_bg=Style.COLOR_BUTTON_SECONDARY, width_flex=1, on_click=self.handle_back_clicked)
        Button(parent, "Sample 10",color_bg=Style.COLOR_TAB_BG,           width_flex=1, on_click=self.handle_sample_clicked)
        Button(parent, "DISTINCT", color_bg=Style.COLOR_TAB_BG,           width_flex=1, on_click=self.handle_distinct_clicked)


    # ══════════════════════════════════════════════════════════════
    # GRID DATA — TABLES MODE
    # ══════════════════════════════════════════════════════════════

    def refresh_grid(self):
        if self.view_mode == "tables":  self.populate_tables_grid()
        else:                           self.populate_fields_grid()

    def populate_tables_grid(self):
        grid = self.form.widgets.get("grid_sql_tables")
        if not grid: return

        try:
            rows = self.scan_schema()
        except Exception as e:
            grid.set_data([[str(e)]], columns=["error"])
            self.set_status(f"Could not read schema: {e}")
            return

        rows = self.apply_filter(rows)
        rows = self.merge_analysis_into(rows)
        cols = self.columns_for_tables_view()
        grid.set_data(rows, columns=cols)

    def columns_for_tables_view(self):
        if self.analysis_cache:
            return ["Type", "Name", "Cols", "Idx", "Rows", "AvgLen", "Disk"]
        return     ["Type", "Name", "Cols", "Idx"]

    def scan_schema(self):
        conn   = sqlite3.connect(self.db_path)
        try:
            cur  = conn.execute(
                "SELECT type, name FROM sqlite_master "
                "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' "
                "ORDER BY type, name"
            )
            entries = cur.fetchall()
            rows    = []
            for kind, name in entries:
                col_count = self.count_columns(conn, name)
                idx_count = self.count_indexes(conn, name) if kind == "table" else 0
                rows.append([kind, name, col_count, idx_count])
            return rows
        finally:
            conn.close()

    def count_columns(self, conn, table_name):
        cur = conn.execute(f"PRAGMA table_info({self.quote_ident(table_name)})")
        return len(cur.fetchall())

    def count_indexes(self, conn, table_name):
        cur = conn.execute(f"PRAGMA index_list({self.quote_ident(table_name)})")
        return len(cur.fetchall())

    def apply_filter(self, rows):
        if self.filter_mode == "Tables": return [r for r in rows if r[0] == "table"]
        if self.filter_mode == "Views" : return [r for r in rows if r[0] == "view"]
        return rows

    def merge_analysis_into(self, rows):
        if not self.analysis_cache: return rows
        out = []
        for r in rows:
            kind, name = r[0], r[1]
            stats = self.analysis_cache.get(name)
            if stats:
                row_count, payload = stats
                avg_len = (payload // row_count) if row_count else 0
                out.append(r + [row_count, f"{avg_len} B", self.format_bytes(payload)])
            else:
                out.append(r + ["—", "—", "—"])
        return out

    # ══════════════════════════════════════════════════════════════
    # GRID DATA — FIELDS MODE (drill-down)
    # ══════════════════════════════════════════════════════════════

    def populate_fields_grid(self):
        grid = self.form.widgets.get("grid_sql_tables")
        if not grid: return
        if not self.selected_table:
            self.go_to_tables_view()
            return

        try:
            rows = self.scan_table_columns(self.selected_table)
        except Exception as e:
            grid.set_data([[str(e)]], columns=["error"])
            return

        grid.set_data(rows, columns=["#", "Name", "Type", "Null?", "PK", "Default"])

    def scan_table_columns(self, table_name):
        conn = sqlite3.connect(self.db_path)
        try:
            cur  = conn.execute(f"PRAGMA table_info({self.quote_ident(table_name)})")
            out  = []
            for cid, name, ctype, notnull, dflt, pk in cur.fetchall():
                null_label    = "NO" if notnull else "YES"
                pk_label      = "✓"  if pk      else ""
                default_label = "—"  if dflt is None else str(dflt)
                out.append([cid + 1, name, ctype or "—", null_label, pk_label, default_label])
            return out
        finally:
            conn.close()

    # ══════════════════════════════════════════════════════════════
    # MODE SWITCHING (tables ⇄ fields)
    # ══════════════════════════════════════════════════════════════

    def go_to_fields_view(self, table_name):
        self.view_mode      = "fields"
        self.selected_table = table_name
        self.swap_action_row()
        self.populate_fields_grid()
        self.set_status(f"Fields of {table_name}")

    def go_to_tables_view(self):
        self.view_mode = "tables"
        self.swap_action_row()
        self.populate_tables_grid()

    def swap_action_row(self):
        row = self.form.widgets.get("row_sql_actions")
        if not row: return
        row.clear_children()
        if self.view_mode == "tables":  self.build_table_mode_buttons(row)
        else:                           self.build_field_mode_buttons(row)

    # ══════════════════════════════════════════════════════════════
    # ROW CLICK HANDLERS
    # ══════════════════════════════════════════════════════════════

    def handle_table_row_clicked(self, table_name):
        if self.view_mode != "tables": return
        self.selected_table = table_name
        self.set_status(f"Selected: {table_name}")

    def handle_table_row_dbl_click(self, table_name):
        if self.view_mode != "tables": return
        self.go_to_fields_view(table_name)


    def handle_filter_changed(self, mode):
        self.filter_mode = mode
        self.rebuild_filter_row()
        self.populate_tables_grid()

    def rebuild_filter_row(self):
        row = self.form.widgets.get("row_sql_filter")
        if not row: return
        row.clear_children()
        Detail(row, "View:", width_flex=0, fit_content=True)
        self.build_filter_buttons(row)

    # ══════════════════════════════════════════════════════════════
    # ACTION BUTTON HANDLERS — TABLES MODE
    # ══════════════════════════════════════════════════════════════

    def handle_preview_clicked(self):
        if not self.require_selected_table(): return
        sql = f"SELECT *\nFROM {self.selected_table}\nLIMIT 100"
        self.push_query(sql, f"Preview ready for {self.selected_table}")

    def handle_script_clicked(self):
        if not self.require_selected_table(): return
        try:
            sql = self.fetch_create_sql("table", self.selected_table)
        except Exception as e:
            self.set_status(f"Script error: {e}")
            return
        if not sql:
            self.set_status(f"No CREATE statement found for {self.selected_table}")
            return
        self.push_query(sql + ";", f"DDL for {self.selected_table}")

    def handle_index_clicked(self):
        if not self.require_selected_table(): return
        try:
            stmts = self.fetch_index_sqls(self.selected_table)
        except Exception as e:
            self.set_status(f"Index error: {e}")
            return
        if not stmts:
            self.push_query(f"-- No indexes on {self.selected_table}", f"No indexes on {self.selected_table}")
            return
        joined = ";\n\n".join(stmts) + ";"
        self.push_query(joined, f"{len(stmts)} index(es) on {self.selected_table}")

    def handle_analyze_clicked(self):
        started = time.perf_counter()
        try:
            self.analysis_cache = self.run_analyze()
        except Exception as e:
            self.set_status(f"Analyze error: {e}")
            return
        elapsed_ms = (time.perf_counter() - started) * 1000
        self.populate_tables_grid()
        self.set_status(f"Analyzed {len(self.analysis_cache)} tables in {elapsed_ms:.0f} ms")

    def handle_refresh_clicked(self):
        self.analysis_cache = {}
        self.update_db_size_label()
        self.populate_tables_grid()
        self.set_status("Schema refreshed")

    # ══════════════════════════════════════════════════════════════
    # ACTION BUTTON HANDLERS — FIELDS MODE
    # ══════════════════════════════════════════════════════════════

    def handle_back_clicked(self):
        self.go_to_tables_view()

    def handle_sample_clicked(self):
        if not self.selected_table: return
        sql = f"SELECT *\nFROM {self.selected_table}\nORDER BY RANDOM()\nLIMIT 10"
        self.push_query(sql, f"Sample 10 from {self.selected_table}")

    def handle_distinct_clicked(self):
        if not self.selected_table: return
        try:
            cols = self.first_column_name(self.selected_table)
        except Exception as e:
            self.set_status(f"DISTINCT error: {e}")
            return
        sql = (f"SELECT {cols} AS value, COUNT(*) AS n\n"
               f"FROM {self.selected_table}\n"
               f"GROUP BY {cols}\n"
               f"ORDER BY n DESC\n"
               f"LIMIT 100")
        self.push_query(sql, f"DISTINCT {cols} from {self.selected_table}")

    # ══════════════════════════════════════════════════════════════
    # SCHEMA HELPERS
    # ══════════════════════════════════════════════════════════════

    def fetch_create_sql(self, kind, name):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type=? AND name=?",
                (kind, name),
            )
            row = cur.fetchone()
            return row[0] if row and row[0] else ""
        finally:
            conn.close()

    def fetch_index_sqls(self, table_name):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='index' AND tbl_name=? AND sql IS NOT NULL "
                "ORDER BY name",
                (table_name,),
            )
            return [r[0] for r in cur.fetchall()]
        finally:
            conn.close()

    def first_column_name(self, table_name):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(f"PRAGMA table_info({self.quote_ident(table_name)})")
            row = cur.fetchone()
            if not row: raise RuntimeError("table has no columns")
            return row[1]
        finally:
            conn.close()

    def run_analyze(self):
        """Estimate row count and payload bytes per table.  Skips views."""
        conn   = sqlite3.connect(self.db_path)
        result = {}
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            )
            tables = [r[0] for r in cur.fetchall()]
            for t in tables:
                result[t] = self.analyze_table(conn, t)
        finally:
            conn.close()
        return result

    def analyze_table(self, conn, table_name):
        cols = [r[1] for r in conn.execute(
            f"PRAGMA table_info({self.quote_ident(table_name)})"
        ).fetchall()]
        if not cols: return (0, 0)
        length_expr = " + ".join(
            f"COALESCE(LENGTH(CAST({self.quote_ident(c)} AS BLOB)), 0)"
            for c in cols
        )
        sql = (f"SELECT COUNT(*), COALESCE(SUM({length_expr}), 0) "
               f"FROM {self.quote_ident(table_name)}")
        row_count, payload = conn.execute(sql).fetchone()
        return (row_count or 0, payload or 0)

    def quote_ident(self, name):
        return '"' + name.replace('"', '""') + '"'

    # ══════════════════════════════════════════════════════════════
    # DB SIZE / FORMATTING
    # ══════════════════════════════════════════════════════════════

    def format_db_size(self):
        try:
            size_bytes = os.path.getsize(self.db_path)
            return f"Size: {self.format_bytes(size_bytes)}"
        except OSError:
            return "Size: —"

    def format_bytes(self, n):
        if n < 1024:                  return f"{n} B"
        if n < 1024 * 1024:           return f"{n/1024:.1f} KB"
        if n < 1024 * 1024 * 1024:    return f"{n/(1024*1024):.1f} MB"
        return f"{n/(1024*1024*1024):.2f} GB"

    def update_db_size_label(self):
        lbl = self.form.widgets.get("lbl_sql_db_size")
        if lbl: lbl.set_text(self.format_db_size())

    # ══════════════════════════════════════════════════════════════
    # DB PICKER
    # ══════════════════════════════════════════════════════════════

    def handle_pick_db_clicked(self):
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.asksaveasfilename(
            title            = "Open or create SQLite database",
            initialdir       = self.last_db_folder,
            defaultextension = ".db",
            confirmoverwrite = False,
            filetypes        = [("SQLite DB", "*.db *.sqlite *.sqlite3"), ("All files", "*.*")],
        )
        root.destroy()
        if not picked: return

        created = not os.path.exists(picked)
        if created:
            sqlite3.connect(picked).close()

        self.db_path        = picked
        self.last_db_folder = os.path.dirname(picked)
        self.analysis_cache = {}
        self.selected_table = None
        self.view_mode      = "tables"
        self.update_db_button()
        self.update_db_size_label()
        self.swap_action_row()
        self.populate_tables_grid()
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
        row = Row(parent)
        Title(row, "Query", glow=True)
        Body (row, "", name="lbl_sql_status", text_align=RIGHT)

        TextArea(parent, "SELECT * FROM batch_history LIMIT 696", name="code_sql", height_flex=1)

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
        if cb: self.run_query(cb.text)

    def handle_open_sql_clicked(self):
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.askopenfilename(
            title      = "Open SQL file",
            initialdir = self.last_db_folder,
            filetypes  = [("SQL files", "*.sql *.txt"), ("All files", "*.*")],
        )
        root.destroy()
        if not picked: return
        with open(picked, "r", encoding="utf-8") as private_file:
            sql = private_file.read()
        self.current_query = sql
        self.update_query_box(sql)
        self.set_status(f"Loaded SQL from {os.path.basename(picked)}")

    def handle_save_sql_clicked(self):
        cb = self.form.widgets.get("code_sql")
        if not cb: return
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.asksaveasfilename(
            title            = "Save SQL file",
            initialdir       = self.last_db_folder,
            defaultextension = ".sql",
            filetypes        = [("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        root.destroy()
        if not picked: return
        with open(picked, "w", encoding="utf-8") as private_file:
            private_file.write(cb.text)
        self.set_status(f"Saved SQL to {os.path.basename(picked)}")

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE — results grid
    # ══════════════════════════════════════════════════════════════

    def results(self, parent):
        Title         (parent, text="Results", glow=True)
        card = CardCol(parent, height_flex=1, pad=0)
        PowerGrid     (card,   name="grid_sql_results")

    # ══════════════════════════════════════════════════════════════
    # QUERY EXECUTION
    # ══════════════════════════════════════════════════════════════

    def make_preset_click(self, sql):
        def clicked(): self.run_query(sql)
        return clicked

    def push_query(self, sql, status_msg):
        """Put a SQL string into the query box without executing."""
        self.current_query = sql
        self.update_query_box(sql)
        self.set_status(status_msg)

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

            cols = [desc[0] for desc in cursor.description]
            rows = [list(r) for r in cursor.fetchall()]
            conn.close()

            elapsed_ms = (time.perf_counter() - started) * 1000
            self.populate_grid(cols, rows)
            self.set_status(f"{len(rows)} rows returned in {elapsed_ms:.1f} ms")

        except Exception as e:
            self.set_status(f"Error: {e}")
            self.populate_grid(["error"], [[str(e)]])

    def update_query_box(self, sql):
        cb = self.form.widgets.get("code_sql")
        if cb: cb.set_text(sql)

    def populate_grid(self, cols, rows):
        grid = self.form.widgets.get("grid_sql_results")
        if not grid: return
        if not rows:
            grid.set_data([["No results"]], columns=["status"])
            return
        grid.set_data(rows, columns=cols)

    def set_status(self, msg):
        lbl = self.form.widgets.get("lbl_sql_status")
        if lbl: lbl.set_text(msg)

    # ══════════════════════════════════════════════════════════════
    # GUARDS
    # ══════════════════════════════════════════════════════════════

    def require_selected_table(self):
        if self.selected_table:
            return True
        self.set_status("Select a table first")
        return False