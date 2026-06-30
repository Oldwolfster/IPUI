# SQL.py  Update: PowerGrid-driven tables browser w/ drill-down, analyze, script/index buttons
# Replaces button-list with sortable grid; adds DB size readout, filter dropdown,
# action buttons (Preview/Script/Index/Analyze/Refresh), and double-click drill-down to fields.
# Update: Split/Unsplit toggle for dual query+results panels

import os
import sqlite3
import time
import tkinter as tk
from tkinter import filedialog
from ipui import *
from ipui.utils.MgrAccessImport import MgrAccessImport
from ipui.utils.MgrClipboard import MgrClipboard
from ipui.utils.MgrPrefs import MgrPrefs

DB_PATH = r"src\ipui\assets\sample_db\OptimizerShowdown.db" #OLD


class SQL(_BaseTab):
    """Showcase tab demonstrating PowerGrid SQL capabilities."""
    DEFAULT_DB_PATH = r"src\ipui\assets\sample_db\OptimizerShowdown.db"
    PREFS_APP = "testprefapp"  # subclasses set e.g. "neuroforge" to enable persistence
    #ACCDB_TEST_PATH = r"C:\Users\silian\.neuroforge\projects\PredictiveBaseBallData.accdb"
    # ══════════════════════════════════════════════════════════════
    # SETUP
    # ══════════════════════════════════════════════════════════════

    def ip_setup_early(self, ip):
        self.prefs           = MgrPrefs(self.PREFS_APP) if self.PREFS_APP else None
        saved                = self.prefs.load("sql") if self.prefs else {}
        self.private_sql_path_1 = None
        self.private_sql_path_2 = None
        self.db_path         = saved.get("db_path") or self.DEFAULT_DB_PATH
        if not os.path.exists(self.db_path):
            self.db_path     = self.DEFAULT_DB_PATH         # stale pref → fall back

        self.db_folder       = saved.get("db_folder")  or os.path.dirname(os.path.abspath(self.db_path))
        self.sql_folder      = saved.get("sql_folder") or self.db_folder

        self.view_mode       = "tables"        # "tables" | "fields"
        self.selected_table  = None
        self.filter_mode     = "All"           # "All" | "Tables" | "Views"
        self.analysis_cache  = {}              # {table_name: (rows, payload_bytes)}
        self.private_split   = False           # split toggle state
        self.current_query   = "select optimizer, loss_function, count(epoch_count) as run_count, round(avg(epoch_count),2)  as epochs_to_solve\n\nfrom batch_history\n\ngroup by optimizer, loss_function\n\norder by 4"


        #if self.ACCDB_TEST_PATH: MgrAccessImport.import_from(self.ACCDB_TEST_PATH)

    def save_prefs(self):
        if not self.prefs: return
        self.prefs.save("sql", {
            "db_path"    : self.db_path,
            "db_folder"  : self.db_folder,
            "sql_folder" : self.sql_folder,
        })
    # ══════════════════════════════════════════════════════════════
    # LEFT PANE — table browser
    # ══════════════════════════════════════════════════════════════

    def tables(self, parent):
        Title(parent, "Database", glow=True)
        self.build_db_header(parent)
        self.build_filter_row(parent)
        self.build_grid_card(parent)
        self.build_action_row(parent)

    def build_db_header(self, parent):
        row = Row(parent)
        self.private_btn_db = Button(
            row,
            os.path.basename(self.db_path),
            color_bg   = Style.COLOR_TAB_BG,
            flex_width = 1,
            on_click   = self.handle_pick_db_clicked,
        )
        self.private_btn_db.tooltip = self.db_path
        Detail(parent, self.format_db_size(), name="lbl_sql_db_size", text_align=RIGHT)

    def build_filter_row(self, parent):
        row = Row(parent, name="row_sql_filter")
        Detail(row, "View:", flex_width=0, fit_content=True)
        self.build_filter_buttons(row)

    def build_filter_buttons(self, parent):
        for mode in ("All", "Tables", "Views"):
            is_active = (mode == self.filter_mode)
            color     = Style.COLOR_BUTTON_CTA if is_active else Style.COLOR_TAB_BG
            Button(parent, mode,
                   color_bg  = color,
                   flex_width = 1,
                   on_click  = self.make_filter_click(mode))

    def make_filter_click(self, mode):
        def clicked(): self.handle_filter_changed(mode)
        return clicked

    def build_grid_card(self, parent):
        card = CardCol(parent, name="card_sql_tables_grid", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_sql_tables")
        grid.on_row_click       (self.handle_table_row_clicked,   "Name")
        grid.on_row_double_click(self.handle_table_row_dbl_click, "Name")
        self.refresh_grid()

    def build_action_row(self, parent):
        row = Row(parent, name="row_sql_actions")
        self.build_table_mode_buttons(row)

    def build_table_mode_buttons(self, parent):
        Button(parent, "Preview",  color_bg=Style.COLOR_TAB_BG,         flex_width=1, on_click=self.handle_preview_clicked, tooltip="testing")
        Button(parent, "Script",   color_bg=Style.COLOR_TAB_BG,         flex_width=1, on_click=self.handle_script_clicked)
        Button(parent, "Index",    color_bg=Style.COLOR_TAB_BG,         flex_width=1, on_click=self.handle_index_clicked)
        Button(parent, "Analyze",  color_bg=Style.COLOR_BUTTON_ACCENT,  flex_width=1, on_click=self.handle_analyze_clicked)
        Button(parent, "Refresh",  color_bg=Style.COLOR_TAB_BG,         flex_width=1, on_click=self.handle_refresh_clicked)

    def build_field_mode_buttons(self, parent):
        Button(parent, "← Back",    color_bg=Style.COLOR_BUTTON_SECONDARY, flex_width=1, on_click=self.handle_back_clicked)
        Button(parent, "Sample 10", color_bg=Style.COLOR_TAB_BG,           flex_width=1, on_click=self.handle_sample_clicked)
        Button(parent, "DISTINCT",  color_bg=Style.COLOR_TAB_BG,           flex_width=1, on_click=self.handle_distinct_clicked)

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
        try:
            cur = conn.execute(f"PRAGMA table_info({self.quote_ident(table_name)})")
            return len(cur.fetchall())
        except sqlite3.Error:
            return "?"

    def count_indexes(self, conn, table_name):
        try:
            cur = conn.execute(f"PRAGMA index_list({self.quote_ident(table_name)})")
            return len(cur.fetchall())
        except sqlite3.Error:
            return "?"

    def apply_filter(self, rows):
        if self.filter_mode == "Tables": return [r for r in rows if r[0] == "table"]
        if self.filter_mode == "Views" : return [r for r in rows if r[0] == "view"]
        return rows

    def merge_analysis_into(self, rows):
        if not self.analysis_cache: return rows
        out = []
        for r in rows:
            kind, name = r[0], r[1]
            stats      = self.analysis_cache.get(name)
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
                null_label    = "NO"  if notnull    else "YES"
                pk_label      = "✓"   if pk         else ""
                default_label = "—"   if dflt is None else str(dflt)
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
        Detail(row, "View:", flex_width=0, fit_content=True)
        self.build_filter_buttons(row)

    # ══════════════════════════════════════════════════════════════
    # ACTION BUTTON HANDLERS — TABLES MODE
    # ══════════════════════════════════════════════════════════════

    def handle_preview_clicked(self):
        if not self.require_selected_table(): return
        try:
            cols = self.column_names(self.selected_table)
        except Exception as e:
            self.set_status(f"Preview error: {e}")
            return
        select = "\n    , ".join(cols) if cols else "*"
        sql    = f"SELECT {select}\nFROM {self.selected_table}\nLIMIT 1000"
        self.push_query(sql, f"Preview ready for {self.selected_table}")
        self.run_query(sql)

    def column_names(self, name):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(f"SELECT * FROM {self.quote_ident(name)} LIMIT 0")
            return [d[0] for d in cur.description]
        finally:
            conn.close()

    def handle_script_clicked(self):
        if not self.require_selected_table(): return
        try:
            sql = self.fetch_create_sql("table", self.selected_table) \
               or self.fetch_create_sql("view",  self.selected_table)
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
    # DB SIZE / FORMATTING
    # ══════════════════════════════════════════════════════════════

    def format_db_size(self):
        try:
            size_bytes = os.path.getsize(self.db_path)
            return f"Size: {self.format_bytes(size_bytes)}"
        except OSError:
            return "Size: —"

    def format_bytes(self, n):
        if n < 1024:                return f"{n} B"
        if n < 1024 * 1024:         return f"{n/1024:.1f} KB"
        if n < 1024 * 1024 * 1024:  return f"{n/(1024*1024):.1f} MB"
        return f"{n/(1024*1024*1024):.2f} GB"

    def update_db_size_label(self):
        lbl = self.form.widgets.get("lbl_sql_db_size")
        if lbl: lbl.set_text(self.format_db_size())

    # ══════════════════════════════════════════════════════════════
    # DB PICKER
    # ══════════════════════════════════════════════════════════════

    def handle_pick_db_clickedOLD(self):
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.asksaveasfilename(
            title            = "Open or create SQLite database",
            initialdir       = self.db_folder,
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
        self.db_folder      = os.path.dirname(picked)
        self.analysis_cache = {}
        self.selected_table = None
        self.view_mode      = "tables"
        self.save_prefs()
        self.update_db_button()
        self.update_db_size_label()

    def handle_pick_db_clicked(self):
        picked = self.prompt_for_db_path()
        if not picked: return

        if picked.lower().endswith(".accdb"):
            target = self.import_from_accdb(picked)
            if not target: return                                 # import bailed
            picked = target

        self.load_db(picked)

    def prompt_for_db_path(self):
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.asksaveasfilename(
            title            = "Open or create database",
            initialdir       = self.db_folder,
            defaultextension = ".db",
            confirmoverwrite = False,
            filetypes        = [
                ("SQLite / NeuroForge DB", "*.db *.sqlite *.sqlite3 *.nf *.accdb"),
                #("Access DB",              "*.accdb"),
                ("All files",              "*.*"),
            ],
        )
        root.destroy()
        return picked

    def import_from_accdb(self, accdb_path):
        # Returns the sibling .db path on success, None on cancel/abort.
        # On Houston-style errors MgrAccessImport raises — we don't catch;
        # caller's db_path stays unchanged because we never reach load_db.
        name = os.path.basename(accdb_path)
        self.set_status(f"Importing from {name}... (see console for progress)")
        MgrAccessImport.import_from(accdb_path)
        target = os.path.splitext(accdb_path)[0] + ".db"
        self.set_status(f"Imported {name}")
        return target

    def load_db(self, picked):
        created = not os.path.exists(picked)
        if created:
            sqlite3.connect(picked).close()

        self.db_path        = picked
        self.db_folder      = os.path.dirname(picked)
        self.analysis_cache = {}
        self.selected_table = None
        self.view_mode      = "tables"
        self.save_prefs()
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
    # MIDDLE PANE — query editor (single or split)
    # ══════════════════════════════════════════════════════════════

    def query(self, parent):
        row   = Row(parent)
        label = "Unsplit" if self.private_split else "Split"
        Title (row, "Query", glow=True)
        Body  (row, "", name="lbl_sql_status", text_align=RIGHT)
        Button(row, label, color_bg=Style.COLOR_TAB_BG, on_click=self.handle_split_clicked)
        if self.private_split:
            self.build_query_slot(parent, 1)
            self.build_query_slot(parent, 2)
        else:
            self.build_query_slot(parent, 1)

    def build_query_slot(self, parent, slot):
        """One TextArea + Run/Open/Save button row for the given slot."""
        initial  = self.current_query if slot == 1 and hasattr(self, "current_query") else ""
        sql_card = Card(parent, scroll_v=True, pad=2, flex_height=1)
        txt = TextArea(sql_card, initial, name=f"code_sql_{slot}", flex_height=1, wrap=False, scroll_h=True)
        Button(txt, "rocket")
        row = Row(parent)
        Button(row, "Run Query", color_bg=Style.COLOR_BUTTON_CTA,       on_click=self.make_run_click(slot))
        Button(row, "Open SQL",  color_bg=Style.COLOR_BUTTON_SECONDARY,  on_click=self.make_open_click(slot))
        Button(row, "Save SQL",  color_bg=Style.COLOR_TAB_BG,            on_click=self.make_save_click(slot))
        Button(row, "SQL Beau",  color_bg=Style.COLOR_TAB_BG,            on_click=self.make_beau_click(slot))   # NEW

    def make_beau_click(self, slot):
        def clicked():
            from ipui.utils.MgrSqlBeautification import MgrSqlBeautification
            cb = self.form.widgets.get(f"code_sql_{slot}")
            if cb: cb.set_text(MgrSqlBeautification.format_sql(cb.text))
        return clicked

    def handle_split_clicked(self):
        self.private_split = not self.private_split
        self.form.set_pane(1, self.query)
        self.form.set_pane(2, self.results)

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE — results grid (single or split)
    # ══════════════════════════════════════════════════════════════

    def results(self, parent):
        row = Row(parent)
        Title(row, "Results", glow=True)
        Spacer(row)
        Button(row, "Copy", color_bg=Style.COLOR_TAB_BG, on_click=self.handle_copy_results)
        if self.private_split:
            self.build_results_slot(parent, 1)
            self.build_results_slot(parent, 2)
        else:
            self.build_results_slot(parent, 1)

    def build_results_slot(self, parent, slot):
        """One results PowerGrid for the given slot."""
        card = CardCol(parent, flex_height=1, pad=0)
        PowerGrid(card, name=f"grid_sql_results_{slot}")

        # SQL.py method: handle_copy_results  NEW: Copy top results grid
    def handle_copy_results(self):
        grid = self.form.widgets.get("grid_sql_results_1")
        if not grid: return
        payload = grid.copy_payload_tsv()
        if payload:
            MgrClipboard.copy(payload)
            self.set_status("Copied to clipboard")



    # ══════════════════════════════════════════════════════════════
    # SLOT-AWARE HANDLER FACTORIES
    # ══════════════════════════════════════════════════════════════

    def make_run_click(self, slot):
        def clicked():
            cb = self.form.widgets.get(f"code_sql_{slot}")
            if cb: self.run_query(cb.text, slot)
        return clicked

    def make_open_click(self, slot):
        def clicked(): self.handle_open_sql_clicked(slot)
        return clicked

    def make_save_click(self, slot):
        def clicked(): self.handle_save_sql_clicked(slot)
        return clicked

    # ══════════════════════════════════════════════════════════════
    # QUERY EXECUTION
    # ══════════════════════════════════════════════════════════════

    def make_preset_click(self, sql):
        def clicked(): self.run_query(sql)
        return clicked

    def push_query(self, sql, status_msg):
        """Put a SQL string into query slot 1 without executing."""
        self.current_query = sql
        self.update_query_box(sql)
        self.set_status(status_msg)

    def run_query(self, sql, slot=1):
        self.current_query = sql
        started = time.perf_counter()
        try:
            conn   = sqlite3.connect(self.db_path)
            cursor = conn.execute(sql)
            if cursor.description is None:
                conn.commit()
                conn.close()
                elapsed_ms = (time.perf_counter() - started) * 1000
                self.populate_grid(["status"], [["Statement executed successfully"]], slot)
                self.set_status(f"Statement executed in {elapsed_ms:.1f} ms")
                return
            cols       = [desc[0] for desc in cursor.description]
            rows       = [list(r) for r in cursor.fetchall()]
            conn.close()
            elapsed_ms = (time.perf_counter() - started) * 1000
            self.populate_grid(cols, rows, slot)
            self.set_status(f"{len(rows)} rows returned in {elapsed_ms:.1f} ms")
        except Exception as e:
            self.set_status(f"Error: {e}")
            self.populate_grid(["error"], [[str(e)]], slot)

    def update_query_box(self, sql):
        cb = self.form.widgets.get("code_sql_1")
        if cb: cb.set_text(sql)

    def populate_grid(self, cols, rows, slot=1):
        grid = self.form.widgets.get(f"grid_sql_results_{slot}")
        if not grid: return
        if not rows:
            grid.set_data([["No results"]], columns=["status"])
            return
        grid.set_data(rows, columns=cols)

    def set_status(self, msg):
        self.form.widgets.get("lbl_sql_status").set_text(msg)

    # ══════════════════════════════════════════════════════════════
    # OPEN / SAVE SQL (slot-aware)
    # ══════════════════════════════════════════════════════════════

    def handle_open_sql_clicked(self, slot=1):
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.askopenfilename(
            title      = "Open SQL file",
            initialdir = self.sql_folder,
            filetypes  = [("SQL files", "*.sql *.txt"), ("All files", "*.*")],
        )
        root.destroy()
        if not picked: return
        with open(picked, "r", encoding="utf-8") as private_file:
            sql = private_file.read()
        self.current_query = sql
        self.sql_folder    = os.path.dirname(picked)
        self.save_prefs()
        cb = self.form.widgets.get(f"code_sql_{slot}")
        if cb: cb.set_text(sql)
        self.set_sql_path(slot, picked)
        self.set_status(f"Loaded SQL from {os.path.basename(picked)}")


    def handle_save_sql_clicked(self, slot=1):
        cb = self.form.widgets.get(f"code_sql_{slot}")
        if not cb: return
        existing = self.get_sql_path(slot)
        if existing:
            self.save_sql_to(cb, existing)
            return
        root = tk.Tk()
        root.withdraw()
        picked = filedialog.asksaveasfilename(
            title            = "Save SQL file",
            initialdir       = self.sql_folder,
            defaultextension = ".sql",
            filetypes        = [("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        root.destroy()
        if not picked: return
        self.set_sql_path(slot, picked)
        self.save_sql_to(cb, picked)


    def save_sql_to(self, cb, path):
        """ Write file and update status"""
        with open(path, "w", encoding="utf-8") as private_file:
            private_file.write(cb.text)
        self.sql_folder = os.path.dirname(path)
        self.save_prefs()
        self.set_status(f"Saved to {os.path.basename(path)}")


    def get_sql_path(self, slot):    return self.private_sql_path_1 if slot == 1 else self.private_sql_path_2


    def set_sql_path(self, slot, path):
        if slot == 1: self.private_sql_path_1 = path
        else:         self.private_sql_path_2 = path
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
    # GUARDS
    # ══════════════════════════════════════════════════════════════

    def require_selected_table(self):
        if self.selected_table:
            return True
        self.set_status("Select a table first")
        return False



        ############
        # Connection from pipe
        ###


    def load_query_for_table(self, tbl, db_path, start_gd=None, end_gd=None):
        self.db_path = db_path
        self.save_prefs()
        self.update_db_size_label()
        self.selected_table = tbl
        sql = self.build_select_all(tbl, start_gd, end_gd)
        self.push_query(sql, f"Loaded {tbl}")
        self.run_query (sql)


    # ════════════════════════════════════════════════════════════════════════════
    # SQL.py  method: build_select_all  NEW: vertical SELECT with PRAGMA-order cols
    # ════════════════════════════════════════════════════════════════════════════

    def build_select_all(self, tbl, start_gd, end_gd):
        cols       = self.fetch_column_names(tbl)
        col_block  = ",\n    ".join(cols) if cols else "*"
        where      = self.build_gd_where(cols, start_gd, end_gd)
        return f"SELECT\n    {col_block}\nFROM {tbl}{where}" #\nLIMIT 200"


    # ════════════════════════════════════════════════════════════════════════════
    # SQL.py  method: fetch_column_names  NEW: PRAGMA-order column list
    # ════════════════════════════════════════════════════════════════════════════

    def fetch_column_names(self, tbl):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(f"PRAGMA table_info({self.quote_ident(tbl)})")
            return [r[1] for r in cur.fetchall()]
        finally:
            conn.close()


    # ════════════════════════════════════════════════════════════════════════════
    # SQL.py  method: build_gd_where  NEW: GD range filter when table has a GD col
    # Skips the WHERE if start/end aren't given OR if the table has no GD column.
    # ════════════════════════════════════════════════════════════════════════════

    def build_gd_where(self, cols, start_gd, end_gd):
        if start_gd is None or end_gd is None: return ""
        if "GD" not in cols:                   return ""
        return f"\nWHERE GD BETWEEN {start_gd} AND {end_gd}"