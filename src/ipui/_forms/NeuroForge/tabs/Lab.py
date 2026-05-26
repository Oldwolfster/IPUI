# Lab.py  NEW FILE  Phase 5 v1 — single-batch run analysis with filter + sort + loss-curve overlay
# Cohort: one batch at a time (cross-batch deferred per "apples vs oranges" discussion).
# Auto-selects most recent batch on first load.

import sqlite3
from ipui import *


class Lab(_BaseTab):
    """Lab tab — investigation workspace for analyzing runs within a cohort."""

    MAX_PLOTTED = 8     # Soft cap on loss-curve overlay; readability past this gets bad

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ══════════════════════════════════════════════════════════════

    def ip_setup_early(self, ip):
        if not hasattr(self.form, 'lab_cohort_batch_id'):
            self.form.lab_cohort_batch_id = None
        if not hasattr(self.form, 'lab_plotted_runs'):
            self.form.lab_plotted_runs    = []
        if not hasattr(self.form, 'lab_filter_text'):
            self.form.lab_filter_text     = ""

    def ip_activated(self, ip):
        if self.form.lab_cohort_batch_id is None:
            self.form.lab_cohort_batch_id = self.query_latest_batch_id()
        self.refresh_all()

    # ══════════════════════════════════════════════════════════════
    # TAB PANES
    # ══════════════════════════════════════════════════════════════

    def cohort(self, parent) -> None:
        """Left pane — cohort picker (which batch to analyze)."""
        Title(parent, "Cohort", glow=True)
        Body(parent, "Pick a batch to analyze:")
        card = CardCol(parent, flex_height=1)
        grid = PowerGrid(card, name="grid_lab_cohort", flex_height=1)
        grid.on_row_click(self.on_cohort_selected, "Batch")
        self.populate_cohort_grid()

    def runs(self, parent) -> None:
        """Middle pane — filtered runs in the current cohort."""
        Title(parent, "Runs", glow=True, name="lbl_lab_runs_title")
        filter_row = Row(parent)
        Body(filter_row, "Filter:")
        TextBox(
            filter_row,
            placeholder = "type to filter (any column)…",
            name        = "txt_lab_filter",
            on_submit   = self.on_filter_submitted,
            on_change   = self.on_filter_changed,
            flex_width  = 1,
        )
        card = CardCol(parent, flex_height=1)
        grid = PowerGrid(card, name="grid_lab_runs", flex_height=1)
        grid.on_row_click(self.on_run_plotted, "Run")
        self.populate_runs_grid()

    def viz(self, parent) -> None:
        """Right pane — loss-curve overlay of plotted runs."""
        Title(parent, "Loss Curves", glow=True, name="lbl_lab_viz_title")
        Body(parent, "", name="lbl_lab_viz_status")
        self.render_viz_content(parent)

    # ══════════════════════════════════════════════════════════════
    # COHORT SELECTION
    # ══════════════════════════════════════════════════════════════

    def on_cohort_selected(self, batch_id):
        self.form.lab_cohort_batch_id = batch_id
        self.form.lab_plotted_runs    = []
        self.refresh_runs_pane()
        self.refresh_viz_pane()

    def populate_cohort_grid(self):
        grid = self.form.widgets.get("grid_lab_cohort")
        if not grid:                                                                                    return
        rows = self.query_cohort_list()
        if not rows:
            grid.set_data([["No batches yet"]])
            return
        current  = self.form.lab_cohort_batch_id
        header   = ["Batch", "Name", "Runs"]
        data     = [header]
        for r in rows:
            name   = r["batch_name"] if r["batch_name"] else f"Batch {r['batch_id']}"
            marker = "▶ " if r["batch_id"] == current else "   "
            data.append([r["batch_id"], marker + name, r["completed_runs"] or 0])
        grid.set_data(data)

    # ══════════════════════════════════════════════════════════════
    # FILTER
    # ══════════════════════════════════════════════════════════════

    def on_filter_submitted(self, text):
        self.form.lab_filter_text = text.lower().strip()
        self.populate_runs_grid()

    def on_filter_changed(self, text):
        self.form.lab_filter_text = text.lower().strip()
        self.populate_runs_grid()

    # ══════════════════════════════════════════════════════════════
    # RUNS GRID (middle pane)
    # ══════════════════════════════════════════════════════════════

    def populate_runs_grid(self):
        grid = self.form.widgets.get("grid_lab_runs")
        if not grid:                                                                                    return
        batch_id = self.form.lab_cohort_batch_id
        if batch_id is None:
            grid.set_data([["Select a batch from the left"]])
            return
        rows = self.query_cohort_runs(batch_id)
        if not rows:
            grid.set_data([["No completed runs in this cohort yet"]])
            return
        filtered = self.apply_filter(rows, self.form.lab_filter_text)
        plotted  = set(self.form.lab_plotted_runs)
        header   = ["Plt", "Run", "Optimizer", "Loss", "Arch", "LR", "MAE", "Acc%", "Epochs"]
        data     = [header]
        for r in filtered:
            run_id = r["run_id"]
            marker = "●" if run_id in plotted else ""
            data.append([
                marker,
                run_id,
                r["optimizer"]          or "—",
                r["loss_function"]      or "—",
                r["architecture"]       or "—",
                smart_format(r["learning_rate"]) if r["learning_rate"] is not None else "—",
                smart_format(r["best_mae"])      if r["best_mae"]      is not None else "—",
                r["accuracy"]           if r["accuracy"]    is not None else "—",
                r["epoch_count"]        or "—",
            ])
        self.update_runs_title(len(filtered), len(rows))
        grid.set_data(data)

    def update_runs_title(self, shown, total):
        lbl = self.form.widgets.get("lbl_lab_runs_title")
        if not lbl:                                                                                     return
        if shown == total:
            lbl.set_text(f"Runs ({total})")
        else:
            lbl.set_text(f"Runs ({shown} of {total})")

    def apply_filter(self, rows, filter_text):
        """Case-insensitive substring match across every field. Empty filter = all rows."""
        if not filter_text:                                                                             return rows
        out = []
        for r in rows:
            haystack = " ".join(str(v).lower() for v in dict(r).values() if v is not None)
            if filter_text in haystack:
                out.append(r)
        return out

    # ══════════════════════════════════════════════════════════════
    # RUN PLOT TOGGLE (clicking a run adds/removes its curve)
    # ══════════════════════════════════════════════════════════════

    def on_run_plotted(self, run_id):
        plotted = self.form.lab_plotted_runs
        if run_id in plotted:
            self.form.lab_plotted_runs = [r for r in plotted if r != run_id]
        elif len(plotted) >= self.MAX_PLOTTED:
            return
        else:
            plotted.append(run_id)
        self.populate_runs_grid()
        self.refresh_viz_pane()

    # ══════════════════════════════════════════════════════════════
    # VIZ PANE (right)
    # ══════════════════════════════════════════════════════════════

    def refresh_viz_pane(self):
        self.form.set_pane(2, self.viz)

    def refresh_runs_pane(self):
        self.form.set_pane(1, self.runs)

    def refresh_all(self):
        self.populate_cohort_grid()
        self.populate_runs_grid()
        self.refresh_viz_pane()

    def render_viz_content(self, parent):
        plotted = self.form.lab_plotted_runs
        if not plotted:
            Body(parent, "Click runs in the middle pane to plot their loss curves.")
            return
        series = []
        for run_id in plotted:
            points = self.query_epoch_history(run_id)
            if not points:                                                                              continue
            series.append({
                "label": f"Run {run_id}",
                "x":     [p["epoch"] for p in points],
                "y":     [p["mae"]   for p in points],
            })
        if not series:
            Body(parent, "Plotted runs have no epoch history yet.")
            return
        Body(parent, f"{len(series)} run{'s' if len(series) != 1 else ''} plotted (max {self.MAX_PLOTTED})")
        chart = Chart(parent, flex_height=1)
        chart.set_data(series, x_label="Epoch", y_label="MAE")

    # ══════════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════════

    def query_latest_batch_id(self):
        db_path = self.get_db_path()
        if not db_path:                                                                                 return None
        conn = sqlite3.connect(db_path)
        row  = conn.execute("SELECT batch_id FROM batch_specs ORDER BY created_at DESC LIMIT 1").fetchone()
        conn.close()
        return row[0] if row else None

    def query_cohort_list(self):
        """Batches in the project, with completed-run counts so user can pick a meaty cohort."""
        db_path = self.get_db_path()
        if not db_path:                                                                                 return []
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT s.batch_id, s.batch_name, "
            "       (SELECT COUNT(*) FROM batch_history h "
            "        WHERE h.batch_id = s.batch_id AND status = 'completed') AS completed_runs "
            "FROM batch_specs s "
            "ORDER BY s.created_at DESC"
        ).fetchall()
        conn.close()
        return rows

    def query_cohort_runs(self, batch_id):
        """All completed runs in this batch with the columns Lab cares about."""
        db_path = self.get_db_path()
        if not db_path:                                                                                 return []
        conn             = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT run_id, optimizer, loss_function, architecture, "
            "       learning_rate, best_mae, accuracy, epoch_count "
            "FROM batch_history "
            "WHERE batch_id = ? AND status = 'completed' "
            "ORDER BY best_mae ASC",
            (batch_id,)
        ).fetchall()
        conn.close()
        return rows

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