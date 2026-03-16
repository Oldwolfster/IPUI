# PygameBall.py  Update: ip service portal replaces ctx

import pygame
from ipui.Style import Style
from ipui.engine._BasePane import _basePane
from ipui.widgets.Row import Row, CardCol, Col
from ipui.widgets.Label import Title, Body, Detail, Heading
from ipui.widgets.CodeBox import CodeBox
from ipui.widgets.Card import Card


class PygameBall(_basePane):
    """Live demo of IPUI lifecycle hooks: ip_think, ip_renderpre, ip_renderpost."""

    IP_LIFECYCLE = "persist"       # Ball keeps bouncing even when tab is hidden

    def initialize(self):
        self.ball_x     = 200.0
        self.ball_y     = 200.0
        self.ball_dx    = 220.0
        self.ball_dy    = 170.0
        self.ball_r     = 12
        self.trail      = []
        self.arena_rect = None

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS — the three columns
    # ══════════════════════════════════════════════════════════════

    def overview(self, parent):
        """Left pane — explanation."""
        Title(parent, "Pygame Lifecycle Hooks", glow=True)
        Body(parent, "IPUI takes over the pygame loop so you "
                      "don't have to. But you still get full access.")

        card = Card(parent)
        Heading(card, "Three Hooks:", glow=True)
        Body(card, "ip_think(ip)\n"
                   "  Every frame. State, physics, logic.\n"
                   "  The ball's position updates here.")
        Body(card, "ip_renderpre(ip)\n"
                   "  Before UI draws. Backgrounds, game world.\n"
                   "  The ball and trail draw here.")
        Body(card, "ip_renderpost(ip)\n"
                   "  After UI draws. Overlays, cursors.\n"
                   "  The FPS counter draws here.")

        card = Card(parent)
        Heading(card, "The ip Service Portal:", glow=True)
        Body(card, "ip.dt        Seconds since last frame")
        Body(card, "ip.fps       Current FPS")
        Body(card, "ip.surface   The draw surface")
        Body(card, "ip.mouse_pos Mouse position")
        Body(card, "ip.key_pressed('space')  Just pressed?")
        Body(card, "ip.help()    Print the full guide")

    def ball(self, parent):
        """Middle pane — the ball bounces here."""
        self.arena_widget = parent
        Title(parent, "The Arena", glow=True)
        Detail(parent, "Ball bounces in ip_renderpre. Physics in ip_think.",
               name="lbl_ball_info")

    def code(self, parent):
        """Right pane — source code."""
        Title(parent, "The Source", glow=True)
        Body(parent, "This pane reads its own file. What you see is what runs.")
        card = Card(parent, scrollable=True, height_flex=99)
        CodeBox(card,
            data  = __file__,
            start = "# ══ LIFECYCLE",
            end   = "# ══ PANE BUILDERS",)

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS — this is what makes the ball bounce
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ip):
        """Physics: move ball, bounce off arena walls."""
        if ip.dt <= 0:
            return
        self.ball_x += self.ball_dx * ip.dt
        self.ball_y += self.ball_dy * ip.dt
        self.bounce_off_walls()
        self.update_trail()

    def ip_renderpost(self, ip):
        """Draw trail and ball into the arena pane, BEFORE UI renders."""
        arena = getattr(self, 'arena_widget', None)
        if not arena or not arena.rect:
            return
        self.draw_trail(ip.surface, arena.rect)
        self.draw_ball(ip.surface, arena.rect)
        self.ip_renderpost2(ip)

    def ip_renderpost2(self, ip):
        """Draw FPS overlay AFTER UI renders."""
        arena = getattr(self, 'arena_widget', None)
        if not arena or not arena.rect:
            return
        r    = arena.rect
        font = Style.FONT_DETAIL
        text = f"FPS: {ip.fps}  Frame: {ip.frame}"
        surf = font.render(text, True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (r.left + 8, r.bottom - surf.get_height() - 4))

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS — (CodeBox reads up to here)
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════
    # BALL HELPERS
    # ══════════════════════════════════════════════════════════════

    def bounce_off_walls(self):
        arena = getattr(self, 'arena_widget', None)
        if not arena or not arena.rect:
            return
        r  = arena.rect
        br = self.ball_r
        if self.ball_x - br < 0 or self.ball_x + br > r.width:
            self.ball_dx = -self.ball_dx
            self.ball_x  = max(br, min(self.ball_x, r.width - br))
        if self.ball_y - br < 0 or self.ball_y + br > r.height:
            self.ball_dy = -self.ball_dy
            self.ball_y  = max(br, min(self.ball_y, r.height - br))

    def update_trail(self):
        self.trail.append((self.ball_x, self.ball_y))
        if len(self.trail) > 30:
            self.trail.pop(0)

    def draw_trail(self, surface, r):
        for i, (tx, ty) in enumerate(self.trail):
            alpha   = (i + 1) / len(self.trail) if self.trail else 1
            radius  = max(2, int(self.ball_r * alpha * 0.6))
            brightness = int(80 * alpha)
            color   = (brightness, int(brightness * 0.6), 0)
            sx      = r.left + int(tx)
            sy      = r.top  + int(ty)
            if r.collidepoint(sx, sy):
                pygame.draw.circle(surface, color, (sx, sy), radius)

    def draw_ball(self, surface, r):
        sx = r.left + int(self.ball_x)
        sy = r.top  + int(self.ball_y)
        pygame.draw.circle(surface, Style.COLOR_PAL_ORANGE_BRIGHT, (sx, sy), self.ball_r)
        pygame.draw.circle(surface, Style.COLOR_TEXT_ACCENT, (sx, sy), self.ball_r, 2)
