import ipui
from ipui import *


class Form_ParticleLife(BaseForm):

    TAB_LAYOUT = {
        "Rules": ["world_rules", "interaction_rules", "dynamics_rules"],
        "Particles": [("particles",1),( "matrix",3)],
        "Settings": ["settings"],
        "Particle Life": ["particle_life"],
        "Stats": ["stats"],
        "Iamnothere":["ifnone"]
    }

    def build(self):
        row          = Row(self)
        Banner       ( row, "ParticleLife", glow=True)
        Spacer       ( row)
        btn          = Button(row, "Back to\nShowcase",   color_bg=Style.COLOR_TAB_BG,width_flex=0)
        btn.on_click = lambda: IPUI.back()