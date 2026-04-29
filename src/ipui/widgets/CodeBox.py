# CodeBox.py  Update: auto-dedent + copy button

import inspect
import time
import pygame
from ipui.Style import Style
from ipui.engine._BaseWidget import _BaseWidget


class CodeBox(_BaseWidget):
    """
    desc:        Read-only monospace code display via introspection.
    when_to_use: Show actual running source code in the UI.
    best_for:    Showcases, tutorials, paradigm comparisons.
    example:     CodeBox(parent, data=self.my_method, start="x = 1", end="return")
    api:         (read-only for now)
    """

    def build(self):
        self.font                   = Style.FONT_MONO
        self.color_txt              = Style.COLOR_TEXT
        self.color_bg               = self.color_bg or Style.COLOR_CODE_BG
        self.on_click               = self.handle_copy_click
        self.hover_bright           = False
        self.private_copy_rect      = None
        self.private_copy_flash     = 0
        self.private_copy_surf      = Style.FONT_DETAIL.render("Copy",    True, Style.COLOR_TEXT)
        self.private_copied_surf    = Style.FONT_DETAIL.render("Copied!", True, (100, 220, 100))
        if self.parent:
            self.parent.pad         = 0
            self.parent.gap         = 0

        if not self.data:
            self.my_surface         = self.font.render("# no method set", True, self.color_txt)
            return

        lines                       = self.extract_lines()
        self.my_surface             = self.render_code(lines)
        self.scroll_offset          = self.find_scroll(lines)



    def set_text(self, text):
        self.data = text
        self.clear_children()
        self.build()

    def extract_lines(self):
        import inspect
        if isinstance(self.data, str):
            if '\n' in self.data:                                # NEW
                lines = self.data.splitlines()                   # NEW
            else:
                with open(self.data, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
        else:
            lines = inspect.getsource(self.data).splitlines()

        if self.start:
            for i, line in enumerate(lines):
                if self.start in line:
                    lines = lines[i:]
                    break

        if self.end:
            for i, line in enumerate(lines):
                if self.end in line and 'end=' not in line:
                    lines = lines[:i]
                    break

        return self.dedent(lines)

    def dedent(self, lines):
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if not indents:
            return lines
        trim = min(indents)
        if trim == 0:
            return lines
        return [line[trim:] if line.strip() else line for line in lines]

    def find_scroll(self, lines):
        if not self.initial_value:
            return 0
        line_h = self.font.get_height()
        for i, line in enumerate(lines):
            if self.initial_value in line:
                return i * line_h
        return 0

    def render_code(self, lines):
        line_h  = self.font.get_height()
        surfs   = [self.font.render(ln, True, self.color_txt) for ln in lines]
        width   = max((s.get_width() for s in surfs), default=0)
        height  = line_h * len(lines)

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for i, surf in enumerate(surfs):
            surface.blit(surf, (0, i * line_h))

        return surface

    def draw(self, surface):
        super().draw(surface)
        self.draw_copy_button(surface)

    def draw_copy_button(self, surface):
        if self.rect is None or not self.data:
            return
        flashing = time.time() - self.private_copy_flash < 1.0
        label    = self.private_copied_surf if flashing else self.private_copy_surf
        pad      = 4
        bw       = label.get_width()  + pad * 2
        bh       = label.get_height() + pad * 2
        bx       = self.rect.right - bw - 6
        by       = self.rect.top + 6
        btn_rect = pygame.Rect(bx, by, bw, bh)
        self.private_copy_rect = btn_rect
        bg       = (100, 220, 100, 180) if flashing else (60, 60, 60, 180)
        btn_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        btn_surf.fill(bg)
        btn_surf.blit(label, (pad, pad))
        surface.blit(btn_surf, (bx, by))

    def handle_copy_click(self):
        pos = pygame.mouse.get_pos()
        if self.private_copy_rect and self.private_copy_rect.collidepoint(pos):
            from ipui.utils.MgrClipboard import MgrClipboard
            lines = self.dedent(self.extract_lines())
            MgrClipboard.copy("\n".join(lines))
            self.private_copy_flash = time.time()