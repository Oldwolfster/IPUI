# TestDisabled.py  NEW: Test pane for disabled reason tooltip
from ipui import *


class TestDisabled(_basePane):

    def test_disabled(self, parent):
        Title(parent, "Disabled Tooltip Test", glow=True)

        Body(parent, "Hover each button for ~1 second:")

        Spacer(parent)
        btn1 = Button(parent, "Disabled with reason",
                       color_bg=Style.COLOR_PAL_GREEN_DARK)
        btn1.enabled = "You need to log in first"

        Spacer(parent)
        btn2 = Button(parent, "Disabled no reason",
                       color_bg=Style.COLOR_PAL_GREEN_DARK)
        btn2.enabled = False

        Spacer(parent)
        Button(parent, "Enabled normally",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=lambda: self.form.show_modal("I work!"))