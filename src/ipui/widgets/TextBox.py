# TextBox.py  Single-line text input.
#
# Inherits from Label:  my_surface, compute_intrinsic, measure_constrained,
#                        render_multiline, composite_glow, text_align, wrapping.
# Adds:                 Chrome (bg, border, focus glow), cursor, key handling,
#                        click-to-position, arrow navigation, text clipping,
#                        selection, clipboard, double-click, drag-to-select.
#
# MgrInput protocol:
#   handle_text_input(key, char, ctrl, shift)  — keyboard when focused
#   handle_focus_click(pos)                    — click while gaining focus
#   handle_drag_move(pos)                      — drag-select
#   handle_drag_end()                          — end drag-select
#   handle_double_click(pos)                   — select word

import time
import pygame
from ipui.utils.EZ import EZ
from ipui.utils.MgrClipboard import MgrClipboard
from ipui.widgets.Label import Label
from ipui.Style import Style
from ipui.engine.Key import Key


class TextBox(Label):
    """
    desc:        Single-line text input built on Label. Focus, cursor, pipeline sync.
    when_to_use: Any time the user types something.
    best_for:    Names, numbers, search filters, seed entry.
    example:     TextBox(parent, placeholder="Search...", on_submit=handler, pipeline_key="query")
    api:         set_text(text), set_focus(), submit(), sync_from_pipeline()
    """

    # ══════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════

    def build(self):
        EZ.warn_scroll             ( self)
        self.validate_params       ( )
        self.flex_width            = 1
        self.font                  = self.font or Style.FONT_BODY
        if self.tab_order is None  : self.tab_order=0 # Will be set in base_widget
        self.wrap                  = False
        self.focusable             = True
        self.color_bg              = Style.COLOR_CARD_BG
        self.color_txt             = Style.COLOR_TEXT
        self.color_placeholder     = Style.COLOR_TEXT_MUTED
        self.border_color          = Style.COLOR_BORDER
        self.border_focused        = Style.COLOR_TEXT_ACCENT
        self.placeholder           = self.placeholder or ""
        self.text                  = self.initial_value or self.text or ""
        self.is_focused            = False
        self.cursor_pos            = len(self.text)
        self.selection_anchor      = len(self.text)
        self.cursor_timer          = 0
        self.scroll_v              = 0
        self.pad_x                 = 12
        self.pad_y                 = 4
        self.rebuild_surface()
        self.sync_from_pipeline()


        self.private_undo_stack    = [(self.text, self.cursor_pos, self.selection_anchor)]  # NEW
        self.private_redo_stack    = []                                          # NEW
        self.private_undo_last_time= 0                                           # NEW
        self.private_undo_last_len = len(self.text)
        self.on_click              = self.handle_click_position
        self.on_double_click       = self.select_word_at_mouse

    def validate_params(self):
        if self.flex_width is False:
            EZ.err("TextBox does not support flex_width=False. TextBoxes always stretch to fill available space. Remove flex_width=False.")

    # ══════════════════════════════════════════════════════════════
    # SURFACE — rebuild my_surface from current text or placeholder
    # ══════════════════════════════════════════════════════════════

    def rebuild_surface(self):
        display         = self.text if self.text else self.placeholder
        color           = self.color_txt if self.text else self.color_placeholder
        self.my_surface = self.font.render(display, True, color)

    # ══════════════════════════════════════════════════════════════
    # MEASURE
    # ══════════════════════════════════════════════════════════════

    def measure(self):
        h = self.font.get_height() + self.pad_y * 2
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
        clip = pygame.Rect(r.left + self.pad_x, r.top, r.width - self.pad_x * 2, r.height)  # NEW
        old_clip = surface.get_clip()  # (unchanged)
        surface.set_clip(old_clip.clip(clip))  # (unchanged)
        self.ensure_cursor_visible()  # (unchanged)
        tx = r.left + self.pad_x - self.scroll_v
        ty = r.centery - self.my_surface.get_height() // 2
        self.draw_selection_highlight(surface, tx, ty)
        surface.blit(self.my_surface, (tx, ty))
        surface.set_clip(old_clip)

    def draw_selection_highlight(self, surface, tx, ty):
        sel = self.selection_range()
        if not sel:
            return
        start, end = sel
        x1        = tx + self.font.size(self.text[:start])[0]
        x2        = tx + self.font.size(self.text[:end])[0]
        h         = self.font.get_height()
        highlight = pygame.Surface((x2 - x1, h), pygame.SRCALPHA)
        highlight.fill((70, 130, 200, 120))
        surface.blit(highlight, (x1, ty))

    def draw_cursor(self, surface):
        self.cursor_timer += 1
        if self.cursor_timer % 60 >= 30:
            return
        r             = self.rect
        cx            = r.left  + self.pad_x + self.cursor_pixel_x() - self.scroll_v   # NEW
        cy            = r.centery - self.font.get_height() // 2                        # (unchanged)
        ch            = self.font.get_height()                                         # (unchanged)
        content_left  = r.left  + self.pad_x                                           # NEW
        content_right = r.right - self.pad_x
        if cx < content_left or cx > content_right:
            return
        pygame.draw.line(surface, self.color_txt, (cx, cy), (cx, cy + ch), 2)

    # ══════════════════════════════════════════════════════════════
    # SELECTION
    # ══════════════════════════════════════════════════════════════

    def selection_range(self):
        if self.cursor_pos == self.selection_anchor:
            return None
        return (min(self.cursor_pos, self.selection_anchor),
                max(self.cursor_pos, self.selection_anchor))

    def delete_selection(self):
        sel = self.selection_range()
        if not sel:
            return False
        start, end           = sel
        self.text            = self.text[:start] + self.text[end:]
        self.cursor_pos      = start
        self.selection_anchor = start
        self.cursor_timer    = 0
        return True

    def select_word_at_mouse(self):
        pos = pygame.mouse.get_pos()
        clicked_pos = self.pos_from_pixel(pos[0])
        #print(f"in select_word_at_mouse")
        self.select_word_at(clicked_pos)
        #print(f"AFTER select_word: anchor={self.selection_anchor} cursor={self.cursor_pos}")

    def select_word_at(self, pos):
        #print(f"postion ={pos}")
        if not self.text:
            return
        start = pos
        end   = pos
        while start > 0 and self.text[start - 1] != ' ':
            start -= 1
        while end < len(self.text) and self.text[end] != ' ':
            end += 1
        self.selection_anchor = start
        self.cursor_pos       = end
        self.cursor_timer     = 0

    def select_all(self):
        self.selection_anchor = 0
        self.cursor_pos       = len(self.text)
        self.cursor_timer     = 0

    # ══════════════════════════════════════════════════════════════
    # CURSOR MATH
    # ══════════════════════════════════════════════════════════════

    def cursor_pixel_x(self):
        return self.font.size(self.text[:self.cursor_pos])[0]

    def ensure_cursor_visible(self):
        if not self.rect:
            return
        visible_w = self.rect.width - self.pad_x * 2
        cx        = self.cursor_pixel_x()
        if cx - self.scroll_v > visible_w:
            self.scroll_v = cx - visible_w + 2
        if cx - self.scroll_v < 0:
            self.scroll_v = max(0, cx - 2)

    def pos_from_pixel(self, mouse_x):
        r       = self.rect
        local_x = mouse_x - r.left - self.pad_x + self.scroll_v
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
    # MgrInput PROTOCOL — focus click, drag, double-click
    # ══════════════════════════════════════════════════════════════

    def handle_click_position(self):
        pos = pygame.mouse.get_pos()
        if self.rect and self.rect.collidepoint(pos):
            self.cursor_timer     = 0
            clicked_pos           = self.pos_from_pixel(pos[0])
            self.cursor_pos       = clicked_pos
            self.selection_anchor = clicked_pos



    def handle_drag_move(self, pos):
        """Called by MgrInput during mouse drag (text selection)."""
        if self.rect:
            self.cursor_pos   = self.pos_from_pixel(pos[0])
            self.cursor_timer = 0

    def handle_drag_end(self):
        """Called by MgrInput when mouse is released."""
        pass  # Nothing to clean up for single-line

    # ══════════════════════════════════════════════════════════════
    # MgrInput PROTOCOL — keyboard input
    # ══════════════════════════════════════════════════════════════

    def handle_text_input(self, key, char, ctrl, shift):
        """Called by MgrInput when a key is pressed and this widget is focused.
        key:   Key.* constant (int)
        char:  printable character or None
        ctrl:  bool
        shift: bool
        Returns True if consumed."""
        if   key == Key.RETURN:    self.submit();                  return True
        elif key == Key.LEFT:      self.move_left(ctrl, shift);    return True
        elif key == Key.RIGHT:     self.move_right(ctrl, shift);   return True
        elif key == Key.HOME:      self.move_home(shift);          return True
        elif key == Key.END:       self.move_end(shift);           return True
        elif key == Key.BACKSPACE: self.delete_back(ctrl);         return True
        elif key == Key.DELETE:    self.delete_forward();          return True
        elif ctrl and key == Key.A:self.select_all();              return True
        elif ctrl and key == Key.C:self.copy();                    return True
        elif ctrl and key == Key.V:self.paste();                   return True
        elif ctrl and key == Key.X:self.cut();                     return True
        elif ctrl and shift and key == Key.Z: self.do_redo();      return True
        elif ctrl and key == Key.Z:           self.do_undo();      return True
        elif ctrl and key == Key.Y:           self.do_redo();      return True


        elif char:
            self.insert_char(char)
            return True
        return False

    # ══════════════════════════════════════════════════════════════
    # CURSOR MOVEMENT
    # ══════════════════════════════════════════════════════════════

    def move_left(self, ctrl=False, shift=False):
        self.flush_undo_chunk()
        if self.cursor_pos <= 0:
            if not shift:
                self.selection_anchor = self.cursor_pos
            return
        if ctrl:
            self.cursor_pos = self.word_boundary_left()
        else:
            self.cursor_pos -= 1
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    def move_right(self, ctrl=False, shift=False):
        self.flush_undo_chunk()
        if self.cursor_pos >= len(self.text):
            if not shift:
                self.selection_anchor = self.cursor_pos
            return
        if ctrl:
            self.cursor_pos = self.word_boundary_right()
        else:
            self.cursor_pos += 1
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    def move_home(self, shift=False):
        self.flush_undo_chunk()
        self.cursor_pos   = 0
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    def move_end(self, shift=False):
        self.flush_undo_chunk()
        self.cursor_pos   = len(self.text)
        if not shift:
            self.selection_anchor = self.cursor_pos
        self.cursor_timer = 0

    # ══════════════════════════════════════════════════════════════
    # WORD BOUNDARIES
    # ══════════════════════════════════════════════════════════════

    def word_boundary_left(self):
        pos = self.cursor_pos - 1
        while pos > 0 and self.text[pos - 1] == ' ':
            pos -= 1
        while pos > 0 and self.text[pos - 1] != ' ':
            pos -= 1
        return pos

    def word_boundary_right(self):
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
        self.delete_selection()
        self.text            = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
        self.cursor_pos      += 1
        self.selection_anchor = self.cursor_pos
        self.cursor_timer    = 0
        self.on_text_changed()

    def delete_back(self, ctrl=False):
        if self.delete_selection():
            self.on_text_changed()
            return
        if self.cursor_pos <= 0:
            return
        if ctrl:
            new_pos         = self.word_boundary_left()
            self.text       = self.text[:new_pos] + self.text[self.cursor_pos:]
            self.cursor_pos = new_pos
        else:
            self.text       = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
        self.selection_anchor = self.cursor_pos
        self.cursor_timer    = 0
        self.on_text_changed()

    def delete_forward(self):
        if self.delete_selection():
            self.on_text_changed()
            return
        if self.cursor_pos >= len(self.text):
            return
        self.text            = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
        self.selection_anchor = self.cursor_pos
        self.cursor_timer    = 0
        self.on_text_changed()

    # ══════════════════════════════════════════════════════════════
    # CLIPBOARD
    # ══════════════════════════════════════════════════════════════

    def copy(self):

        sel = self.selection_range()
        if sel:
            MgrClipboard.copy(self.text[sel[0]:sel[1]])
        else:
            MgrClipboard.copy(self.text)

    def paste(self):

        clip = MgrClipboard.paste()
        if clip:
            clip = clip.replace('\n', ' ').replace('\r', '')
            pygame.event.clear(pygame.KEYDOWN) #discard repeats queued during subprocess
            self.delete_selection()
            self.text            = self.text[:self.cursor_pos] + clip + self.text[self.cursor_pos:]
            self.cursor_pos      += len(clip)
            self.selection_anchor = self.cursor_pos
            self.cursor_timer    = 0
            self.on_text_changed()

    def cut(self):

        sel = self.selection_range()
        if sel:
            MgrClipboard.copy(self.text[sel[0]:sel[1]])
            self.delete_selection()
        else:
            MgrClipboard.copy(self.text)
            self.text            = ""
            self.cursor_pos      = 0
            self.selection_anchor = 0
        self.cursor_timer = 0
        self.on_text_changed()

    # ══════════════════════════════════════════════════════════════
    # CHANGE NOTIFICATION
    # ══════════════════════════════════════════════════════════════

    def on_text_changed(self):
        self.record_undo()
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
        if not self.pipeline_key and not self.on_change and not self.on_submit:
            self.text             = ""
            self.cursor_pos       = 0
            self.selection_anchor = 0
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
            self.text             = val_str
            self.cursor_pos       = len(self.text)
            self.selection_anchor = self.cursor_pos
            self.rebuild_surface()

    # ══════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════

    # TextBox.py  property: text setter override  New: editors set the backing store, never build
    # Reuses _BaseWidget's getter (via Label); refresh is handled by rebuild_surface(), not build().
    @Label.text.setter
    def text(self, value):
        self.private_text = value


    def set_text(self, text):
        self.text             = text
        self.cursor_pos       = len(self.text)
        self.selection_anchor = self.cursor_pos
        self.rebuild_surface()

    def set_focus(self):
        self.is_focused   = True
        self.cursor_timer = 0



    # ══════════════════════════════════════════════════════════════
    # UNDO / REDO ENGINE
    # ══════════════════════════════════════════════════════════════

    # TextBox.py  method: snapshot_state   NEW   Capture current editable state as a tuple.
    def snapshot_state(self):
        return (self.text, self.cursor_pos, self.selection_anchor)

    # TextBox.py  method: restore_state    NEW   Apply a snapshot, refresh surface, notify pipeline/on_change.
    def restore_state(self, snap):
        self.text, self.cursor_pos, self.selection_anchor = snap
        self.cursor_timer          = 0
        self.private_undo_last_len = len(self.text)
        self.private_undo_last_time= 0                                       # force next edit to start fresh chunk
        self.rebuild_surface()
        self.fire_change()                                                   # pipeline + on_change stay in sync with visible text

    # TextBox.py  method: record_undo      NEW   Called from on_text_changed. Coalesce-or-push snapshot.
    def record_undo(self):
        now          = time.time()
        new_len      = len(self.text)
        delta        = new_len - self.private_undo_last_len
        idle         = (now - self.private_undo_last_time) > 0.7            # 700ms idle = chunk boundary
        kind_flipped = (delta > 0) != (self.private_undo_last_len < new_len + (new_len - self.private_undo_last_len))  # type vs delete
        big_jump     = abs(delta) > 1                                       # paste / cut / multi-char op
        new_chunk    = idle or big_jump or self.private_undo_last_time == 0

        if new_chunk:                                                       # push a fresh snapshot
            self.private_undo_stack.append(self.snapshot_state())
            if len(self.private_undo_stack) > 100:
                self.private_undo_stack.pop(0)                              # cap memory at 100
        else:                                                               # coalesce: update top-of-stack
            self.private_undo_stack[-1] = self.snapshot_state()

        self.private_redo_stack.clear()                                     # any new edit kills redo history
        self.private_undo_last_time= now
        self.private_undo_last_len = new_len

    # TextBox.py  method: flush_undo_chunk NEW   Force next edit to start a new undo chunk (caret moves call this).
    def flush_undo_chunk(self):
        self.private_undo_last_time = 0

    # TextBox.py  method: do_undo          NEW   Pop undo, push current onto redo, restore.
    def do_undo(self):
        if len(self.private_undo_stack) <= 1:                               # stack always holds at least the seed
            return
        current = self.private_undo_stack.pop()
        self.private_redo_stack.append(current)
        self.restore_state(self.private_undo_stack[-1])

    # TextBox.py  method: do_redo          NEW   Pop redo, push onto undo, restore.
    def do_redo(self):
        if not self.private_redo_stack:
            return
        snap = self.private_redo_stack.pop()
        self.private_undo_stack.append(snap)
        self.restore_state(snap)