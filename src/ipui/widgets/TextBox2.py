# TextBox2.py  NEW: Label-based text input. A Label that accepts keyboard input.
#
# Inherits from Label:  my_surface, compute_intrinsic, measure_constrained,
#                        render_multiline, composite_glow, text_align, wrapping.
# Adds:                 Chrome (bg, border, focus glow), cursor, key handling,
#                        click-to-position, arrow navigation, text clipping.

import pygame

from ipui.utils import MgrClipboard
from ipui.widgets.Label import Label
from ipui.Style import Style


class TextBox2(Label):
    """
    desc:        Single-line text input built on Label. Focus, cursor, pipeline sync.
    when_to_use: Any time the user types something.
    best_for:    Names, numbers, search filters, seed entry.
    example:     TextBox2(parent, placeholder="Search...", on_submit=handler, pipeline_key="query")
    api:         set_text(text), set_focus(), submit(), sync_from_pipeline()
    """

    # ══════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════

    def build(self):
        self.my_name            = f"TextBox: {self.placeholder}"
        self.font               = self.font or Style.FONT_BODY
        self.wrap               = False
        self.color_bg           = Style.COLOR_CARD_BG
        self.color_txt          = Style.COLOR_TEXT
        self.color_placeholder  = Style.COLOR_TEXT_MUTED
        self.border_color       = Style.COLOR_BORDER
        self.border_focused     = Style.COLOR_TEXT_ACCENT
        self.placeholder        = self.placeholder or ""
        self.text               = self.initial_value or ""
        self.is_focused         = False
        self.cursor_pos         = len(self.text)
        self.cursor_timer       = 0
        self.scroll_x           = 0
        self.rebuild_surface()
        self.sync_from_pipeline()

    # ══════════════════════════════════════════════════════════════
    # SURFACE — rebuild my_surface from current text or placeholder
    # ══════════════════════════════════════════════════════════════

    def rebuild_surface(self):
        display = self.text if self.text else self.placeholder
        color   = self.color_txt if self.text else self.color_placeholder
        self.my_surface = self.font.render(display, True, color)

    # ══════════════════════════════════════════════════════════════
    # MEASURE
    # ══════════════════════════════════════════════════════════════

    def measure(self):
        h = self.font.get_height() + self.pad * 2
        w = 200
        return (w, h)

    # ══════════════════════════════════════════════════════════════
    # DRAW — chrome + clipped text + cursor
    # ══════════════════════════════════════════════════════════════

    def draw(self, surface):
        if self.rect is None:
            return
        self.draw_chrome(surface, self.rect, self.resolve_bg())
        self.draw_text(surface)
        if self.is_focused:
            self.draw_cursor(surface)

    def draw_chrome(self, surface, rect, bg_color):
        radius   = Style.TOKEN_CORNER_RADIUS
        border_w = 3 if self.is_focused else 2
        border_c = self.border_focused if self.is_focused else self.border_color
        if bg_color:
            pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
        pygame.draw.rect(surface, border_c, rect, border_w, border_radius=radius)

    def draw_text(self, surface):
        r        = self.rect
        clip     = pygame.Rect(r.left + self.pad, r.top, r.width - self.pad * 2, r.height)
        old_clip = surface.get_clip()
        surface.set_clip(old_clip.clip(clip))
        self.ensure_cursor_visible()
        tx = r.left + self.pad - self.scroll_x
        ty = r.centery - self.my_surface.get_height() // 2
        surface.blit(self.my_surface, (tx, ty))
        surface.set_clip(old_clip)

    def draw_cursor(self, surface):
        self.cursor_timer += 1
        if self.cursor_timer % 60 >= 30:
            return
        r  = self.rect
        cx = r.left + self.pad + self.cursor_pixel_x() - self.scroll_x
        cy = r.centery - self.font.get_height() // 2
        ch = self.font.get_height()
        # Clip cursor to content area
        content_left  = r.left + self.pad
        content_right = r.right - self.pad
        if cx < content_left or cx > content_right:
            return
        pygame.draw.line(surface, self.color_txt, (cx, cy), (cx, cy + ch), 2)

    # ══════════════════════════════════════════════════════════════
    # CURSOR MATH
    # ══════════════════════════════════════════════════════════════

    def cursor_pixel_x(self):
        """Pixel x of cursor relative to text start."""
        return self.font.size(self.text[:self.cursor_pos])[0]

    def ensure_cursor_visible(self):
        """Scroll so cursor is always within the visible content area."""
        if not self.rect:
            return
        visible_w = self.rect.width - self.pad * 2
        cx        = self.cursor_pixel_x()
        if cx - self.scroll_x > visible_w:
            self.scroll_x = cx - visible_w + 2
        if cx - self.scroll_x < 0:
            self.scroll_x = max(0, cx - 2)

    def pos_from_pixel(self, mouse_x):
        """Convert a screen x coordinate to a cursor position in text."""
        r        = self.rect
        local_x  = mouse_x - r.left - self.pad + self.scroll_x
        best_pos = 0
        best_d   = abs(local_x)
        for i in range(1, len(self.text) + 1):
            px = self.font.size(self.text[:i])[0]
            d  = abs(local_x - px)
            if d < best_d:
                best_d   = d
                best_pos = i
        return best_pos

    # ══════════════════════════════════════════════════════════════
    # FOCUS
    # ══════════════════════════════════════════════════════════════

    def handle_focus(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.is_focused   = True
            self.cursor_timer = 0
            self.cursor_pos   = self.pos_from_pixel(pos[0])
            return True
        self.is_focused = False
        return False

    # ══════════════════════════════════════════════════════════════
    # KEY HANDLING
    # ══════════════════════════════════════════════════════════════

    def handle_key(self, event):
        if not self.is_focused:
            return False
        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL

        if   event.key == pygame.K_RETURN:    self.submit();          return True
        elif event.key == pygame.K_ESCAPE:    self.is_focused = False; return True
        elif event.key == pygame.K_LEFT:      self.move_left(ctrl);   return True
        elif event.key == pygame.K_RIGHT:     self.move_right(ctrl);  return True
        elif event.key == pygame.K_HOME:      self.move_home();       return True
        elif event.key == pygame.K_END:       self.move_end();        return True
        elif event.key == pygame.K_BACKSPACE: self.delete_back(ctrl); return True
        elif event.key == pygame.K_DELETE:    self.delete_forward();  return True
        elif ctrl and event.key == pygame.K_a:self.select_all();      return True
        elif ctrl and event.key == pygame.K_c:self.copy();            return True
        elif ctrl and event.key == pygame.K_v:self.paste();           return True
        elif ctrl and event.key == pygame.K_x:self.cut();             return True
        elif event.unicode and event.unicode.isprintable():
            self.insert_char(event.unicode)
            return True
        return False

    # ══════════════════════════════════════════════════════════════
    # CURSOR MOVEMENT
    # ══════════════════════════════════════════════════════════════

    def move_left(self, ctrl=False):
        if self.cursor_pos <= 0:
            return
        if ctrl:
            self.cursor_pos = self.word_boundary_left()
        else:
            self.cursor_pos -= 1
        self.cursor_timer = 0

    def move_right(self, ctrl=False):
        if self.cursor_pos >= len(self.text):
            return
        if ctrl:
            self.cursor_pos = self.word_boundary_right()
        else:
            self.cursor_pos += 1
        self.cursor_timer = 0

    def move_home(self):
        self.cursor_pos   = 0
        self.cursor_timer = 0

    def move_end(self):
        self.cursor_pos   = len(self.text)
        self.cursor_timer = 0

    # ══════════════════════════════════════════════════════════════
    # WORD BOUNDARIES
    # ══════════════════════════════════════════════════════════════

    def word_boundary_left(self):
        """Find start of previous word."""
        pos = self.cursor_pos - 1
        while pos > 0 and self.text[pos - 1] == ' ':
            pos -= 1
        while pos > 0 and self.text[pos - 1] != ' ':
            pos -= 1
        return pos

    def word_boundary_right(self):
        """Find end of next word."""
        pos = self.cursor_pos
        while pos < len(self.text) and self.text[pos] == ' ':
            pos += 1
        while pos < len(self.text) and self.text[pos] != ' ':
            pos += 1
        return pos

    # ══════════════════════════════════════════════════════════════
    # TEXT EDITING
    # ══════════════════════════════════════════════════════════════

    def insert_char(self, char):
        self.text       = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
        self.cursor_pos += 1
        self.cursor_timer = 0
        self.on_text_changed()

    def delete_back(self, ctrl=False):
        if self.cursor_pos <= 0:
            return
        if ctrl:
            new_pos   = self.word_boundary_left()
            self.text = self.text[:new_pos] + self.text[self.cursor_pos:]
            self.cursor_pos = new_pos
        else:
            self.text       = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
        self.cursor_timer = 0
        self.on_text_changed()

    def delete_forward(self):
        if self.cursor_pos >= len(self.text):
            return
        self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
        self.cursor_timer = 0
        self.on_text_changed()

    # ══════════════════════════════════════════════════════════════
    # CLIPBOARD
    # ══════════════════════════════════════════════════════════════

    def select_all(self):
        # TODO: visual selection in v0.2
        pass

    def copy(self):

        MgrClipboard.copy(self.text)

    def paste(self):

        clip = MgrClipboard.paste()
        if clip:
            clip = clip.replace('\n', ' ').replace('\r', '')
            self.text       = self.text[:self.cursor_pos] + clip + self.text[self.cursor_pos:]
            self.cursor_pos += len(clip)
            self.cursor_timer = 0
            self.on_text_changed()

    def cut(self):
        # TODO: cut selection in v0.2. For now, cut all.
        from ipui.utils.MgrClipboard import MgrClipboard
        MgrClipboard.copy(self.text)
        self.text       = ""
        self.cursor_pos = 0
        self.cursor_timer = 0
        self.on_text_changed()

    # ══════════════════════════════════════════════════════════════
    # CHANGE NOTIFICATION
    # ══════════════════════════════════════════════════════════════

    def on_text_changed(self):
        self.rebuild_surface()
        self.fire_change()

    def fire_change(self):
        if self.pipeline_key and self.form:
            self.form.pipeline_set(self.pipeline_key, self.text)
        if self.on_change:
            self.on_change(self.text)

    # ══════════════════════════════════════════════════════════════
    # SUBMIT
    # ══════════════════════════════════════════════════════════════

    def submit(self):
        if self.pipeline_key and self.form:
            self.form.pipeline_set(self.pipeline_key, self.text)
        if self.on_submit and self.text:
            self.on_submit(self.text)
        if not self.pipeline_key:
            self.text       = ""
            self.cursor_pos = 0
        self.rebuild_surface()
        self.set_focus()

    # ══════════════════════════════════════════════════════════════
    # PIPELINE SYNC
    # ══════════════════════════════════════════════════════════════

    def sync_from_pipeline(self):
        val = self.form.pipeline_read(self.pipeline_key)
        if val is None:
            return
        val_str = str(val)
        if val_str != self.text:
            self.text       = val_str
            self.cursor_pos = len(self.text)
            self.rebuild_surface()

    # ══════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════

    def set_text(self, text):
        self.text       = text
        self.cursor_pos = len(self.text)
        self.rebuild_surface()

    def set_focus(self):
        self.is_focused   = True
        self.cursor_timer = 0