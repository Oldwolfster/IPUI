from ipui import *


class YourChoice(_BaseTab):
    # ══════════════════════════════════════════════════════════════
    # Declare reactive bindings: when a trigger key changes, compute
    # fires and result is applied to the named widget's property.
    # ══════════════════════════════════════════════════════════════

    DECLARATION_UPDATES = {
        "lbl_snark":{     # "first" or "last" changes → compute_snark() → sets lbl_snark.text
            "property": "text",
            "compute": "snark",
            "triggers": ["first", "last"]
        },

        "btn_react": {  # "first" or "last" changes → should_clear_be_enabled() → sets btn_reactive_clear.enabled
            "property": "enabled",
            "compute": "chk_btn",
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
        Title    ( header, "Two Styles", glow=True)

    def react_column_left(self, two_cols):
        col_1    = Col(two_cols, width_flex=2)
        card     = Card(col_1)
        Body     ( card, "Declare relationships.")
        Body     ( card, "Magic handles the rest.")
        self    . reactive_name_game(col_1)

    def react_column_rite(self, two_cols):
        card     = Card(two_cols                        , width_flex=3)
        Heading  ( card, "Steps:"                   ,text_align=RIGHT)
        Spacer   ( card)
        Body     ( card, "Create two methods"       ,text_align=RIGHT)
        Body     ( card, "snark and chk_btn"        ,text_align=RIGHT)
        Body     ( card, "build widgets"            ,text_align=RIGHT)
        Body     ( card, "Set DECLARATION_UPDATES"  ,text_align=RIGHT)
        Body     ( card, "")
        Body     ( card, "IPUI is flexible - You can do hybrid"         ,text_align=RIGHT,glow=True)


    def reactive_code_box(self, main_left_window):
        card     = Card(main_left_window, scrollable=True, height_flex=99)
        CodeBox  ( card,                        ####################################
                   data=__file__,               # These 4 lines are what creates
                   start="# ═══",               # The CodeBox you are reading now :)
                   end="IMPERATIVE — manual",)  ####################################

    def reactive_name_game(self, parent):
        card            = CardCol (parent, width_flex    =1)
        row             = Row     (card  )

        TextBox(row,                            ################################################
            placeholder = "First name",         #### Reactive does not need 'on_change'.
            pipeline_key= "first",              #### DECLARATION_UPDATES has that covered.
                )                               ################################################

        Spacer(row,width_flex=.01)

        TextBox(row,
            placeholder = "Last name",     ################################################
            pipeline_key= "last",          #### Reactive does not need 'on_change'.
            )                              #### DECLARATION_UPDATES has that covered.
                                           ################################################
        row             = Row(card)
        Button          ( row, "Clear",
            name        = "btn_react",
            color_bg    = Style.COLOR_BUTTON_CTA,
            on_click    = self.reactive_clear,
            enabled     = False)

        Spacer          (row   , height_flex=.1)
        Body            (card   , YourChoice.DEFAULT_MESSAGE,
            name        = "lbl_snark",
            text_align  = 'c')

    def reactive_clear(self):               ############################################################
        self.form.pipeline_set("first", "") #### Notice no need to touch widgets
        self.form.pipeline_set("last", "")  #### Set data and Declaration Updates does the trick.
                                            ############################################################

    #══════════════════════════════════════════════════════════════
    # IMPERATIVE — manual wiring
    # No declares for imperative
    #══════════════════════════════════════════════════════════════

    def imperative(self, parent):
        self     . imp_header(parent)           # call method to create imperative header row
        two_cols = Row(parent)                  # create a row called two columns.
        self     . imperative_left(two_cols)    # first column  (Name game)
        #Spacer   ( two_cols, width_flex=.3)
        self     . imperative_right(two_cols)   #
        self     . imperative_code(parent)

    def imp_header(self, pane_root):           # you can name the 2nd param whatever helps you
        header  = Row(pane_root)               # create a row to put multiple widgets horizontally

        Title   (header, "Same Result", glow=True)
        Spacer  ( header)
        Title   ( header, "Imperative", glow=True)

    def imperative_left(self, two_cols):          #### LEFT = steps (faces reactive's right)
        card     = Card(two_cols, width_flex=3)
        Heading  ( card, "Steps:")
        Spacer   ( card)
        Body     ( card, "Create two methods")
        Body     ( card, "snark and chk_btn")
        Body     (card,  "build widgets")
        Body     ( card, "Use event handler to update widget...")
        Body     ( card, "")
        Body     (card,  "What is simplest for the task at hand?",glow=True)

    def imperative_right(self, two_cols):         #### RIGHT = demo (faces reactive's left)
        col      = Col(two_cols, width_flex=2)
        card     = Card(col)
        Body     ( card, "Full control and simple."   ,text_align=RIGHT)
        Body     ( card, "(My personal favorite ;)" ,text_align=RIGHT)
        self     . imperative_name_game(col)

    def imperative_name_game(self, parent):
        card    = CardCol(parent, width_flex=1)
        row     = Row    (card)

        # Storing direct references instead of relying on the registry
        self.txt_first = TextBox(row, placeholder="First name",
                                      on_change=self.imp_name_changed)
        Spacer(row,width_flex=.01)
        self.txt_last  = TextBox(row, placeholder="Last name",
                                      on_change=self.imp_name_changed)


        row            = Row(card)
        Spacer(row, height_flex=.1)
        self.btn_clear = Button(row, "Clear",
                                      color_bg=Style.COLOR_BUTTON_CTA,
                                      on_click=self.imp_clear,
                                      enabled=False)


        self.lbl_snark = Body(card, YourChoice.DEFAULT_MESSAGE, text_align=CENTER)

    def imp_name_changed(self, text):
        # Reading state directly from the objects
        first = self.txt_first.text  # Assuming property access, or .get_text()
        last  = self.txt_last.text

        # Updating objects directly
        self.lbl_snark.set_text(self.snark(first, last))
        self.btn_clear.enabled = self.chk_btn(first, last)

    def imp_clear(self):
        # Direct UI updates
        self.txt_first.set_text("")
        self.txt_last.set_text("")
        self.lbl_snark.set_text("Go ahead, type something...")
        self.btn_clear.enabled = False

    def imperative_code(self, parent):
        card     = Card(parent, scrollable=True, height_flex=99)
        CodeBox  ( card,                  ####################################
            data  = __file__,             # These 3 lines are what creates
            start = "#═════════",         # The CodeBox you are reading now :)
            end = "# ══════════",)        ####################################

    # ══════════════════════════════════════════════════════════════
    # Shared code - Same for Reactive and Imperative.
    # ══════════════════════════════════════════════════════════════
    DEFAULT_MESSAGE = "Go ahead type something..."

    def chk_btn(self, first, last):
        return bool(first or last)

    def snark(self, first, last):
        if first and last:
            return f"Ah yes, {first} {last}.\nYour code is legendary."
        if first:
            return f"{first}? Cool name.\nLast name 'null'?"
        if last:
            return f"Just '{last}'? Like Madonna,\nbut with less dancing."
        return "Go ahead, type something..."