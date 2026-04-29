from ipui import *
from ipui.engine.Key import Key
import math
import pygame

class Asteroids(_BaseForm):
    def build(self):
        row = Row(self)
        Banner(row, "Asteroids", glow=True, text_align=CENTER)
        Detail(row, "← → rotate   ↑ thrust", text_align=CENTER)
        self.lbl_score = Body(row, "Score: 0", text_align=CENTER)

    def ip_setup(self, ip):
        self.ship_x     = 0.5
        self.ship_y     = 0.5
        self.ship_angle = -90.0
        self.ship_dx    = 0.0
        self.ship_dy    = 0.0

    def ip_think(self, ip):
        if ip.key_down(Key.LEFT):
            self.ship_angle -= 180 * ip.dt
        if ip.key_down(Key.RIGHT):
            self.ship_angle += 180 * ip.dt

        if ip.key_down(Key.UP):
            angle_rad = math.radians(self.ship_angle)
            thrust    = 0.35
            self.ship_dx += math.cos(angle_rad) * thrust * ip.dt
            self.ship_dy += math.sin(angle_rad) * thrust * ip.dt

        self.ship_x += self.ship_dx * ip.dt
        self.ship_y += self.ship_dy * ip.dt
        self.wrap_around_screen(ip)

    def wrap_around_screen(self,ip):
        if self.ship_x < 0: self.ship_x = 1
        if self.ship_x > 1: self.ship_x = 0
        if self.ship_y < 0: self.ship_y = 1
        if self.ship_y > 1: self.ship_y = 0

    def ip_draw(self, ip):
        cx, cy = ip.to_screen(self.ship_x, self.ship_y)
        radius = ip.scale_y(0.035)
        points = []

        for angle_offset in (0, 140, 220):
            angle_rad = math.radians(self.ship_angle + angle_offset)
            px = cx + math.cos(angle_rad) * radius
            py = cy + math.sin(angle_rad) * radius
            points.append((px, py))

        pygame.draw.polygon(ip.surface, (230, 230, 230), points, width=2)

if __name__ == "__main__":
    show(Asteroids)