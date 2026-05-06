from ipui._forms.ParticleLife.Form_ParticleLife import Form_ParticleLife
from ipui import *

class FormShowcase(_BaseForm):

    TAB_LAYOUT = {
        "Welcome"       : ["left_pane"      ,"proud_features"   ,"detail"       ],
        "Bouncing Ball": [("arena", .3), None],
        "Tab System"    : ["explain"        ,"showcase"                         ],
        "Widgets"       : ["catalog_grid"   ,"detail"                           ],
        "Widget Tree"   : ["widget_tree"    ,"widget_detail"                    ],
        "Wiring"        : ["reactive"       ,"imperative"                       ],
        "Pygame"        : [("overview", 2)  ,(None      , 3)    ,("code"   , 2) ],
        "Breakout"      : ["greet"          ,None               ,"code"         ],
        "SQLDELETE"           : [("tables"  ,.5)  ,("query"   ,.7)    ,("results", 1) ],
        "Paint"         : [("tools"   ,.3)  ,None                               ],
        "Designer"      : [("tab_map" , 1)  ,("preview" , 3)    ,("toolbox", 1) ],
    }

    def build(self):
        self.build_header()

    def build_header(self):
        header = Row(self)
        left = Row(header, width_flex=1)  # NEW - left container
        Banner(header, "IPUI", text_align='c', glow=True, width_flex=0,fit_content=True)
        right = Row(header, width_flex=1)  # NEW - right container

        # Left content
        Button(left, "Documentation", color_bg=Style.COLOR_BUTTON_CTA, on_click=lambda: self.show_modal("Press F12 - then select 'Documentation' tab"))

        # Right content
        Spacer(right) #pushes buttons to corner

        btn = Button(right, "Particle Life", color_bg=Style.COLOR_TAB_BG, pad_y=8)
        btn.on_click = lambda: self.open_particle_life()
        btn = Button(right, "Asteroids", color_bg=Style.COLOR_TAB_BG)
        btn.on_click = lambda: self.open_asteroids()
        btn = Button(right, "NeuroForge", color_bg=Style.COLOR_BUTTON_CTA)
        btn.on_click = lambda: self.open_neuroforge()

    def open_todo(self):

        from ipui._forms.Todo.FormTodo import TodoApp
        IPUI.show(TodoApp, "To Do")


    def open_asteroids(self):

        from ipui._forms.Asteroids.FormAsteroids import Asteroids
        IPUI.show(Asteroids, "NeuroForge")

    def open_neuroforge(self):

        from ipui._forms.NeuroForge.FormNeuroForge import FormNeuroForge
        IPUI.show(FormNeuroForge, "NeuroForge")


    def open_particle_life(self):
        IPUI.show(Form_ParticleLife, "IPUI - Easy to get right, hard to get wrong!")

    def ip_setup(self, ip):
        from pathlib import Path
        atest = Path(__file__).parent / "atest.py"
        if atest.exists(): atest.unlink()