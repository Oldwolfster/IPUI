# NeuronCell.py

from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.MgrColor import MgrColor
from ipui.Style import Style


class NeuronCell(_BaseWidget):
    """
    desc:        A single neuron cell for neural network visualizations.
    when_to_use: Created automatically by NeuroForge network diagrams.
    best_for:    Displaying individual neurons with activation highlighting.
    example:     NeuronCell(parent)
    api:         set_highlighted(bool)
    """
    CELL_SIZE = 24

    def build(self):
        self.widget_type = "NeuronCell"
        self.color_bg    = Style.COLOR_CARD_BG
        self.highlighted = False
        self.pad         = 0
        self.gap         = 0
        MgrColor.apply_bevel(self, "raised")

    def set_highlighted(self, value):
        self.highlighted = value
        MgrColor.apply_bevel(self, "hot" if value else "raised")

    def measure(self):
        s = NeuronCell.CELL_SIZE
        return (s, s)