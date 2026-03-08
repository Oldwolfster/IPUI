# Export.py  class: Export  New: _basePane migration from frmExport.py
from ipui.engine._BasePane  import _basePane
from ipui.widgets.Row         import CardCol
from ipui.widgets.Label        import Title, Heading, Body


class EZ_PANE(_basePane):
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