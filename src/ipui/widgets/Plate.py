import pygame
from ipui.engine.MgrColor import MgrColor
from ipui.Style import Style
from ipui.widgets.Card import Card


class Plate(Card):
    """
    desc:        Card's raised cousin — same shape, opposite bevel direction.
    when_to_use: Inside a Card to break the recessed-on-recessed visual chain.
    best_for:    Alternating depth so nested containers stay visually distinct.
    example:     Plate(parent, flex_height=1)
    api:         (layout only — no custom methods)
    """
    def build(self):
        super().build()                                 # inherits Card's build (color_bg, sunken bevel)
        MgrColor.apply_bevel(self, "raised") 