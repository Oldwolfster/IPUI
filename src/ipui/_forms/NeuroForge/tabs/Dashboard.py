# Dashboard.py  Complete file replacement  Final clean version through Phase 4
# Changes from prior version:
#   - render_right_pie no longer calls chart_type="pie" (Chart is line-only); renders as text card
#   - refresh_right_pane uses canonical form.set_pane(2, ...) instead of children.clear() hack
#   - best_runs is now just the state-router; no right_pane_parent stash
#   - try/except: return None stripped from all SQL helpers (rug-slide cleanup)
#   - dead methods removed: best_runsOkd, load_best_runs, populate_best_runs_*, query_best_runs
#   - blank-line and indentation cleanup

import sqlite3
from datetime import datetime
from ipui import *
from ipui._forms.NeuroForge.SubProcesses import SubProcesses


class EZ_Pane(_BaseTab):
    """Dashboard tab — project-level batch and run analysis."""

    MAX_COMPARE = 4

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ══════════════════════════════════════════════════════════════

    def ip_setup_early(self, ip):
        if not hasattr(self.form, 'compared_runs'):
            self.form.compared_runs = []

    def ip_activated(self, ip):
        self.load_batches()

    # ══════════════════════════════════════════════════════════════
    # TAB PANES  (names must match strings in FormNeuroForge.TAB_LAYOUT)
    # ══════════════════════════════════════════════════════════════

    def batches(self, parent) -> None:
        """Left pane — batch list."""
        Title(parent, "Batches", glow=True)
        card = CardCol(parent, flex_height=1)
        grid = PowerGrid(card, name="grid_batches", flex_height=1)
        grid.on_row_click(self.on_batch_selected, "Batch")
        self.load_batches()

    def batch_runs(self, parent) -> None:
        """Middle pane — run comparison."""
        Title(parent, "Run Comparison", glow=True)
        Body(parent, "", name="lbl_compare_status")
        Row(parent, name="row_remove_buttons")
        card = CardCol(parent, flex_height=1)
        PowerGrid(card, name="grid_comparison", flex_height=1)
        self.refresh_comparison()

    def best_runs(self, parent) -> None:
        """Right pane — state-driven (Launch CTA / progress card / loss curves)."""
        completed, pending = self.query_project_counts()
        compared           = getattr(self.form, 'compared_runs', [])
        if completed + pending == 0:
            self.render_right_launch_cta(parent)
        elif not compared:
            self.render_right_progress(parent, completed, pending)
        else:
            self.render_right_loss_curves(parent, compared)

    # ══════════════════════════════════════════════════════════════
    # BATCH SELECTION — swap left pane to runs
    # ══════════════════════════════════════════════════════════════

    def on_batch_selected(self, batch_id) -> None:
        self.form.selected_batch_id = batch_id
        self.show_batch_runs()

    def show_batches(self):
        self.load_batches()
        self.form.set_pane(0, self.batches)

    def show_batch_runs(self):
        self.form.set_pane(0, self.pane_batch_runs)

    def pane_batch_runs(self, parent):
        batch_id = self.form.selected_batch_id
        header   = Row(parent)
        btn      = Button(header, "← Back")
        btn.on_click_me(self.show_batches)
        current_name = self.fetch_batch_name(batch_id) or f"Batch {batch_id}"
        TextBox(
            header,
            placeholder = f"Batch {batch_id}",
            name        = "txt_dash_batch_name",
            on_submit   = self.on_batch_name_submitted,
            flex_width  = 1,
        ).set_text(current_name)
        remaining = self.count_remaining(batch_id)
        if remaining > 0:
            resume_btn = Button(header, f"Resume Remaining ({remaining})")
            resume_btn.on_click_me(self.resume_batch_clicked)
        notes = self.load_notes_for_batch(batch_id)
        card  = CardCol(parent, flex_height=1)
        grid  = PowerGrid(card, name="grid_batch_runs", flex_height=1)
        grid.on_row_click(self.on_run_toggled, "Run")
        self.load_batch_runs(batch_id)
        self.build_notes_panel(parent, batch_id, notes)

    # ══════════════════════════════════════════════════════════════
    # BATCH NAME EDIT
    # ══════════════════════════════════════════════════════════════

    def on_batch_name_submitted(self, new_name):
        batch_id = getattr(self.form, 'selected_batch_id', None)
        if batch_id is None:                                                                            return
        self.update_batch_name(batch_id, new_name.strip())
        self.load_batches()

    def update_batch_name(self, batch_id, new_name):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE batch_specs SET batch_name = ? WHERE batch_id = ?",
            (new_name, batch_id)
        )
        conn.commit()
        conn.close()

    def fetch_batch_name(self, batch_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return None
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT batch_name FROM batch_specs WHERE batch_id = ?",
            (batch_id,)
        ).fetchone()
        conn.close()
        return row["batch_name"] if row else None

    # ══════════════════════════════════════════════════════════════
    # RESUME
    # ══════════════════════════════════════════════════════════════

    def count_remaining(self, batch_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return 0
        conn = sqlite3.connect(db_path)
        row  = conn.execute(
            "SELECT COUNT(1) FROM batch_history "
            "WHERE batch_id = ? AND (status IS NULL OR status != 'completed')",
            (batch_id,)
        ).fetchone()
        conn.close()
        return row[0] if row else 0

    def resume_batch_clicked(self):
        batch_id  = self.form.selected_batch_id
        remaining = self.count_remaining(batch_id)
        self.form.msgbox(
            f"Resume batch {batch_id}?\n\n{remaining} run{'s' if remaining != 1 else ''} remaining.",
            MSG_BTNS_YES_NO + MSG_ICON_QUESTION + MSG_DEFAULT_2,
            "Resume Batch",
            on_result = self.on_resume_confirmed,
        )

    def on_resume_confirmed(self, result):
        if result != MSG_RESULT_YES:                                                                    return
        batch_id = self.form.selected_batch_id
        self.form.active_batch_id = batch_id
        self.load_run_details_for(batch_id)
        self.form.show_tab("Colosseum")
        self.form.switch_tab("Colosseum")
        SubProcesses.launch_shards(self.form, batch_id)

    def load_run_details_for(self, batch_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT run_id, key, value FROM batch_details WHERE batch_id = ?",
            (batch_id,)
        ).fetchall()
        conn.close()
        details = {}
        for run_id, key, value in rows:
            if run_id not in details:
                details[run_id] = {}
            details[run_id][key] = value
        self.form.run_details = details

    # ══════════════════════════════════════════════════════════════
    # NOTES (batch-level)
    # ══════════════════════════════════════════════════════════════

    def build_notes_panel(self, parent, batch_id, notes):
        Title(parent, "Notes", glow=True)
        panel = CardCol(parent, flex_height=1, name="card_notes")
        if notes:
            grid = PowerGrid(panel, name="grid_notes", flex_height=1)
            self.populate_notes_grid(grid, notes)
        else:
            Body(panel, "No notes yet — add the first one below.", name="lbl_no_notes")
        add_row = Row(parent)
        TextBox(
            add_row,
            placeholder = "Add a note and press Enter…",
            name        = "txt_new_note",
            on_submit   = self.on_note_submitted,
            flex_width  = 1,
        )

    def populate_notes_grid(self, grid, notes):
        header = ["When", "Note"]
        data   = [header]
        for n in notes:
            data.append([self.format_date(n["created_at"]), n["note_text"]])
        grid.set_data(data)

    def load_notes_for_batch(self, batch_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return []
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT obs_id, note_text, created_at FROM observations "
            "WHERE target_type = 'batch' AND target_id = ? "
            "ORDER BY created_at DESC",
            (batch_id,)
        ).fetchall()
        conn.close()
        return rows

    def add_note(self, batch_id, note_text):
        text = note_text.strip()
        if not text:                                                                                    return
        db_path = self.get_db_path()
        if not db_path:                                                                                 return
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO observations (target_type, target_id, note_text) "
            "VALUES ('batch', ?, ?)",
            (batch_id, text)
        )
        conn.commit()
        conn.close()

    def on_note_submitted(self, note_text):
        batch_id = getattr(self.form, 'selected_batch_id', None)
        if batch_id is None:                                                                            return
        self.add_note(batch_id, note_text)
        self.show_batch_runs()

    # ══════════════════════════════════════════════════════════════
    # RUN TOGGLE — add/remove from comparison
    # ══════════════════════════════════════════════════════════════

    def on_run_toggled(self, run_id) -> None:
        compared = self.form.compared_runs
        ids      = [r["run_id"] for r in compared]
        if run_id in ids:
            self.form.compared_runs = [r for r in compared if r["run_id"] != run_id]
        elif len(compared) >= self.MAX_COMPARE:
            return
        else:
            run = self.fetch_full_run(run_id)
            if run:
                compared.append(run)
        self.refresh_batch_runs()
        self.refresh_comparison()
        self.refresh_right_pane()

    # ══════════════════════════════════════════════════════════════
    # BATCH RUNS GRID (left pane drill-in)
    # ══════════════════════════════════════════════════════════════

    def load_batches(self) -> None:
        rows = self.query_batches()
        if rows is None:                                                                                return
        self.form.proj_batches = rows
        self.populate_batch_grid(rows)

    def populate_batch_grid(self, rows) -> None:
        grid = self.form.widgets.get("grid_batches")
        if not grid:                                                                                    return
        header = ["Batch", "Date", "Total", "Done", "%", "Best MAE", "Worst MAE", "Best Acc", "Name"]
        data   = [header]
        for r in rows:
            total    = r["total_runs"]
            done     = r["run_count"]
            pct_str  = self.compute_percent(done, total)
            name_str = r["batch_name"] if r["batch_name"] else f"Batch {r['batch_id']}"
            data.append([
                r["batch_id"],
                self.format_date(r["created_at"]),
                total,
                done,
                pct_str,
                smart_format(r["best_mae"])  if r["best_mae"]  is not None else "—",
                smart_format(r["worst_mae"]) if r["worst_mae"] is not None else "—",
                smart_format(r["best_acc"])  if r["best_acc"]  is not None else "—",
                name_str,
            ])
        grid.set_data(data)

    def compute_percent(self, done, total):
        if not total:                                                                                   return "—"
        return f"{int(round(100 * (done or 0) / total))}%"

    def load_batch_runs(self, batch_id) -> None:
        rows = self.query_batch_runs(batch_id)
        grid = self.form.widgets.get("grid_batch_runs")
        if not grid:                                                                                    return
        if not rows:
            grid.set_data([["No runs found"]])
            return
        selected = self.get_compared_ids()
        header   = ["Sel", "Run", "Epochs", "MAE", "Acc%"]
        data     = [header]
        for r in rows:
            run_id = r["run_id"]
            marker = "●" if run_id in selected else ""
            data.append([
                marker,
                run_id,
                r["epoch_count"] or "—",
                smart_format(r["best_mae"]) if r["best_mae"] is not None else "—",
                r["accuracy"] if r["accuracy"] is not None else "—",
            ])
        grid.set_data(data)

    def refresh_batch_runs(self):
        batch_id = getattr(self.form, 'selected_batch_id', None)
        if batch_id is not None:
            self.load_batch_runs(batch_id)

    # ══════════════════════════════════════════════════════════════
    # COMPARISON (middle pane)
    # ══════════════════════════════════════════════════════════════

    def refresh_comparison(self):
        compared = getattr(self.form, 'compared_runs', [])
        self.refresh_compare_status(compared)
        self.refresh_remove_buttons(compared)
        self.refresh_compare_grid(compared)

    def refresh_compare_status(self, compared):
        lbl = self.form.widgets.get("lbl_compare_status")
        if not lbl:                                                                                     return
        count = len(compared)
        if count == 0:
            lbl.set_text("Select runs from the left to compare")
        elif count >= self.MAX_COMPARE:
            lbl.set_text(f"{count} runs selected (max {self.MAX_COMPARE})")
        else:
            lbl.set_text(f"{count} run{'s' if count != 1 else ''} selected")

    def refresh_remove_buttons(self, compared):
        row = self.form.widgets.get("row_remove_buttons")
        if not row:                                                                                     return
        row.children.clear()
        for run in compared:
            rid = run["run_id"]
            btn = Button(row, f"Remove {rid}", color_bg=Style.COLOR_BUTTON_DANGER)
            btn.on_click_me(self.make_remove_click(rid))

    def make_remove_click(self, run_id):
        def clicked():
            self.form.compared_runs = [
                r for r in self.form.compared_runs if r["run_id"] != run_id
            ]
            self.refresh_batch_runs()
            self.refresh_comparison()
            self.refresh_right_pane()
        return clicked

    def refresh_compare_grid(self, compared):
        grid = self.form.widgets.get("grid_comparison")
        if not grid:                                                                                    return
        if not compared:
            grid.set_data([["Select runs to compare"]])
            return
        fields = self.compare_fields()
        header = ["Field"] + [f"Run {r['run_id']}" for r in compared]
        data   = [header]
        for field in fields:
            row = [field]
            for run in compared:
                val = run.get(field, "—")
                if val is None:
                    val = "—"
                elif isinstance(val, float):
                    val = smart_format(val)
                row.append(val)
            data.append(row)
        grid.set_data(data)

    def compare_fields(self):
        return [
            "status",             "seed",
            "epoch_count",        "best_mae",
            "final_mae",          "accuracy",
            "convergence_condition",
            "runtime_seconds",
            "learning_rate",      "batch_size",
            "architecture",       "optimizer",
            "weight_initializer", "loss_function",
            "hidden_activation",  "output_activation",
            "target_scaler",      "input_scalers",
            "problem_type",       "sample_count",
            "target_min",         "target_max",
            "target_min_label",   "target_max_label",
            "target_mean",        "target_stdev",
        ]

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE — state-driven rendering
    # ══════════════════════════════════════════════════════════════

    def refresh_right_pane(self):
        self.form.set_pane(2, self.best_runs)

    def render_right_launch_cta(self, parent):
        Title(parent, "Get Started", glow=True)
        Body(parent, "No batches yet.\nKick off your first run with default settings.")
        btn = Button(parent, "Launch Run")
        btn.on_click_me(self.form.launch_colosseum)

    def render_right_progress(self, parent, completed, pending):
        Title(parent, "Project Progress", glow=True)
        total = completed + pending
        pct   = int(round(100 * completed / total)) if total else 0
        card  = CardCol(parent, flex_height=1)
        Title(card, f"{pct}% Complete", glow=True)
        Body(card, f"Completed: {completed}")
        Body(card, f"Pending:   {pending}")
        Body(card, f"Total:     {total}")
        Body(parent, "Select runs from the left to see their loss curves.")

    def render_right_loss_curves(self, parent, compared):
        Title(parent, f"Loss Curves ({len(compared)} run{'s' if len(compared) != 1 else ''})", glow=True)
        series = []
        for run in compared:
            run_id = run["run_id"]
            points = self.query_epoch_history(run_id)
            if not points:                                                                              continue
            series.append({
                "label": f"Run {run_id}",
                "x":     [p["epoch"] for p in points],
                "y":     [p["mae"]   for p in points],
            })
        if not series:
            Body(parent, "Selected runs have no epoch history yet.")
            return
        chart = Chart(parent, flex_height=1)
        chart.set_data(series, x_label="Epoch", y_label="MAE")

    # ══════════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════════

    def query_batches(self):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return None
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT s.batch_id, s.batch_name, s.created_at, "
            "       s.gladiators, s.arenas, "
            "       (SELECT COUNT(DISTINCT d.run_id) FROM batch_details d "
            "        WHERE d.batch_id = s.batch_id) AS total_runs, "
            "       (SELECT COUNT(*) FROM batch_history h "
            "        WHERE h.batch_id = s.batch_id AND status = 'completed') AS run_count, "
            "       (SELECT ROUND(MIN(best_mae), 4) FROM batch_history h "
            "        WHERE h.batch_id = s.batch_id) AS best_mae, "
            "       (SELECT ROUND(MAX(best_mae), 4) FROM batch_history h "
            "        WHERE h.batch_id = s.batch_id) AS worst_mae, "
            "       (SELECT MAX(accuracy) FROM batch_history h "
            "        WHERE h.batch_id = s.batch_id) AS best_acc "
            "FROM batch_specs s ORDER BY s.created_at DESC"
        ).fetchall()
        conn.close()
        return rows

    def query_batch_runs(self, batch_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return None
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT run_id, epoch_count, best_mae, accuracy, runtime_seconds "
            "FROM batch_history "
            "WHERE batch_id = ? "
            "ORDER BY best_mae ASC",
            (batch_id,)
        ).fetchall()
        conn.close()
        return rows

    def fetch_full_run(self, run_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return None
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM batch_history WHERE run_id = ?",
            (run_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def query_project_counts(self):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return (0, 0)
        conn = sqlite3.connect(db_path)
        row  = conn.execute(
            "SELECT "
            "  SUM(CASE WHEN status =  'completed' THEN 1 ELSE 0 END) AS completed, "
            "  SUM(CASE WHEN status != 'completed' OR status IS NULL THEN 1 ELSE 0 END) AS pending "
            "FROM batch_history"
        ).fetchone()
        conn.close()
        return (row[0] or 0, row[1] or 0)

    def query_epoch_history(self, run_id):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return []
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT epoch, mae FROM epoch_history "
            "WHERE run_id = ? AND mae IS NOT NULL "
            "ORDER BY epoch ASC",
            (run_id,)
        ).fetchall()
        conn.close()
        return rows

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def get_db_path(self):
        project = getattr(self.form, 'active_project', None)
        if not project:                                                                                 return None
        return str(project.path)

    def get_compared_ids(self):
        compared = getattr(self.form, 'compared_runs', [])
        return {r["run_id"] for r in compared}

    @staticmethod
    def format_date(raw) -> str:
        if not raw:                                                                                     return "—"
        try:
            dt = datetime.fromisoformat(str(raw))
            return dt.strftime("%m/%d %H:%M")
        except ValueError:
            return str(raw)[:10]