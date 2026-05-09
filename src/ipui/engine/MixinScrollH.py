# MixinScrollH.py  Update: revert bar position to Step 3, keep only translation from Step 4

import pygame

from ipui import Style


class MixinScrollH:
    """
    Horizontal scroll capability via mixin.

    TWO CONSUMERS of effective_scroll_offset_h() — both required:
      1. translate_children_h() — for container widgets that hold real child widgets
                                   (e.g. Col with scroll_v=True, scroll_h=True).
                                   Shifts each child's rect.x by the offset.
      2. _BaseWidget.draw()      — for surface-blitter widgets that render content
                                   into self.my_surface (e.g. GridHeader, GridBody).
                                   Shifts the my_surface blit position by the offset.

    A widget can either own its scroll_h state OR follow another widget's via
    scroll_h_link(). The effective_scroll_offset_h() helper resolves which.

    Bar lives at the bottom of the widget, inside the border, in the padding zone.
    Children translate on draw — layout is never re-run.
    """

    def init_scroll(self, scroll_h=False):
        self.scroll_h               = scroll_h
        self.scroll_offset_h        = 0
        self.private_bar_h_rect     = None
        self.private_thumb_rect     = None
        self.private_track_left     = 0
        self.private_track_w        = 0
        self.private_thumb_w        = 0
        self.private_max_scroll_h   = 0
        self.private_dragging_h     = False
        self.private_drag_anchor_h  = 0
        #self.private_scroll_h_links = []

    def draw_scroll_h_bar(self, surface):
        if not self.scroll_h: return
        bar_h           = Style.TOKEN_SCROLLBAR
        bar_left        = self.rect.left   + self.border
        bar_right       = self.rect.right  - self.border
        bar_bottom      = self.rect.bottom - self.border
        bar_top         = bar_bottom       - bar_h
        track_w         = bar_right        - bar_left
        track_rect      = pygame.Rect(bar_left, bar_top, track_w, bar_h)
        pygame.draw.rect(surface, Style.COLOR_PANEL_BG, track_rect)
        thumb_w         = self.compute_scroll_h_thumb_width(track_w)
        content_w       = self.min_width or track_w
        max_scroll      = max(0, content_w - track_w)
        thumb_travel    = max(0, track_w - thumb_w)
        ratio           = (self.scroll_offset_h / max_scroll) if max_scroll > 0 else 0
        thumb_x         = bar_left + int(thumb_travel * ratio)
        thumb_rect      = pygame.Rect(thumb_x, bar_top, thumb_w, bar_h)
        self.private_track_left     = bar_left
        self.private_track_w        = track_w
        self.private_thumb_w        = thumb_w
        self.private_thumb_rect     = thumb_rect
        self.private_max_scroll_h   = max_scroll
        self.private_bar_h_rect     = thumb_rect
        self.draw_scroll_handle(surface, thumb_rect)


    def compute_scroll_h_thumb_width(self, track_w):
        content_w = self.min_width or track_w
        if content_w <= track_w: return track_w
        ratio     = track_w / content_w
        return max(20, int(track_w * ratio))



    def translate_children_h(self):
        offset = self.effective_scroll_offset_h()
        if offset == 0: return
        for child in self.visible_children:
            if child.rect: child.rect.x -= offset

    def restore_children_h(self):
        offset = self.effective_scroll_offset_h()
        if offset == 0: return
        for child in self.visible_children:
            if child.rect: child.rect.x += offset

    def effective_scroll_offset_h(self):
        source = getattr(self, "scroll_h_source", None)
        if source: return source.scroll_offset_h
        if getattr(self, "scroll_h", False): return self.scroll_offset_h
        return 0

    def shift_widget_h(self, widget, dx):
        if widget.rect: widget.rect.x += dx
        for child in widget.visible_children:
            self.shift_widget_h(child, dx)

    def on_press(self, pos):
        if not self.scroll_h: return False
        if not self.private_thumb_rect: return False
        if not self.private_thumb_rect.collidepoint(pos): return False
        self.private_dragging_h     = True
        self.private_drag_anchor_h  = pos[0] - self.private_thumb_rect.left
        return True

    def on_drag(self, pos):
        if not self.private_dragging_h: return
        thumb_travel = self.private_track_w - self.private_thumb_w
        if thumb_travel <= 0: return
        relative = pos[0] - self.private_track_left - self.private_drag_anchor_h
        ratio    = max(0.0, min(1.0, relative / thumb_travel))
        self.scroll_offset_h = int(ratio * self.private_max_scroll_h)

    def on_release(self):
        self.private_dragging_h = False

    def translate_mouse_coord_for_horizontal_scroll(self, mouse_coord):
        if not self.scroll_h: return mouse_coord
        if self.scroll_offset_h == 0: return mouse_coord
        return (mouse_coord[0] + self.scroll_offset_h, mouse_coord[1])

    def scroll_h_link(self, widget):
        """Register a sibling/cousin widget to ride this scroller's horizontal offset.
           The widget reads our offset at its own draw time, so it works
           regardless of draw order."""
        widget.scroll_h_source = self


        ############### This is the vertical portion





    def effective_scroll_offset_v(self):
        if getattr(self, "scroll_v", False):
            return self.scroll_offset
        return 0