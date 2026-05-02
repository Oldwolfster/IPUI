from ipui import *


class TestScrollH(_BaseTab):
    def left_pane(self, parent):
        self.section(parent, "Pane 1: container widgets")

        self.test_row_many_buttons(parent)
        self.test_cardrow_many_buttons(parent)
        self.test_nested_card_scroller(parent)

    def center_pane(self, parent):
        self.section(parent, "Pane 2: leaf widgets")

        self.test_label_surface(parent)
        self.test_button_surface(parent)
        self.test_icon_row_inside_plate(parent)

    def right_pane(self, parent):
        self.section(parent, "Pane 3: mixed configurations")

        self.test_vertical_scroll_with_horizontal_child(parent)
        self.test_horizontal_and_vertical_same_widget(parent)
        self.test_two_independent_scrollers(parent)

    def section(self, parent, text):
        Title(parent, text, text_align=CENTER)

    def test_box(self, parent, title):
        box = Card(parent, scroll_v=True, height_flex=1, pad=6, gap=6)
        Heading(box, title, text_align=CENTER)
        return box

    def test_row_many_buttons(self, parent):
        box = self.test_box(parent, "1. Row(scroll_h=True) with many buttons")
        row = Row(box, scroll_h=True, pad=8, gap=8)
        for i in range(18):
            Button(row, f"Button {i}", on_click=lambda i=i: self.form.show_modal(f"Row button {i}"))

    def test_cardrow_many_buttons(self, parent):
        box = self.test_box(parent, "2. CardRow(scroll_h=True) with wide content")
        row = CardRow(box, scroll_h=True, pad=8, gap=8)
        for word in ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India"]:
            Button(row, f"{word} command", color_bg=Style.COLOR_TAB_BG)

    def test_nested_card_scroller(self, parent):
        box = self.test_box(parent, "3. Card(scroll_h=True) containing a wide Row")
        card = Card(box, scroll_h=True, pad=8, gap=8)
        row = Row(card, gap=8)
        for i in range(12):
            Plate(row, fit_content=True).tap(lambda p, i=i: Body(p, f"Tile {i}: wide nested content"))

    def test_label_surface(self, parent):
        box = self.test_box(parent, "4. Body(scroll_h=True) long text surface")
        Body(
            box,
            "This is one very long single-line Body widget intended to test horizontal scrolling on a leaf text surface.",
            scroll_h=True,
        )

    def test_button_surface(self, parent):
        box = self.test_box(parent, "5. Button(scroll_h=True) long caption")
        Button(
            box,
            "A very long button caption that should create more content width than the pane can show",
            scroll_h=True,
            on_click=lambda: self.form.show_modal("Long scroll_h button clicked"),
        )

    def test_icon_row_inside_plate(self, parent):
        box = self.test_box(parent, "6. Plate(scroll_h=True) mixed labels and buttons")
        plate = Plate(box, scroll_h=True, pad=8, gap=8)
        row = Row(plate, gap=8)
        for i in range(10):
            Body(row, f"Metric {i}")
            Button(row, "Open")

    def test_vertical_scroll_with_horizontal_child(self, parent):
        box = self.test_box(parent, "7. Vertical scroll parent, horizontal child")
        outer = Card(box, scroll_v=True, height_flex=1, pad=8, gap=8)
        for n in range(4):
            Body(outer, f"Vertical filler line {n}")
        row = Row(outer, scroll_h=True, pad=8, gap=8)
        for i in range(16):
            Button(row, f"Wide action {i}")
        for n in range(4, 10):
            Body(outer, f"Vertical filler line {n}")

    def test_horizontal_and_vertical_same_widget(self, parent):
        box = self.test_box(parent, "8. Card(scroll_v=True, scroll_h=True)")
        both = Card(box, scroll_v=True, scroll_h=True, height_flex=1, pad=8, gap=8)
        for r in range(8):
            row = Row(both, gap=8)
            for c in range(8):
                Button(row, f"R{r} C{c}")

    def test_two_independent_scrollers(self, parent):
        box = self.test_box(parent, "9. Two independent Row(scroll_h=True) widgets")
        for prefix in ["Top", "Bottom"]:
            row = Row(box, scroll_h=True, pad=8, gap=8)
            for i in range(14):
                Button(row, f"{prefix} {i}")
