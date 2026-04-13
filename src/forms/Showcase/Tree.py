from ipui import *

class Tree(_BaseTab):

    # ══════════════════════════════════════════════════════════════
    # PANE 1 — The Tree
    # ══════════════════════════════════════════════════════════════

    def widget_tree(self, parent):
        header = Row(parent, justify_spread=True)
        Title(header, "Widget Tree", glow=True)
        btn = Button(header, "Refresh",
            color_bg = Style.COLOR_PAL_GREEN_DARK)
        btn.on_click_me(self.refresh_tree)

        PowerGrid(parent, name="grid_tree", height_flex=True)
        self.refresh_tree()

    # ══════════════════════════════════════════════════════════════
    # PANE 2 — Widget Detail
    # ══════════════════════════════════════════════════════════════

    def widget_detail(self, parent):
        Title(parent, "Widget Detail", glow=True)
        PowerGrid(parent, name="grid_detail", height_flex=True)
        Body(parent, "← Click a row to inspect",
            name = "lbl_detail_hint")

    # ══════════════════════════════════════════════════════════════
    # TREE WALKER
    # ══════════════════════════════════════════════════════════════

    def refresh_tree(self):
        rows = []
        self.walk(self.form, 0, rows)
        grid = self.form.widgets.get("grid_tree")
        if not grid:
            return
        columns = ["Tree", "Type", "Name", "Kids", "Size", "wid"]
        grid.set_data(rows, columns=columns)
        grid.on_row_click(self.on_tree_row_clicked, "wid")

    def walk(self, widget, depth, rows):
        indent      = "  " * depth + self.node_icon(widget)
        wtype       = widget.widget_type
        label       = widget.display_name
        kids        = len(widget.children)
        rect        = widget.rect
        size        = f"{rect.width}x{rect.height}" if rect else "—"
        rows.append([indent, wtype, label, kids, size, widget.widget_id])
        for child in widget.children:
            self.walk(child, depth + 1, rows)



    def walk(self, widget, depth, rows):
        indent      = "  " * depth + self.node_icon(widget)
        wtype       = widget.widget_type
        reg_name    = widget.display_name
        label       = reg_name or str(widget.text or "")[:30]
        kids        = len(widget.children)
        rect        = widget.rect
        size        = f"{rect.width}x{rect.height}" if rect else "—"
        rows.append([indent, wtype, label, kids, size, widget.widget_id])
        for child in widget.children:
            self.walk(child, depth + 1, rows)


    def node_icon(self, widget):
        if widget.children:
            return "▼ "
        return "· "

    # ══════════════════════════════════════════════════════════════
    # ROW CLICK — show widget properties
    # ══════════════════════════════════════════════════════════════

    def on_tree_row_clicked(self, wid):
        widget = self.form.widget_registry.get(wid)
        if not widget:
            return
        grid = self.form.widgets["grid_detail"]
        props = self.gather_properties(widget)
        props += self.gather_derives(widget)  # NEW
        grid.set_data(props, columns=["Property", "Value"])

    def show_widget_detail(self, widget):
        grid = self.form.widgets["grid_detail"]
        props = self.gather_properties(widget)
        grid.set_data(props, columns=["Property", "Value"])

    def gather_properties(self, widget):
        rect = widget.rect
        props = [
            ["type",        type(widget).__name__],
            ["name",        str(widget.display_name)],
            ["text",        str(widget.text or '—')[:40],],
            ["visible",     str(widget.visible)],
            ["enabled",     str(widget.enabled)],
            ["children",    str(len(widget.children))],
            ["width_flex",  str(widget.width_flex)],
            ["height_flex", str(widget.height_flex)],
            ["pad",         str(widget.pad)],
            ["border",      str(widget.border)],
            ["x",           str(rect.x) if rect else "—"],
            ["y",           str(rect.y) if rect else "—"],
            ["width",       str(rect.width) if rect else "—"],
            ["height",      str(rect.height) if rect else "—"],
            ["font",        str(getattr(widget, 'font', '—'))],
            ["scrollable",  str(getattr(widget, 'scrollable', False))],
            ["horizontal",  str(getattr(widget, 'horizontal', False))],
            ["color_bg",    str(widget.color_bg)],
        ]
        return props

    def gather_derives(self, widget):
        derives = []
        reg_name = widget.display_name
        if not reg_name:
            return derives
        entry = self.form.pipeline.derives.get(reg_name)
        if entry:
            derives.append(["derive target", "YES"])
            derives.append(["  property", entry["property"]])
            derives.append(["  compute", entry["compute"].__name__])
            derives.append(["  triggers", ", ".join(entry["triggers"])])
        for key, entry in self.form.pipeline.derives.items():
            if entry["compute"].__name__ and reg_name in (entry.get("triggers") or []):
                derives.append(["triggers →", key])
        pipe_val = self.form.pipeline.data.get(reg_name)
        if pipe_val is not None:
            derives.append(["pipeline value", str(pipe_val)[:40]])
        return derives


    # ══════════════════════════════════════════════════════════════
    # Auto Refresh
    def ip_think(self, ip):
        if ip.is_active_pane: self.refresh_tree()
    # ══════════════════════════════════════════════════════════════