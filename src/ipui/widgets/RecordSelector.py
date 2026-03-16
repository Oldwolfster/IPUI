# RecordSelector.py  NEW: Pagination bar composed from IPUI widgets

from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.Button import Button
from ipui.widgets.Label import Body
from ipui.widgets.TextBox import TextBox
from ipui.Style import Style


class RecordSelector(_BaseWidget):
    """
    desc:        Pagination bar. Navigate large datasets by page.
    when_to_use: Any grid or list with more rows than fit on screen.
    best_for:    PowerGrid pagination, large dataset navigation.
    example:     rs = RecordSelector(parent, on_change=handler); rs.set_data(total_rows=500, page_size=50)
    api:         set_data(total_rows, page_size), go_to_page(n)
    """

    def build(self):
        self.my_name      = "RecordSelector"
        self.horizontal   = True
        self.color_bg     = Style.COLOR_PANEL_BG
        self.current_page = 1

        self.total_rows   = 0
        self.page_size    = 100
        self.build_controls()

    def build_controls(self):
        smaller_pad=0
        self.btn_first  = Button(self, " |< ",
                                 color_bg=Style.COLOR_TAB_BG,
                                 on_click=self.go_first,
                                 pad=smaller_pad)
        self.btn_prev   = Button(self, " < ",
                                 color_bg=Style.COLOR_TAB_BG,
                                 on_click=self.go_prev,pad=smaller_pad)
        self.tb_page    = TextBox(self,
                                  initial_value="1",
                                  on_submit=self.handle_page_typed,pad=smaller_pad)
        self.lbl_of     = Body(self, "of 1",pad=smaller_pad)
        self.btn_next   = Button(self, " > ",
                                 color_bg=Style.COLOR_TAB_BG,
                                 on_click=self.go_next,pad=smaller_pad)
        self.btn_last   = Button(self, " >| ",
                                 color_bg=Style.COLOR_TAB_BG,
                                 on_click=self.go_last,pad=smaller_pad)
        self.lbl_status = Body(self, " ",pad=smaller_pad)

    # ══════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════

    def set_data(self, total_rows, page_size=100):
        self.total_rows   = total_rows
        self.page_size    = page_size
        self.current_page = 1
        self.refresh_display()

    def go_to_page(self, page):
        page = max(1, min(page, self.last_page()))
        if page == self.current_page:
            return
        self.current_page = page
        self.refresh_display()
        self.fire_page_change()

    # ══════════════════════════════════════════════════════════════
    # NAVIGATION
    # ══════════════════════════════════════════════════════════════

    def go_first(self):
        self.go_to_page(1)

    def go_prev(self):
        self.go_to_page(self.current_page - 1)

    def go_next(self):
        self.go_to_page(self.current_page + 1)

    def go_last(self):
        self.go_to_page(self.last_page())

    def handle_page_typed(self, text):
        try:
            page = int(text)
        except ValueError:
            self.refresh_display()
            return
        self.go_to_page(page)

    # ══════════════════════════════════════════════════════════════
    # DISPLAY
    # ══════════════════════════════════════════════════════════════

    def refresh_display(self):
        self.tb_page.set_text(str(self.current_page))
        self.lbl_of.set_text(f" of {self.last_page()}")
        self.lbl_status.set_text(self.format_status())
        self.update_buttons()

    def format_status(self):
        if self.total_rows <= 0:
            return ""
        start = self.start_row()
        end   = self.end_row()
        return f"Showing {start:,}\u2013{end:,} of {self.total_rows:,}"

    def update_buttons(self):
        at_start = self.current_page <= 1
        at_end   = self.current_page >= self.last_page()
        if at_start:
            self.btn_first.set_disabled()
            self.btn_prev.set_disabled()
        else:
            self.btn_first.set_enabled()
            self.btn_prev.set_enabled()
        if at_end:
            self.btn_next.set_disabled()
            self.btn_last.set_disabled()
        else:
            self.btn_next.set_enabled()
            self.btn_last.set_enabled()

    # ══════════════════════════════════════════════════════════════
    # CALLBACK
    # ══════════════════════════════════════════════════════════════

    def fire_page_change(self):
        if self.on_change:
            self.on_change(self.current_page, self.start_row(), self.end_row())

    # ══════════════════════════════════════════════════════════════
    # MATH
    # ══════════════════════════════════════════════════════════════

    def last_page(self):
        if self.page_size <= 0 or self.total_rows <= 0:
            return 1
        return max(1, (self.total_rows + self.page_size - 1) // self.page_size)

    def start_row(self):
        return (self.current_page - 1) * self.page_size + 1

    def end_row(self):
        return min(self.current_page * self.page_size, self.total_rows)