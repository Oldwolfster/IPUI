# Ludus.py  Update: Batch drill-down + run comparison

import sqlite3
from datetime import datetime
from ipui import *


class EZ_Pane(_basePane):
    """Ludus tab — historical batch and run analysis across the project."""

    MAX_COMPARE = 4

    # ══════════════════════════════════════════════════════════════
    # TAB PANES  (names must match strings in FormNeuroForge.tab_data)
    # ══════════════════════════════════════════════════════════════

    def batches(self, parent) -> None:
        """Left pane — batch list."""
        Title(parent, "Batches", glow=True)
        card = CardCol(parent, height_flex=True)
        grid = PowerGrid(card, name="grid_batches", height_flex=True)
        grid.on_row_click(self.on_batch_selected, "Batch")
        self.load_batches()

    def batch_runs(self, parent) -> None:
        """Middle pane — run comparison."""
        Title(parent, "Run Comparison", glow=True)
        Body(parent, "", name="lbl_compare_status")
        Row(parent, name="row_remove_buttons")
        card = CardCol(parent, height_flex=True)
        PowerGrid(card, name="grid_comparison", height_flex=True)
        self.refresh_comparison()

    def best_runs(self, parent) -> None:
        """Right pane — top runs across all batches with chart."""
        Title(parent, "Best Runs", glow=True)
        sub = CardCol(parent, height_flex=True)
        PowerGrid(sub, data=[["Loading..."]], name="grid_proj_runs", height_flex=True)
        ChartWidget(parent, name="chart_proj_runs", height_flex=True)
        self.load_best_runs()

    # ══════════════════════════════════════════════════════════════
    # BATCH SELECTION — swap left pane to runs
    # ══════════════════════════════════════════════════════════════

    def on_batch_selected(self, batch_id) -> None:
        self.form.selected_batch_id = batch_id
        self.form.compared_runs     = []
        self.swap_pane(0, self.pane_batch_runs)()

    def pane_batch_runs(self, parent) -> None:
        """Left pane after batch click — runs for that batch."""
        batch_id = self.form.selected_batch_id
        header   = Row(parent, justify_spread=True)
        Title(header, f"Batch {batch_id}", glow=True)
        btn = Button(header, "Back", color_bg=Style.COLOR_TAB_BG)
        btn.on_click_me(self.swap_pane(0, self.batches))
        card = CardCol(parent, height_flex=True)
        grid = PowerGrid(card, name="grid_batch_runs", height_flex=True)
        grid.on_row_click(self.on_run_toggled, "Run")
        self.load_batch_runs(batch_id)

    # ══════════════════════════════════════════════════════════════
    # RUN TOGGLE — add/remove from comparison
    # ══════════════════════════════════════════════════════════════

    def on_run_toggled(self, run_id) -> None:
        compared = self.form.compared_runs
        ids      = [r["run_id"] for r in compared]
        if run_id in ids:
            self.form.compared_runs = [
                r for r in compared if r["run_id"] != run_id
            ]
        elif len(compared) >= self.MAX_COMPARE:
            return
        else:
            run = self.fetch_full_run(run_id)
            if run:
                compared.append(run)
        self.refresh_batch_runs()
        self.refresh_comparison()

    # ══════════════════════════════════════════════════════════════
    # BATCH RUNS GRID (left pane)
    # ══════════════════════════════════════════════════════════════

    def load_batches(self) -> None:
        rows = self.query_batches()
        if rows is None:
            return
        self.form.proj_batches = rows
        self.populate_batch_grid(rows)

    def populate_batch_grid(self, rows) -> None:
        grid = self.form.widgets.get("grid_batches")
        if not grid:
            return
        header = ["Batch", "Date", "Runs", "Best MAE"]
        data   = [header]
        for r in rows:
            date_str = self.format_date(r["created_at"])
            mae_str  = smart_format(r["best_mae"]) if r["best_mae"] is not None else "—"
            data.append([r["batch_id"], date_str, r["run_count"], mae_str])
        grid.set_data(data)

    def load_batch_runs(self, batch_id) -> None:
        rows = self.query_batch_runs(batch_id)
        grid = self.form.widgets.get("grid_batch_runs")
        if not grid:
            return
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
        if not lbl:
            return
        count = len(compared)
        if count == 0:
            lbl.set_text("Select runs from the left to compare")
        elif count >= self.MAX_COMPARE:
            lbl.set_text(f"{count} runs selected (max {self.MAX_COMPARE})")
        else:
            lbl.set_text(f"{count} run{'s' if count != 1 else ''} selected")

    def refresh_remove_buttons(self, compared):
        row = self.form.widgets.get("row_remove_buttons")
        if not row:
            return
        row.children.clear()
        for run in compared:
            rid = run["run_id"]
            btn = Button(row, f"Remove {rid}",
                color_bg = Style.COLOR_PAL_RED_DARK)
            btn.on_click_me(self.make_remove_click(rid))

    def make_remove_click(self, run_id):
        def clicked():
            self.form.compared_runs = [
                r for r in self.form.compared_runs
                if r["run_id"] != run_id
            ]
            self.refresh_batch_runs()
            self.refresh_comparison()
        return clicked

    def refresh_compare_grid(self, compared):
        grid = self.form.widgets.get("grid_comparison")
        if not grid:
            return
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
    # BEST RUNS (right pane)
    # ══════════════════════════════════════════════════════════════

    def load_best_runs(self) -> None:
        rows = self.query_best_runs()
        if rows is None:
            return
        self.form.proj_best_runs = rows
        self.populate_best_runs_grid(rows)
        self.populate_best_runs_chart(rows)

    def populate_best_runs_grid(self, rows) -> None:
        grid = self.form.widgets.get("grid_proj_runs")
        if not grid:
            return
        header = ["Run", "Batch", "Epochs", "MAE", "Acc%"]
        data   = [header]
        for r in rows:
            data.append([
                r["run_id"],
                r["batch_id"],
                r["epoch_count"] or "—",
                smart_format(r["best_mae"]),
                r["accuracy"] if r["accuracy"] is not None else "—",
            ])
        if len(data) == 1:
            data.append(["No completed runs yet"])
        grid.set_data(data)

    def populate_best_runs_chart(self, rows) -> None:
        chart = self.form.widgets.get("chart_proj_runs")
        if not chart or not rows:
            return
        maes = [r["best_mae"] for r in rows if r["best_mae"] is not None]
        if not maes:
            return
        chart.set_data([{
            "label": "Best MAE",
            "x":     list(range(len(maes))),
            "y":     maes,
        }], x_label="Rank", y_label="MAE")

    # ══════════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════════

    def query_batches(self):
        db_path = self.get_db_path()
        if not db_path:
            return None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT s.batch_id, s.batch_name, s.created_at, "
                "  s.gladiators, s.arenas, "
                "  (SELECT COUNT(*) FROM batch_history h "
                "   WHERE h.batch_id = s.batch_id) AS run_count, "
                "  (SELECT ROUND(MIN(best_mae), 4) FROM batch_history h "
                "   WHERE h.batch_id = s.batch_id) AS best_mae "
                "FROM batch_specs s ORDER BY s.created_at DESC"
            ).fetchall()
            conn.close()
            return rows
        except Exception:
            return None

    def query_batch_runs(self, batch_id):
        db_path = self.get_db_path()
        if not db_path:
            return None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT run_id, epoch_count, best_mae, "
                "       accuracy, runtime_seconds "
                "FROM batch_history "
                "WHERE batch_id = ? "
                "ORDER BY best_mae ASC",
                (batch_id,)
            ).fetchall()
            conn.close()
            return rows
        except Exception:
            return None

    def query_best_runs(self):
        db_path = self.get_db_path()
        if not db_path:
            return None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT run_id, batch_id, epoch_count, best_mae, "
                "       accuracy, runtime_seconds "
                "FROM batch_history "
                "WHERE best_mae IS NOT NULL "
                "ORDER BY best_mae ASC LIMIT 20"
            ).fetchall()
            conn.close()
            return rows
        except Exception:
            return None

    def fetch_full_run(self, run_id):
        db_path = self.get_db_path()
        if not db_path:
            return None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM batch_history WHERE run_id = ?",
                (run_id,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception:
            return None

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def get_db_path(self):
        project = getattr(self.form, 'active_project', None)
        if not project:
            return None
        return str(project.path)

    def get_compared_ids(self):
        compared = getattr(self.form, 'compared_runs', [])
        return {r["run_id"] for r in compared}

    @staticmethod
    def format_date(raw) -> str:
        if not raw:
            return "—"
        try:
            dt = datetime.fromisoformat(str(raw))
            return dt.strftime("%m/%d %H:%M")
        except Exception:
            return str(raw)[:10]