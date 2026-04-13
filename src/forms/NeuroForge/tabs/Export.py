# Export.py  class: Export  New: _BaseTab migration from frmExport.py
from ipui import *

class EZ_PANE(_BaseTab):
    """Pane builder for the Export tab."""

    def build(self, parent: CardCol) -> None:
        """Render the Export Coming Soon pane."""
        card = CardCol(parent, width_flex=True, height_flex=True)
        Title(card, "Export to PyTorch", glow=True)

        card = CardCol(card)
        Heading(card, "Coming Soon")
        Body(card,    "Export your trained model as a .pt file")
        Body(card,    "Compatible with PyTorch 2.x")
        Body(card,    "Includes architecture, weights, input scaling/pipeline target scaling")