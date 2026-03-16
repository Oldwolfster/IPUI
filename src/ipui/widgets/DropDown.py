# DropDown.py (complete new file)
from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.SelectionList import SelectionList
from ipui.widgets.TextBox import TextBox
from ipui.Style import Style
import pygame


class DropDown(_BaseWidget):
    """
    desc:        TextBox that opens a filterable SelectionList as a floating overlay.
    when_to_use: Single selection from a long list, with type-to-filter.
    best_for:    Choosing one optimizer, one activation, one anything from a big catalog.
    example:     DropDown(parent, placeholder="Select...", data=opts, on_change=handler)
    api:         get_selected(), get_selected_data(), set_filter(text), set_max_visible(n)
    Usage:
        dd = DropDown(parent, placeholder="Select...",
                      data={"SGD": {}, "Adam": {}},
                      pipeline_key="optimizer",
                      on_change=some_callback)
    """

    MAX_VISIBLE = 8

    def build(self):
        self.is_open       = False
        self.max_visible   = self.MAX_VISIBLE

        self.textbox       = TextBox(self,
            placeholder    = self.placeholder,
            font           = Style.FONT_HEADING,
            on_change      = self.on_text_changed,
        )

        self.list           = SelectionList(self,
            data            = self.data or {},
            single_select   = True,
            on_change       = self.on_list_changed,
            tooltip_class   = self.tooltip_class,
        )
        self.list.do_not_allocate = True
        self.list.visible         = False
        self.sync_from_pipeline()

    # ==============================================================
    # OPEN / CLOSE
    # ==============================================================

    def open_panel(self):
        if self.is_open: return
        self.is_open           = True
        self.list.visible      = True
        self.list.set_filter("")

    def close_panel(self):
        if not self.is_open: return
        self.is_open           = False
        self.list.visible      = False

    # ==============================================================
    # EVENTS
    # ==============================================================


    def dispatch_click(self, pos):
        """Intercept clicks on the floating panel before normal dispatch."""
        if self.is_open and self.list.rect and self.list.rect.collidepoint(pos):
            self.list.dispatch_click(pos)
            return True
        if self.is_open and self.rect and self.rect.collidepoint(pos):
            return super().dispatch_click(pos)
        self.close_panel()
        return super().dispatch_click(pos)

    def handle_focus(self, pos):
        """Click on textbox area toggles the panel."""
        if self.rect and self.rect.collidepoint(pos):
            if self.is_open: self.close_panel()
            else:            self.open_panel()
            self.textbox.handle_focus(pos)
            return True
        return False


    def clear_focus(self):
        """Let dispatch_click decide whether to close — not clear_focus."""
        self.textbox.is_focused = False

    def handle_key(self, event):
        """Escape closes the panel."""
        if event.key == 27 and self.is_open:
            self.close_panel()
            return True
        return False

    def on_text_changed(self, text):
        """Typing filters the list and opens the panel."""
        if not self.is_open: self.open_panel()
        self.list.set_filter(text)

    def on_list_changed(self, selected):
        """User clicked an item in the list."""
        if selected:
            self.textbox.set_text(selected[0])
        self.close_panel()
        if self.pipeline_key and self.form:
            self.form.pipeline_set(self.pipeline_key, selected)
        if self.on_change:
            self.on_change(selected)

    # ==============================================================
    # OVERLAY
    # ==============================================================

    def draw_overlay(self, surface):
        """Position and draw the floating SelectionList."""
        if not self.is_open:     return
        if self.textbox.rect is None: return
        panel_rect = self.compute_panel_rect()
        #self.list.layout(panel_rect)
        self.form.MEASUREDRAWLAY.layout_node(self.list, panel_rect)
        self.list.rect = panel_rect
        self.list.draw(surface)


    def draw(self, surface):
        super().draw(surface)
        self.draw_chevron(surface)



    def draw_chevron(self, surface):
        """Draw a triangle indicator scaled to textbox height."""
        size =.469  #(scale is 0 to 1)
        r            = self.textbox.rect
        if r is None : return
        h            = int(r.height * size)
        w            = int(h * 1.4)
        cx           = r.right - w // 2 - self.textbox.pad
        cy           = r.centery
        half_w       = w // 2
        half_h       = h // 2
        if self.is_open: points = [(cx - half_w, cy + half_h), (cx + half_w, cy + half_h), (cx, cy - half_h)]
        else:            points = [(cx - half_w, cy - half_h), (cx + half_w, cy - half_h), (cx, cy + half_h)]
        pygame.draw.polygon(surface, Style.COLOR_TEXT_MUTED, points)

    def compute_panel_rect(self):
        """Place panel directly below the textbox, matching its width."""
        tb         = self.textbox.rect
        row_h      = Style.FONT_HEADING.get_height() + Style.TOKEN_PAD * 2
        item_count = len([i for i in self.list.items if i.visible])
        show_count = max(1, min(item_count, self.max_visible))
        panel_h    = row_h * show_count + self.list.list_card.frame_size
        return       pygame.Rect(tb.left, tb.bottom, tb.width, panel_h)

    # ==============================================================
    # SELECTION API (mirrors SelectionList)
    # ==============================================================

    def set_filter(self, text):        self.list.set_filter(text)
    def get_selected(self):            return self.list.get_selected()
    def get_selected_data(self):       return self.list.get_selected_data()

    def sync_from_pipeline(self):
        """Sync selection from pipeline and update textbox display."""
        self.list.sync_from_pipeline()
        selected = self.get_selected()
        if selected: self.textbox.set_text(selected[0])

    def set_max_visible(self, count):
        """Set how many rows show when dropped down."""
        self.max_visible = count