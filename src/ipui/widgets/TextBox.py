import pygame

from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style

class TextBox(_BaseWidget):
    """
    desc:        Single-line text input with focus, cursor blink, and pipeline sync.
    when_to_use: Any time the user types something.
    best_for:    Names, numbers, search filters, seed entry.
    example:     TextBox(parent, placeholder="Search...", on_submit=handler, pipeline_key="query")
    api:         set_text(text), set_focus(), submit(), sync_from_pipeline()
    """
    def build(self):
        self.my_name            = f"TextBox: {self.placeholder}"
        self.font               = self.font or Style.FONT_BODY
        self.color_bg           = Style.COLOR_CARD_BG
        self.color_txt          = Style.COLOR_TEXT
        self.color_placeholder  = Style.COLOR_TEXT_MUTED
        self.border_color       = Style.COLOR_BORDER
        self.border_focused     = Style.COLOR_TEXT_ACCENT
        self.placeholder        = self.placeholder or ""
        self.text               = self.initial_value or ""
        self.is_focused         = False
        self.cursor_timer       = 0
        h                       = self.font.get_height() + self.pad * 2     # calc height
        w = self.font.size(self.placeholder or "")[0] + self.pad * 2        # just enough for placeholder
        self.my_surface = pygame.Surface((w, h), pygame.SRCALPHA)      # Surface and h set to work with layout
        self.sync_from_pipeline()

    def measure(self):
        h = self.font.get_height() + self.pad * 2
        w = 200
        return (w, h)

    def draw_chrome(self, surface, rect, bg_color):
        radius      = Style.TOKEN_CORNER_RADIUS
        border_w    = 3 if self.is_focused else 2
        border_c    = self.border_focused if self.is_focused else self.border_color
        if bg_color:
            pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
        pygame.draw.rect(surface, border_c, rect, border_w, border_radius=radius)

    def draw(self, surface):
        if self.rect is None:
            return
        self.current_bg = self.resolve_bg()
        self.draw_chrome(surface, self.rect, self.current_bg)
        r           = self.rect
        display     = self.text if self.text else self.placeholder
        color       = self.color_txt if self.text else self.color_placeholder
        text_surf   = self.font.render(display, True, color)
        text_rect   = text_surf.get_rect(midleft=(r.left + self.pad, r.centery))
        surface.blit(text_surf, text_rect)
        if self.is_focused:
            self.draw_cursor(surface, text_rect, r)

    def draw_cursor(self, surface, text_rect, r):
        self.cursor_timer += 1
        if self.cursor_timer % 60 < 30:
            cx  = text_rect.right + 2 if self.text else r.left + self.pad
            cy1 = r.centery - self.font.get_height() // 2
            cy2 = r.centery + self.font.get_height() // 2
            pygame.draw.line(surface, self.color_txt, (cx, cy1), (cx, cy2), 2)

    def handle_focus(self, pos):
        if self.rect and self.rect.collidepoint(pos):
            self.is_focused     = True
            self.cursor_timer   = 0
            return True
        self.is_focused = False
        return False


    def handle_key(self, event):
        if not self.is_focused:
            return False
        if   event.key == pygame.K_RETURN:      self.submit();              return True
        elif event.key == pygame.K_BACKSPACE:    self.text = self.text[:-1]; self.fire_change(); return True
        elif event.key == pygame.K_ESCAPE:       self.is_focused = False;    return True
        elif event.unicode and event.unicode.isprintable():
            self.text += event.unicode
            self.fire_change()
            return True
        return False

    def fire_change(self):
        if self.pipeline_key and self.form:    self.form.pipeline_set(self.pipeline_key, self.text)
        if self.on_change:    self.on_change(self.text)

    def submit(self):
        if self.pipeline_key and self.form:  #Probably redundant... better safe than sorry
            self.form.pipeline_set(self.pipeline_key, self.text)
        if self.on_submit and self.text:
            self.on_submit(self.text)
        if not self.pipeline_key:
            self.text = ""
        self.set_focus()

    def sync_from_pipeline(self):
        val = self.form.pipeline_read(self.pipeline_key)
        if val is None:
            return
        val_str = str(val)
        if val_str != self.text and not self.is_focused:
            self.text = val_str

    def set_text(self, text):   self.text = text
    def set_focus(self):        self.is_focused = True; self.cursor_timer = 0