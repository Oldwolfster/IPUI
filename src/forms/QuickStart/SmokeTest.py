# SmokeTest.py  New: one-class smoke test using form-as-pane
from ipui import *

class SmokeTest(_BaseForm):
    TAB_LAYOUT = {
        "Smoke Test": ["go"],           # ← This one works immediately
        "Widgets":    ["demo"],         # ← Will trigger template picker
        "Relax":      ["sit", "chill"], # ← Will trigger template picker
    }

    def go(self, parent):               # ← named go to match value of above dictionary
        Banner  (parent, "IPUI"              , text_align=CENTER, glow=True)
        Title   (parent, "Easy to get right!", text_align=CENTER)
        Body    (parent, "Hard to get wrong.", text_align=CENTER)
        Button  (parent, "Click Me :)"       , on_click=self.show_hello,
                 color_bg=Style.COLOR_PAL_GREEN_DARK)

    def show_hello(self): self.show_modal("Hello World!\nWelcome to IPUI")

if __name__ == "__main__": show(SmokeTest)