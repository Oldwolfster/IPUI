# DebugRef.py  NEW: Widget catalog / API reference pane (stub)
from ipui.engine._BasePane import _basePane
from ipui.widgets.Label import Title, Body


class DebugRef(_basePane):

    def debug_ref(self, parent):
        Title(parent, "Widget Reference", glow=True)
        Body(parent, "Coming soon — widget catalog, API docs, examples")
