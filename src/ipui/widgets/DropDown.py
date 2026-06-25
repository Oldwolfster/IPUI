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
        self.on_click      = self.toggle_panel

        self.textbox       = TextBox(self,
            placeholder    = self.placeholder,
            font           = Style.FONT_HEADING,
            on_change      = self.on_text_changed,
        )
        self.textbox.on_click = self.handle_textbox_click

        self.list           = SelectionList(self,
            data            = self.data or {},
            single_select   = True,
            on_change       = self.on_list_changed,
            tooltip_class   = self.tooltip_class,
        )
        self.list.do_not_allocate   = True        # skip layout allocation
        self.list.is_overlay        = True        # but include in input dispatch
        self.list.visible           = False
        self.sync_from_pipeline()


    def handle_textbox_click(self):
        """Click on textbox opens the panel; does not close (user may be re-engaging filter)."""
        if not self.is_open: self.open_panel()
    # ==============================================================
    # OPEN / CLOSE
    # ==============================================================

    def toggle_panel(self):
        if self.is_open: self.close_panel()
        else:            self.open_panel()

    def open_panel(self):
        if self.is_open: return
        self.is_open           = True
        self.list.visible      = True
        self.list.set_filter("")
        if self.form: self.form.active_dropdown = self

    def close_panel(self):
        if not self.is_open: return
        self.is_open           = False
        self.list.visible      = False
        if self.form and self.form.active_dropdown is self:          # NEW
            self.form.active_dropdown = None
    # ==============================================================
    # EVENTS — PUNTED: DropDown rebuild is a separate effort.
    # Click toggles open/close. ESC not yet wired. Panel click TODO.
    # ==============================================================

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
        """Draw the option panel directly — no child layout needed."""
        if not self.is_open or not self.textbox.rect: return
        panel = self.compute_panel_rect()
        self.private_panel_rect = panel
        pygame.draw.rect(surface, Style.COLOR_CARD_BG, panel)
        pygame.draw.rect(surface, Style.COLOR_CARD_BORDER, panel, 1)
        font  = Style.FONT_BODY
        row_h = font.get_height() + Style.TOKEN_PAD * 2
        mx, my = pygame.mouse.get_pos()
        y = panel.top
        self.private_hit_rects = []
        for item in self.list.items:
            if not item.visible: continue
            if y + row_h > panel.bottom: break
            r = pygame.Rect(panel.left, y, panel.width, row_h)
            if r.collidepoint(mx, my):
                pygame.draw.rect(surface, Style.COLOR_PANEL_BG, r)
            txt = font.render(item.text, True, Style.COLOR_TEXT)
            surface.blit(txt, (r.left + Style.TOKEN_PAD, r.top + Style.TOKEN_PAD))
            self.private_hit_rects.append((item, r))
            y += row_h
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
        cx           = r.right - w // 2 - self.textbox.pad_x
        cy           = r.centery
        half_w       = w // 2
        half_h       = h // 2
        if self.is_open: points = [(cx - half_w, cy + half_h), (cx + half_w, cy + half_h), (cx, cy - half_h)]
        else:            points = [(cx - half_w, cy - half_h), (cx + half_w, cy - half_h), (cx, cy + half_h)]
        pygame.draw.polygon(surface, Style.COLOR_TEXT_MUTED, points)

    def compute_panel_rect(self):
        """Place panel directly below the textbox, matching its width."""
        tb          = self.textbox.rect
        row_h       = (self.list.items and self.list.items[0].min_height) or 24
        row_h       = row_h + (Style.TOKEN_BORDER+ Style.TOKEN_PAD) *2
        item_count  = len([i for i in self.list.items if i.visible])
        show_count  = max(1, min(item_count, self.max_visible))
        panel_h     = row_h * show_count + self.list.list_card.frame_size
        return        pygame.Rect(tb.left, tb.bottom, tb.width, panel_h)

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