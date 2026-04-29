# DebugPipeline.py  NEW: Pipeline state inspector pane (stub)
from ipui.engine._BaseTab import _BaseTab
from ipui.widgets.Label import Title, Body


class DebugPipeline(_BaseTab):

    def debug_pipeline(self, parent):
        Title(parent, "Pipeline State", glow=True)
        Body(parent, "Coming soon — derives, triggers, current values")
