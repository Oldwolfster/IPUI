# Breakout.py  Update: delegate-based state machine

import random
import pygame

from ipui import *
from ipui.engine.Key import Key
from ipui.engine.Mouse import Mouse


class Breakout(_BaseTab):
    """Arcade demo with attract mode, levels, and forgiving paddle."""
    # ══════════════════════════════════════════════════════════════
    # SETUP
    # ══════════════════════════════════════════════════════════════

    def ip_setup_pane(self):
        self.ball_r       = 0.015
        self.paddle_w     = 0.15
        self.paddle_h     = 0.02
        self.paddle_y     = 0.95
        self.hitbox_extra = 0.02
        self.auto_paddle  = 0.5
        self.base_speed   = 0.5
        self.speed_bump   = 0.12
        self.score        = 0
        self.lives        = 3
        self.level        = 1
        self.bricks       = []
        self.ip.state.add ("DEMO"        , self.state_demo)
        self.ip.state.add ("READY"       , self.state_ready)
        self.ip.state.add ("PLAYING"     , self.state_playing)
        self.ip.state.add ("LEVEL_UP"    , self.state_level_up, "READY", 1.5)
        self.ip.state.add ("GAME_OVER"   , self.state_game_over, "DEMO", 1.5)
        self.ip.state.debug()
        self.start_demo()

    def start_demo(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.reset_bricks()
        self.reset_ball()
        self.ip.state.go("DEMO")
        self.build_hud()


    def start_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.reset_bricks()
        self.reset_ball()
        self.ip.state.go("READY")
        self.build_hud()

    def reset_ball(self):
        speed        = self.base_speed + self.speed_bump * (self.level - 1)
        self.ball_x  = 0.5
        self.ball_y  = self.paddle_y - self.ball_r - 0.01
        self.ball_dx = speed * 0.8
        self.ball_dy = -speed

    # ══════════════════════════════════════════════════════════════
    # STATE DELEGATES
    # ══════════════════════════════════════════════════════════════

    def state_demo(self):
        if not self.bricks or self.lives <= 0:
            self.start_demo()
            return
        if self.ip.key_pressed(Key.Q) or self.ip.key_pressed(Key.SPACE):
            self.start_game()
            return
        self.auto_paddle = self.ball_x
        self.run_physics(self.ip)

    def state_ready(self):
        ip = self.ip
        self.ball_x = self.paddle_x(ip)
        self.ball_y = self.paddle_y - self.ball_r - 0.01
        if ip.key_pressed(Key.SPACE):
            ip.state.go("PLAYING")
            return
        if ip.mouse_pressed(Mouse.LEFT) and ip.mouse_inside_pane():
            ip.state.go("PLAYING")

    def state_playing(self):
        self.run_physics(self.ip)

    def state_level_up(self):
        pass

    def state_game_over(self):
        pass

    # ══════════════════════════════════════════════════════════════
    # LEVELS
    # ══════════════════════════════════════════════════════════════

    def next_level(self):
        self.level += 1
        self.reset_bricks()
        self.reset_ball()
        self.update_hud()
        self.ip.state.go("LEVEL_UP")

    # ══════════════════════════════════════════════════════════════
    # BRICKS
    # ══════════════════════════════════════════════════════════════

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

    # ══════════════════════════════════════════════════════════════
    # HUD
    # ══════════════════════════════════════════════════════════════

    def build_hud(self):
        canvas = self.form.tab_strip.panes[1]
        canvas.clear_children()
        row = Row(canvas)
        Title(row, " ", name="lbl_score", glow=True)
        Spacer(row)
        Body(row, " ", name="lbl_level")
        Spacer(row)
        Body(row, " ", name="lbl_lives")
        self.update_hud()

    def update_hud(self):
        lbl = self.form.widgets.get("lbl_score")
        if lbl:
            lbl.set_text(f"Score: {self.score}")
        lbl = self.form.widgets.get("lbl_level")
        if lbl:
            lbl.set_text(f"Level: {self.level}")
        lbl = self.form.widgets.get("lbl_lives")
        if lbl:
            lbl.set_text("DEMO" if self.ip.state.is_("DEMO") else f"Lives: {self.lives}")

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS
    # ══════════════════════════════════════════════════════════════



    def run_physics(self, ip):
        self.move_ball(ip.dt)
        self.bounce_walls()
        self.bounce_paddle(ip)
        self.bounce_bricks()
        self.check_ball_lost()

    def ip_draw(self, ip):
        if not ip.rect_pane:
            return
        self.draw_arena(ip)
        self.draw_bricks(ip)
        self.draw_paddle(ip)
        self.draw_ball(ip)

    def ip_draw_hud(self, ip):
        if ip.state.is_("LEVEL_UP"):
            self.draw_state_message(ip, "LEVEL UP!")
        elif ip.state.is_("GAME_OVER"):
            self.draw_state_message(ip, "GAME OVER")
        elif ip.state.is_("READY"):
            self.draw_state_message(ip, "Click to Launch!")

    # ══════════════════════════════════════════════════════════════
    # PADDLE
    # ══════════════════════════════════════════════════════════════

    def paddle_x(self, ip):
        if self.ip.state.is_("DEMO"):
            return max(0.0, min(1.0, self.auto_paddle))
        r = ip.rect_pane
        if not r or r.width == 0:
            return 0.5
        return max(0.0, min(1.0, (ip.mouse_x - r.left) / r.width))

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

    def bounce_paddle(self, ip):
        px    = self.paddle_x(ip)
        extra = self.hitbox_extra
        left  = px - self.paddle_w / 2 - extra
        right = px + self.paddle_w / 2 + extra
        top   = self.paddle_y - self.paddle_h
        bot   = self.paddle_y + self.ball_r + 0.02
        if (self.ball_dy > 0
        and top <= self.ball_y + self.ball_r <= bot
        and left <= self.ball_x <= right):
            self.ball_dy = -abs(self.ball_dy)
            if self.ip.state.is_("DEMO"):
                self.ball_dx = random.uniform(-0.5, 0.5)
            else:
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
            self.update_hud()
            if not self.bricks:
                self.next_level()

    def check_ball_lost(self):
        if self.ball_y + self.ball_r < 1.0:
            return
        self.lives -= 1
        self.update_hud()
        if self.lives <= 0:
            self.ip.state.go("GAME_OVER")
            return
        self.reset_ball()
        if not self.ip.state.is_("DEMO"):
            self.ip.state.go("READY")

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

    def draw_state_message(self, ip, msg):
        rect = ip.rect_pane
        if not rect:
            return
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        ip.surface.blit(overlay, (rect.left, rect.top))
        font      = Style.FONT_BANNER or pygame.font.SysFont("monospace", 48)
        color     = Style.COLOR_PAL_ORANGE_BRIGHT
        text_surf = font.render(msg, True, color)
        x         = rect.centerx - text_surf.get_width()  // 2
        y         = rect.centery - text_surf.get_height() // 2
        ip.surface.blit(text_surf, (x, y))

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

    def game_hud(self, parent):
        """Score and lives as real IPUI widgets floating over the game."""
        row = Row(parent)
        Title(row, "Score: 0", name="lbl_score", glow=True)
        Spacer(row)
        Body(row, "Lives: 3", name="lbl_lives")

    def code(self, parent):
        Title(parent, "The Source", glow=True)
        Body(parent, "This pane reads its own file.")
        card = Card(parent, scrollable=True, height_flex=99)
        CodeBox(card,
            data  = __file__,)