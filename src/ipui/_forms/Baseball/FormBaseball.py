from ipui._forms.ParticleLife.Form_ParticleLife import Form_ParticleLife
from ipui import *

class FormBaseball(_BaseForm):

    TAB_LAYOUT = {
        "Pipe"      : ["all_in_one"                                         ],
        "DB"        : [("database_browser", .169), ("fld_registry", .269), ("the_object", .369), ("the_inspector", .2369)],
        #"Pipe"      : ["all_in_one"                                         ],
        "Workshop"  : [("database_browser", .4), ("source", 1.2), ("columns", .569), ("tbl_ctrls", .369)],
        "Predict"   : [("controls", 0.2),("by_model", 0.75)                 ],
        "SQL"       : [("tables"  ,.5)  ,("query"   ,.7)    ,("results", 1) ],
        "Log"       : ["all_in_one"],  # NEW
        #"Registry"  : [("database_browser", .169),    ("registry_list", .3), ("columns ", .369),("tbl_ctrls", .369)],

        "Docs"      : [("tables"  ,.5)  ,("query"   ,.7)    ,("results", 1) ],
    }
    def shutdown(self): raise SystemExit
    def build(self):
        self.build_header()

    def build_header(self):
        header = Row(self)
        left = Row(header, flex_width=1)  # NEW - left container
        Banner(header, "IPUI - Baseball v8", text_align='c', glow=True, flex_width=0,fit_content=True)
        right = Row(header, flex_width=1)  # NEW - right container

        # Left content
        Button(left, "    EXIT     ",color_bg= Style.COLOR_BUTTON_DANGER,on_click=self.shutdown)

        # Right content
        Spacer(right) #pushes buttons to corner

        btn = Button(right, "Particle Life", pad_y=8)
        btn.on_click = lambda: self.open_particle_life()
        btn = Button(right, "Asteroids")
        btn.on_click = lambda: self.open_asteroids()
        btn = Button(right, "NeuroForge", color_bg=Style.COLOR_BUTTON_CTA)
        btn.on_click = lambda: self.open_neuroforge()


    def open_asteroids(self):

        from ipui._forms.Asteroids.FormAsteroids import Asteroids
        IPUI.show(Asteroids, "NeuroForge")

    def open_neuroforge(self):

        from ipui._forms.NeuroForge.FormNeuroForge import FormNeuroForge
        IPUI.show(FormNeuroForge, "NeuroForge")

    def open_particle_life(self):
        IPUI.show(Form_ParticleLife, "IPUI - Easy to get right, hard to get wrong!")
