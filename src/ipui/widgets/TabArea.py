# TabArea.py  New: Outer border wrapper grouping contiguous panes
from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.MgrColor import MgrColor
from ipui.widgets.Row import CardRow, CardCol
from ipui.Style import Style


class TabArea(_BaseWidget):
    """
    desc:        Groups contiguous panes with a thin outer border. Contains an inner CardRow that holds Pane widgets.
    when_to_use: Created automatically by TabStrip. Not intended for direct use.
    best_for:    Internal framework use — visual grouping of adjacent panes in a tab.
    example:     (created by TabStrip from TAB_LAYOUT declarations)
    api:         inner — the CardRow child where Panes are attached.
    """
    def build(self):
        self.widget_type = "TabAr"
        self.color_bg = Style.COLOR_CARD_BG
        self.pad=2
        MgrColor        .apply_bevel(self, "sunken")
        self.inner    = CardRow(self, width_flex=True, height_flex=True)
        self.inner.widget_type = "TabArea Content"
        # outer = CardCol(self, width_flex=True, height_flex=True, pad=2)
