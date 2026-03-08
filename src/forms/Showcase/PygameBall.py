# Welcome.py  Update: lifecycle hooks demo
from ipui.Style import Style
from ipui.engine._BasePane import _basePane
from ipui.widgets.Row import Row, CardCol
from ipui.widgets.Label import Title, Body, Detail


class PygameBall(_basePane):

    def initialize(self):
        self.ball_x     = 100
        self.ball_y     = 100
        self.ball_dx    = 120
        self.ball_dy    = 90
        self.fps        = 0
        self.last_event = "None yet"

    def welcome(self, parent):
        card = CardCol(parent, width_flex=True, height_flex=True)
        Title(card, "IPUI Lifecycle Hooks", glow=True)
        Body(card, "This pane demos on_event, on_update, and on_draw.")
        Body(card, "The bouncing ball is drawn via on_draw().")
        Body(card, "Ball physics run in on_update(dt).")
        Body(card, "Last event shown via on_event().")
        Detail(card, "", name="lbl_fps")
        Detail(card, "", name="lbl_event")

    def select_project(self, parent):
        card = CardCol(parent, height_flex=True)
        Title(card, "How It Works", glow=True)
        Body(card, "on_event(event)  — raw pygame events after IPUI processes")
        Body(card, "on_update(dt)    — per-frame logic, dt in seconds")
        Body(card, "on_draw(surface) — custom drawing after widgets render")

    def metaphor(self, parent):
        card = CardCol(parent, height_flex=True)
        Title(card, "The Unity Model", glow=True)
        Body(card, "Just like MonoBehaviour gives you Start, Update, OnGUI...")
        Body(card, "IPUI gives you on_event, on_update, on_draw.")
        Body(card, "Override them on your Form. Zero cost if you don't.")