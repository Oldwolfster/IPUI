import pygame
from ipui import *

class PygameBall(_BaseTab):
    """Live demo of IPUI lifecycle hooks: ip_think, ip_draw, ip_draw_hud."""
    def ip_setup(self, ip):
        THINK_ALWAYS    = True
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
        Body(parent, "IPUI gives you pygame on a platter.")
        card = Card(parent)
        Heading(card, "Three Main Hooks:", glow=True)
        Body(card, "ip_think(ip)\n"
                   "  Every frame. State, physics, logic.\n"
                   "  The ball's position updates here.")
        Body(card, "ip_draw(ip)\n"
                   "  Before UI draws. Backgrounds, game world.\n"
                   "  The ball and trail draw here.")
        Body(card, "ip_draw_hud(ip)\n"
                   "  After UI draws. Overlays, cursors.\n"
                   "  The FPS counter draws here.")

        # Pygame.py  method: (replace existing "ip Service Portal" card)  Update: brag-worthy ip card showing all 8 families + ip.help() hook
        card = Card(parent)
        Heading(card, "The ip Service Portal", glow=True)
        Body(card, "One object. Everything you need. No hunting.")
        Body(card, "  Identity   form, tab, is_active_tab")
        Body(card, "  Timing     dt, fps, frame, elapsed")
        Body(card, "  Geometry   rect_pane, to_screen, to_local")
        Body(card, "  Mouse      mouse_pos, mouse_pressed, mouse_inside")
        Body(card, "  Keyboard   key_pressed, mod_shift, mod_ctrl")
        Body(card, "  State      ip.state.add / go / debug")
        Body(card, "  Rendering  surface, events, unhandled")
        Body(card, "  Cache      cache_get, cache_set — frame-to-frame scratch")
        Body(card, "  Type ip. — your IDE shows the rest.")




    def code(self, parent):
        """Right pane — source code."""
        card = Col(parent)
        Title(card, "Speed", glow=True,text_align=CENTER)
        row = Row(card)
        Button(row, "Slower",               on_click=self.go_slower)
        Body(row, "1.0x", name="lbl_speed", text_align='c', width_flex=1)
        Button(row, "Faster", on_click=self.go_faster)

        Body(parent,"")     #small spacer
        card = Card(parent,height_flex=1,pad=0)
        Title(card, "The Source", glow=True,text_align=CENTER)
        card = Card(card, scroll_v=True, scroll_h=True, height_flex=99)
        CodeBox(card,    data  = __file__, height_flex=1)

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


    def ip_draw(self, ip):
        """Draw trail and ball into the None gap, BEFORE UI renders."""
        arena = ip.rect_pane
        if not arena:
            return
        self.draw_trail(ip.surface, arena)
        self.draw_ball(ip.surface, arena)

    def ip_draw_hud(self, ip):
        self.text_without_ipui(ip)

    def text_without_ipui(self,ip):
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
        pygame.draw.circle(surface, Style.COLOR_BUTTON_ACCENT, (sx, sy), self.ball_r)
        pygame.draw.circle(surface, Style.COLOR_TEXT_ACCENT, (sx, sy), self.ball_r, 2)