# TestRecordSelector.py  NEW: Test pane for RecordSelector widget

from ipui import *




class TestRecordSelector(_basePane):
    """Drop this into any tab to test RecordSelector standalone."""

    def test_pager(self, parent):
        Title(parent, "RecordSelector Test", glow=True)

        sub = CardCol(parent)
        Heading(sub, "Small Dataset (47 rows, 10 per page)")
        self.rs_small = RecordSelector(sub, on_change=self.handle_page_change)
        self.rs_small.set_data(total_rows=47, page_size=10)

        sub = CardCol(parent)
        Heading(sub, "Large Dataset (2,847 rows, 100 per page)")
        self.rs_large = RecordSelector(sub, on_change=self.handle_page_change)
        self.rs_large.set_data(total_rows=2847, page_size=100)

        sub = CardCol(parent)
        Heading(sub, "Edge Case (0 rows)")
        self.rs_empty = RecordSelector(sub, on_change=self.handle_page_change)
        self.rs_empty.set_data(total_rows=0, page_size=50)

        sub = CardCol(parent)
        Heading(sub, "Edge Case (1 page exactly)")
        self.rs_exact = RecordSelector(sub, on_change=self.handle_page_change)
        self.rs_exact.set_data(total_rows=50, page_size=50)

        Spacer(parent)
        self.lbl_event = Detail(parent, "Page events will appear here")

    def handle_page_change(self, page, start_row, end_row):
        self.lbl_event.set_text(
            f"Page {page} selected — rows {start_row:,} to {end_row:,}")



    def test_bottom(self, parent):
        Title(parent, "Grid Structure Test", glow=True)

        power_grid_body = CardCol(parent, height_flex=True, pad=0)
        Spacer(power_grid_body, name="grid_area")
        self.rs_bottom = RecordSelector(power_grid_body, on_change=self.handle_page_change)
        self.rs_bottom.set_data(total_rows=296, page_size=50)