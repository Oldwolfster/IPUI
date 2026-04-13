# DebugOverlay.py  NEW: Diagnostic overlay widgets pane (stub)
from ipui.engine._BaseTab import _BaseTab
from ipui.widgets.Label import Title, Body


class Overlay(_BaseTab):

    def debug_overlay(self, parent):
        Title(parent, "Overlay Widgets", glow=True)
        Body(parent, "Coming soon — toggle rect outlines, filter by type")
