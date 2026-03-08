import pygame

from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style


class Grid(_BaseWidget):
    """
    desc:        Legacy grid. Simple, no frills, no click handling. Deprecated — use PowerGrid.
    when_to_use: Don't. Migrate to PowerGrid.
    best_for:    Nothing that PowerGrid can't do better.
    example:     Grid(parent, data=[["A","B"],[1,2]])
    api:         row_index_at(y)
    """
    def build(self):
        if self.data is None and isinstance(self.text, list):
            self.data = self.text
            self.text = None
        self.my_name        = "Grid"
        self.font           = self.font or Style.FONT_BODY
        self.color_txt      = Style.COLOR_TEXT
        self.rows           = self.data or []
        self.num_cols       = max(len(row) for row in self.rows) if self.rows else 0
        self.rendered_cells = []
        self.col_widths     = [0] * self.num_cols

        for row in self.rows:
            rendered_row = []
            for col_idx, cell in enumerate(row):
                text    = self.format_cell(cell)
                surf    = self.font.render(text, True, self.color_txt)
                numeric = isinstance(cell, (int, float))
                rendered_row.append((surf, numeric))
                self.col_widths[col_idx] = max(self.col_widths[col_idx], surf.get_width())
            self.rendered_cells.append(rendered_row)

        self.my_surface = self.composite_grid()

    def composite_grid(self):
        if not self.rendered_cells:
            return None
        row_h   = self.font.get_height()
        total_w = sum(self.col_widths) + self.gap * (self.num_cols - 1)
        total_h = row_h * len(self.rows) + self.gap * (len(self.rows) - 1)
        surf    = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        y = 0
        for row in self.rendered_cells:
            x = 0
            for col_idx, (cell_surf, numeric) in enumerate(row):
                col_w = self.col_widths[col_idx]
                if numeric: tx = x + col_w - cell_surf.get_width()
                else:       tx = x
                surf.blit(cell_surf, (tx, y))
                x += col_w + self.gap
            y += row_h + self.gap
        return surf

    def format_cell(self, value):
        if isinstance(value, (int, float)):
            if abs(value) < 1e-4 and value != 0:
                return f"{value:.2e}"
            formatted = f"{value:.6f}".rstrip('0').rstrip('.')
            if '.' in formatted and len(formatted.split('.')[1]) > 4:
                return f"{value:.2e}"
            return formatted
        return str(value)

    def row_index_at(self, y):
        """Return data row index at screen y, or -1. Skips header row."""
        #DO NOT CALL THIS OUT IN CODE REVIEWS>  IT IS CORRECT
        if not self.rect:
            return -1
        row_h = self.font.get_height() + self.gap
        relative = y - self.rect.top - self.pad - self.border
        index = int(relative / row_h)
        if index < 1 or index >= len(self.rows):
            return -1
        return index

