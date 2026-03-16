# TextArea.py  NEW: Multi-line text editor. TextBox that wraps and scrolls.
#
# Inherits from TextBox: cursor, selection, clipboard, key handling, chrome.
# Adds:                  Multi-line editing, vertical cursor navigation,
#                         line-aware Home/End, Enter inserts newline.

import pygame

from ipui.utils import MgrClipboard
from ipui.widgets.TextBox import TextBox
from ipui.Style import Style


class TextArea(TextBox):
    """
    desc:        Multi-line text editor built on TextBox. Wraps, scrolls, full editing.
    when_to_use: SQL queries, notes, code input, any multi-line text.
    best_for:    The SQL tab query box, config editors, comment fields.
    example:     TextArea(parent, placeholder="Enter SQL...", height_flex=True)
    api:         set_text(text), set_focus(), sync_from_pipeline()
    """

    # ══════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════

# TextArea.py method: build  Update: Set line_height before super
    def build(self):
        self.font          = self.font or Style.FONT_BODY
        self.line_height   = self.font.get_height()
        self.display_lines = [""]
        super().build()
        self.wrap          = True
        self.text_align    = 'l'
        self.display_lines = self.text.split("\n") if self.text else [""]

    # ══════════════════════════════════════════════════════════════
    # SURFACE — rebuild for multi-line
    # ══════════════════════════════════════════════════════════════

    def rebuild_surface(self):
        display = self.text if self.text else self.placeholder
        color   = self.color_txt if self.text else self.color_placeholder
        lines   = display.split("\n")
        self.display_lines = lines if self.text else lines
        surfs   = [self.font.render(line or " ", True, color) for line in lines]
        w       = max(s.get_width() for s in surfs) if surfs else 1
        h       = self.line_height * len(lines)
        self.my_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        y = 0
        for s in surfs:
            self.my_surface.blit(s, (0, y))
            y += self.line_height

    # ══════════════════════════════════════════════════════════════
    # MEASURE — taller than TextBox
    # ══════════════════════════════════════════════════════════════

    def measure(self):
        line_count = max(1, self.text.count("\n") + 1) if self.text else 3
        h = self.line_height * line_count + self.pad * 2
        w = 200
        return (w, h)

    # ══════════════════════════════════════════════════════════════
    # DRAW — multi-line with vertical clipping
    # ══════════════════════════════════════════════════════════════

    def draw_text(self, surface):
        r        = self.rect
        clip     = pygame.Rect(r.left + self.pad, r.top + self.pad,
                               r.width - self.pad * 2, r.height - self.pad * 2)
        old_clip = surface.get_clip()
        surface.set_clip(old_clip.clip(clip))
        tx = r.left + self.pad
        ty = r.top  + self.pad
        self.draw_selection_highlight(surface, tx, ty)
        surface.blit(self.my_surface, (tx, ty))
        surface.set_clip(old_clip)

    # ══════════════════════════════════════════════════════════════
    # SELECTION HIGHLIGHT — multi-line aware
    # ══════════════════════════════════════════════════════════════

    def draw_selection_highlight(self, surface, tx, ty):
        sel = self.selection_range()
        if not sel:
            return
        start, end     = sel
        start_line, start_col = self.pos_to_line_col(start)
        end_line,   end_col   = self.pos_to_line_col(end)
        for line_idx in range(start_line, end_line + 1):
            line_text = self.display_lines[line_idx] if line_idx < len(self.display_lines) else ""
            line_y    = ty + line_idx * self.line_height
            if line_idx == start_line and line_idx == end_line:
                x1 = tx + self.font.size(line_text[:start_col])[0]
                x2 = tx + self.font.size(line_text[:end_col])[0]
            elif line_idx == start_line:
                x1 = tx + self.font.size(line_text[:start_col])[0]
                x2 = tx + self.font.size(line_text)[0] + 4
            elif line_idx == end_line:
                x1 = tx
                x2 = tx + self.font.size(line_text[:end_col])[0]
            else:
                x1 = tx
                x2 = tx + self.font.size(line_text)[0] + 4
            if x2 > x1:
                highlight = pygame.Surface((x2 - x1, self.line_height), pygame.SRCALPHA)
                highlight.fill((70, 130, 200, 120))
                surface.blit(highlight, (x1, line_y))

    # ══════════════════════════════════════════════════════════════
    # CURSOR — multi-line position
    # ══════════════════════════════════════════════════════════════

    def draw_cursor(self, surface):
        self.cursor_timer += 1
        if self.cursor_timer % 60 >= 30:
            return
        r              = self.rect
        line, col      = self.pos_to_line_col(self.cursor_pos)
        line_text      = self.display_lines[line] if line < len(self.display_lines) else ""
        cx             = r.left + self.pad + self.font.size(line_text[:col])[0]
        cy             = r.top  + self.pad + line * self.line_height
        content_bottom = r.top + r.height - self.pad
        if cy < r.top + self.pad or cy + self.line_height > content_bottom:
            return
        pygame.draw.line(surface, self.color_txt, (cx, cy), (cx, cy + self.line_height), 2)

    def cursor_pixel_x(self):
        line, col = self.pos_to_line_col(self.cursor_pos)
        line_text = self.display_lines[line] if line < len(self.display_lines) else ""
        return self.font.size(line_text[:col])[0]

    def ensure_cursor_visible(self):
        pass  # Scrolling handled by parent scrollable container

    # ══════════════════════════════════════════════════════════════
    # LINE / COL CONVERSION
    # ══════════════════════════════════════════════════════════════

    def pos_to_line_col(self, pos):
        """Convert flat cursor position to (line_index, column)."""
        pos   = max(0, min(pos, len(self.text)))
        count = 0
        for i, line in enumerate(self.display_lines):
            line_len = len(line)
            if count + line_len >= pos and i == len(self.display_lines) - 1:
                return (i, pos - count)
            if count + line_len >= pos and i < len(self.display_lines) - 1:
                if pos - count <= line_len:
                    return (i, pos - count)
            count += line_len + 1  # +1 for the \n
        return (len(self.display_lines) - 1, len(self.display_lines[-1]) if self.display_lines else 0)

    def line_col_to_pos(self, line, col):
        """Convert (line_index, column) to flat cursor position."""
        pos = 0
        for i in range(min(line, len(self.display_lines))):
            pos += len(self.display_lines[i]) + 1  # +1 for \n
        if line < len(self.display_lines):
            col = min(col, len(self.display_lines[line]))
        pos += col
        return min(pos, len(self.text))

    # ══════════════════════════════════════════════════════════════
    # CLICK — multi-line position
    # ══════════════════════════════════════════════════════════════

    def pos_from_pixel(self, mouse_x, mouse_y=None):
        """Convert screen coordinates to flat cursor position."""
        r = self.rect
        if mouse_y is None:
            mouse_y = r.top + self.pad
        local_y   = mouse_y - r.top - self.pad
        line_idx  = max(0, min(int(local_y // self.line_height), len(self.display_lines) - 1))
        line_text = self.display_lines[line_idx] if line_idx < len(self.display_lines) else ""
        local_x   = mouse_x - r.left - self.pad
        best_col  = 0
        best_d    = abs(local_x)
        for c in range(1, len(line_text) + 1):
            px = self.font.size(line_text[:c])[0]
            d  = abs(local_x - px)
            if d < best_d:
                best_d   = d
                best_col = c
        return self.line_col_to_pos(line_idx, best_col)

    def handle_focus(self, pos):
        import time
        if self.rect and self.rect.collidepoint(pos):
            self.is_focused            = True
            self.cursor_timer          = 0
            now                        = time.time()
            clicked_pos                = self.pos_from_pixel(pos[0], pos[1])
            if now - self.private_last_click < 0.4:
                self.select_word_at(clicked_pos)
                self.private_text_dragging = False
            else:
                self.cursor_pos            = clicked_pos
                self.selection_anchor      = clicked_pos
                self.private_text_dragging = True
            self.private_last_click = now
            return True
        self.is_focused = False
        return False

    def handle_mouse_move(self, pos):
        if self.private_text_dragging and self.rect:
            self.cursor_pos   = self.pos_from_pixel(pos[0], pos[1])
            self.cursor_timer = 0
            return True
        return super(TextBox, self).handle_mouse_move(pos)

    # ══════════════════════════════════════════════════════════════
    # KEY HANDLING — override Enter behavior, add Up/Down
    # ══════════════════════════════════════════════════════════════

    def handle_key(self, event):
        if not self.is_focused:
            return False
        mods  = pygame.key.get_mods()
        ctrl  = mods & pygame.KMOD_CTRL
        shift = mods & pygame.KMOD_SHIFT

        if   event.key == pygame.K_RETURN:    self.insert_newline();          return True
        elif event.key == pygame.K_ESCAPE:    self.is_focused = False;        return True
        elif event.key == pygame.K_UP:        self.move_up(shift);            return True
        elif event.key == pygame.K_DOWN:      self.move_down(shift);          return True
        elif event.key == pygame.K_LEFT:      self.move_left(ctrl, shift);    return True
        elif event.key == pygame.K_RIGHT:     self.move_right(ctrl, shift);   return True
        elif event.key == pygame.K_HOME:      self.move_home(shift);          return True
        elif event.key == pygame.K_END:       self.move_end(shift);           return True
        elif event.key == pygame.K_BACKSPACE: self.delete_back(ctrl);         return True
        elif event.key == pygame.K_DELETE:    self.delete_forward();          return True
        elif ctrl and event.key == pygame.K_a:self.select_all();              return True
        elif ctrl and event.key == pygame.K_c:self.copy();                    return True
        elif ctrl and event.key == pygame.K_v:self.paste();                   return True
        elif ctrl and event.key == pygame.K_x:self.cut();                     return True
        elif event.key == pygame.K_TAB:       self.insert_tab();              return True
        elif event.unicode and event.unicode.isprintable():
            self.insert_char(event.unicode)
            return True
        return False

    # ══════════════════════════════════════════════════════════════
    # MULTI-LINE EDITING
    # ══════════════════════════════════════════════════════════════

    def insert_newline(self):
        self.delete_selection()
        self.text            = self.text[:self.cursor_pos] + "\n" + self.text[self.cursor_pos:]
        self.cursor_pos      += 1
        self.selection_anchor = self.cursor_pos
        self.cursor_timer    = 0
        self.on_text_changed()

    def insert_tab(self):
        self.delete_selection()
        spaces               = "    "
        self.text            = self.text[:self.cursor_pos] + spaces + self.text[self.cursor_pos:]
        self.cursor_pos      += len(spaces)
        self.selection_anchor = self.cursor_pos
        self.cursor_timer    = 0
        self.on_text_changed()

    # ══════════════════════════════════════════════════════════════
    # VERTICAL CURSOR MOVEMENT
    # ══════════════════════════════════════════════════════════════

    def move_up(self, shift=False):
        line, col = self.pos_to_line_col(self.cursor_pos)
        if line <= 0:
            self.cursor_pos = 0
        else:
            prev_line = self.display_lines[line - 1]
            new_col   = min(col, len(prev_line))
            self.cursor_pos = self.line_col_to_pos(line - 1, new_col)
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    def move_down(self, shift=False):
        line, col = self.pos_to_line_col(self.cursor_pos)
        if line >= len(self.display_lines) - 1:
            self.cursor_pos = len(self.text)
        else:
            next_line = self.display_lines[line + 1]
            new_col   = min(col, len(next_line))
            self.cursor_pos = self.line_col_to_pos(line + 1, new_col)
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    # ══════════════════════════════════════════════════════════════
    # HOME/END — line-aware (not whole document)
    # ══════════════════════════════════════════════════════════════

    def move_home(self, shift=False):
        line, col     = self.pos_to_line_col(self.cursor_pos)
        self.cursor_pos = self.line_col_to_pos(line, 0)
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    def move_end(self, shift=False):
        line, col       = self.pos_to_line_col(self.cursor_pos)
        line_text       = self.display_lines[line] if line < len(self.display_lines) else ""
        self.cursor_pos = self.line_col_to_pos(line, len(line_text))
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    # ══════════════════════════════════════════════════════════════
    # SUBMIT — TextArea doesn't submit on Enter
    # ══════════════════════════════════════════════════════════════

    def submit(self):
        pass  # Enter inserts newline. Use a button for submit.

    # ══════════════════════════════════════════════════════════════
    # PASTE — preserve newlines in multi-line
    # ══════════════════════════════════════════════════════════════

    def paste(self):

        clip = MgrClipboard.paste()
        if clip:
            clip = clip.replace('\r\n', '\n').replace('\r', '\n')
            self.delete_selection()
            self.text            = self.text[:self.cursor_pos] + clip + self.text[self.cursor_pos:]
            self.cursor_pos      += len(clip)
            self.selection_anchor = self.cursor_pos
            self.cursor_timer    = 0
            self.on_text_changed()