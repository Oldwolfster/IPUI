# DebugOverlay.py  NEW: Diagnostic overlay widgets pane (stub)
from ipui.engine._BasePane import _basePane
from ipui.widgets.Label import Title, Body


class Overlay(_basePane):

    def debug_overlay(self, parent):
        Title(parent, "Overlay Widgets", glow=True)
        Body(parent, "Coming soon — toggle rect outlines, filter by type")
