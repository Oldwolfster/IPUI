# Breakout.py  New: Arcade-style demo — None panes, set_pane, ip_renderpre

import pygame
from ipui.Style import Style
from ipui.engine._BasePane import _basePane
from ipui.widgets.Row import Row
from ipui.widgets.Label import Title, Body, Heading, Banner, Detail
from ipui.widgets.Card import Card
from ipui.widgets.Button import Button


class Breakout(_basePane):
    """Arcade demo: transparent None pane becomes the game canvas."""

    IP_LIFECYCLE = "persist"

    def initialize(self):
        self.playing      = False
        self.paused       = False
        self.score        = 0
        self.ball_x       = 300.0
        self.ball_y       = 400.0
        self.ball_dx      = 250.0
        self.ball_dy      = -200.0
        self.ball_r       = 8
        self.paddle_x     = 250.0
        self.paddle_w     = 100
        self.paddle_h     = 12
        self.bricks       = []

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def greet(self, parent):
        Banner(parent, "BREAKOUT", glow=True)
        Body(parent, "Classic arcade action powered by IPUI lifecycle hooks.")

        card = Card(parent)
        Heading(card, "How it works:", glow=True)
        Body(card, "The middle pane is None in TAB_LAYOUT — "
                   "a transparent canvas. ip_renderpre draws "
                   "the game behind the UI. set_pane loads "
                   "controls into the canvas at runtime.")

        card = Card(parent)
        Heading(card, "Please insert a quarter", glow=True)
        Body(card, "OR press Q")
        Button(card, "Insert Quarter",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=self.start_game)

    def game_controls(self, parent):
        """Loaded into the None slot via set_pane on game start."""
        Detail(parent, "Arrow keys to move paddle", text_align='c')
        row = Row(parent)
        Button(row, "Pause",
               color_bg=Style.COLOR_TAB_BG, width_flex=True,
               on_click=self.toggle_pause)
        Button(row, "Quit",
               color_bg=Style.COLOR_TAB_BG, width_flex=True,
               on_click=self.end_game)

    def scoreboard(self, parent):
        Title(parent, "Scoreboard", glow=True)
        Body(parent, "Score: 0", name="lbl_score")
        card = Card(parent)
        Heading(card, "Controls:", glow=True)
        Body(card, "← →  Move paddle")
        Body(card, "Q      Start game")
        Body(card, "P      Pause")

    # ══════════════════════════════════════════════════════════════
    # GAME STATE
    # ══════════════════════════════════════════════════════════════

    def start_game(self):
        self.playing  = True
        self.paused   = False
        self.score    = 0
        self.ball_x   = 300.0
        self.ball_y   = 400.0
        self.ball_dx  = 250.0
        self.ball_dy  = -200.0
        self.spawn_bricks()
        self.form.set_pane(1, self.game_controls)
        self.update_score()

    def toggle_pause(self):
        self.paused = not self.paused

    def end_game(self):
        self.playing = False

    def update_score(self):
        lbl = self.form.widgets.get("lbl_score")
        if lbl:
            lbl.set_text(f"Score: {self.score}")

    def spawn_bricks(self):
        self.bricks = []
        colors = [
            Style.COLOR_PAL_ORANGE_BRIGHT,
            (255, 200, 60),
            (100, 220, 100),
            (100, 180, 255),
            (200, 120, 255),
        ]
        for row in range(5):
            for col in range(8):
                self.bricks.append({
                    "x"     : col * 70 + 10,
                    "y"     : row * 25 + 30,
                    "w"     : 64,
                    "h"     : 18,
                    "alive" : True,
                    "color" : colors[row % len(colors)],
                })

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ip):
        if ip.key_pressed("q") and not self.playing:
            self.start_game()
        if ip.key_pressed("p") and self.playing:
            self.toggle_pause()
        if not self.playing or self.paused:
            return
        self.move_paddle(ip)
        self.move_ball(ip)
        self.check_collisions()

    def ip_renderpre(self, ip):
        if not self.playing:
            return
        arena = self.get_arena()
        if not arena:
            return
        self.draw_bricks(ip.surface, arena)
        self.draw_paddle(ip.surface, arena)
        self.draw_ball_sprite(ip.surface, arena)

    def ip_renderpost(self, ip):
        if not self.playing:
            return
        arena = self.get_arena()
        if not arena:
            return
        font = Style.FONT_DETAIL
        text = f"FPS: {ip.fps}"
        surf = font.render(text, True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (arena.right - surf.get_width() - 8,
                               arena.top + 4))
        if self.paused:
            font = Style.FONT_TITLE
            surf = font.render("PAUSED", True, Style.COLOR_PAL_ORANGE_BRIGHT)
            ip.surface.blit(surf, (arena.centerx - surf.get_width() // 2,
                                   arena.centery - surf.get_height() // 2))

    # ══════════════════════════════════════════════════════════════
    # ARENA
    # ══════════════════════════════════════════════════════════════

    def get_arena(self):
        pane = self.form.tab_strip.panes[1]
        if pane and pane.rect:
            return pane.rect
        return None

    # ══════════════════════════════════════════════════════════════
    # PHYSICS
    # ══════════════════════════════════════════════════════════════

    def move_paddle(self, ip):
        arena = self.get_arena()
        if not arena:
            return
        speed = 400.0 * ip.dt
        if ip.key_down("left"):  self.paddle_x -= speed
        if ip.key_down("right"): self.paddle_x += speed
        self.paddle_x = max(0, min(self.paddle_x, arena.width - self.paddle_w))

    def move_ball(self, ip):
        self.ball_x += self.ball_dx * ip.dt
        self.ball_y += self.ball_dy * ip.dt
        arena = self.get_arena()
        if arena:
            self.bounce_walls(arena)
            self.bounce_paddle(arena)

    def bounce_walls(self, arena):
        r = self.ball_r
        if self.ball_x - r < 0:
            self.ball_x  = r
            self.ball_dx = abs(self.ball_dx)
        if self.ball_x + r > arena.width:
            self.ball_x  = arena.width - r
            self.ball_dx = -abs(self.ball_dx)
        if self.ball_y - r < 0:
            self.ball_y  = r
            self.ball_dy = abs(self.ball_dy)
        if self.ball_y + r > arena.height:
            self.ball_y  = arena.height - r
            self.ball_dy = -abs(self.ball_dy)

    def bounce_paddle(self, arena):
        paddle_top = arena.height - 40
        if self.ball_dy > 0 and self.ball_y + self.ball_r >= paddle_top:
            if self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_w:
                self.ball_dy = -abs(self.ball_dy)
                self.ball_y  = paddle_top - self.ball_r

    def check_collisions(self):
        for brick in self.bricks:
            if not brick["alive"]:
                continue
            if self.ball_hits_brick(brick):
                brick["alive"] = False
                self.ball_dy   = -self.ball_dy
                self.score    += 10
                self.update_score()

    def ball_hits_brick(self, brick):
        closest_x = max(brick["x"], min(self.ball_x, brick["x"] + brick["w"]))
        closest_y = max(brick["y"], min(self.ball_y, brick["y"] + brick["h"]))
        dx = self.ball_x - closest_x
        dy = self.ball_y - closest_y
        return (dx * dx + dy * dy) < (self.ball_r * self.ball_r)

    # ══════════════════════════════════════════════════════════════
    # DRAWING
    # ══════════════════════════════════════════════════════════════

    def draw_bricks(self, surface, arena):
        for brick in self.bricks:
            if not brick["alive"]:
                continue
            r = pygame.Rect(arena.left + brick["x"],
                            arena.top  + brick["y"],
                            brick["w"], brick["h"])
            pygame.draw.rect(surface, brick["color"], r)
            pygame.draw.rect(surface, (40, 40, 50), r, 1)

    def draw_paddle(self, surface, arena):
        paddle_top = arena.height - 40
        r = pygame.Rect(arena.left + int(self.paddle_x),
                        arena.top  + paddle_top,
                        self.paddle_w, self.paddle_h)
        pygame.draw.rect(surface, Style.COLOR_TEXT, r)

    def draw_ball_sprite(self, surface, arena):
        sx = arena.left + int(self.ball_x)
        sy = arena.top  + int(self.ball_y)
        pygame.draw.circle(surface, Style.COLOR_PAL_ORANGE_BRIGHT, (sx, sy), self.ball_r)