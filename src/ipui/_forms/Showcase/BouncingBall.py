from ipui import *
import pygame

class BouncingBall(_BaseTab):

    BINDINGS = {
        "lbl_quadrant":  {"property": "text", "compute": "compute_quadrant",  "triggers": ["ball_x", "ball_y"]},
        "lbl_direction": {"property": "text", "compute": "compute_direction", "triggers": ["ball_dx", "ball_dy"]},
        "lbl_warning":   {"property": "text", "compute": "compute_warning",   "triggers": ["ball_x", "ball_y"]},
    }

    # replace Arena with this - Reactive uses named widgets instead of instance references
    def arena(self, parent):
        Body(parent, "Quadrant: —"  , name="lbl_quadrant" ) # NOTE: No self.lbl_quadrant
        Body(parent, "Direction: —" , name="lbl_direction") # NOTE: No self.lbl_direction
        Body(parent, ""             , name="lbl_warning"  ) # NOTE: No self.lbl_warning

    def ip_setup(self, ip):                          # ← runs once
        self.ball_x,  self.ball_y  = 0.5, 0.5        # start in the middle (normalized)
        self.ball_dx, self.ball_dy = 0.4, 0.3        # velocity (normalized units / sec)

    def ip_think(self, ip):
        self.ball_x += self.ball_dx * ip.dt                 # No change
        self.ball_y += self.ball_dy * ip.dt                 # No change
        self.bounce_off_walls()                             # No change

        # Replace Imperative update with Reactive update.   # Set pipeline values
        self.form.pipeline_set("ball_x",  self.ball_x)      # framework sees the change,
        self.form.pipeline_set("ball_y",  self.ball_y)      # calls the right compute methods,
        self.form.pipeline_set("ball_dx", self.ball_dx)     # and updates the widgets.
        self.form.pipeline_set("ball_dy", self.ball_dy)


    def ip_draw(self, ip):                           # ← custom rendering
        pos = ip.to_screen(self.ball_x, self.ball_y) # normalized → screen pixels
        r   = ip.scale_y(0.02)                       # normalized radius → pixels
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, r)

    def compute_quadrant (self, ball_x, ball_y):  return f"Quadrant: {('NW' if ball_y<0.5 else 'SW') if ball_x<0.5 else ('NE' if ball_y<0.5 else 'SE')}"
    def compute_direction(self, ball_dx, ball_dy): return f"Direction: {'Right ' if ball_dx>0 else 'Left '}{'Down' if ball_dy>0 else 'Up'}"
    def compute_warning  (self, ball_x, ball_y):  return "I don't want to hit the wall" if min(ball_x, ball_y, 1-ball_x, 1-ball_y) < 0.05 else ""


    def bounce_off_walls(self):
        if self.ball_x < 0: self.ball_dx =  0.4
        if self.ball_x > 1: self.ball_dx = -0.4
        if self.ball_y < 0: self.ball_dy =  0.3
        if self.ball_y > 1: self.ball_dy = -0.3