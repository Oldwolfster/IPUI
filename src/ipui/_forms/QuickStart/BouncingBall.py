from ipui import *
from ipui.widgets.Label import Detail
import pygame

class BouncingBall(_BaseTab):

    def arena(self, parent):                        # ← pane method: builds the UI
        Title(parent, text="Bouncing Ball")         # Print Title
        card=Card(parent, scrollable=True)          # Create a card for codebox
        CodeBox(card,data  =__file__)               # Put Codebox in the card

    def ip_setup(self, ip):                         # ← hook: runs once, initializes state
        self.ball_x, self.ball_y   = 0.5, 0.5       # put ball in middle of screen
        self.ball_dx, self.ball_dy = 0.4, 0.3       # set ball x and y movement

    def ip_think(self, ip):                         # ← hook: runs every frame
        self.ball_x += self.ball_dx * ip.dt         # move ball * ip.dt normalizes based on fps
        self.ball_y += self.ball_dy * ip.dt         # same but in y dimension
        self.bounce_off_walls(ip.rect_pane)         # check if it needs to bounce

    def ip_draw(self, ip):                          # ← hook: custom drawing
        pos = ip.to_screen(self.ball_x,self.ball_y) # convert normalized to screen coords
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, ip.scale_y(0.02))

    def bounce_off_walls(self, arena):
        if self.ball_x < 0: self.ball_dx = .4       # reverse if at left edge
        if self.ball_x > 1: self.ball_dx = -.4      # reverse if at right edge
        if self.ball_y < 0: self.ball_dy = .3       # reverse if it hit's top
        if self.ball_y > 1: self.ball_dy = -.3      # reverse if it hits bottom