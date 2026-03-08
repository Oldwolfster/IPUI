import pygame
from ipui.engine.MgrColor import MgrColor
from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style


class Card(_BaseWidget):
    """
    desc:        Simple card wrapper. Background and bevel, nothing else.
    when_to_use: When you need a visual container but not a row or column.
    best_for:    Wrapping a single widget or custom drawing area.
    example:     Card(parent, height_flex=True)
    api:         (layout only — no custom methods)
    """
    def build(self):
        self.my_name  = "Card"
        self.color_bg = Style.COLOR_CARD_BG
        MgrColor.apply_bevel(self, "sunken")