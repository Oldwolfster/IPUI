from ipui import *
from ipui.engine.Key import Key
import math
import pygame
import random

class Asteroids(_BaseForm):
    def build(self):
        row = Row(self)
        Title(row, "Asteroids", glow=True, text_align=CENTER)
        #self.show_modal("Yo")
        #Detail(row, "← → rotate   ↑ thrust   space fire   R restart", text_align=CENTER)
        self.lbl_score = Title(row, "Score: 0", text_align=CENTER,glow=True)
        self.lbl_level = Title(row, "Level: 1", text_align=CENTER,glow=True)
        #self.lbl_state = Body(row, "Playing", text_align=CENTER)

    def ip_setup(self, ip):
        self.reset_game()

    def reset_game(self):
        self.ship_x     = 0.5
        self.ship_y     = 0.5
        self.ship_angle = -90.0
        self.ship_dx    = 0.0
        self.ship_dy    = 0.0

        self.score      = 0
        self.level      = 1
        self.game_over  = False
        self.bullets    = []
        self.asteroids  = []

        self.spawn_asteroids()

    def ip_think(self, ip):
        if ip.key_pressed(Key.Q):
            IPUI.back()

        if ip.key_pressed(Key.R):
            self.reset_game()

        if self.game_over:
            self.update_labels()
            return

        if ip.key_down(Key.LEFT):
            self.ship_angle -= 180 * ip.dt
        if ip.key_down(Key.RIGHT):
            self.ship_angle += 180 * ip.dt

        if ip.key_down(Key.UP):
            angle_rad = math.radians(self.ship_angle)
            thrust    = 0.35
            self.ship_dx += math.cos(angle_rad) * thrust * ip.dt
            self.ship_dy += math.sin(angle_rad) * thrust * ip.dt

        if ip.key_pressed(Key.SPACE):
            self.fire_bullet()

        self.ship_x += self.ship_dx * ip.dt
        self.ship_y += self.ship_dy * ip.dt
        self.wrap_ship_around_screen()

        self.update_bullets(ip)
        self.update_asteroids(ip)
        self.check_bullet_hits()
        self.check_ship_hits()

        self.update_labels()

    def update_labels(self):
        self.lbl_score.set_text(f"Score: {self.score}")
        self.lbl_level.set_text(f"Level: {self.level}")

    def fire_bullet(self):
        angle_rad    = math.radians(self.ship_angle)
        bullet_speed = 0.8
        nose_offset  = 0.04

        self.bullets.append({
            "x"   : self.ship_x + math.cos(angle_rad) * nose_offset,
            "y"   : self.ship_y + math.sin(angle_rad) * nose_offset,
            "dx"  : math.cos(angle_rad) * bullet_speed,
            "dy"  : math.sin(angle_rad) * bullet_speed,
            "life": 1.2,
        })

    def spawn_asteroids(self):
        self.asteroids.clear()
        asteroid_count = min(3 + self.level - 1, 8)

        for _ in range(asteroid_count):
            while True:
                x = random.random()
                y = random.random()
                dx = x - self.ship_x
                dy = y - self.ship_y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance > 0.2:
                    break

            self.asteroids.append({
                "x" : x,
                "y" : y,
                "dx": random.uniform(-0.12, 0.12),
                "dy": random.uniform(-0.12, 0.12),
                "r" : random.uniform(0.035, 0.06),
            })

    def update_bullets(self, ip):
        bullets_alive = []

        for bullet in self.bullets:
            bullet["x"]    += bullet["dx"] * ip.dt
            bullet["y"]    += bullet["dy"] * ip.dt
            bullet["life"] -= ip.dt

            self.wrap_object_around_screen(bullet)

            if bullet["life"] > 0:
                bullets_alive.append(bullet)

        self.bullets = bullets_alive

    def update_asteroids(self, ip):
        for asteroid in self.asteroids:
            asteroid["x"] += asteroid["dx"] * ip.dt
            asteroid["y"] += asteroid["dy"] * ip.dt
            self.wrap_object_around_screen(asteroid)

    def check_bullet_hits(self):
        bullets_alive = []
        asteroids_hit = set()

        for bullet in self.bullets:
            bullet_hit = False

            for i, asteroid in enumerate(self.asteroids):
                dx       = bullet["x"] - asteroid["x"]
                dy       = bullet["y"] - asteroid["y"]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= asteroid["r"]:
                    bullet_hit = True
                    asteroids_hit.add(i)
                    self.score += 10
                    break

            if not bullet_hit:
                bullets_alive.append(bullet)

        asteroids_alive = []
        for i, asteroid in enumerate(self.asteroids):
            if i not in asteroids_hit:
                asteroids_alive.append(asteroid)

        self.bullets   = bullets_alive
        self.asteroids = asteroids_alive

        if not self.asteroids:
            self.level += 1
            self.spawn_asteroids()

    def check_ship_hits(self):
        ship_radius = 0.025

        for asteroid in self.asteroids:
            dx       = self.ship_x - asteroid["x"]
            dy       = self.ship_y - asteroid["y"]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= asteroid["r"] + ship_radius:
                self.game_over = True
                return

    def wrap_ship_around_screen(self):
        if self.ship_x < 0: self.ship_x = 1
        if self.ship_x > 1: self.ship_x = 0
        if self.ship_y < 0: self.ship_y = 1
        if self.ship_y > 1: self.ship_y = 0

    def wrap_object_around_screen(self, obj):
        if obj["x"] < 0: obj["x"] = 1
        if obj["x"] > 1: obj["x"] = 0
        if obj["y"] < 0: obj["y"] = 1
        if obj["y"] > 1: obj["y"] = 0

    def ip_draw(self, ip):
        self.draw_ship(ip)
        self.draw_bullets(ip)
        self.draw_asteroids(ip)

    def ip_draw_hud(self, ip):
        if not self.game_over:        return
        surf = MgrFont.render_lines("GAME OVER\nPress R to Restart\nPress Q to Quit",                                    Style.FONT_TITLE, (230, 230, 230))
        rect = surf.get_rect(center=ip.rect_screen.center)
        ip.surface.blit(surf, rect)




    def draw_ship(self, ip):
        if self.game_over:
            return

        cx, cy = ip.to_screen(self.ship_x, self.ship_y)
        radius = ip.scale_y(0.035)
        points = []

        for angle_offset in (0, 140, 220):
            angle_rad = math.radians(self.ship_angle + angle_offset)
            px = cx + math.cos(angle_rad) * radius
            py = cy + math.sin(angle_rad) * radius
            points.append((px, py))

        pygame.draw.polygon(ip.surface, (230, 230, 230), points, width=2)

    def draw_bullets(self, ip):
        for bullet in self.bullets:
            bx, by = ip.to_screen(bullet["x"], bullet["y"])
            pygame.draw.circle(ip.surface, (230, 230, 230), (int(bx), int(by)), 3)

    def draw_asteroids(self, ip):
        for asteroid in self.asteroids:
            ax, ay = ip.to_screen(asteroid["x"], asteroid["y"])
            ar     = ip.scale_y(asteroid["r"])
            pygame.draw.circle(ip.surface, (180, 180, 180), (int(ax), int(ay)), int(ar), width=2)

if __name__ == "__main__":
    show(Asteroids)