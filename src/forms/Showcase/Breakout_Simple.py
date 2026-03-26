# Breakout.py  Update: merged greet, HUD in canvas, CodeBox on right

import pygame

from ipui import *


class Breakout(_basePane):
    """Arcade demo: press Q or click to start."""

    IP_LIFECYCLE = "persist"

    def ip_setup_pane(self):
        self.playing    = False
        self.ball_x     = 0.5
        self.ball_y     = 0.5
        self.ball_dx    = 0.4
        self.ball_dy    = -0.5
        self.ball_r     = 0.015
        self.paddle_w   = 0.15
        self.paddle_h   = 0.02
        self.paddle_y   = 0.95
        self.bricks     = []
        self.score      = 0
        self.lives      = 3


    def game_hud(self, parent):
        """Score and lives as real IPUI widgets floating over the game."""
        row=Row(parent)
        Title(row, "Score: 0", name="lbl_score", glow=True)
        Spacer(row )
        Body(row, "Lives: 3", name="lbl_lives")

    def code(self, parent):
        Title(parent, "The Source", glow=True)
        Body(parent, "This pane reads its own file.")
        card = Card(parent, scrollable=True, height_flex=99)
        CodeBox(card,
            data  = __file__,)
            #start = "class Breakout",
            #end   = "# ══ PANE BUILDERS",)

    # ══════════════════════════════════════════════════════════════
    # GAME CONTROLS
    # ══════════════════════════════════════════════════════════════

    def start_game(self):
        self.playing = True
        self.score   = 0
        self.lives   = 3
        self.ball_x  = 0.5
        self.ball_y  = 0.7
        self.ball_dx = 0.4
        self.ball_dy = -0.5
        self.reset_bricks()
        self.build_hud()
        self.update_score()

    def build_hud(self):
        canvas = self.form.tab_strip.panes[1]
        canvas.clear_children()
        Title(canvas, "Score: 0", name="lbl_score", glow=True)
        Body(canvas, "Lives: 3", name="lbl_lives")

    def reset_bricks(self):
        self.bricks = []
        colors = [
            Style.COLOR_PAL_RED_DARK,
            Style.COLOR_PAL_ORANGE_BRIGHT,
            (255, 220, 60),
            Style.COLOR_PAL_GREEN_DARK,
            (80, 160, 255),
        ]
        rows = 5
        cols = 8
        bw   = 1.0 / cols
        bh   = 0.03
        top  = 0.08
        for r in range(rows):
            for c in range(cols):
                self.bricks.append({
                    "x": c * bw,
                    "y": top + r * (bh + 0.01),
                    "w": bw - 0.01,
                    "h": bh,
                    "color": colors[r % len(colors)],
                })

    def update_score(self):
        lbl = self.form.widgets.get("lbl_score")
        if lbl:
            lbl.set_text(f"Score: {self.score}")
        lbl = self.form.widgets.get("lbl_lives")
        if lbl:
            lbl.set_text(f"Lives: {self.lives}")

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS — this is what makes the game run
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ip):
        if ip.key_pressed("q") or ip.key_pressed("space"):
            if not self.playing:
                self.start_game()
        if not self.playing:
            return
        self.move_ball(ip.dt)
        self.bounce_walls()
        self.bounce_paddle(ip)
        self.bounce_bricks()
        self.check_ball_lost()

    def ip_renderpre(self, ip):
        if not self.playing or not ip.rect_pane:
            return
        self.draw_arena(ip)
        self.draw_bricks(ip)
        self.draw_paddle(ip)
        self.draw_ball(ip)

    def ip_renderpost(self, ip):
        pass



    # ══════════════════════════════════════════════════════════════
    # PHYSICS
    # ══════════════════════════════════════════════════════════════

    def move_ball(self, dt):
        self.ball_x += self.ball_dx * dt
        self.ball_y += self.ball_dy * dt

    def bounce_walls(self):
        r = self.ball_r
        if self.ball_x - r < 0:
            self.ball_x  = r
            self.ball_dx = abs(self.ball_dx)
        if self.ball_x + r > 1.0:
            self.ball_x  = 1.0 - r
            self.ball_dx = -abs(self.ball_dx)
        if self.ball_y - r < 0:
            self.ball_y  = r
            self.ball_dy = abs(self.ball_dy)

    def paddle_x(self, ip):
        r = ip.rect_pane
        if not r or r.width == 0:
            return 0.5
        return max(0.0, min(1.0, (ip.mouse_x - r.left) / r.width))

    def bounce_paddle(self, ip):
        px    = self.paddle_x(ip)
        left  = px - self.paddle_w / 2
        right = px + self.paddle_w / 2
        top   = self.paddle_y - self.paddle_h
        if (self.ball_dy > 0
        and top <= self.ball_y + self.ball_r <= self.paddle_y
        and left <= self.ball_x <= right):
            self.ball_dy = -abs(self.ball_dy)
            offset       = (self.ball_x - px) / (self.paddle_w / 2)
            self.ball_dx = offset * 0.6

    def bounce_bricks(self):
        hit = None
        for brick in self.bricks:
            if (brick["x"] <= self.ball_x <= brick["x"] + brick["w"]
            and brick["y"] <= self.ball_y <= brick["y"] + brick["h"]):
                hit = brick
                break
        if hit:
            self.bricks.remove(hit)
            self.ball_dy = -self.ball_dy
            self.score  += 10
            self.update_score()

    def check_ball_lost(self):
        if self.ball_y + self.ball_r < 1.0:
            return
        self.lives -= 1
        self.update_score()
        if self.lives <= 0:
            self.playing = False
            return
        self.ball_x  = 0.5
        self.ball_y  = 0.7
        self.ball_dy = -abs(self.ball_dy)

    # ══════════════════════════════════════════════════════════════
    # DRAWING
    # ══════════════════════════════════════════════════════════════

    def draw_arena(self, ip):
        pygame.draw.rect(ip.surface, (15, 15, 30), ip.rect_pane)

    def draw_bricks(self, ip):
        for b in self.bricks:
            pos  = ip.to_screen(b["x"], b["y"])
            w    = ip.scale_x(b["w"])
            h    = ip.scale_y(b["h"])
            rect = pygame.Rect(pos[0], pos[1], w, h)
            pygame.draw.rect(ip.surface, b["color"], rect)
            pygame.draw.rect(ip.surface, (255, 255, 255), rect, 1)

    def draw_paddle(self, ip):
        px   = self.paddle_x(ip)
        left = px - self.paddle_w / 2
        pos  = ip.to_screen(left, self.paddle_y)
        w    = ip.scale_x(self.paddle_w)
        h    = ip.scale_y(self.paddle_h)
        pygame.draw.rect(ip.surface, Style.COLOR_PAL_ORANGE_BRIGHT,
                         pygame.Rect(pos[0], pos[1], w, h))

    def draw_ball(self, ip):
        pos = ip.to_screen(self.ball_x, self.ball_y)
        r   = ip.scale_y(self.ball_r)
        pygame.draw.circle(ip.surface, (255, 255, 255), pos, r)


    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def greet(self, parent):
        Banner(parent, "BREAKOUT", glow=True)
        Body(parent, "A None pane in TAB_LAYOUT creates a "
                     "transparent canvas for pygame drawing.")
        card = Card(parent)
        Heading(card, "Please insert a quarter", glow=True)
        Body(card, "OR press Q")
        Button(card, "Insert Quarter",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=self.start_game)
        card = Card(parent)
        Heading(card, "You Can Build This!", glow=True)
        Body(card, "A real Breakout game. Right here. Right now.\n"
                  "10 minutes if you're fast.\n"
                  "60 minutes if you just learned what a keyboard is.\n"
                  "Either way, you'll be smashing bricks before lunch.")
        card = Card(parent)
        Heading(card, "What You Get For Free")
        Body(card, "A big empty space to draw in\n"
                  "7. A thinking loop for physics\n"
                  "8. A drawing loop for painting\n"
                  "9. Score as IPUI widgets in the canvas\n"
                  "10. All coordinates normalized 0-1")