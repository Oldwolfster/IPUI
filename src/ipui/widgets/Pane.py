# Pane.py  New: Tab pane container — named CardCol for widget tree clarity
from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.MgrColor import MgrColor
from ipui.Style import Style


class Pane(_BaseWidget):
    """
    desc:        A single pane slot inside a TabArea. Named in the widget tree by its TAB_LAYOUT builder string.
    when_to_use: Created automatically by TabStrip. Not intended for direct use.
    best_for:    Internal framework use — hosts pane content built by _basePane methods.
    example:     (created by TabStrip from TAB_LAYOUT declarations)
    api:         (layout only — no custom methods)
    """
    def build(self):
        self.color_bg   = Style.COLOR_CARD_BG
        MgrColor        . apply_bevel(self, "sunken")