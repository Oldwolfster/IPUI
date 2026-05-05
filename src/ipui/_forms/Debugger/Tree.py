# DebugTree.py  Widget tree inspector pane for FormDebugger
from email import header

from ipui import *
from ipui.utils.MgrClipboard import MgrClipboard

import time
class Tree(_BaseTab):

    # ══════════════════════════════════════════════════════════════
    # DAG — Reactive updates
    # ══════════════════════════════════════════════════════════════

    BINDINGS = {
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
        return f"Widget Tree — {type(widget).__name__}: {widget.display_name} (wid {selected_wid})"
    # ══════════════════════════════════════════════════════════════
    # PANE 1 — Info (field legend)
    # ══════════════════════════════════════════════════════════════

    # Tree.py method: info  Update: replace stale column legends with current legend, actions, and reading guide

    def info(self, parent):
        from ipui.widgets.Row import CardCol

        row = Row(parent)
        self.btn_flex = Button(row, "Flex", width_flex=2,
            color_bg = Style.COLOR_BUTTON_CTA,
            on_click = lambda: self.set_column_mode("flex"))
        Spacer(row, width_flex=3)
        self.btn_tok  = Button(row, "TOK",  width_flex=2,
            color_bg = Style.COLOR_TAB_BG,
            on_click = lambda: self.set_column_mode("tokens"))

        Spacer(parent)
        card = CardCol(parent)
        Title(card, "Actions")
        Body(card, "Click row - Inspect all properties")
        Body(card, "Double-click - Flash widget on screen")
        Body(card, "Copy - Full tree to clipboard")
        Body(card, "F12- Toggle debugger anytime")

        Spacer(parent)
        card = CardCol(parent)
        Title(card, "Reading the Tree")
        Body(card, "Dp shows nesting depth")
        Body(card, "Flex 0,0  fixed size")
        Body(card, "Flex 1,0  fills width")
        Body(card, "Flex 0,1  fills height")
        Body(card, "TOK shows border/pad/gap")
        Body(card, "Min is the floor — shrink past it and content collides")
        Body(card, "Pos / Size is where it actually landed")
    # ══════════════════════════════════════════════════════════════
    # PANE 2 — Widget Tree
    # ══════════════════════════════════════════════════════════════

    def debug_tree(self, parent):
        from ipui.widgets.Row import Row
        from ipui.widgets.Button import Button                            
        from ipui.Style import Style                                      
        header = Row(parent, justify_spread=True)                         
        Title(header, "Widget Tree", glow=True, name="dbg_tree_title")   
        Button(header, "Copy", color_bg=Style.COLOR_BUTTON_CTA,
        on_click=self.copy_tree)
        #on_click=lambda: self.form.show_modal("Coming Soon!", min_seconds=1.69))
        PowerGrid(parent, name="dbg_tree_grid", height_flex=1)
        #Body(parent, "Click row to inspect", name="dbg_tree_hint")
        self.refresh()

    def refresh(self):
        target = self.get_target()
        if not target:
            return
        grid = self.form.widgets.get("dbg_tree_grid")
        if not grid:
            return
        old_scroll = grid.scroll_offset
        old_page   = grid.record_selector.current_page

        rows       = []
        self.walk(target, 0, rows)
        col4       = "TOK" if self.column_mode == "tokens" else "Flex"
        cols       = ["wid", "Dp", "Type", "Name", col4, "Min", "Pos", "Size"]
        grid.set_data(rows, columns=cols)
        grid.on_row_click(self.on_row_click, "wid")
        grid.on_row_double_click(self.on_tree_row_double_clicked, "wid")
        grid.record_selector.go_to_page(old_page)
        grid.scroll_offset = old_scroll


    def on_tree_row_double_clicked(self, wid):
        target = self.form.target()
        if not target:              return
        widget = target.widget_registry.get(wid)
        if not widget:              return
        if not widget.rect:         return
        IPUI.pulse_widget = widget
        IPUI.pulse_start  = time.time()
        IPUI.pulse_return = type(self.form)
        IPUI.back()
    # ══════════════════════════════════════════════════════════════
    # PANE 3 — Widget Detail
    # ══════════════════════════════════════════════════════════════


    def details(self, parent):
        from ipui.widgets.Row import Row
        from ipui.widgets.Button import Button
        from ipui.Style import Style
        header = Row(parent, justify_spread=True)
        Title(header, "Widget Detail", glow=True)
        btn = Button(header, "Copy", color_bg=Style.COLOR_BUTTON_CTA)
        btn.on_click_me(self.copy_detail)
        #btn.on_click = lambda: self.form.show_modal("Coming Soon!",  min_seconds=1.69)
        PowerGrid(parent, name="dbg_detail_grid", height_flex=1)
        #Body(parent, "← Click a row", name="dbg_detail_hint")


    def copy_tree(self):
        grid = self.form.widgets.get("dbg_tree_grid")
        if not grid or not grid.rows_all:        # REPLACE
            return
        lines = []
        lines.append("  ".join(grid.columns))
        for row in grid.rows_all:
            lines.append("  ".join(str(c) for c in row))
        MgrClipboard.copy("\n".join(lines))


    def copy_detail(self):
        grid = self.form.widgets.get("dbg_detail_grid")
        if not grid or not grid.rows_all: return
        lines = []
        for row in grid.rows_all: lines.append(f"{row[0]:25} {row[1]}")
        MgrClipboard.copy("\n".join(lines))

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
    def ip_setup_early(self, ip):
        self.column_mode = "flex"
    def ip_activated(self, ip):
        self.refresh()
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
        rect       = widget.rect
        rx, ry     = (rect.x, rect.y)             if rect else ("—", "—")
        rw, rh     = (rect.width, rect.height)    if rect else ("—", "—")
        minx       = getattr(widget, 'width_minimum',  '?')
        miny       = getattr(widget, 'height_minimum', '?')
        if self.column_mode == "tokens":
            col4 = f"{widget.border}/{widget.pad_x}/{widget.pad_y}/{widget.gap}"
        else:
            col4 = f"{widget.width_flex}, {widget.height_flex}"
        rows.append([
            widget.widget_id,
            depth,
            type(widget).__name__,
            widget.display_name,
            col4,
            f"{minx}, {miny}",
            f"{rx}, {ry}",
            f"{rw} x {rh}",
        ])
        for child in widget.children:
            self.walk(child, depth + 1, rows)
    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def get_target(self):
        return getattr(IPUI, 'debug_target', None)


    def set_column_mode(self, mode):
        self.column_mode    = mode
        active              = Style.COLOR_BUTTON_CTA
        inactive            = Style.COLOR_TAB_BG
        self.btn_flex.color_bg = active if mode == "flex"   else inactive
        self.btn_tok .color_bg = active if mode == "tokens" else inactive
        self.refresh()

