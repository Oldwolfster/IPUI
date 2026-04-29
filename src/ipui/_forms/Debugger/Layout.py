# DebugLayout.py  NEW: Layout solver inspector pane (stub)
from ipui.engine._BaseTab import _BaseTab
from ipui.widgets.Row import CardCol
from ipui.widgets.Label import Title, Body


class Layout(_BaseTab):

    def debug_layout(self, parent):
        Title(parent, "Layout Solver", glow=True)
        Body(parent, "Coming soon — flex budget, sizes, violators per container")
