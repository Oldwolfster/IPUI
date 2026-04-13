from __future__ import annotations

from ipui import *
from ipui.widgets.Label import Detail


class Magic(_BaseTab):

    def ip_setup_pane(self):
        if self.form.pipeline_read("magic_mode") is None:
            self.form.pipeline_set("magic_mode", "pipeline")

    # ============================================================
    # LEFT PANE (Teaching)
    # ============================================================

    def debug_magic_teach(self, parent):
        self.magic_globals(parent)
        self.magic_teaching_cards(parent)

    def magic_globals(self, parent):
        header = Row(parent, justify_spread=True)
        Title(header, "Magic — Framework Tracking", glow=True)

        btns = Row(parent)

        Button(btns, "Pipeline", color_bg=Style.COLOR_TAB_BG, on_click=lambda: self.set_mode("pipeline"))
        Button(btns, "Registry", color_bg=Style.COLOR_TAB_BG, on_click=lambda: self.set_mode("registry"))
        Button(btns, "DAG",      color_bg=Style.COLOR_TAB_BG, on_click=lambda: self.set_mode("dag"))
        Button(btns, "Refresh",  color_bg=Style.COLOR_PAL_GREEN_DARK, on_click=self.refresh)

    def magic_teaching_cards(self, parent):
        mode = (self.form.pipeline_read("magic_mode") or "pipeline").lower()

        if mode == "registry":
            self.teach_registry(parent)
        elif mode == "dag":
            self.teach_dag(parent)
        else:
            self.teach_pipeline(parent)

    def teach_pipeline(self, parent):
        card = CardCol(parent, width_flex=True)
        Title(card, "Data Pipeline", glow=True)
        Body(card, "What it is", glow=True)
        Detail(card, "• The framework’s key/value store (single source of truth).")
        Detail(card, "• UI reads from it; user actions write to it.")
        Spacer(card)

        card2 = CardCol(parent, width_flex=True)
        Body(card2, "Why it exists", glow=True)
        Detail(card2, "• Eliminates 'where did that value come from?' confusion.")
        Detail(card2, "• Makes state visible + debuggable in one place.")
        Spacer(card2)

        card3 = CardCol(parent, width_flex=True)
        Body(card3, "Common mistakes", glow=True)
        Detail(card3, "• Setting a key no one listens to (no derives / no reads).")
        Detail(card3, "• Typos in keys become silent bugs without tooling.")

    def teach_registry(self, parent):
        card = CardCol(parent, width_flex=True)
        Title(card, "Named Widgets Registry", glow=True)
        Body(card, "What it is", glow=True)
        Detail(card, "• Every named widget is tracked automatically.")
        Detail(card, "• Access anything by name: form.widgets['widget_name']")
        Spacer(card)

        card2 = CardCol(parent, width_flex=True)
        Body(card2, "Why it matters", glow=True)
        Detail(card2, "• No passing widget references around.")
        Detail(card2, "• No globals. No self.btn_save_ref_copy_backup_final.")
        Spacer(card2)

        card3 = CardCol(parent, width_flex=True)
        Body(card3, "Common mistakes", glow=True)
        Detail(card3, "• Forgetting to give the widget a name=...")
        Detail(card3, "• Looking on the wrong form instead of the target form's widgets.")

    def teach_dag(self, parent):
        card = CardCol(parent, width_flex=True)
        Title(card, "Reactive DAG", glow=True)
        Body(card, "What it is", glow=True)
        Detail(card, "• A directed acyclic graph of updates.")
        Detail(card, "• Pipeline keys trigger derives. Derives update widgets.")
        Spacer(card)

        card2 = CardCol(parent, width_flex=True)
        Body(card2, "Why it matters", glow=True)
        Detail(card2, "• Change one source value, downstream UI updates predictably.")
        Detail(card2, "• No manual callback spaghetti for every tiny screen change.")
        Spacer(card2)

        card3 = CardCol(parent, width_flex=True)
        Body(card3, "Common mistakes", glow=True)
        Detail(card3, "• Triggers point at the wrong pipeline keys.")
        Detail(card3, "• The derive target is unnamed, so nothing can be updated.")

    def set_mode(self, mode):
        self.form.pipeline_set("magic_mode", mode)
        self.form.set_pane(0, self.debug_magic_teach)
        self.form.set_pane(1, self.debug_magic_show)
        self.refresh()

    # ============================================================
    # RIGHT PANE (Data / UI)
    # ============================================================

    def debug_magic_show(self, parent):
        mode = (self.form.pipeline_read("magic_mode") or "pipeline").lower()

        if mode == "registry":
            self.debug_magic_registry(parent)
        elif mode == "dag":
            self.debug_magic_dag(parent)
        else:
            self.debug_magic_pipeline(parent)

    def debug_magic_pipeline(self, parent):
        panel = CardCol(parent, name="magic_show_panel", width_flex=True, height_flex=True)

        Title(panel, "Pipeline Store", glow=True)
        Detail(panel, "Key/value state tracked by the framework.")
        PowerGrid(panel, name="magic_grid_pipeline_data", height_flex=True)

        self.refresh_pipeline_data(self.get_target())

    def debug_magic_registry(self, parent):
        panel = CardCol(parent, name="magic_show_panel", width_flex=True, height_flex=True)

        Title(panel, "Widgets Registry", glow=True)
        Detail(panel, "Every named widget tracked on the target form.")
        PowerGrid(panel, name="magic_grid_registry_data", height_flex=True)

        self.refresh_registry_data(self.get_target())

    def debug_magic_dag(self, parent):
        panel = CardCol(parent, name="magic_show_panel", width_flex=True, height_flex=True)

        Title(panel, "Reactive DAG", glow=True)
        Detail(panel, "Derives wired from pipeline keys to named widgets.")
        PowerGrid(panel, name="magic_grid_dag_data", height_flex=True)


    # ============================================================
    # Data builders
    # ============================================================

    def refresh(self):
        target = self.get_target()
        if not target:
            return

        mode = (self.form.pipeline_read("magic_mode") or "pipeline").lower()

        if mode == "registry":
            self.refresh_registry_data(target)
        elif mode == "dag":
            self.refresh_dag_data(target)
        else:
            self.refresh_pipeline_data(target)

    def refresh_pipeline_data(self, target):
        grid = self.form.widgets.get("magic_grid_pipeline_data")
        if not grid or not target:
            return

        rows = []
        data = getattr(target.pipeline, "data", {}) or {}

        for k in sorted(data.keys(), key=lambda x: str(x)):
            v = data.get(k)
            rows.append([str(k), self.safe_cell(v)])

        grid.set_data(rows, columns=["key", "value"])

    def refresh_registry_data(self, target):
        grid = self.form.widgets.get("magic_grid_registry_data")
        if not grid or not target:
            return

        rows = []
        widgets = getattr(target, "widgets", {}) or {}

        for name, widget in sorted(widgets.items()):
            rows.append([
                name,
                type(widget).__name__,
                self.safe_cell(getattr(widget, "text", "")),
            ])

        grid.set_data(rows, columns=["name", "type", "text"])

    def refresh_dag_data(self, target):
        grid = self.form.widgets.get("magic_grid_dag_data")
        if not grid or not target:
            return

        rows = []
        derives  = getattr(target.pipeline, "derives", {}) or {}
        data     = getattr(target.pipeline, "data", {}) or {}
        widgets = getattr(target, "widgets", {}) or {}

        for control_name in sorted(derives.keys()):
            entry    = derives[control_name]
            prop     = entry.get("property", "")
            compute  = entry.get("compute")
            triggers = entry.get("triggers", []) or []

            trigger_values = [data.get(t) for t in triggers]

            result = ""
            if compute:
                try:
                    result = self.safe_cell(compute(*trigger_values))
                except Exception as ex:
                    result = f"<error: {ex}>"

            rows.append([
                control_name,
                "Y" if control_name in widgets else "N",
                prop,
                compute.__name__ if compute else "",
                ", ".join(str(t) for t in triggers),
                self.safe_cell(trigger_values),
                result,
            ])

        print(f"rows={rows}")
        grid.set_data(
            rows,
            columns=["target", "bound", "compute", "triggers", "current_values", "result"]
            #columns = ["target", "bound", "property", "compute", "triggers", "current_values", "result"]
        )

    # ============================================================
    # Helpers
    # ============================================================

    def get_target(self):
        if hasattr(self.form, "target"):
            return self.form.target()
        return getattr(IPUI, "debug_target", None)

    def safe_cell(self, value):
        MAX_LEN = 120
        try:
            s = repr(value)
        except Exception:
            s = str(value)
        s = s.replace("\n", " ")
        return s[:MAX_LEN]