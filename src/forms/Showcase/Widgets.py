# Widgets.py  NEW: Self-documenting widget showcase pane
from ipui import *

class EZ_Pane(_basePane):
    """
    desc:        Auto-discovers every widget in IPUI and displays its docstring and source.
    when_to_use: The Showcase tab. Never goes stale — add a widget, it appears.
    best_for:    Proving that self-documenting frameworks aren't a myth.
    example:     (this IS the example)
    api:         (none — it just works)
    """

    def ip_setup_pane(self):
        self.catalog = WidgetCatalog()

    def catalog_grid(self, parent):
        """Main pane — DataGrid of all discovered widgets."""
        Title(parent, "Widget Catalog", glow=True)
        Body(parent, f"{len(self.catalog.entries)} widgets discovered at runtime")

        card = CardCol(parent, height_flex=True, scrollable=True)
        grid = PowerGrid(card, name="grid_widgets")
        grid.set_data(self.catalog.as_grid_data())
        grid.set_column_max("Description", 500)
        grid.on_row_click(self.on_widget_selected, "Widget")

        self.attach_tooltips(grid)

    def detail(self, parent):
        """Right pane — selected widget detail card."""
        Title(parent, "Widget Detail", glow=True)
        Body(parent, "Click a widget to inspect it.", name="lbl_widget_detail")

    def code(self, parent):
        """Right pane — selected widget detail card."""
        Title(parent, "Source Code", glow=True)
        Body(parent, "Click a widget to inspect it.", name="lbl_widget_detail")

    # ══════════════════════════════════════════════════════════════
    # INTERACTION
    # ══════════════════════════════════════════════════════════════

    def on_widget_selected(self, widget_name):
        """Show full widget info in the detail pane."""
        entry = self.catalog.entry_for(widget_name)
        if not entry:
            return

        self.form.set_pane(1, self.show_detail  , entry)
        self.form.set_pane(2, self.show_code    , entry)

    def show_detail(self, parent, entry):
        """Build the detail pane for a selected widget."""
        Title(parent, entry["name"], glow=True)
        Body(parent, f"Discovered live from {entry['file']}  ·  {entry['lines']} lines")

        sub = CardCol(parent)
        if entry["desc"]:        Body(sub, entry["desc"])
        if entry["when_to_use"]: self.field(sub, "When to use", entry["when_to_use"])
        if entry["best_for"]:    self.field(sub, "Best for",    entry["best_for"])

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

    def show_code(self, parent, entry):
        parent.pad=0
        Title(parent, "  Source Code:", glow=True)
        Body(parent, f"  {entry['lines']} lines")
        sub = Col(parent,  scrollable=True, color_bg=Style.COLOR_PAL_GRAY_950)
        CodeBox(sub, data=entry.get("source", ""))

    def field(self, parent, label, value):
        """Render a label: value pair."""
        Heading(parent, f"{label}:")
        Body(parent, value)

    # ══════════════════════════════════════════════════════════════
    # TOOLTIPS
    # ══════════════════════════════════════════════════════════════

    def attach_tooltips(self, grid):
        """Attach hover tooltips to each grid row showing source preview."""
        return
        for item in grid.row_widgets:
            row_data = item.get("_row_data", {})
            name     = row_data.get("Widget", "")
            entry    = self.catalog.entry_for(name)
            if entry and hasattr(item, "widget"):
                item["widget"].tool_tip_huge = TooltipWidget(name, entry)