# NetworkDiagram.py

import pygame
from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.MgrColor import MgrColor
from ipui.widgets.Card import Card
from ipui.widgets.NeuronCell import NeuronCell
from ipui.Style import Style
from ipui.widgets.Row import CardCol
from ipui.widgets.Spacer import Spacer
from ipui.widgets.Label import Detail, Title, Body


class NetworkDiagram(_BaseWidget):
    """
    desc:        Custom widget.  Interactive neural network visualization. Click layers to inspect them.
    when_to_use: Showing network architecture visually.
    best_for:    The Workbench tab. Lets users see and select layers.
    example:     diagram = NetworkDiagram(parent, width_flex=True, height_flex=True)
    api:         set_layers(layers), set_selected(index), on_layer_selected
    """
    MAX_DISPLAY    = 8
    CELL_SIZE      = NeuronCell.CELL_SIZE
    CELL_GAP       = 4
    COL_GAP        = 32

    def build(self):
        self.layers           = []
        self.selected_layer   = -1
        self.on_layer_selected = None
        self.color_bg         = Style.COLOR_CARD_BG
        self.pad              = Style.TOKEN_PAD
        self.border           = 0
        MgrColor.apply_bevel(self, "sunken")

    def set_layers(self, layers):
        self.layers = list(layers)
        self.rebuild_cells()

    def set_selected(self, index):
        self.selected_layer = index
        self.apply_highlights()


    def rebuild_cells(self):
        self.children.clear()
        for layer_idx, count in enumerate(self.layers):
            shown = min(count, self.MAX_DISPLAY)
            for neuron_idx in range(shown):
                cell = NeuronCell(self)
                self.check_for_Percy(cell, layer_idx, neuron_idx, count)
                cell.data = {"layer": layer_idx, "neuron": neuron_idx}
                cell.on_click = self.make_cell_click(layer_idx)

        self.apply_highlights()

    def make_cell_click(self, layer_idx):
        def clicked():
            self.set_selected(layer_idx)
            if self.on_layer_selected:
                self.on_layer_selected(layer_idx)
        return clicked

    def check_for_Percy(self, cell, layer_idx, neuron_idx, count):
        if self.layers == [1]:
            card = Card(cell, border=30)
            sub = CardCol(card)
            Title(sub, "Percy", glow=True, text_align='c')
            Title(sub, "the", glow=True, text_align='c')
            Title(sub, "Perceptron", glow=True, text_align='c')
            Spacer(card)
            card2 = CardCol(card)
            Body(card2, "Answer = Input × Weight + Bias", text_align='c')

    def cell_label(self, layer_idx, neuron_idx, count):
        if self.layers == [1]:
            return "Percy"
        return str(neuron_idx + 1)

    def apply_highlights(self):
        for child in self.children:
            layer_idx    = child.data["layer"]
            child.set_highlighted(layer_idx == self.selected_layer)

    def layout(self, rect):
        self.rect = rect
        if not self.layers:
            return
        #frame       = self.frame_size
        #inner       = rect.inflate(-frame, -frame)
        #num_cols    = len(self.layers)
        frame = self.frame_size
        inner = rect.inflate(-frame, -frame)
        self.CELL_SIZE = self.calc_scale(inner)
        num_cols = len(self.layers)
        total_w     = num_cols * self.CELL_SIZE + (num_cols - 1) * self.COL_GAP
        start_x     = inner.left + (inner.width - total_w) // 2

        max_shown   = min(max(self.layers), self.MAX_DISPLAY)
        col_height  = max_shown * self.CELL_SIZE + (max_shown - 1) * self.CELL_GAP
        label_h     = Style.FONT_DETAIL.get_height() + 4
        total_h     = label_h + col_height
        center_y    = inner.top + (inner.height - total_h) // 2
        cells_top   = center_y + label_h

        child_idx = 0
        for col, count in enumerate(self.layers):
            shown       = min(count, self.MAX_DISPLAY)
            col_h       = shown * self.CELL_SIZE + (shown - 1) * self.CELL_GAP
            col_x       = start_x + col * (self.CELL_SIZE + self.COL_GAP)
            col_y       = cells_top + (col_height - col_h) // 2

            for row in range(shown):
                cell_y  = col_y + row * (self.CELL_SIZE + self.CELL_GAP)
                cell_r  = pygame.Rect(col_x, cell_y, self.CELL_SIZE, self.CELL_SIZE)

                #self.form.layout_engine.layout_node(self.children[child_idx], cell_r)
                self.children[child_idx].rect = cell_r #self.children[child_idx].layout(cell_r)
                child_idx += 1

    def draw(self, surface):
        if self.rect is None:
            return
        bg = self.resolve_bg()
        self.draw_chrome(surface, self.rect, bg)
        self.draw_labels(surface)
        old_clip = surface.get_clip()
        surface.set_clip(self.rect)
        for child in self.children:
            child.draw(surface)
        surface.set_clip(old_clip)

    def draw_labels(self, surface):
        if not self.layers:
            return
        frame       = self.frame_size
        inner       = self.rect.inflate(-frame, -frame)
        num_cols    = len(self.layers)
        total_w     = num_cols * self.CELL_SIZE + (num_cols - 1) * self.COL_GAP
        start_x     = inner.left + (inner.width - total_w) // 2

        max_shown   = min(max(self.layers), self.MAX_DISPLAY)
        col_height  = max_shown * self.CELL_SIZE + (max_shown - 1) * self.CELL_GAP
        label_h     = Style.FONT_DETAIL.get_height() + 4
        total_h     = label_h + col_height
        center_y    = inner.top + (inner.height - total_h) // 2

        font        = Style.FONT_DETAIL
        for col, count in enumerate(self.layers):
            col_x   = start_x + col * (self.CELL_SIZE + self.COL_GAP)
            label   = str(count)
            color   = Style.COLOR_PAL_ORANGE_FORGE if col == self.selected_layer else Style.COLOR_TEXT
            surf    = font.render(label, True, color)
            lx      = col_x + (self.CELL_SIZE - surf.get_width()) // 2
            surface.blit(surf, (lx, center_y))

    def calc_scale(self, inner):
        if not self.layers:
            return self.CELL_SIZE
        num_cols = len(self.layers)
        max_shown = min(max(self.layers), self.MAX_DISPLAY)
        label_h = Style.FONT_DETAIL.get_height() + 4

        avail_w = inner.width - (num_cols - 1) * self.COL_GAP
        avail_h = inner.height - label_h - (max_shown - 1) * self.CELL_GAP
        fit_w = avail_w // num_cols
        fit_h = avail_h // max_shown
        return max(8, min(fit_w, fit_h))