# DebugPipeline.py  NEW: Pipeline state inspector pane (stub)
from ipui.engine._BasePane import _basePane
from ipui.widgets.Label import Title, Body


class DebugPipeline(_basePane):

    def debug_pipeline(self, parent):
        Title(parent, "Pipeline State", glow=True)
        Body(parent, "Coming soon — derives, triggers, current values")
