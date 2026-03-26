# PygameBall2.py  Update: ball bounces in None gap via ip_renderpre

import pygame
from ipui import *


class PygameBall(_basePane):
    """Live demo of IPUI lifecycle hooks: ip_think, ip_renderpre, ip_renderpost."""

    IP_LIFECYCLE = "persist"       # Ball keeps bouncing even when tab is hidden

    def ip_setup_pane(self):
        self.ball_x     = 200.0
        self.ball_y     = 200.0
        self.ball_dx    = 220.0
        self.ball_dy    = 170.0
        self.ball_r     = 12
        self.trail      = []
        self.speed      = 1.0

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def overview(self, parent):
        """Left pane — explanation and speed controls."""
        Title(parent, "Pygame + IPUI", glow=True)
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
        Heading(card, "The ip Object:", glow=True)
        Body(card, "ip.dt        Seconds since last frame")
        Body(card, "ip.fps       Current FPS")
        Body(card, "ip.surface   The draw surface")
        Body(card, "ip.events    All pygame events")
        Body(card, "ip.unhandled Events UI didn't consume")
        Body(card, "ip.frame     Frame counter")

        card = Card(parent)
        Heading(card, "Speed:", glow=True)
        row = Row(card)
        Button(row, "Slower",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.go_slower)
        Body(row, "1.0x", name="lbl_speed", text_align='c', width_flex=True)
        Button(row, "Faster",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.go_faster)

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
    # SPEED CONTROLS
    # ══════════════════════════════════════════════════════════════

    def go_faster(self):
        self.speed = min(5.0, self.speed + 0.5)
        self.update_speed_label()

    def go_slower(self):
        self.speed = max(0.0, self.speed - 0.5)
        self.update_speed_label()

    def update_speed_label(self):
        lbl = self.form.widgets.get("lbl_speed")
        if lbl:
            lbl.set_text(f"{self.speed:.1f}x")

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS — this is what makes the ball bounce
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ip):
        """Physics: move ball, bounce off arena walls."""
        dt = ip.dt * self.speed
        if dt <= 0:
            return
        self.ball_x += self.ball_dx * dt
        self.ball_y += self.ball_dy * dt
        arena = ip.rect_pane
        if arena:
            self.bounce_off_walls(arena)
        self.update_trail()

    def ip_renderpre(self, ip):
        """Draw trail and ball into the None gap, BEFORE UI renders."""
        arena = ip.rect_pane
        if not arena:
            return
        self.draw_trail(ip.surface, arena)
        self.draw_ball(ip.surface, arena)

    def ip_renderpost(self, ip):
        """Draw FPS overlay AFTER UI renders."""
        arena = ip.rect_pane
        if not arena:
            return
        font = Style.FONT_DETAIL
        text = f"FPS: {ip.fps}  Frame: {ip.frame}"
        surf = font.render(text, True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (arena.left + 8, arena.top + 4))

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS — (CodeBox reads up to here)
    # ══════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════
    # ARENA — the None gap between overview and code panes
    # ══════════════════════════════════════════════════════════════

    def compute_arenaDleteme(self, ip):
        """Find the transparent gap where the ball bounces.
        The None slot in TAB_LAYOUT leaves an empty Col between
        the two TabAreas. Its rect IS the arena."""
        tab_strip = getattr(ip.form, 'tab_strip', None)
        if not tab_strip:
            return None
        content = tab_strip.content
        if not content or not content.rect:
            return None
        for child in content.children:
            if child.rect and not child.children:
                return child.rect
        return None

    # ══════════════════════════════════════════════════════════════
    # BALL HELPERS
    # ══════════════════════════════════════════════════════════════

    def bounce_off_walls(self, arena):
        br = self.ball_r
        w  = arena.width
        h  = arena.height
        if self.ball_x - br < 0 or self.ball_x + br > w:
            self.ball_dx = -self.ball_dx
            self.ball_x  = max(br, min(self.ball_x, w - br))
        if self.ball_y - br < 0 or self.ball_y + br > h:
            self.ball_dy = -self.ball_dy
            self.ball_y  = max(br, min(self.ball_y, h - br))

    def update_trail(self):
        self.trail.append((self.ball_x, self.ball_y))
        if len(self.trail) > 30:
            self.trail.pop(0)

    def draw_trail(self, surface, arena):
        for i, (tx, ty) in enumerate(self.trail):
            alpha      = (i + 1) / len(self.trail) if self.trail else 1
            radius     = max(2, int(self.ball_r * alpha * 0.6))
            brightness = int(80 * alpha)
            color      = (brightness, int(brightness * 0.6), 0)
            sx         = arena.left + int(tx)
            sy         = arena.top  + int(ty)
            if arena.collidepoint(sx, sy):
                pygame.draw.circle(surface, color, (sx, sy), radius)

    def draw_ball(self, surface, arena):
        sx = arena.left + int(self.ball_x)
        sy = arena.top  + int(self.ball_y)
        pygame.draw.circle(surface, Style.COLOR_PAL_ORANGE_BRIGHT, (sx, sy), self.ball_r)
        pygame.draw.circle(surface, Style.COLOR_TEXT_ACCENT, (sx, sy), self.ball_r, 2)