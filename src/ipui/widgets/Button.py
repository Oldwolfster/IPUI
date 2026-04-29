from ipui.Style import Style
from ipui.engine.MgrColor import MgrColor
from ipui.engine._BaseWidget import _BaseWidget

class Button(_BaseWidget):
    """
    desc:        One click. Beveled like forged steel. Disables with a reason, glows when it matters.
    when_to_use: Any action the user can trigger.
    best_for:    Navigation, form submission, launching, pane swapping.
    example:     btn = Button(parent, "Launch", color_bg=Style.COLOR_BUTTON_CTA)
    api:         set_disabled(reason), set_enabled(), set_radiate(), on_click_me(callback)
    """

    def build(self):
        self.text_align     = self.text_align if self.text_align is not None else 'c'
        self.fit_content    = True
        self.border_radius  = self.border_radius if self.border_radius is not None else Style.TOKEN_CORNER_RADIUS
        self.font           = self.font or Style.FONT_BODY
        self.color_txt      = Style.COLOR_TEXT
        self.color_bg       = self.color_bg or Style.COLOR_BUTTON_BG
        self.pad=5
        MgrColor            . apply_bevel(self, "raised")
        self.my_surface     = self.render_multiline(self.text)

    def set_radiate(self):
        MgrColor.apply_bevel( self, "hot")
        self.show_glow      = True