from ipui import *
from ipui.widgets.Label import Detail


class TemplateStarterKit(_basePane):

    DECLARATION_UPDATES= {
        "lbl_snark": {
            "property": "text",
            "compute": "compute_snark",
            "triggers": ["first", "last"],
        },
        "btn_reactive_clear": {
            "property": "enabled",
            "compute": "is_name_present",
            "triggers": ["first", "last"],
        },
    }

    # ══════════════════════════════════════════════════════════════
    # REACTIVE — pipeline derives
    # ══════════════════════════════════════════════════════════════

    def method_1_IPUI_TAB_BUILDER(self, parent):
        self.squish_extras(3)
        Title(parent, "Reactive", glow=True)
        card = Card(parent)
        Heading(card, "The Derives Approach", glow=True)
        Body(card, "Declare relationships.\nPipeline handles the rest.")
        self.reactive_name_game(parent)

    def reactive_name_game(self, parent):
        card            = CardCol(parent, width_flex=True)
        row             = Row(card, justify_center=True)
        TextBox(row,
            placeholder = "First name",
            pipeline_key = "first",
            width_flex  = False)
        TextBox(row,
            placeholder = "Last name",
            pipeline_key = "last",
            width_flex  = False)
        Spacer(card)
        row             = Row(card)
        Spacer(row, width_flex=3)
        Button(row, "Clear",
            name        = "btn_reactive_clear",
            color_bg    = Style.COLOR_PAL_GREEN_DARK,
            on_click    = self.reactive_clear,
            width_flex  = 2)
        Spacer(row, width_flex=1)
        Spacer(card, height_flex=1)
        Body(card, "Go ahead, type something...",
            name        = "lbl_snark",
            text_align  = 'r')
        Spacer(parent, height_flex=1)

    def compute_snark(self, first, last):
        if first or last:
            return f"You don't look like a '{last}, {first}' to me."
        return "Go ahead, type something..."

    def is_name_present(self, first, last):
        return bool(first or last)

    def reactive_clear(self):
        self.form.pipeline_set("first", "")
        self.form.pipeline_set("last", "")


    # ══════════════════════════════════════════════════════════════
    # IMPERATIVE — manual wiring
    # ══════════════════════════════════════════════════════════════


    def method_2_IPUI_TAB_BUILDER(self, parent):
        self.left_pane_top  (parent)          #Use methods to break task in to pieces
        self.name_game      (parent)

    def left_pane_top(self, parent):
        Title           ( parent, "IPUI — Making Your Life Easy", glow=True)
        card            = Card(parent)
        Heading         ( card, "The Imperative Approach", glow=True)
        Body            ( card, "Wire events yourself.\nFull control\nFull responsibility.")
        Spacer          ( parent, height_flex=1)
        Heading         ( parent, "Cards give a recessed 3d-look")
        Spacer          ( parent, height_flex=1)

    def name_game(self, parent):

        card            = CardCol(parent, width_flex=True)
        row             = Row(card, justify_center=True)    # Row Switches to horizontal so we can center
        self.txt_name   = TextBox(row,
            placeholder = "Enter your name",
            on_change   = self.name_changed,
            width_flex  = False, )
        Spacer          ( card)                             # Vertical space is default
        row             = Row(card)                         # Row switches to horizontal
        Spacer          ( row, width_flex=3)
        self.btn_clear  = Button(row, "Clear",
            color_bg    = Style.COLOR_PAL_GREEN_DARK,
            on_click    = self.clear_clicked,
            width_flex  = 2)
        Spacer(row      , width_flex=1)
        self.btn_clear  . set_disabled()
        Spacer(card     , height_flex=1)
        self.snark_text = "Go ahead, type something..."  # We will need this twice.  Variable ensures no drift
        self.lbl_snark  = Body(card, self.snark_text,text_align='r') #r for right
        Spacer(parent   , height_flex=1)
     
    def name_changed(self, text):
        if text:
            self.btn_clear.set_enabled  ()
            self.lbl_snark.set_text     (f"You don't look like a '{text}' to me.")
        else:
            self.btn_clear.set_disabled ()
            self.lbl_snark.set_text     (self.snark_text)

    def clear_clicked(self):
        self.txt_name   .set_text       ("")
        self.btn_clear  .set_disabled   ()
        self.lbl_snark  .set_text       (self.snark_text)


    def method_3_IPUI_TAB_BUILDER(self, parent):
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

