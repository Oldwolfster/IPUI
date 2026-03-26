# StateMachine.py  New: Universal state machine for IPUI

import pygame
from ipui.Style import Style


class StateMachine:
    """Declarative state machine accessible via ip.state.

    Zero-config usage:
        ip.state.set("LOADING")
        ip.state.current            # "LOADING"

    Pre-configured usage:
        ip.state.configure({
            "DEMO"     : {"next": "READY"},
            "READY"    : {"next": "PLAYING", "message": "Click!"},
            "LEVEL_UP" : {"next": "READY",   "duration": 1.5, "message": "LEVEL UP!"},
        })
        ip.state.set("LEVEL_UP")    # shows message, auto-transitions after 1.5s
        ip.state.next()             # follows the "next" chain

    Named state machines:
        ip.state("combat").set("ATTACKING")
    """

    def __init__(self):
        self.current         = None
        self.private_config  = {}
        self.private_timer   = 0.0
        self.private_named   = {}

    # ══════════════════════════════════════════════════════════════
    # CALLABLE — ip.state / ip.state() / ip.state("name")
    # ══════════════════════════════════════════════════════════════

    def __call__(self, name=None):
        if name is None:
            return self
        if name not in self.private_named:
            self.private_named[name] = StateMachine()
        return self.private_named[name]

    # ══════════════════════════════════════════════════════════════
    # CONFIGURATION
    # ══════════════════════════════════════════════════════════════

    def configure(self, states_dict):
        self.private_config = dict(states_dict)
        if self.current is None and states_dict:
            first = next(iter(states_dict))
            self.current = first

    # ══════════════════════════════════════════════════════════════
    # TRANSITIONS
    # ══════════════════════════════════════════════════════════════

    def set(self, name):
        self.current       = name
        entry              = self.private_config.get(name, {})
        self.private_timer = entry.get("duration", 0.0)

    def next(self):
        entry    = self.private_config.get(self.current, {})
        next_key = entry.get("next")
        if next_key:
            self.set(next_key)

    # ══════════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════════

    @property
    def message(self):
        entry = self.private_config.get(self.current, {})
        return entry.get("message")

    @property
    def duration(self):
        entry = self.private_config.get(self.current, {})
        return entry.get("duration", 0.0)

    @property
    def is_flash(self):
        return self.duration > 0

    @property
    def timer(self):
        return self.private_timer

    def is_(self, name):
        return self.current == name

    def in_(self, *names):
        return self.current in names

    # ══════════════════════════════════════════════════════════════
    # TICK — called by engine each frame
    # ══════════════════════════════════════════════════════════════

    def tick(self, dt):
        self.tick_self(dt)
        for sm in self.private_named.values():
            sm.tick_self(dt)

    def tick_self(self, dt):
        if self.private_timer <= 0:
            return
        self.private_timer -= dt
        if self.private_timer <= 0:
            self.private_timer = 0
            self.next()

    # ══════════════════════════════════════════════════════════════
    # FLASH DRAWING — called by engine in renderpost
    # ══════════════════════════════════════════════════════════════

    def draw_flash(self, ip):
        self.draw_flash_self(ip)
        for sm in self.private_named.values():
            sm.draw_flash_self(ip)

    def draw_flash_self(self, ip):
        msg = self.message
        if not msg:
            return
        if self.private_timer <= 0 and self.duration > 0:
            return
        rect = ip.rect_pane
        if not rect:
            return
        self.draw_overlay(ip.surface, rect)
        self.draw_message(ip.surface, rect, msg)

    def draw_overlay(self, surface, rect):
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (rect.left, rect.top))

    def draw_message(self, surface, rect, msg):
        font      = Style.FONT_BANNER or pygame.font.SysFont("monospace", 48)
        color     = Style.COLOR_PAL_ORANGE_BRIGHT
        text_surf = font.render(msg, True, color)
        x         = rect.centerx - text_surf.get_width()  // 2
        y         = rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (x, y))