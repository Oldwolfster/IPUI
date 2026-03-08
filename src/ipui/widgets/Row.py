import pygame

from ipui.Style import Style
from ipui.engine.MgrColor import MgrColor
from ipui.engine._BaseWidget import _BaseWidget


class Row(_BaseWidget):
    """
    desc:        Horizontal layout. No background, no border. Pure structure.
    when_to_use: Placing widgets side by side.
    best_for:    Button bars, label+value pairs, headers with actions.
    example:     row = Row(parent, justify_spread=True)
    api:         (layout only — no custom methods)
    """
    def build(self):
        self.my_name    = "Row"
        self.horizontal = True
        self.pad        = 0
        self.border     = 0


class Col(_BaseWidget):
    """
    name:        Col
    desc:        Vertical layout. No background, no border. Pure structure.
    when_to_use: Stacking widgets top to bottom without visual chrome.
    best_for:    Invisible grouping when CardCol is too heavy.
    example:     col = Col(parent)
    api:         (layout only — no custom methods)
    """
    def build(self):
        self.my_name = "Col"
        self.pad     = 0
        self.border  = 0


class CardRow(_BaseWidget):
    """
    name:        CardRow
    desc:        Horizontal card. Beveled, background-filled, feels like a tray.
    when_to_use: Horizontal grouping that needs visual presence.
    best_for:    Tab button rows, toolbar areas, side-by-side panels.
    example:     CardRow(parent, width_flex=True)
    api:         (layout only — no custom methods)
    """
    def build(self):
        self.my_name    = "CardRow"
        self.horizontal = True
        self.color_bg   = Style.COLOR_CARD_BG
        MgrColor.apply_bevel(self, "sunken")


class CardCol(_BaseWidget):
    """
    name:        CardCol
    desc:        Vertical card. The most-used container in IPUI. Scrollable on demand.
    when_to_use: Almost everywhere. It's the default "put stuff here" container.
    best_for:    Pane content, settings groups, scrollable lists, form sections.
    example:     CardCol(parent, height_flex=True, scrollable=True)
    api:         (layout only — no custom methods)
    """
    def build(self):
        self.my_name  = "CardCol"
        self.color_bg = Style.COLOR_CARD_BG
        MgrColor.apply_bevel(self, "sunken")