from ipui.engine._BaseForm import _BaseForm
from ipui.engine.IPUI import IPUI


class FormDebugger(_BaseForm):
    TAB_LAYOUT = {
        "Tree"          :[("info",.9)           , ("debug_tree" ,3)   ,("details", 1.5)  ],
        "Documentation" :[("debug_ref", 1)      , ("ref_detail", 2)                     ],
        "Magic"         :[("magic_explain", 2)  , ("debug_magic_show", 3),              ],
        "Optimizer"     :[("bench_flat_wall", 1), ("bench_deep_tree",  1),("bench_wrap_storm", 1),("bench_target",    .5),    ],
        "Layout"        :["debug_layout"                                                ],
        "Overlay"       :["debug_overlay"                                               ],
    }

    #pipeline_debug = True

    def build(self):
        pass

    def target(self):
        """The form we are inspecting."""
        return getattr(IPUI, 'debug_target', None)