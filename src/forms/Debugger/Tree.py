# DebugTree.py  Widget tree inspector pane for FormDebugger
from email import header

from ipui import *
from ipui.utils.MgrClipboard import Clipboard


class Tree(_basePane):

    # ══════════════════════════════════════════════════════════════
    # DAG — Reactive updates
    # ══════════════════════════════════════════════════════════════

    DECLARATION_UPDATES = {
        "dbg_tree_title": {
            "property": "text",
            "compute":  "compute_title",
            "triggers": ["selected_wid"],
        },
    }



    def compute_title(self, selected_wid):
        target = self.get_target()
        if not target or not selected_wid:
            return "Widget Tree"
        widget = target.widget_registry.get(int(selected_wid))
        if not widget:
            return "Widget Tree"


        type_name = widget.widget_type

        name = self.reg_name(widget) or str(widget.text or "")[:30]
        return f"Widget Tree — {type_name}: {name} (wid {selected_wid})"


        return f"Widget Tree — {type_name}: {name} (wid {selected_wid})"

    # ══════════════════════════════════════════════════════════════
    # PANE 1 — Info (field legend)
    # ══════════════════════════════════════════════════════════════

    def info(self, parent):
        from ipui.widgets.Row import CardCol

        row = Row(parent)
        Button(row, "Flex", width_flex=2, color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=lambda: self.form.show_modal("Coming Soon!", min_seconds=1.69))
        Spacer(row, width_flex=3)
        Button(row, "Hide", width_flex=2, color_bg=Style.COLOR_TAB_BG,
               on_click=lambda: self.form.show_modal("Coming Soon!", min_seconds=1.69))

        Spacer(parent)
        card = CardCol(parent)
        Title(card, "Identity")
        Body(card, "wid  Widget ID")
        Body(card, "Tr   Tree depth")
        Body(card, "Type Widget class")
        Body(card, "Name Registry or auto")

        Spacer(parent)
        card = CardCol(parent)
        Title(card, "Sizing Intent")
        Heading(card, "Flex — Size relative to each other")
        Body(card, "fx   Flex width")
        Body(card, "fy   Flex height")
        Heading(card, "Intrinsic — Minimum content size")
        Body(card, "minX Intrinsic width")
        Body(card, "minY Intrinsic height")

        Spacer(parent)
        card = CardCol(parent)
        Title(card, "Actual Layout")
        Body(card, "rX   Actual X position")
        Body(card, "rY   Actual Y position")
        Body(card, "rW   Actual width")
        Body(card, "rH   Actual height")

    # ══════════════════════════════════════════════════════════════
    # PANE 2 — Widget Tree
    # ══════════════════════════════════════════════════════════════

    def debug_tree(self, parent):
        # Tree.py method: debug_tree  Update: add header with Copy button
        

        from ipui.widgets.Row import Row                                  
        from ipui.widgets.Button import Button                            
        from ipui.Style import Style                                      
        header = Row(parent, justify_spread=True)                         
        Title(header, "Widget Tree", glow=True, name="dbg_tree_title")   
        Button(header, "Copy1", color_bg=Style.COLOR_PAL_GREEN_DARK,
        on_click=self.copy_tree)
        #on_click=lambda: self.form.show_modal("Coming Soon!", min_seconds=1.69))
        PowerGrid(parent, name="dbg_tree_grid", height_flex=True)
        Body(parent, "Click row to inspect", name="dbg_tree_hint")
        self.refresh()

    def refresh(self):
        target = self.get_target()
        if not target:
            return
        rows = []
        self.walk(target, 0, rows)
        grid = self.form.widgets.get("dbg_tree_grid")
        if not grid:
            return
        cols = ["Tr", "Type", "Name", "fw", "fh", "minX", "minY", "rX", "rY", "rW", "rH", "wid"]
        grid.set_data(rows, columns=cols)
        grid.on_row_click(self.on_row_click, "wid")

    # ══════════════════════════════════════════════════════════════
    # PANE 3 — Widget Detail
    # ══════════════════════════════════════════════════════════════


    def details(self, parent):
        from ipui.widgets.Row import Row
        from ipui.widgets.Button import Button
        from ipui.Style import Style
        header = Row(parent, justify_spread=True)
        Title(header, "Widget Detail", glow=True)
        btn = Button(header, "Copy", color_bg=Style.COLOR_PAL_GREEN_DARK)
        #btn.on_click_me(self.copy_detail)
        btn.on_click = lambda: self.form.show_modal("Coming Soon!",  min_seconds=1.69)
        PowerGrid(parent, name="dbg_detail_grid", height_flex=True)
        Body(parent, "← Click a row", name="dbg_detail_hint")


    def copy_tree(self):
        grid = self.form.widgets.get("dbg_tree_grid")
        if not grid or not grid.data:
            return
        lines = []
        for row in grid.data:
            lines.append("  ".join(str(c) for c in row))
        Clipboard.copy("\n".join(lines))

    # Tree.py method: copy_detail  NEW: Copy detail grid to clipboard
    def copy_detail(self):
        grid = self.form.widgets.get("dbg_detail_grid")
        if not grid or not grid.data:
            return
        lines = []
        for row in grid.data:
            lines.append(f"{row[0]:25} {row[1]}")
        Clipboard.copy("\n".join(lines))

    def populate_detail_grid(self, widget):
        grid = self.form.widgets.get("dbg_detail_grid")
        if not grid:
            return
        props = [["type", type(widget).__name__]]
        for key, val in sorted(widget.__dict__.items()):
            props.append([key, str(val)[:60]])
        grid.set_data(props, columns=["Property", "Value"])

    # ══════════════════════════════════════════════════════════════
    # EVENTS — Row click
    # ══════════════════════════════════════════════════════════════

    def on_row_click(self, wid):
        self.form.pipeline_set("selected_wid", wid)
        target = self.get_target()
        if not target:
            return
        widget = target.widget_registry.get(wid)
        if not widget:
            return
        self.populate_detail_grid(widget)

    # ══════════════════════════════════════════════════════════════
    # TREE WALKER
    # ══════════════════════════════════════════════════════════════

    def walk(self, widget, depth, rows):
        indent = "  " * depth + self.icon(widget)
        rect   = widget.rect
        type_name = widget.widget_type
        name = self.clean_widget_tree(type_name, self.reg_name(widget) or widget.widget_type)
        rows.append([
            indent,
            type_name,
            name,
            widget.width_flex,
            widget.height_flex,
            getattr(widget, 'width_minimum', '?'),
            getattr(widget, 'height_minimum', '?'),
            rect.x      if rect else "—",
            rect.y      if rect else "—",
            rect.width  if rect else "—",
            rect.height if rect else "—",
            widget.widget_id,
        ])
        for child in widget.children:
            self.walk(child, depth + 1, rows)

    def node_icon(self, widget):
        if widget.children:
            return "+ "
        return "· "

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

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════


    def clean_widget_tree(self, type_name, name):
        MAX_LEN = 20

        name = (name or "").strip()

        # Remove redundant type prefix (e.g., "Button: Foo" -> "Foo")
        tn = (type_name or "").strip().rstrip(":")
        if tn:
            lower = name.lower()
            tn_lower = tn.lower()
            if lower.startswith(tn_lower):
                rest = name[len(tn):]
                rest = rest.lstrip()
                if rest.startswith(":"):
                    rest = rest[1:]
                name = rest.strip() or name

        # Roboto font doesn’t have full glyph coverage; keep it alnum + space.
        name = "".join(ch for ch in name if ch.isalnum() or ch == " ")
        name = " ".join(name.split())

        return name[:MAX_LEN].strip()

    def get_target(self):
        return getattr(IPUI, 'debug_target', None)

    def icon(self, widget):
        if widget.children:
            return "▼ "
        return "· "

    def reg_name(self, widget):
        target = self.get_target()
        if not target:
            return ""
        for key, val in target.widgets.items():
            if val is widget:
                return key
        return ""

    # ══════════════════════════════════════════════════════════════
    # Auto Refresh
    #def ip_think(self, ip):
     #   if ip.is_active_pane: self.refresh_tree()
    # ══════════════════════════════════════════════════════════════
