# Colosseum.py  NEW FILE  (replaces frmColosseum.py — _basePane migration)

import multiprocessing
import time

from forms.NeuroForge.custom_widgets.ProjectManager import ProjectManager
from ipui import *


NUM_CORES = multiprocessing.cpu_count() - 1

VARYING_PRIORITY = [
    "gladiator", "arena", "seed",
    "optimizer", "hidden_activation", "output_activation",
    "loss_function", "weight_initializer",
    "input_scaler", "target_scaler",
]


class EZ_Pane(_basePane):
    """Colosseum tab — real-time training monitoring with live charts and grids."""

    def initialize(self):
        """Load run details and determine varying columns for the active batch."""
        batch_id = getattr(self.form, 'active_batch_id', None)
        if batch_id:
            self.load_run_details(batch_id)
            self.determine_varying_columns()

    # ══════════════════════════════════════════════════════════════
    # TAB PANES  (names must match strings in FormNeuroForge.tab_data)
    # ══════════════════════════════════════════════════════════════

    def status(self, parent) -> None:
        """Left pane — core status grid and live training chart."""
        header = Row(parent, justify_spread=True)
        Title(header, "Batch Status", glow=True)
        row = Row(header, gap=6)
        TextBox(row, placeholder="Name Batch Here", name="txt_batch_name")
        TextBox(row, placeholder="Add Note Here",   name="txt_batch_note")

        sub       = CardCol(parent, height_flex=True, scrollable=True)
        core_rows = [["Core", "Run", "Epoch", "MAE", "Status"]]
        for i in range(NUM_CORES):
            core_rows.append([f"#{i+1}", "—", "—", "—", "idle"])
        PowerGrid(sub, data=core_rows, name="grid_cores")

        ChartWidget(parent, name="chart_live", height_flex=True)

    def runs(self, parent) -> None:
        """Middle pane — completed run results grid and detail chart."""
        header = Row(parent, justify_spread=True)
        Title(header, "Run Results", glow=True)
        Body(header, "— | — | —", name="lbl_run_header")

        table_card = CardCol(parent, height_flex=True)
        #PowerGrid(table_card, data=[["Waiting for results..."]], name="grid_runs")
        #table_card.on_click_me(self.on_runs_grid_clicked)
        grid = PowerGrid(table_card, data=[["Waiting for results..."]], name="grid_runs")  # NEW
        grid.on_row_click(self.show_run_detail, "Run")
        ChartWidget(parent, name="chart_detail", height_flex=True)

    def analysis(self, parent) -> None:
        """Right pane — selected run detail comparison grid."""
        header = Row(parent, justify_spread=True)
        Title(header, "Run Detail", glow=True)
        btn_clear = Button(header, "Clear",      color_bg=Style.COLOR_TAB_BG,        name="btnDetailClear")
        btn_clear.on_click_me(self.clear_detail)
        btn_scope = Button(header, "NeuroScope", color_bg=Style.COLOR_PAL_GREEN_DARK, name="btnDetailScope")
        btn_scope.on_click_me(self.launch_neuroscope)

        sub = CardCol(parent, height_flex=True)
        PowerGrid(sub, data=[["Select a run from results"]], name="grid_detail")



    # ══════════════════════════════════════════════════════════════
    # RUN DETAIL
    # ══════════════════════════════════════════════════════════════

    def show_run_detail(self, run_id: int) -> None:
        """Load and display detail for a selected run (supports 2-run comparison)."""
        import sqlite3
        form = self.form
        if not hasattr(form, 'selected_runs'):
            form.selected_runs = []
        form.selected_runs.insert(0, run_id)
        form.selected_runs = form.selected_runs[:2]

        db_path = str(form.active_project.path)
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            run_rows = []
            for rid in form.selected_runs:
                row = conn.execute(
                    "SELECT * FROM batch_history WHERE run_id = ?", (rid,)
                ).fetchone()
                if row:
                    run_rows.append(row)
            conn.close()
        except Exception:
            return
        if not run_rows:
            return

        grid = form.widgets.get("grid_detail")
        if not grid:
            return

        header = ["Field"] + [f"Run {r['run_id']}" for r in run_rows]
        rows   = [header]
        for key in run_rows[0].keys():
            line = self.format_detail_field(key, run_rows[0][key])
            if not line:
                continue
            name = line.split(":")[0]
            vals = [name]
            for r in run_rows:
                formatted = self.format_detail_field(key, r[key])
                val       = formatted.split(":", 1)[1].strip() if formatted else "—"
                vals.append(val)
            rows.append(vals)

        grid.data = rows
        grid.build()
        self.update_detail_chart()

    def update_detail_chart(self) -> None:
        """Update the detail chart with history for selected runs."""
        form  = self.form
        chart = form.widgets.get("chart_detail")
        if not chart:
            return
        states   = getattr(form, 'shard_states', {})
        selected = getattr(form, 'selected_runs', [])
        lines    = []
        for run_id in selected:
            rid   = str(run_id)
            state = states.get(rid, {})
            if state.get("history"):
                lines.append({
                    "label": self.build_run_label(rid),
                    "x":     list(range(1, len(state["history"]) + 1)),
                    "y":     state["history"],
                })
        if lines:
            chart.set_data(lines, x_label="Epoch", y_label="MAE")

    def clear_detail(self) -> None:
        """Clear the run detail grid and selection."""
        self.form.selected_runs = []
        grid = self.form.widgets.get("grid_detail")
        if grid:
            grid.data = [["Select a run from results"]]
            grid.build()

    def launch_neuroscope(self) -> None:
        """Launch external NeuroScope viewer for selected runs."""
        form = self.form
        if not hasattr(form, 'selected_runs') or not form.selected_runs:
            return
        import subprocess
        import os
        db_path = str(form.active_project.path)
        run_ids = ",".join(str(r) for r in form.selected_runs)
        subprocess.Popen([
            ProjectManager.NNA_PYTHON, ProjectManager.NNA_MAIN,
            "--mode", "neuroscope",
            "--db", db_path,
            "--run_ids", run_ids,
        ], cwd=ProjectManager.NNA_ROOT,
            env={**os.environ, "PYTHONPATH": ProjectManager.NNA_ROOT})

    # ══════════════════════════════════════════════════════════════
    # POLLING  (called from FormNeuroForge.update via tab_strip.tab())
    # ══════════════════════════════════════════════════════════════

    def poll_shards(self) -> None:
        """Read shard output files and update all displays."""
        from pathlib import Path
        form     = self.form
        temp_dir = Path.home() / ".neuroforge" / "temp"
        if not temp_dir.exists():
            return
        if not hasattr(form, 'shard_states'):
            form.shard_states = {}
        if not hasattr(form, 'file_positions'):
            form.file_positions = {}

        for mae_file in temp_dir.glob("mae_*"):
            run_id    = mae_file.name.replace("mae_", "").replace(".txt", "")
            new_lines = self.tail_read(mae_file, form.file_positions)
            if not new_lines:
                continue
            state = form.shard_states.get(run_id, {
                "phase": "LR Sweep", "display": "—", "mae": "—", "history": [],
            })
            for line in new_lines:
                self.parse_shard_line(state, line.strip())
            form.shard_states[run_id] = state

        self.update_display_slots()
        self.update_core_grid()
        self.check_chart_update()
        self.poll_completed_runs()
        self.log_shard_summary()

    def log_shard_summary(self) -> None:
        """Log count of active shards (currently disabled)."""
        pass

    # ══════════════════════════════════════════════════════════════
    # SHARD PARSING
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def parse_shard_line(state: dict, line: str) -> None:
        """Parse a single line from a shard output file into state."""
        if not line:
            return
        if line == "DONE":
            state["phase"] = "DONE"
        elif line.startswith("BEST_LR"):
            state["phase"]   = "Training"
            state["display"] = "0"
            state["mae"]     = "—"
        elif line.startswith("LR "):
            parts            = line.split(",")
            state["display"] = parts[0].strip()
            state["mae"]     = parts[1].strip() if len(parts) > 1 else "—"
        elif line.startswith("FAILED"):
            state["phase"]   = "FAILED"
            state["display"] = "—"
            state["mae"]     = line.replace("FAILED ", "")[:40]
        else:
            try:
                mae              = float(line)
                state["history"].append(mae)
                state["display"] = str(len(state["history"]))
                state["mae"]     = f"{mae:.6f}"
            except ValueError:
                pass

    @staticmethod
    def tail_read(path, file_positions: dict) -> list:
        """Read new lines from a file since last position."""
        key      = str(path)
        last_pos = file_positions.get(key, 0)
        try:
            with open(path, "r") as f:
                f.seek(last_pos)
                new_data = f.read()
                file_positions[key] = f.tell()
            return new_data.splitlines() if new_data else []
        except (IOError, OSError):
            return []

    # ══════════════════════════════════════════════════════════════
    # CHART UPDATES
    # ══════════════════════════════════════════════════════════════

    def check_chart_update(self) -> None:
        """Throttled check — update live chart if new data or 1s elapsed."""
        form   = self.form
        states = getattr(form, 'shard_states', {})
        if not any(s.get("history") for s in states.values()):
            return
        new_total = sum(len(s.get("history", [])) for s in states.values())
        old_total = getattr(form, 'last_chart_points', 0)
        now       = time.time()
        last      = getattr(form, 'last_chart_time', 0)
        if new_total != old_total or now - last >= 1.0:
            form.last_chart_time   = now
            form.last_chart_points = new_total
            self.update_chart()

    def update_chart(self) -> None:
        """Refresh the live training chart with current shard data."""
        form  = self.form
        chart = form.widgets.get("chart_live")
        if not chart:
            return
        states = getattr(form, 'shard_states', {})
        slots  = getattr(form, 'display_slots', [])
        lines  = []
        for run_id in slots:
            if not run_id:
                continue
            state = states.get(run_id, {})
            if state.get("history"):
                lines.append({
                    "label": self.build_run_label(run_id),
                    "x":     list(range(1, len(state["history"]) + 1)),
                    "y":     state["history"],
                })
        if lines:
            chart.set_data(lines, x_label="Epoch", y_label="MAE")

    # ══════════════════════════════════════════════════════════════
    # GRID UPDATES
    # ══════════════════════════════════════════════════════════════

    def update_display_slots(self) -> None:
        """Assign active runs to display slots, recycling finished ones."""
        form = self.form
        if not hasattr(form, 'display_slots'):
            form.display_slots = []
        slots  = form.display_slots
        states = form.shard_states
        shown  = {s for s in slots if s}
        new_ids = [rid for rid in states
                   if rid not in shown and states[rid]["phase"] != "DONE"]
        for new_id in new_ids:
            placed = False
            for i, slot_id in enumerate(slots):
                if slot_id and states.get(slot_id, {}).get("phase") == "DONE":
                    slots[i] = new_id
                    placed   = True
                    break
            if not placed:
                slots.append(new_id)

    def update_core_grid(self) -> None:
        """Refresh the core status grid with current shard states."""
        form = self.form
        grid = form.widgets.get("grid_cores")
        if not grid:
            return
        varying     = getattr(form, 'varying_columns', [])
        run_details = getattr(form, 'run_details', {})
        states      = getattr(form, 'shard_states', {})
        slots       = getattr(form, 'display_slots', [])

        header = ["Run"] + [c.replace("_", " ").title() for c in varying] + ["Epoch/LR", "MAE", "Status"]
        rows   = [header]
        for run_id in slots:
            if not run_id:
                continue
            state = states.get(run_id, {"display": "—", "mae": "—", "phase": "idle"})
            try:
                detail = run_details.get(int(run_id), run_details.get(run_id, {}))
            except ValueError:
                detail = {}
            context = [self.strip_prefix(detail.get(key, "—")) for key in varying]
            rows.append([run_id] + context + [state["display"], state["mae"], state["phase"]])

        if len(rows) == 1:
            rows.append(["—"] + ["—"] * len(varying) + ["—", "—", "idle"])
        grid.data = rows
        grid.build()

    def poll_completed_runs(self) -> None:
        """Query DB for completed runs and refresh the results grid."""
        import sqlite3
        form     = self.form
        batch_id = getattr(form, 'active_batch_id', None)
        if not batch_id:
            return
        db_path = str(form.active_project.path)
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT run_id, epoch_count, accuracy, best_mae, status "
                "FROM batch_history WHERE batch_id = ? ORDER BY best_mae",
                (batch_id,)
            ).fetchall()
            conn.close()
        except Exception:
            return

        completed = len([r for r in rows if r["status"] == "completed"])
        in_prog   = len([rid for rid, s in form.shard_states.items()
                         if s["phase"] in ("Training", "LR Sweep")])
        total     = len(form.run_details)
        queued    = max(0, total - completed - in_prog)

        lbl = form.widgets.get("lbl_run_header")
        if lbl:
            lbl.set_text(f"{completed} complete | {in_prog} in progress | {queued} queued")

        form.completed_runs = rows
        self.update_runs_grid()

    def update_runs_grid(self) -> None:
        """Refresh the completed runs grid."""
        form = self.form
        grid = form.widgets.get("grid_runs")
        if not grid:
            return
        varying     = getattr(form, 'varying_columns', [])
        run_details = getattr(form, 'run_details', {})
        rows_data   = getattr(form, 'completed_runs', [])

        header = ["Run"] + [c.replace("_", " ").title() for c in varying] + ["Epochs", "MAE", "Acc%"]
        rows   = [header]
        for r in rows_data:
            rid    = r["run_id"]
            detail = run_details.get(rid, run_details.get(str(rid), {}))
            context = [self.strip_prefix(detail.get(key, "—")) for key in varying]
            rows.append([
                rid, *context,
                r["epoch_count"] or "—",
                r["best_mae"]    if r["best_mae"]  is not None else "—",
                r["accuracy"]    if r["accuracy"]   is not None else "—",
            ])
        grid.data = rows
        grid.build()

    # ══════════════════════════════════════════════════════════════
    # DATA LOADING
    # ══════════════════════════════════════════════════════════════

    def load_run_details(self, batch_id: int) -> None:
        """Load run detail key/value pairs from the project database."""
        import sqlite3
        db_path = str(self.form.active_project.path)
        conn    = sqlite3.connect(db_path)
        rows    = conn.execute(
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

    def determine_varying_columns(self) -> None:
        """Find which run detail keys vary across runs (up to 3)."""
        form = self.form
        if not form.run_details:
            form.varying_columns = []
            return
        varying = []
        for key in VARYING_PRIORITY:
            values = {d.get(key) for d in form.run_details.values() if d.get(key)}
            if len(values) > 1:
                varying.append(key)
            if len(varying) >= 3:
                break
        form.varying_columns = varying

    # ══════════════════════════════════════════════════════════════
    # FORMAT HELPERS
    # ══════════════════════════════════════════════════════════════

    def build_run_label(self, run_id) -> str:
        """Build a short label for a run from its varying columns."""
        form        = self.form
        varying     = getattr(form, 'varying_columns', [])
        run_details = getattr(form, 'run_details', {})
        try:
            detail = run_details.get(int(run_id), run_details.get(run_id, {}))
        except ValueError:
            detail = {}
        parts = [self.strip_prefix(detail.get(key, "")) for key in varying]
        parts = [p for p in parts if p]
        return " · ".join(parts) if parts else f"Run {run_id}"

    @staticmethod
    def format_detail_field(key: str, val) -> str:
        """Format a single detail field for display, or None to skip."""
        skip_fields   = {"problem_type", "sample_count", "batch_id",
                         "created_at", "completed_at"}
        prefix_fields = {"optimizer", "weight_initializer", "loss_function",
                         "hidden_activation", "output_activation",
                         "target_scaler", "input_scalers"}
        rename_fields = {"convergence_condition": "Convg"}

        if key in skip_fields or key.startswith("target_"):
            return None
        name = rename_fields.get(key, key.replace("_", " ").title())
        if key in prefix_fields and val and isinstance(val, str):
            val = EZ_Pane.strip_prefix(val)
        return f"{name}: {smart_format(val)}"

    @staticmethod
    def strip_prefix(value) -> str:
        """Remove dimension prefix (e.g. 'optimizer_SGD' → 'SGD')."""
        if not isinstance(value, str):
            return str(value) if value else "—"
        return value.split("_", 1)[1] if "_" in value else value

    @staticmethod
    def clear_temp_folder() -> None:
        """Remove stale MAE files from the temp directory."""
        from pathlib import Path
        temp_dir = Path.home() / ".neuroforge" / "temp"
        if not temp_dir.exists():
            return
        for f in temp_dir.glob("mae_*"):
            try:
                f.unlink()
            except OSError:
                pass