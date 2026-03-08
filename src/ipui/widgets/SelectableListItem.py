import pygame

from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.MgrColor import MgrColor
from ipui.Style import Style


class SelectableListItem(_BaseWidget):

    def build(self):
        self.my_name      = f"SelectableListItem: {self.text}"
        self.font         = self.font or Style.FONT_BODY
        self.color_bg     = Style.COLOR_CARD_BG
        self.color_txt    = Style.COLOR_TEXT
        self.is_selected  = False
        self.show_glow    = False
        self.my_surface   = self.font.render(self.text, True, self.color_txt)
        MgrColor.apply_bevel(self, "raised")

    def toggle_selected(self):
        self.is_selected = not self.is_selected
        self.apply_selection_visual()

    def apply_selection_visual(self):
        if self.is_selected:
            MgrColor.apply_bevel(self, "sunken")
            self.show_glow = True
        else:
            MgrColor.apply_bevel(self, "raised")
            self.show_glow = False