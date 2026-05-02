# TablessMinimal.py  New: tabless _BaseForm minimal example (README L981-996)
from ipui import *

class TablessMinimal(_BaseForm):

    def build(self):
        Banner(self, "My App", glow=True, text_align=CENTER)                # README L985
        Title (self, "No tabs. No panes. Just widgets.", text_align=CENTER) # README L986
        Body  (self, "Everything lives right here.", text_align=CENTER)     # README L987
        Button(self, "Do Something",                                        # README L988
               color_bg = Style.COLOR_BUTTON_CTA,
               on_click = self.do_something)
        Button(self, "Back to ReadmeTests", on_click=lambda: back())        # README L1253

    def do_something(self):                                                 # README L992
        self.show_modal("It works!")                                        # README L993
