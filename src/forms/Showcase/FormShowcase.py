# FormShowcase.py  NEW: PIP demo entry form
from forms.ParticleLife.Form_ParticleLife import Form_ParticleLife
from ipui import Spacer
from ipui.engine._BaseForm import _BaseForm
from ipui.engine.IPUI import IPUI
from ipui.Style import Style
from ipui.widgets.Button import Button
from ipui.widgets.Row import Row
from ipui.widgets.Label import Banner


class FormShowcase(_BaseForm):

    TAB_LAYOUT = {
        "Welcome"       : ["welcome"        ,"select_project"   ,"metaphor"     ],
        "FixScroll"     : [("pane1"  ,1)    ,("pane2", 3)                       ],
        "Your Choice"   : ["reactive"       ,"imperative"                       ],
        "Breakout_clone": ["greet"          ,"game"             ,"scoreboard"   ],
        "Breakout"      : ["greet"          , None              ,"code"   ],
        "SQL"           : [("tables", .5)   ,("query", .7)      ,("results", 1) ],
        "PygameBall2"   : [("overview",2)   ,(None, 3)          ,("code",2)     ],
        "Designer"      : [("tab_map",1)    ,("preview" ,3)     ,("toolbox", 1) ],
        "Freebies"      : ["the_pitch"      ,"pipeline_demo"    ,"widgets_demo" ],
        "Widgets"       : ["catalog_grid"   ,"detail"           ,"code"         ],
        "Tree"          : ["widget_tree"    ,"widget_detail"                    ],

        "Showcase"  : ["the_pitch"      ,"pipeline_live"]                    ,
    }
    def build(self):
        self.build_header()

    def build_header(self):
        header = Row(self, justify_spread=True)
        Button(header, "Docs",       color_bg=Style.COLOR_TAB_BG,width_flex=1)
        Spacer(header)  #default width_flex should be one.
        Banner(header, "IPUI",       text_align='c', glow=True,width_flex=8)
        btn = Button(header, "See It Live\n Particle Life", color_bg=Style.COLOR_TAB_BG,width_flex=1)#, btn.on_click = lambda:  self.open_particle_life())
        btn.on_click = lambda: self.open_particle_life()
        btn = Button(header, "See It Live\n Neuro Forge", color_bg=Style.COLOR_PAL_GREEN_DARK, width_flex=1)
        btn.on_click = lambda: self.open_neuroforge()


    def open_neuroforge(self):

        from forms.NeuroForge.FormNeuroForge import FormNeuroForge
        IPUI.show(FormNeuroForge, "NeuroForge")


    def open_particle_life(self):
        IPUI.show(Form_ParticleLife, "IPUI - Easy to get right, hard to get wrong!")


    def on_event(self, event):
        pass#w = self.find("lbl_event")
        #if w: w.set_text(f"Last event: {event}")

    # FormShowcase.py method: on_update  NEW: lifecycle hook demo
    def on_update(self, dt):
        pass
        #w = self.find("lbl_fps")
        #if w: w.set_text(f"FPS: {int(1/dt) if dt > 0 else 0}")

        # Bounce the ball
        ###self.ball_x = getattr(self, 'ball_x', 100) + getattr(self, 'ball_dx', 120) * dt
        ###self.ball_y = getattr(self, 'ball_y', 100) + getattr(self, 'ball_dy', 90) * dt

        ###if self.ball_x < 0 or self.ball_x > Style.SCREEN_WIDTH:  self.ball_dx = -self.ball_dx
        ###if self.ball_y < 0 or self.ball_y > Style.SCREEN_HEIGHT: self.ball_dy = -self.ball_dy

    # FormShowcase.py method: on_draw  NEW: lifecycle hook demo
    def on_draw(self, surface):
        return
        import pygame
        x = int(getattr(self, 'ball_x', 100))
        y = int(getattr(self, 'ball_y', 100))
        pygame.draw.circle(surface, Style.COLOR_PAL_ORANGE_BRIGHT, (x, y), 12)