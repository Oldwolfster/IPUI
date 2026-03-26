from ipui import *
from ipui.widgets.CodeBox import CodeBox
from ipui.widgets.Label import Detail


class TemplateShowcase(_basePane):

    def ip_setup_pane(self):
        self.catalog = WidgetCatalog()

    # ══════════════════════════════════════════════════════════════
    # PANE 1 — Scrollable widget gallery
    # ══════════════════════════════════════════════════════════════

    def welcome(self, parent):
        self.squish_extras(3)
        self.form.tab_strip.panes[1].width_flex = 2
        Title(parent, "Widget Showcase", glow=True)
        Body(parent, "Click any 'Docs' button to see documentation →")
        scroller = CardCol(parent, height_flex=True, scrollable=True)
        self.demo_text_hierarchy  (scroller)
        self.demo_button          (scroller)
        self.demo_textbox         (scroller)
        self.demo_spacer          (scroller)
        self.demo_layout          (scroller)
        self.demo_selection_list  (scroller)
        self.demo_dropdown        (scroller)
        self.demo_text_area       (scroller)
        self.demo_power_grid      (scroller)
        self.demo_codebox         (scroller)

    # ──────────────────────────────────────────────────────────
    # Text Hierarchy
    # ──────────────────────────────────────────────────────────

    def demo_text_hierarchy(self, parent):
        card = self.demo_card(parent, "Text Hierarchy", "Banner")
        Banner (card, "Banner — one per screen, max")
        Title  (card, "Title — starts a new topic")
        Heading(card, "Heading — groups related content")
        Body   (card, "Body — the workhorse. Most text is this.")
        Detail (card, "Detail — fine print, timestamps, metadata")

    # ──────────────────────────────────────────────────────────
    # Button — interactive story
    # ──────────────────────────────────────────────────────────

    def demo_button(self, parent):
        card             = self.demo_card(parent, "Button", "Button")
        row              = Row(card)
        self.btn_helpful = Button(row, "Fix My Friend",
                             on_click  = self.handle_helpful,
                             color_bg  = Style.COLOR_PAL_GREEN_DARK)
        self.btn_broken  = Button(row, "Thanks!",
                             on_click  = self.handle_broken,
                             enabled   = "Waiting for help...")
        self.btn_snooty  = Button(row, "I'm Fabulous",
                             on_click  = self.handle_snooty,
                             color_bg  = Style.COLOR_PAL_BLUE_MUTED)
        self.btn_snooty.set_radiate()

    def handle_helpful(self):
        self.btn_broken.set_enabled()

    def handle_broken(self):
        self.form.show_modal("Hey thanks buddy!\nI was stuck there forever.")

    def handle_snooty(self):
        if self.btn_broken.enabled:
            self.form.show_modal("Ugh, that lame button is back.\nI was better off without it.")
            self.btn_broken.set_disabled("Snooty ruined it")
        else:
            self.form.show_modal("I'm Fabulous.\nThank god that lameass button is disabled.")

    # ──────────────────────────────────────────────────────────
    # TextBox — reactive demo
    # ──────────────────────────────────────────────────────────

    def demo_textbox(self, parent):
        card = self.demo_card(parent, "TextBox", "TextBox")
        Body(card, "Type something — watch it react:")
        TextBox(card,
            placeholder  = "Type here...",
            on_change    = self.on_textbox_changed,
            width_flex   = False)
        self.lbl_textbox_echo = Body(card, "Go ahead, type something...")

    def on_textbox_changed(self, text):
        if text:
            self.lbl_textbox_echo.set_text(f"You typed: '{text}'")
        else:
            self.lbl_textbox_echo.set_text("Go ahead, type something...")

    # ──────────────────────────────────────────────────────────
    # Spacer — push things apart
    # ──────────────────────────────────────────────────────────

    def demo_spacer(self, parent):
        card = self.demo_card(parent, "Spacer", "Spacer")
        Body(card, "Spacer eats remaining space. These buttons are pushed apart:")
        row = Row(card)
        Button(row, "Left",  color_bg=Style.COLOR_PAL_GREEN_DARK, width_flex=False)
        Spacer(row)
        Button(row, "Right", color_bg=Style.COLOR_PAL_GREEN_DARK, width_flex=False)

    # ──────────────────────────────────────────────────────────
    # Layout — Row, Col, Card variants
    # ──────────────────────────────────────────────────────────

    def demo_layout(self, parent):
        card = self.demo_card(parent, "Layout Containers", "Row")
        Body(card, "Row = horizontal. Card variants add chrome.")
        row = Row(card)
        CardCol(row, width_flex=True).tap(lambda c: Body(c, "CardCol A"))
        CardCol(row, width_flex=True).tap(lambda c: Body(c, "CardCol B"))
        CardCol(row, width_flex=True).tap(lambda c: Body(c, "CardCol C"))

    # ──────────────────────────────────────────────────────────
    # SelectionList
    # ──────────────────────────────────────────────────────────

    def demo_selection_list(self, parent):
        card = self.demo_card(parent, "SelectionList", "SelectionList")
        Body(card, "Click to select. Multi-select by default.")
        items = {"Alpha": {}, "Bravo": {}, "Charlie": {}, "Delta": {}}
        SelectionList(card, data=items,
            on_change    = self.on_selection_changed,
            height_flex  = True)
        self.lbl_selection = Body(card, "Nothing selected")

    def on_selection_changed(self, selected):
        if selected:
            self.lbl_selection.set_text(f"Selected: {', '.join(selected)}")
        else:
            self.lbl_selection.set_text("Nothing selected")

    # ──────────────────────────────────────────────────────────
    # DropDown
    # ──────────────────────────────────────────────────────────

    def demo_dropdown(self, parent):
        card = self.demo_card(parent, "DropDown", "DropDown")
        Body(card, "Type-to-filter combo box:")
        opts = {"SGD": {}, "Adam": {}, "RMSProp": {}, "AdaGrad": {}}
        DropDown(card,
            placeholder  = "Pick optimizer...",
            data         = opts,
            on_change    = self.on_dropdown_changed)
        self.lbl_dropdown = Body(card, "Nothing selected")

    def on_dropdown_changed(self, selected):
        if selected:
            self.lbl_dropdown.set_text(f"Selected: {selected[0]}")
        else:
            self.lbl_dropdown.set_text("Nothing selected")

    # ──────────────────────────────────────────────────────────
    # TextArea
    # ──────────────────────────────────────────────────────────

    def demo_text_area(self, parent):
        card = self.demo_card(parent, "TextArea", "TextArea")
        Body(card, "Multi-line editor. Try typing:")
        TextArea(card,
            placeholder  = "Enter some text...\nMultiple lines work!",
            height_flex  = True)

    # ──────────────────────────────────────────────────────────
    # PowerGrid
    # ──────────────────────────────────────────────────────────

    def demo_power_grid(self, parent):
        card = self.demo_card(parent, "PowerGrid", "PowerGrid")
        Body(card, "Feed it lists, dicts, or databases — it just works.")
        data = [
            {"Widget": "Button",    "Lines": 25,  "Vibe": "Forged steel"},
            {"Widget": "TextBox",   "Lines": 458, "Vibe": "Label on steroids"},
            {"Widget": "PowerGrid", "Lines": 624, "Vibe": "The baddest grid"},
            {"Widget": "CodeBox",   "Lines": 91,  "Vibe": "Show, don't tell"},
        ]
        grid = PowerGrid(card, name="showcase_grid")
        grid.set_data(data)

    # ──────────────────────────────────────────────────────────
    # CodeBox
    # ──────────────────────────────────────────────────────────

    def demo_codebox(self, parent):
        card = self.demo_card(parent, "CodeBox", "CodeBox")
        Body(card, "I'm showing my own source code right now:")
        CodeBox(card, data=self.demo_codebox)

    # ══════════════════════════════════════════════════════════════
    # Card factory
    # ══════════════════════════════════════════════════════════════

    def demo_card(self, parent, label, widget_name):
        card         = CardCol(parent)
        row          = Row(card)
        Heading(row, label, glow=True)
        Spacer(row)
        btn          = Button(row, "Docs →",
                         color_bg   = Style.COLOR_TAB_BG,
                         width_flex = False)
        btn.on_click = lambda wn=widget_name: self.show_widget_doc(wn)
        return card

    # ══════════════════════════════════════════════════════════════
    # PANE 2 — Documentation viewer
    # ══════════════════════════════════════════════════════════════

    def select_project(self, parent):
        Title(parent, "Widget Docs", glow=True)
        Body(parent, "← Click a 'Docs' button to inspect any widget.")

    # ──────────────────────────────────────────────────────────
    # Detail builder (loaded via set_pane)
    # ──────────────────────────────────────────────────────────

    def show_widget_doc(self, widget_name):
        entry = self.catalog.entry_for(widget_name)
        if not entry:
            return
        self.form.set_pane(1, self.render_doc, entry)

    def render_doc(self, parent, entry):
        Title(parent, entry["name"], glow=True)
        Body(parent, f"From {entry['file']}  ·  {entry['lines']} lines")
        Spacer(parent)
        self.doc_field(parent, "Description",  entry["desc"])
        self.doc_field(parent, "When to use",  entry["when_to_use"])
        self.doc_field(parent, "Best for",     entry["best_for"])
        self.doc_field(parent, "Example",      entry["example"])
        self.doc_field(parent, "API",          entry["api"])
        Spacer(parent)
        Heading(parent, "Source:", glow=True)
        scroller = Col(parent, height_flex=True, scrollable=True,
                       color_bg=Style.COLOR_PAL_GRAY_950)
        CodeBox(scroller, data=entry.get("source", ""))

    def doc_field(self, parent, label, value):
        if not value:
            return
        card = CardCol(parent)
        Heading(card, f"{label}:")
        Body(card, value)

    def metaphor(self, parent):
        Spacer(parent, height_flex=2)
        Title(parent, "Your Turn, Champ", glow=True)
        Spacer(parent, height_flex=1)
        Body(parent, "We built the first two.")
        Body(parent, "We're not doing all of them.")
        Spacer(parent, height_flex=1)
        Heading(parent, "Suggestions:")
        Body(parent, "  • Steal from the pane next door")
        Body(parent, "  • Check out the Widgets tab")
        Body(parent, "  • Break something. You'll learn faster.")
        Spacer(parent, height_flex=3)
        Detail(parent, "— The IPUI Management")

