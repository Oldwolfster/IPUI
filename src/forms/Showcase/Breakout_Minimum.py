# Breakout.py  Update: full Breakout game with ip hooks

import pygame
from ipui.Style import Style
from ipui.engine._BasePane import _basePane
from ipui.widgets.Row import Row
from ipui.widgets.Label import Title, Body, Heading, Banner
from ipui.widgets.Card import Card
from ipui.widgets.Button import Button


class Breakout(_basePane):
    """Arcade demo: press Q or click to start, controls appear on canvas."""

    IP_LIFECYCLE = "persist"

    def initialize(self):
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

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def greet(self, parent):
        Banner(parent, "BREAKOUT", glow=True)
        Body(parent, "This demo shows how a None pane in TAB_LAYOUT "
                     "creates a transparent canvas for pygame drawing.")
        card = Card(parent)
        Heading(card, "Please insert a quarter", glow=True)
        Body(card, "OR press Q")
        Button(card, "Insert Quarter",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=self.start_game)

    def game_controls(self, parent):
        """Loaded into the None slot via set_pane when game starts."""
        Title(parent, "GAME ON!", glow=True, text_align='c')
        Body(parent, "That title is centered. No math. No blit. One line.", text_align='c')
        card = Card(parent)
        Heading(card, "Think You Can Build This?", glow=True)
        Body(card, "A real Breakout game. Right here. Right now.\n"
                  "5 minutes if you're fast.\n"
                  "20 minutes if you just learned what a keyboard is.\n"
                  "Either way, you'll be smashing bricks before lunch.")
        card = Card(parent)
        Heading(card, "The Game")
        Body(card, "1. A paddle at the bottom that follows your mouse\n"
                  "2. A ball that bounces off everything it touches\n"
                  "3. Rows of colorful bricks waiting to be smashed\n"
                  "4. A score that goes up every time a brick explodes\n"
                  "5. Miss the ball? Lose a life. Three strikes you're out.")
        card = Card(parent)
        Heading(card, "What You Get For Free")
        Body(card, "6. A big empty space to draw your game in\n"
                  "7. A thinking loop for physics and collisions\n"
                  "8. A drawing loop for painting your world\n"
                  "9. A scoreboard already waiting on the right\n"
                  "10. Pause and Quit already wired up below")
        row = Row(parent)
        Button(row, "Pause",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.pause_game)
        Button(row, "Quit",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.end_game)

    def scoreboard(self, parent):
        Title(parent, "Scoreboard", glow=True)
        Body(parent, "Score: 0", name="lbl_score")

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
        self.form.set_pane(1, self.game_controls)
        self.update_score()

    def pause_game(self):
        self.playing = not self.playing

    def end_game(self):
        self.playing = False

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
            lbl.set_text(f"Score: {self.score}  Lives: {self.lives}")

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ip):
        if ip.key_pressed("q") or ip.key_pressed("space"):
            if not self.playing:
                self.start_game()
        if not self.playing:
            return
        self.move_ball(ip.dt)
        arena = self.compute_arena(ip)
        if arena:
            self.bounce_walls(arena)
            self.bounce_paddle(ip, arena)
            self.bounce_bricks()
            self.check_ball_lost(arena)

    def ip_renderpre(self, ip):
        if not self.playing:
            return
        arena = self.compute_arena(ip)
        if not arena:
            return
        self.draw_arena(ip.surface, arena)
        self.draw_bricks(ip.surface, arena)
        self.draw_paddle(ip, arena)
        self.draw_ball_circle(ip.surface, arena)

    def ip_renderpost(self, ip):
        pass

    # ══════════════════════════════════════════════════════════════
    # ARENA
    # ══════════════════════════════════════════════════════════════

    def compute_arena(self, ip):
        tab_strip = getattr(ip.form, 'tab_strip', None)
        if not tab_strip or not tab_strip.content:
            return None
        for child in tab_strip.content.children:
            if child.rect and not child.children:
                return child.rect
        return None

    # ══════════════════════════════════════════════════════════════
    # PHYSICS
    # ══════════════════════════════════════════════════════════════

    def move_ball(self, dt):
        self.ball_x += self.ball_dx * dt
        self.ball_y += self.ball_dy * dt

    def bounce_walls(self, arena):
        if self.ball_x - self.ball_r < 0:
            self.ball_x  = self.ball_r
            self.ball_dx = abs(self.ball_dx)
        if self.ball_x + self.ball_r > 1.0:
            self.ball_x  = 1.0 - self.ball_r
            self.ball_dx = -abs(self.ball_dx)
        if self.ball_y - self.ball_r < 0:
            self.ball_y  = self.ball_r
            self.ball_dy = abs(self.ball_dy)

    def get_paddle_x(self, ip, arena):
        mx = ip.mouse_x - arena.left
        return max(0.0, min(1.0, mx / arena.width))

    def bounce_paddle(self, ip, arena):
        px    = self.get_paddle_x(ip, arena)
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

    def check_ball_lost(self, arena):
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

    def draw_arena(self, surface, arena):
        pygame.draw.rect(surface, (15, 15, 30), arena)

    def draw_bricks(self, surface, arena):
        for b in self.bricks:
            rect = pygame.Rect(
                arena.left + int(b["x"] * arena.width),
                arena.top  + int(b["y"] * arena.height),
                int(b["w"] * arena.width),
                int(b["h"] * arena.height),
            )
            pygame.draw.rect(surface, b["color"], rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)

    def draw_paddle(self, ip, arena):
        px   = self.get_paddle_x(ip, arena)
        left = int((px - self.paddle_w / 2) * arena.width)
        rect = pygame.Rect(
            arena.left + left,
            arena.top  + int(self.paddle_y * arena.height),
            int(self.paddle_w * arena.width),
            int(self.paddle_h * arena.height),
        )
        pygame.draw.rect(ip.surface, Style.COLOR_PAL_ORANGE_BRIGHT, rect)

    def draw_ball_circle(self, surface, arena):
        sx = arena.left + int(self.ball_x * arena.width)
        sy = arena.top  + int(self.ball_y * arena.height)
        r  = int(self.ball_r * arena.height)
        pygame.draw.circle(surface, (255, 255, 255), (sx, sy), r)