# Reference.py  Update: one pane per mode, shared menu, green active button

from datetime import datetime

from ipui import *
from ipui.widgets.CodeBox import CodeBox
from ipui.utils.WidgetCatalog import WidgetCatalog


class Reference(_BaseTab):

    def ip_setup_pane(self):
        self.catalog           = WidgetCatalog()
        self.catalog_loaded_at = datetime.now()
        self.active_mode       = "widgets"

    # ══════════════════════════════════════════════════════════════
    # SHARED MENU
    # ══════════════════════════════════════════════════════════════

    def build_menu(self, parent):
        row = Row(parent, justify_center=True)
        modes = [
            ("Widgets",  self.pane_widgets),
            ("ReadMe",   self.pane_markdown),
            ("Pipeline", self.show_stub),
            ("Examples", self.show_stub),
            ("Layout",   self.pane_markdown),
        ]
        for label, builder in modes:
            is_active = (label.lower() == self.active_mode)
            color     = Style.COLOR_PAL_GREEN_DARK if is_active else Style.COLOR_TAB_BG
            if builder:
                btn = Button(row, label, color_bg=color, width_flex=1,
                             on_click=lambda b=builder, l=label: self.set_mode(l.lower(), b))
            else:
                btn = Button(row, label, color_bg=color, width_flex=1,
                             on_click=self.show_stub)

    def set_mode(self, mode, builder):
        self.active_mode = mode
        self.form.set_pane(0, builder)
        self.form.set_pane(1, self.ref_detail)

    def md_file_for_mode(self):
        files = {
            "readme": "docs/README.md",
            "layout": "docs/IPUI_Layout_Guide_Original_Flex.md",
        }
        return files.get(self.active_mode)

    # ══════════════════════════════════════════════════════════════
    # PANE: Widgets (default / startup)
    # ══════════════════════════════════════════════════════════════

    def debug_ref(self, parent):
        self.pane_widgets(parent)

    def pane_widgets(self, parent):
        self.build_menu(parent)
        Title(parent, "Widget Catalog", glow=True)
        Body(parent, f"{len(self.catalog.entries)} widgets discovered at runtime")

        card = CardCol(parent, height_flex=True, scrollable=True)
        grid = PowerGrid(card, name="grid_ref_widgets")
        grid.set_data(self.catalog.as_grid_data())
        grid.set_column_max("Description", 500)
        grid.on_row_click(self.handle_widget_selected, "Widget")

    # ══════════════════════════════════════════════════════════════════
    # PANE: Markdown - no specific method needed.. just set active_mode
    # ══════════════════════════════════════════════════════════════════


    def pane_markdown(self, parent):
        self.build_menu(parent)
        from ipui.widgets.MarkdownTOC import MarkdownTOC
        MarkdownTOC(parent, data=self.md_file_for_mode(), height_flex=True,
                    on_change=self.handle_toc_selected,
                    initial_value=getattr(self, 'active_toc_item', None))

    # ══════════════════════════════════════════════════════════════
    # TOC callback (placeholder until MarkdownBody)
    # ══════════════════════════════════════════════════════════════

    def handle_toc_selected(self, title):
        self.active_toc_item = title
        self.form.set_pane(1, self.pane_md_section, title)

    def pane_md_section(self, parent, title):
        from ipui.widgets.MarkdownBody import MarkdownBody
        card = CardCol(parent, height_flex=True, scrollable=True)
        MarkdownBody(card, data=self.md_file_for_mode(), text=title)

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE
    # ══════════════════════════════════════════════════════════════

    def ref_detail(self, parent):
        Title(parent, "Detail", glow=True)
        Body(parent, "Click a widget to inspect it.",
             name="lbl_ref_detail")

    # ══════════════════════════════════════════════════════════════
    # WIDGET DETAIL
    # ══════════════════════════════════════════════════════════════

    def handle_widget_selected(self, widget_name):
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
        self.form.show_modal("Coming Soon")