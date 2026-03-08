# CodeBox.py  NEW: Read-only monospace code display with introspection

import inspect
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
        self.font       = Style.FONT_MONO
        self.color_txt  = Style.COLOR_TEXT
        self.color_bg   = self.color_bg or Style.COLOR_PAL_GRAY_950
        self.pad        = Style.TOKEN_PAD
        self.border     = Style.TOKEN_BORDER
        self.gap        = 0
        #self.scrollable = True

        if not self.data:
            self.my_surface = self.font.render("# no method set", True, self.color_txt)
            return

        lines              = self.extract_lines()
        print(f"DEBUG CodeBox: {len(lines)} lines")                    # NEW
        if lines: print(f"  FIRST: {lines[0]}")                        # NEW
        if lines: print(f"  LAST:  {lines[-1]}")

        self.my_surface    = self.render_code(lines)
        self.scroll_offset = self.find_scroll(lines)


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

        return lines


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