import ipui
from ipui import *


class Form_ParticleLife(_BaseForm):

    TAB_LAYOUT  =       {
        "ParticleLife"  : [("particle_life", .7), None, None],
        "Rules"         : ["world_rules"    , "interaction_rules", "dynamics_rules"],
        "Particles"     : [("particles",1)  ,( "matrix",3)],
        "Settings"      : ["settings"],

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

    def ip_setup(self,ip):
        import random
        ids = self.pipeline_read("pl.particle_ids") or []
        for a in ids:
            for b in ids:
                key = f"pl.G.{a}.{b}"
                if self.pipeline_read(key) is None:
                    self.pipeline_set(key, round(random.uniform(-1.0, 1.0), 2))


    def build(self):
        row          = Row(self)
        Banner       ( row, "Particle Life", glow=True)
        Spacer       ( row)
        Heading      ( row,"This is O(N^2) so expect poor FPS")
        Spacer(row)
        btn          = Button(row, "Back to\nShowcase",   color_bg=Style.COLOR_TAB_BG,flex_width=0)
        btn.on_click = lambda: IPUI.back()


coolest="""
  "matrix": {
    "A.A": ".06",
    "A.B": ".69",
    "A.C": "0.72",
    "A.D": "-0.151",
    "B.A": ".03",
    "B.B": "-.31",
    "B.C": "-.36",
    "B.D": "0.93",
    "C.A": "-.86",
    "C.B": ".17",
    "C.C": ".06",
    "C.D": "0.56",
    "D.A": ".71",
    "D.B": "-.35",
    "D.C": ".35",
    "D.D": ".35"
  }"""