import ipui
from ipui import *


class Form_ParticleLife(BaseForm):

    TAB_LAYOUT  =       {
        "Rules"         : ["world_rules"    , "interaction_rules", "dynamics_rules"],
        "Particles"     : [("particles",1)  ,( "matrix",3)],
        "Settings"      : ["settings"],
        "ParticleLife"  : ["particle_life",None,None],
        "ParticleLife2" : ["particle_life", "p2", "p3"],
        "Stats"         : ["stats"],

    }

    def build(self):
        row          = Row(self)
        Banner       ( row, "ParticleLife", glow=True)
        Spacer       ( row)
        btn          = Button(row, "Back to\nShowcase",   color_bg=Style.COLOR_TAB_BG,width_flex=0)
        btn.on_click = lambda: IPUI.back()