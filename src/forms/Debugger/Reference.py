# Ref.py  NEW: Debug reference pane with button menu and Widget Catalog

from datetime import datetime

from ipui import *
from ipui.widgets.CodeBox import CodeBox
from ipui.utils.WidgetCatalog import WidgetCatalog


class Ref(_basePane):

    def initialize(self):
        self.catalog            = WidgetCatalog()
        self.catalog_loaded_at  = datetime.now()

        if self.form.pipeline_read("ref_mode") is None:
            self.form.pipeline_set("ref_mode", "widgets")

    # ══════════════════════════════════════════════════════════════
    # LEFT PANE
    # ══════════════════════════════════════════════════════════════

    def debug_ref(self, parent):
        mode = (self.form.pipeline_read("ref_mode") or "widgets").lower()

        if mode == "readme":
            #self.build_markdown(parent, "ipui/docs/README.md")
            self.form.set_pane(1, self.build_markdown_detail, "docs/README.md")
        elif mode == "layout":
            self.build_markdown(parent, "IPUI_Layout_Guide_Original_Flex.md")
        else:
            self.build_widgets(parent)

    def build_markdown_detail(self, parent, file_path):
        from ipui.widgets.MarkdownView import MarkdownView

        card = CardCol(parent, height_flex=True, scrollable=True)
        MarkdownView(card, data=file_path)


    def ref_globals(self, parent):
        row = Row(parent, justify_center=True)

        Button(row, "Widgets",  color_bg=Style.COLOR_TAB_BG, width_flex=1, on_click=lambda: self.set_mode("widgets"))
        Button(row, "ReadMe",   color_bg=Style.COLOR_TAB_BG, width_flex=1, on_click=lambda: self.set_mode("readme"))
        Button(row, "Pipeline", color_bg=Style.COLOR_TAB_BG, width_flex=1, on_click=self.show_stub)
        Button(row, "Examples", color_bg=Style.COLOR_TAB_BG, width_flex=1, on_click=self.show_stub)
        Button(row, "Layout",   color_bg=Style.COLOR_TAB_BG, width_flex=1, on_click=lambda: self.set_mode("layout"))

    def set_mode(self, mode):
        self.form.pipeline_set("ref_mode", mode)
        self.form.set_pane(0, self.debug_ref)
        self.form.set_pane(1, self.ref_detail)

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE
    # ══════════════════════════════════════════════════════════════

    def ref_detail(self, parent):
        Title(parent, "Detail", glow=True)
        Body(parent, "Click a widget to inspect it.",
            name="lbl_ref_detail")

    # ══════════════════════════════════════════════════════════════
    # ReadMe VIEW
    # ══════════════════════════════════════════════════════════════

    def build_markdown(self, parent, file_path):
        self.ref_globals(parent)

        from ipui.widgets.MarkdownView import MarkdownView
        card = CardCol(parent, height_flex=True, scrollable=True)
        MarkdownView(card, data=file_path)

    # ══════════════════════════════════════════════════════════════
    # WIDGETS VIEW
    # ══════════════════════════════════════════════════════════════

    def build_widgets(self, parent):
        self.ref_globals(parent)

        Title(parent, "Widget Catalog", glow=True)
        Body(parent, f"{len(self.catalog.entries)} widgets discovered at runtime")

        card = CardCol(parent, height_flex=True, scrollable=True)
        grid = PowerGrid(card, name="grid_ref_widgets")
        grid.set_data(self.catalog.as_grid_data())
        grid.set_column_max("Description", 500)
        grid.on_row_click(self.on_widget_selected, "Widget")

    def on_widget_selected(self, widget_name):
        entry = self.catalog.entry_for(widget_name)
        if not entry:
            return
        self.form.set_pane(1, self.show_detail, entry)

    def show_detail(self, parent, entry):
        Title(parent, entry["name"], glow=True)
        Body(parent, f"Discovered live from {entry['file']}  ·  {entry['lines']} lines  ·  {self.time_ago_text()}")

        sub = CardCol(parent)
        if entry["desc"]:
            Body(sub, entry["desc"])
        if entry["when_to_use"]:
            self.field(sub, "When to use", entry["when_to_use"])
        if entry["best_for"]:
            self.field(sub, "Best for", entry["best_for"])

        if entry["api"]:
            sub = CardCol(parent)
            Heading(sub, "API:")
            Body(sub, entry["api"])

        if entry.get("example"):
            sub = CardCol(parent)
            Heading(sub, "Example:")
            Body(sub, entry["example"])

        sub = CardCol(parent, height_flex=True, scrollable=True)
        Heading(sub, "Source:")
        CodeBox(sub, data=entry.get("source", ""))

    def field(self, parent, label, value):
        Heading(parent, f"{label}:")
        Body(parent, value)

    def time_ago_text(self):
        seconds = max(0, int((datetime.now() - self.catalog_loaded_at).total_seconds()))

        if seconds < 2:
            return "just now"
        if seconds < 60:
            return f"{seconds} seconds ago"

        minutes = seconds // 60
        if minutes == 1:
            return "1 minute ago"
        if minutes < 60:
            return f"{minutes} minutes ago"

        hours = minutes // 60
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"

    # ══════════════════════════════════════════════════════════════
    # STUBS
    # ══════════════════════════════════════════════════════════════

    def show_stub(self):
        self.form.show_modal("Coming Soon", None, min_seconds=1.69)