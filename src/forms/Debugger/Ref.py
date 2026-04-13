# DebugRef.py  NEW: Widget catalog / API reference pane (stub)
from ipui.engine._BaseTab import _BaseTab
from ipui.widgets.Label import Title, Body


class DebugRef(_BaseTab):

    def debug_ref(self, parent):
        Title(parent, "Widget Reference", glow=True)
        Body(parent, "Coming soon — widget catalog, API docs, examples")
