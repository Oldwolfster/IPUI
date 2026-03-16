# Paradigm.py  NEW: Side-by-side reactive vs imperative showcase

from ipui import *
from ipui.widgets.CodeBox import CodeBox


class YourChoice(_basePane):
    # ══════════════════════════════════════════════════════════════
    # Declare reactive bindings: when a trigger key changes, compute
    # fires and result is applied to the named widget's property.
    # ══════════════════════════════════════════════════════════════

    DECLARATION_UPDATES = {
        "lbl_snark":{     # "first" or "last" changes → compute_snark() → sets lbl_snark.text
            "property": "text",
            "compute": "compute_snark",
            "triggers": ["first", "last"]
        },

        "btn_react": {  # "first" or "last" changes → should_clear_be_enabled() → sets btn_reactive_clear.enabled
            "property": "enabled",
            "compute": "should_clear_be_enabled",
            "triggers": ["first", "last"]
        },
    }

    # ══════════════════════════════════════════════════════════════
    # This builds the UI you see directly above (Reactive)
    # ══════════════════════════════════════════════════════════════
    def reactive(self, parent):
        self     . react_header      (parent)   # call method to create React header row
        two_cols = Row               (parent)   # create a row called two columns.
        self     . react_column_left (two_cols) # first column  (Name game)
        self     . react_column_rite (two_cols) # second column (Steps listing)
        self     . reactive_code_box (parent)   # back to parent - BELOW both columns

    def react_header(self,pane_root):           # you can name the 2nd param whatever helps you
        header  = Row(pane_root)                # create a row to put multiple widgets horizontally
        Title   ( header, "Reactive", glow=True)
        Spacer  ( header)                       # spacer in middle will push title left and detail right.
                                                # OR you could use align.  Either way works.
        Title    ( header, "Two Options", glow=True)
        #Detail  ( header,"Not working? Hit F12 | Magic | Pipeline, Registry and DAG.")

    def react_column_left(self, two_cols):
        col_1    = Col(two_cols, width_flex=1)
        card     = Card(col_1)
        #Heading  ( card, "The Derives Approach", glow=True)
        Body     ( card, "Declare relationships.")
        Body     ( card, "Pipeline handles the rest.")
        self    . reactive_name_game(col_1)

    def react_column_rite(self, two_cols):
        card     = Card(two_cols, width_flex=2)
        Heading  ( card, "Steps:",text_align='r')
        Spacer   ( card)
        Body     ( card, "Create compute_snark",text_align='r')
        Body     ( card, "Create should_clear_be_enabled",text_align='r')
        Spacer   (card)
        Body     ( card, "Add DECLARATION_UPDATES...",text_align='r')
        Body     ( card, "Name of widget, prop to update, and method to call.",text_align='r')
        Spacer   (card)

    def reactive_code_box(self, main_left_window):
        card     = Card(main_left_window, scrollable=True, height_flex=99)
        CodeBox  ( card,                        ##################################
                   data=__file__,               # These 4 lines are what creates
                   start="# ═══",               # The CodBox you are reading now :)
                   end="IMPERATIVE — manual",)  ##################################

    def reactive_name_game(self, parent):
        card            = CardCol (parent, width_flex    =True)
        row             = Row     (card  )

        TextBox(row,                       ################################################
            placeholder = "First name",    #### Reactive does not include 'on_change'.
            pipeline_key= "first",         #### DECLARATION_UPDATES has that covered.
            width_flex  = False)           ################################################

        TextBox(row,
            placeholder = "Last name",     ################################################
            pipeline_key= "last",          #### Reactive does not need 'on_change'.
            width_flex  = False)           #### DECLARATION_UPDATES has that covered.
        #Spacer(card)                      ################################################


        Button          ( card, "Clear",
            name        = "btn_react",
            color_bg    = Style.COLOR_PAL_GREEN_DARK,
            on_click    = self.reactive_clear,
            enabled     = False,                    # CHeck is it necessary in react?
            width_flex  = True                      # Fill the entire width
              )

        Spacer          (card   , height_flex=.1)
        Body            (card   , YourChoice.DEFAULT_MESSAGE,
            name        = "lbl_snark",
            text_align  = 'c')

    def reactive_clear(self):               ############################################################
        self.form.pipeline_set("first", "") #### Notice no need to touch widgets
        self.form.pipeline_set("last", "")  #### Set data and Declaration Updates does the trick.
                                            ############################################################

    # No declares for imperative
    # ══════════════════════════════════════════════════════════════
    # IMPERATIVE — manual wiring
    # ══════════════════════════════════════════════════════════════
    def imperative(self, parent):
        self     . imp_header(parent)           # call method to create imperative header row
        two_cols = Row(parent)                  # create a row called two columns.
        self     . imperative_left(two_cols)    # first column  (Name game)
        #Spacer   ( two_cols, width_flex=.3)
        self     . imperative_right(two_cols)   #
        self     . imperative_code(parent)


    def imp_header(self, pane_root):           # you can name the 2nd param whatever helps you
        header  = Row(pane_root)               # create a row to put multiple widgets horizontally
        #Detail  ( header, "Not working? Add a breakpoint. Run debugger; step one line at a time.")
        Title   (header, "Your Choice", glow=True)
        Spacer  ( header)
        Title   ( header, "Imperative", glow=True)

    def imperative_left(self, two_cols):          #### LEFT = steps (faces reactive's right)
        card     = Card(two_cols, width_flex=2)
        Heading  ( card, "Steps:")
        Spacer   (card)
        Body     ( card, "Create compute_snark")
        Body     ( card, "Create should_clear_be_enabled")
        Spacer   (card)
        Body     ( card, "Populate event handler to...")
        Body     ( card, "Run methods and update widget with response")
        Spacer   (card)

    def imperative_right(self, two_cols):         #### RIGHT = demo (faces reactive's left)
        col      = Col(two_cols, width_flex=1)
        card     = Card(col)
        #Heading  ( card, "The Manual Approach", glow=True)
        Body     ( card, "Wire events yourself.",text_align='r')
        Body     ( card, "Full control and onus.",text_align='r')
        self     . imperative_name_game(col)

    def imperative_name_game(self, parent):
        card = CardCol(parent, width_flex=True)
        row = Row(card)

        # Storing direct references instead of relying on the registry
        self.txt_first = TextBox(row,
                                 placeholder="First name",
                                 on_change=self.imp_name_changed,
                                 width_flex=False)

        self.txt_last = TextBox(row,
                                placeholder="Last name",
                                on_change=self.imp_name_changed,
                                width_flex=False)

        self.btn_clear = Button(card, "Clear",
                                color_bg=Style.COLOR_PAL_GREEN_DARK,
                                on_click=self.imp_clear,
                                enabled=False,
                                width_flex=True)

        Spacer(card, height_flex=.1)

        self.lbl_snark = Body(card, YourChoice.DEFAULT_MESSAGE,
                              text_align='c')

    def imp_name_changed(self, text):
        # Reading state directly from the objects
        first = self.txt_first.text  # Assuming property access, or .get_text()
        last = self.txt_last.text

        # Updating objects directly
        self.lbl_snark.set_text(self.compute_snark(first, last))
        self.btn_clear.enabled = self.should_clear_be_enabled(first, last)

    def imp_clear(self):
        # Direct UI updates
        self.txt_first.set_text("")
        self.txt_last.set_text("")
        self.lbl_snark.set_text("Go ahead, type something...")
        self.btn_clear.enabled = False

    def imperative_code(self, parent):
        card     = Card(parent, scrollable=True, height_flex=99)
        CodeBox  ( card,                        ##################################
            data  = __file__,                   # These 4 lines are what creates
            start = "# No declares for imperative",      # The CodeBox you are reading now :)
            end   = "SHARED COMPUTES", )        ##################################

    # ══════════════════════════════════════════════════════════════
    # Shared code - Same for Reactive and Imperative.
    # ══════════════════════════════════════════════════════════════
    DEFAULT_MESSAGE = "Go ahead\ntype something..."

    def should_clear_be_enabled(self, first, last):
        return bool(first or last)

    def compute_snark(self, first, last):
        if first and last:
            return f"Ah yes, {first} {last}.\nYour code is legendary."
        if first:
            return f"{first}? Cool name.\nLast name 'null'?"
        if last:
            return f"Just '{last}'? Like Madonna,\nbut with less dancing."
        return "Go ahead, type something..."