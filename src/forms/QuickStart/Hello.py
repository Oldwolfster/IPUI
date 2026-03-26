from ipui import *

class Hello(_basePane):
    def world(self, parent):  # Semantic widgets with declarative layout
        Banner  (parent, "IPUI"                 , glow=True,text_align=CENTER)
        Title   (parent, "Easy to get right!"   ,text_align=CENTER)
        Body    (parent, "Hard to get wrong!"   , text_align=CENTER)
        Heading (parent, "Because we've all spent 3 hours debugging a button.",text_align=CENTER,glow=True)
        Button  (parent, "Click Me"             ,justify_spread=False,
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=lambda: self.form.show_modal("Hello World!"))
