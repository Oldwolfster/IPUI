# CopyButton.py  NEW FILE  Reusable overlay copy button. Mounted via _BaseWidget.setup_overlay_button.
#
# Floats top-right of its parent. Excluded from layout (do_not_allocate=True),
# included in input dispatch (is_overlay=True). Drawn by parent's default draw_overlay
# walking overlay children. Owns its own flash timer.

import time
import pygame

from ipui.engine._BaseWidget   import _BaseWidget
from ipui.utils.MgrClipboard   import MgrClipboard
from ipui.Style                import Style


class CopyButton(_BaseWidget):
    """
    desc:        Floating "Copy" button anchored top-right of its parent.
    when_to_use: Don't construct directly — call parent.setup_overlay_button(label, payload_fn).
    best_for:    Any widget exposing copyable text content.
    example:     self.setup_overlay_button("Copy", lambda: self.text)   # in build()
    api:         label (str), payload_fn (callable returning str)
    """

    def build(self):
        self.do_not_allocate    = True
        self.is_overlay         = True
        self.hover_bright       = False
        self.private_label      = self.data or "Copy"           # label passed via data kwarg
        self.private_payload_fn = self.on_change                # payload_fn passed via on_change kwarg
        self.private_flash_at   = 0
        self.private_label_surf = Style.FONT_DETAIL.render(self.private_label, True, Style.COLOR_TEXT)
        self.private_done_surf  = Style.FONT_DETAIL.render("Copied!",          True, (100, 220, 100))
        self.on_click           = self.handle_click
        self.on_change          = None                          # clear — was carrying payload_fn
        self.rect               = pygame.Rect(0, 0, 0, 0)       # placeholder; anchored each draw

    def is_flashing(self):
        return time.time() - self.private_flash_at < 1.0

    def current_label_surf(self):
        return self.private_done_surf if self.is_flashing() else self.private_label_surf

    def anchor_top_right(self):
        if self.parent is None or self.parent.rect is None: return
        label = self.current_label_surf()
        pad   = 4
        bw    = label.get_width()  + pad * 2
        bh    = label.get_height() + pad * 2
        bx    = self.parent.rect.right - bw - 6
        by    = self.parent.rect.top  + 6
        self.rect = pygame.Rect(bx, by, bw, bh)

    def draw(self, surface):
        self.anchor_top_right()
        if self.rect.width == 0: return
        label    = self.current_label_surf()
        bg       = (100, 220, 100, 180) if self.is_flashing() else (60, 60, 60, 180)
        btn_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        btn_surf.fill(bg)
        btn_surf.blit(label, (4, 4))
        surface.blit(btn_surf, self.rect.topleft)

    def handle_click(self):
        if self.private_payload_fn is None: return
        payload = self.private_payload_fn()
        if payload is None: return
        MgrClipboard.copy(str(payload))
        self.private_flash_at = time.time()