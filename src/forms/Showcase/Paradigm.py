# Paradigm.py  NEW: Side-by-side reactive vs imperative showcase

from ipui import *
from ipui.widgets.CodeBox import CodeBox


class Paradigm(_basePane):

    # ══════════════════════════════════════════════════════════════
    #  'Declares' lbl_snark and btn_reactive_clear get updates
    # ══════════════════════════════════════════════════════════════

    DECLARATION_UPDATES = {
        "lbl_snark"          :{"property":"text",    "compute": "compute_snark",   "triggers": ["first", "last"] },
        "btn_reactive_clear" :{"property":"enabled", "compute": "is_name_present", "triggers": ["first", "last"] },
    }

    # ══════════════════════════════════════════════════════════════
    # REACTIVE — pipeline derives
    # ══════════════════════════════════════════════════════════════

    def reactive(self, parent):
        Title(parent, "Reactive", glow=True)

        self.reactive_name_game(parent)
        card = Card(parent)
        Heading(card, "The Derives Approach", glow=True)
        Body(card, "Declare relationships.\nPipeline handles the rest.")

        card = Card(parent, scrollable=True, height_flex=99) #With no height_flex no scroll
        CodeBox(card,
                data=__file__,
                start="# ═══",
                end="IMPERATIVE — manual", )

    def reactive_name_game(self, parent):
        card            = CardCol(parent, width_flex=True)
        row             = Row(card, justify_center=True)
        TextBox(row,
            placeholder = "First name",
            pipeline_key= "first",
            width_flex  = False)
        TextBox(row,
            placeholder = "Last name",
            pipeline_key= "last",
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
        #Spacer(parent, height_flex=1)

    def compute_snark(self, first, last):                                    
        if first and last:                                                   
            return f"Ah yes, {first} {last}. Your code is legendary."        
        if first:                                                            
            return f"{first}? Cool name. Last name 'null'?"                  
        if last:                                                             
            return f"Just '{last}'? Like Madonna, but with less dancing."     
        return "Go ahead, type something..."

    def is_name_present(self, first, last):
        return bool(first or last)

    def reactive_clear(self):
        self.form.pipeline_set("first", "")
        self.form.pipeline_set("last", "")

    # ══════════════════════════════════════════════════════════════
    # IMPERATIVE — manual wiring
    # ══════════════════════════════════════════════════════════════

    def imperative(self, parent):
        Title(parent, "Imperative", glow=True)
        card = Card(parent)
        Heading(card, "The Manual Approach", glow=True)
        Body(card, "Wire events yourself.\nFull control. Full responsibility.")
        self.imp_name_game(parent)

    def imp_name_game(self, parent):
        card            = CardCol(parent, width_flex=True)
        row             = Row(card, justify_center=True)
        self.txt_first  = TextBox(row,
            placeholder = "First name",
            on_change   = self.imp_name_changed,
            width_flex  = False)
        self.txt_last   = TextBox(row,
            placeholder = "Last name",
            on_change   = self.imp_name_changed,
            width_flex  = False)
        Spacer(card)
        row             = Row(card)
        Spacer(row, width_flex=3)
        self.btn_imp    = Button(row, "Clear",
            color_bg    = Style.COLOR_PAL_GREEN_DARK,
            on_click    = self.imp_clear_clicked,
            width_flex  = 2)
        Spacer(row, width_flex=1)
        self.btn_imp.set_disabled()
        Spacer(card, height_flex=1)
        self.imp_default = "Go ahead, type something..."
        self.lbl_imp    = Body(card, self.imp_default, text_align='r')
        Spacer(parent, height_flex=1)

    
    def imp_name_changed(self, text):
        first = self.txt_first.text
        last = self.txt_last.text
        if first and last:  
            self.btn_imp.set_enabled()  
            self.lbl_imp.set_text(f"You don't look like a '{last}, {first}' to me.")  
        else:  
            self.btn_imp.set_disabled()  
            self.lbl_imp.set_text(self.imp_default)  

        if first and last:  
            self.btn_imp.set_enabled()  
            self.lbl_imp.set_text(f"Ah yes, {first} {last}. Your code is legendary.")  
        elif first:  
            self.btn_imp.set_enabled()  
            self.lbl_imp.set_text(f"{first}? Cool name. Last name 'null'?")  
        elif last:  
            self.btn_imp.set_enabled()  
            self.lbl_imp.set_text(f"Just '{last}'? Like Madonna, but with less dancing.")  
        else:  
            self.btn_imp.set_disabled()  
            self.lbl_imp.set_text(self.imp_default)  

    def imp_clear_clicked(self):
        self.txt_first.set_text("")
        self.txt_last.set_text("")
        self.btn_imp.set_disabled()
        self.lbl_imp.set_text(self.imp_default)