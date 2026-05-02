# Dashboard.py  New: tabless layout-without-panes example (README L1064-1076)
from ipui import *

class Dashboard(_BaseForm):

    def build(self):
        row = Row(self, width_flex=1, height_flex=1)                  # README L1066

        sidebar = CardCol(row, width_flex=1)                          # README L1068
        Title (sidebar, "Controls")                                   # README L1069
        Button(sidebar, "Reset", on_click=self.reset)                 # README L1070
        Button(sidebar, "Back",  on_click=lambda: back())             # README L1253

        main = CardCol(row, width_flex=3)                             # README L1072
        Title(main, "Output")                                         # README L1073
        self.lbl_result = Body(main, "Ready")                         # README L1074

    def reset(self):
        self.lbl_result.set_text("Reset!")
