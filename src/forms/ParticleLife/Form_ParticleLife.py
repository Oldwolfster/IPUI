import ipui
from ipui import *


class Form_ParticleLife(_BaseForm):

    TAB_LAYOUT  =       {
        "Rules"         : ["world_rules"    , "interaction_rules", "dynamics_rules"],
        "Particles"     : [("particles",1)  ,( "matrix",3)],
        "Settings"      : ["settings"],
        "ParticleLife"  : [("particle_life",2.7),None,None],
    }

    PIPELINE_DEFAULTS = {
        "pl.sim.paused"             : False,
        "pl.sim.r_min"              : 10.0,
        "pl.sim.r_mid"              : 40.0,
        "pl.sim.r_max"              : 90.0,
        "pl.sim.damping"            : 0.05,
        "pl.sim.v_max"              : 180.0,
        "pl.sim.force_scale"        : 120.0,
        "pl.sim.collision_strength" : 2.0,
        "pl.sim.trail_alpha"        : 36,
        "pl.particle_ids"           : ["A", "B", "C", "D"],
        "pl.p.A.name"               : "A",
        "pl.p.A.r"                  : 255,
        "pl.p.A.g"                  : 120,
        "pl.p.A.b"                  : 0,
        "pl.p.A.count"              : 151,
        "pl.p.B.name"               : "B",
        "pl.p.B.r"                  : 0,
        "pl.p.B.g"                  : 170,
        "pl.p.B.b"                  : 255,
        "pl.p.B.count"              : 151,
        "pl.p.C.name"               : "C",
        "pl.p.C.r"                  : 50,
        "pl.p.C.g"                  : 220,
        "pl.p.C.b"                  : 80,
        "pl.p.C.count"              : 151,
        "pl.p.D.name"               : "D",
        "pl.p.D.r"                  : 220,
        "pl.p.D.g"                  : 60,
        "pl.p.D.b"                  : 220,
        "pl.p.D.count"              : 151,
    }

    def ip_setup_pipeline(self):
        import random
        ids = self.pipeline_read("pl.particle_ids") or []
        for a in ids:
            for b in ids:
                key = f"pl.G.{a}.{b}"
                if self.pipeline_read(key) is None:
                    self.pipeline_set(key, round(random.uniform(-1.0, 1.0), 2))


    def build(self):
        row          = Row(self)
        Banner       ( row, "ParticleLife", glow=True)
        Spacer       ( row)
        btn          = Button(row, "Back to\nShowcase",   color_bg=Style.COLOR_TAB_BG,width_flex=0)
        btn.on_click = lambda: IPUI.back()