# _BaseHugeTooltip.py  Update: Pin mechanic with docked display

import time
import pygame

from ipui.Style import Style


class _BaseHugeTooltip:

    PIN_DELAY      = 1.5
    PIN_BTN_W      = 100
    PIN_BTN_H      = 48
    PIN_BTN_X      = 24
    PIN_BTN_Y      = -24
    DOCK_WIDTH_PCT = 0.45
    CLOSE_BTN_W    = 50
    CLOSE_BTN_H    = 24
    MOVE_BTN_W     = 60
    MOVE_BTN_H     = 24
    MOVE_BTN_W     = 40
    MOVE_BTN_H     = 24

    def __init__(self):
        self.font_header  = Style.FONT_TITLE
        self.font_body    = Style.FONT_BODY
        self.font_small   = Style.FONT_DETAIL
        self.padding      = Style.TOKEN_PAD
        self.row_height   = Style.FONT_BODY.get_height() + 4
        self.bg_color     = Style.COLOR_CARD_BG
        self.border_color = Style.COLOR_BORDER
        self.text_color   = Style.COLOR_TEXT
        self.pinned        = False
        self.dock_right    = True
        self.pin_scroll    = 0
        self.appear_time   = 0
        self.pin_btn_rect  = None
        self.close_btn_rect = None
        self.move_btn_rect  = None
        self.content_rect   = None

    # ══════════════════════════════════════════════════════════════
    # SUBCLASS INTERFACE
    # ══════════════════════════════════════════════════════════════

    def header_text(self) -> str:
        raise NotImplementedError

    def content_to_display(self) -> list[list[str]]:
        raise NotImplementedError

    def pin_buttons(self) -> list[str]:
        """Override to add buttons like Copy, Fork. Close is always added."""
        return []

    # ══════════════════════════════════════════════════════════════
    # COLUMN MEASUREMENT
    # ══════════════════════════════════════════════════════════════

    def calc_col_widths(self, columns):
        widths = []
        for col in columns:
            max_w = 0
            for cell in col:
                w = self.font_body.render(str(cell), True, self.text_color).get_width()
                max_w = max(max_w, w)
            widths.append(max_w + self.padding * 2)
        return widths

    def calc_content_height(self, columns):
        rows = len(columns[0]) if columns else 0
        return rows * self.row_height

    # ══════════════════════════════════════════════════════════════
    # FLOATING (unpinned) DISPLAY
    # ══════════════════════════════════════════════════════════════

    def draw(self) -> pygame.Surface:
        columns    = self.content_to_display()
        col_widths = self.calc_col_widths(columns)
        width      = sum(col_widths) + self.padding * 2
        rows       = len(columns[0]) if columns else 0
        header_h   = self.font_header.get_height() + self.padding
        height     = header_h + rows * self.row_height + self.padding
        surf       = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill(self.bg_color)
        pygame.draw.rect(surf, self.border_color, (0, 0, width, height), 2)
        header_surf = self.font_header.render(self.header_text(), True, self.text_color)
        surf.blit(header_surf, (self.padding, self.padding))
        x = self.padding
        for ci, col in enumerate(columns):
            for ri, txt in enumerate(col):
                label = self.font_body.render(str(txt), True, self.text_color)
                y     = header_h + ri * self.row_height
                surf.blit(label, (x + self.padding, y))
            x += col_widths[ci]
        return surf

    def show_me(self, surface):
        if self.appear_time == 0:
            self.appear_time = time.time()
        tooltip_surf       = self.draw()
        mouse_x, mouse_y   = pygame.mouse.get_pos()
        screen_w            = surface.get_width()
        screen_h            = surface.get_height()
        if mouse_x < screen_w // 2:
            x = mouse_x + 15
        else:
            x = mouse_x - tooltip_surf.get_width() - 15
        x = max(10, min(x, screen_w - tooltip_surf.get_width() - 10))
        y = max(10, min(mouse_y + 15, screen_h - tooltip_surf.get_height() - 10))
        surface.blit(tooltip_surf, (x, y))
        self.draw_pin_button(surface, mouse_x + self.PIN_BTN_X, mouse_y + self.PIN_BTN_Y)

    def draw_pin_button(self, surface, mouse_x, mouse_y):
        elapsed = time.time() - self.appear_time
        if elapsed < self.PIN_DELAY:
            self.pin_btn_rect = None
            return
        bw = self.PIN_BTN_W
        bh = self.PIN_BTN_H
        bx = mouse_x - bw // 2
        by = mouse_y + 18
        screen_w = surface.get_width()
        screen_h = surface.get_height()
        bx = max(4, min(bx, screen_w - bw - 4))
        by = max(4, min(by, screen_h - bh - 4))
        self.pin_btn_rect = pygame.Rect(bx, by, bw, bh)
        alpha = min(1.0, (elapsed - self.PIN_DELAY) / 0.3)
        btn_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        btn_color = (*Style.COLOR_PAL_GREEN_DARK[:3], int(230 * alpha))
        txt_color = (*self.text_color[:3], int(255 * alpha)) if len(self.text_color) >= 3 else self.text_color
        pygame.draw.rect(btn_surf, btn_color, (0, 0, bw, bh), border_radius=4)
        label = self.font_small.render("Pin", True, txt_color)
        lx = (bw - label.get_width()) // 2
        ly = (bh - label.get_height()) // 2
        btn_surf.blit(label, (lx, ly))
        surface.blit(btn_surf, (bx, by))

    # ══════════════════════════════════════════════════════════════
    # PINNED (docked) DISPLAY
    # ══════════════════════════════════════════════════════════════
    def content_with_footer(self):
        columns = self.content_to_display()
        if columns:
            columns[0].append("")
            columns[0].append("── NeuroForge ── neuroforge.io ──")
        return columns

    def draw_docked(self, surface):
        screen_w = surface.get_width()
        screen_h = surface.get_height()
        dock_w = min(self.pin_w + self.padding * 4, screen_w - 20) #  calc
        dock_h = min(self.pin_h + self.padding * 4, screen_h - 20)
        if self.dock_right:
            dock_x = screen_w - dock_w - 10
        else:
            dock_x = 10
        dock_y = 10
        dock_rect = pygame.Rect(dock_x, dock_y, dock_w, dock_h)
        pygame.draw.rect(surface, self.bg_color, dock_rect)
        pygame.draw.rect(surface, self.border_color, dock_rect, 2)
        self.draw_docked_header(surface, dock_rect)
        self.draw_docked_content(surface, dock_rect)

    def draw_docked_header(self, surface, dock_rect):
        pad      = self.padding
        header_h = self.font_header.get_height() + pad * 2
        header_surf = self.font_header.render(self.header_text(), True, self.text_color)
        surface.blit(header_surf, (dock_rect.left + pad, dock_rect.top + pad))
        bx = dock_rect.right - pad - self.CLOSE_BTN_W
        by = dock_rect.top + pad
        self.close_btn_rect = pygame.Rect(bx, by, self.CLOSE_BTN_W, self.CLOSE_BTN_H)
        pygame.draw.rect(surface, Style.COLOR_PAL_RED_DARK, self.close_btn_rect, border_radius=3)
        label = self.font_small.render("Close", True, self.text_color)
        surface.blit(label, (
            bx + (self.CLOSE_BTN_W - label.get_width()) // 2,
            by + (self.CLOSE_BTN_H - label.get_height()) // 2,
        ))
        mx = bx - self.MOVE_BTN_W - pad
        my = by
        self.move_btn_rect = pygame.Rect(mx, my, self.MOVE_BTN_W, self.MOVE_BTN_H)
        arrow = "<< Move" if self.dock_right else "Move >>"
        pygame.draw.rect(surface, Style.COLOR_TAB_BG, self.move_btn_rect, border_radius=3)
        arrow_surf = self.font_small.render(arrow, True, self.text_color)
        surface.blit(arrow_surf, (
            mx + (self.MOVE_BTN_W - arrow_surf.get_width()) // 2,
            my + (self.MOVE_BTN_H - arrow_surf.get_height()) // 2,
        ))

    def draw_docked_content(self, surface, dock_rect):
        pad      = self.padding
        header_h = self.font_header.get_height() + pad * 2
        content_top = dock_rect.top + header_h + pad
        content_h   = dock_rect.height - header_h - pad * 2
        content_w   = dock_rect.width - pad * 2
        self.content_rect = pygame.Rect(dock_rect.left + pad, content_top, content_w, content_h)
        columns    = self.content_with_footer()
        col_widths = self.calc_col_widths(columns)
        total_h    = self.calc_content_height(columns)
        max_scroll = max(0, total_h - content_h)
        self.pin_scroll = max(0, min(self.pin_scroll, max_scroll))
        old_clip = surface.get_clip()
        surface.set_clip(self.content_rect)
        x = self.content_rect.left
        for ci, col in enumerate(columns):
            for ri, txt in enumerate(col):
                label = self.font_body.render(str(txt), True, self.text_color)
                y     = content_top + ri * self.row_height - self.pin_scroll
                surface.blit(label, (x + pad, y))
            x += col_widths[ci]
        surface.set_clip(old_clip)
        if max_scroll > 0:
            self.draw_dock_scrollbar(surface, content_top, content_h, total_h, dock_rect)

    def draw_dock_scrollbar(self, surface, content_top, content_h, total_h, dock_rect):
        bar_w        = 8
        bar_x        = dock_rect.right - bar_w - 4
        track_rect   = pygame.Rect(bar_x, content_top, bar_w, content_h)
        pygame.draw.rect(surface, Style.COLOR_PANEL_BG, track_rect)
        visible_ratio = content_h / total_h
        handle_h      = max(20, int(content_h * visible_ratio))
        max_scroll    = max(1, total_h - content_h)
        scroll_ratio  = self.pin_scroll / max_scroll
        handle_y      = content_top + int((content_h - handle_h) * scroll_ratio)
        handle_rect   = pygame.Rect(bar_x, handle_y, bar_w, handle_h)
        pygame.draw.rect(surface, Style.COLOR_BUTTON_BG, handle_rect)

    # ══════════════════════════════════════════════════════════════
    # HIT TESTING
    # ══════════════════════════════════════════════════════════════

    def hit_test_pin(self, pos):
        if self.pin_btn_rect and self.pin_btn_rect.collidepoint(pos):
            return True
        return False

    def hit_test_close(self, pos):
        if self.close_btn_rect and self.close_btn_rect.collidepoint(pos):
            return True
        return False

    def hit_test_move(self, pos):
        if self.move_btn_rect and self.move_btn_rect.collidepoint(pos):
            return True
        return False

    def hit_test_docked(self, pos):
        """Is the click anywhere on the docked panel?"""
        if not self.content_rect:
            return False
        dock_rect = self.content_rect.inflate(
            self.padding * 4, self.padding * 4)
        return dock_rect.collidepoint(pos)

    # ══════════════════════════════════════════════════════════════
    # PIN ACTIONS
    # ══════════════════════════════════════════════════════════════

    def pin(self):                              # NEW
        self.pinned     = True                  # NEW
        self.pin_scroll = 0                     # NEW
        surf            = self.draw()                      # NEW
        self.pin_w      = surf.get_width()           # NEW
        self.pin_h      = surf.get_height()          # NEW

    def unpin(self):
        self.pinned        = False
        self.pin_scroll    = 0
        self.appear_time   = 0
        self.pin_btn_rect  = None
        self.close_btn_rect = None
        self.move_btn_rect  = None
        self.content_rect   = None

    def toggle_dock_side(self):
        self.dock_right = not self.dock_right

    def handle_pin_scroll(self, button):
        columns   = self.content_to_display()
        total_h   = self.calc_content_height(columns)
        if not self.content_rect:
            return
        content_h  = self.content_rect.height
        max_scroll = max(0, total_h - content_h)
        direction  = -1 if button == 4 else 1
        self.pin_scroll += direction * self.row_height
        self.pin_scroll  = max(0, min(self.pin_scroll, max_scroll))