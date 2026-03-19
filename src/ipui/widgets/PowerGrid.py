# PowerGrid2.py — IPUI Framework Data Grid  NEW: Child-widget architecture
# Header, body, and scroller are proper widgets. Layout engine handles everything.
# Scrolling is unified via _BaseWidget — no custom scroll code.

import inspect
import pygame

from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.Row import Col
from ipui.Style import Style
from ipui.widgets.RecordSelector import RecordSelector


# ══════════════════════════════════════════════════════════════════
# GRID HEADER — displays column names, will handle sort clicks later
# ══════════════════════════════════════════════════════════════════

class GridHeader(_BaseWidget):
    def build(self):
        self.pad      = 0
        self.border   = 0

    def measure(self):
        if self.my_surface:
            return (self.my_surface.get_width(), self.my_surface.get_height())
        return (0, 0)


# ══════════════════════════════════════════════════════════════════
# GRID BODY — holds the composited rows surface
# ══════════════════════════════════════════════════════════════════

class GridBody(_BaseWidget):
    def build(self):
        self.pad      = 0
        self.border   = 0

    def measure(self):
        if self.my_surface:
            return (self.my_surface.get_width(), self.my_surface.get_height())
        return (0, 0)


# ══════════════════════════════════════════════════════════════════
# POWER GRID — the main widget
# ══════════════════════════════════════════════════════════════════

class PowerGrid(_BaseWidget):
    """
    desc:        The sweetest grid in the Pygame ecosystem. Sticky header, internal scroll, sortable headers, zebra rows, three input formats, validated row clicks, pagination.
    when_to_use: Tabular data of any shape.
    best_for:    Batch lists, run results, leaderboards, any data that belongs in rows and columns.
    example:     grid = PowerGrid2(parent, name="results"); grid.set_data(rows, columns=["A","B"])
    api:         set_data(data, columns), on_row_click(callback, column), set_column_max(col, width), set_page_size(n)

    Accepts three input formats via set_data():
        1. List of lists   — set_data([[1,"A"],[2,"B"]], columns=["ID","Name"])
        2. List of dicts   — set_data([{"ID":1,"Name":"A"}, {"ID":2,"Name":"B"}])
        3. Dict of lists   — set_data({"ID":[1,2], "Name":["A","B"]})

    Legacy format (first row as header) is supported when columns is omitted from list-of-lists.

    Row click callback:
        grid.on_row_click(my_handler)              # handler receives dict of row data
        grid.on_row_click(my_handler, "batch_id")  # handler receives value of that column
        grid.on_row_click(my_handler, 0)           # handler receives value of column 0

    Child structure:
        PowerGrid2
        ├── GridHeader       (fixed height)
        ├── Col              (scrollable=True, height_flex=1)
        │   └── GridBody     (full content height — drives scroll)
        └── RecordSelector   (fixed height, hidden when not needed)
    """

    SCROLLBAR_W = 10

    # ══════════════════════════════════════════════════════════════
    # CONSTRUCTION
    # ══════════════════════════════════════════════════════════════

    def build(self):
        if self.height_flex == 0:
            print("[PowerGrid2] Note: height_flex forced to 1 — PowerGrid2 scrolls internally.")
        self.height_flex        = 1
        self.pad                = 0
        self.font               = self.font or Style.FONT_BODY
        self.color_txt          = Style.COLOR_TEXT
        self.color_header       = Style.COLOR_TEXT_ACCENT
        self.color_row_even     = None
        self.color_row_odd      = (255, 255, 255, 12)
        self.columns            = []
        self.rows_all           = []
        self.rows_sorted        = []
        self.col_widths         = []
        self.col_aligns         = []
        self.col_precision      = []
        self.col_max            = {}
        self.row_height         = 0
        self.render_gap         = 0
        self.sort_col           = -1
        self.sort_asc           = True
        self.header_col_rects   = []
        self.available_width    = 0
        self.row_click_callback = None
        self.row_click_column   = None
        self.page_size          = 50
        self.build_body()
        if self.data            : self.set_data(self.data)

    def build_body(self):
        self.grid_header     = GridHeader(self)
        self.grid_scroller   = Col(self, scrollable=True, height_flex=1)
        self.grid_body       = GridBody(self.grid_scroller)
        self.record_selector = RecordSelector(self, on_change=self.handle_page_change)

    # ══════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════

    def set_data(self, data, columns=None, query=None, table=None):
        """Accept lists, dicts, SQLite path, or connection."""
        self.sql_source = None
        if query or table:
            from ipui.utils.SQLDataSource import SQLDataSource
            self.sql_source = SQLDataSource(data, query=query, table=table)
            self.columns, self.rows_all = self.sql_source.fetch()
        else:
            self.columns, self.rows_all = Normalizer.normalize(data, columns)
        # THIS WORKS!!  Resets position.  temp disable --> self.grid_scroller.scroll_offset = 0
        self.update_record_selector()
        self.rebuild()

    def set_column_max(self, col, max_width):
        """Cap a column's pixel width.  Accepts index or column name."""
        idx = col if isinstance(col, int) else self.columns.index(col)
        self.col_max[idx] = max_width

    def set_page_size(self, size):
        """Set rows per page. 0 = no pagination."""
        self.page_size = size
        self.update_record_selector()
        self.rebuild()

    def on_row_click(self, callback, column=None):
        """Register a callback for row clicks.

        Args:
            callback: A callable that accepts exactly one argument.
            column:   What to pass to the callback:
                      None          → dict of {column_name: value} for the row
                      "column_name" → value of that column
                      0, 1, 2...    → value of column at that index

        Raises:
            TypeError:  if callback is not callable
            ValueError: if callback doesn't accept exactly 1 parameter
        """
        RowClickValidator.validate_callback(callback)
        self.row_click_callback = callback
        self.row_click_column   = column

    # ══════════════════════════════════════════════════════════════
    # PAGINATION
    # ══════════════════════════════════════════════════════════════

    def update_record_selector(self):
        if self.page_size <= 0 or len(self.rows_all) <= self.page_size:
            if self.record_selector:
                self.record_selector.visible = False
            return
        if not self.record_selector:
            from ipui.widgets.RecordSelector import RecordSelector
            self.record_selector = RecordSelector(self,
                                                  on_change=self.handle_page_change)
        self.record_selector.visible = True
        self.record_selector.set_data(
            total_rows=len(self.rows_all),
            page_size=self.page_size)

    def handle_page_change(self, page, start_row, end_row):
        self.grid_scroller.scroll_offset = 0
        self.rebuild()

    def rows_page(self):
        if self.page_size <= 0 or not self.record_selector:
            return self.rows_sorted
        if not self.record_selector.visible:
            return self.rows_sorted
        rs    = self.record_selector
        start = rs.start_row() - 1
        end   = rs.end_row()
        return self.rows_sorted[start:end]

    # ══════════════════════════════════════════════════════════════
    # REBUILD — the single orchestrator
    # ══════════════════════════════════════════════════════════════

    def rebuild(self):
        self.rows_sorted = self.apply_sort()
        self.detect_col_alignment()
        self.detect_col_precision(self.rows_sorted)
        page = self.rows_page()
        self.measure_columns(page)
        self.calc_render_gap()
        self.composite(page)

    # ══════════════════════════════════════════════════════════════
    # SORT
    # ══════════════════════════════════════════════════════════════

    def apply_sort(self):
        if self.sort_col < 0:
            return self.rows_all
        return sorted(
            self.rows_all,
            key=lambda r: SortHelper.sort_key(r, self.sort_col),
            reverse=not self.sort_asc,
        )

    def toggle_sort(self, col_idx):
        if col_idx == self.sort_col:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_col = col_idx
            self.sort_asc = True
        if self.record_selector and self.record_selector.visible:
            self.record_selector.go_to_page(1)
        self.rebuild()

    # ══════════════════════════════════════════════════════════════
    # COLUMN ANALYSIS
    # ══════════════════════════════════════════════════════════════

    def detect_col_alignment(self):
        """Right-align columns where majority of non-placeholder values are numeric."""
        num_cols        = len(self.columns)
        self.col_aligns = ['l'] * num_cols
        for i in range(num_cols):
            numeric_count = 0
            total_count   = 0
            for row in self.rows_all:
                if i >= len(row):
                    continue
                val = row[i]
                if val is None or val == "—" or val == "":
                    continue
                total_count += 1
                if CellFormatter.is_numeric(val):
                    numeric_count += 1
            if total_count > 0 and numeric_count / total_count > 0.5:
                self.col_aligns[i] = 'r'

    def detect_col_precision(self, rows):
        """Find the max decimal places needed per numeric column."""
        num_cols           = len(self.columns)
        self.col_precision = [-1] * num_cols
        for i in range(num_cols):
            if self.col_aligns[i] != 'r':
                continue
            max_dec    = 0
            has_sci    = False
            has_normal = False
            for row in rows:
                if i >= len(row):
                    continue
                val = row[i]
                if not CellFormatter.is_numeric(val):
                    continue
                val = CellFormatter.to_number(val)
                if CellFormatter.needs_scientific(val):
                    has_sci = True
                    continue
                has_normal = True
                max_dec    = max(max_dec, CellFormatter.natural_decimals(val))
            if has_normal:
                self.col_precision[i] = min(max_dec, 6)
            elif has_sci:
                self.col_precision[i] = -2

    # ══════════════════════════════════════════════════════════════
    # MEASURE COLUMNS
    # ══════════════════════════════════════════════════════════════

    def measure_columns(self, rows):
        num_cols        = len(self.columns)
        self.col_widths = [0] * num_cols
        for i in range(num_cols):
            self.col_widths[i] = self.font.size(self.header_label(i))[0]
        for row in rows:
            for i in range(min(num_cols, len(row))):
                text = self.format_cell(row[i], i)
                w    = self.font.size(text)[0]
                self.col_widths[i] = max(self.col_widths[i], w)
        for i, cap in self.col_max.items():
            if i < num_cols:
                self.col_widths[i] = min(self.col_widths[i], cap)

    def calc_render_gap(self):
        """Distribute extra width as spacing between columns."""
        rect = self.grid_scroller.rect if self.grid_scroller.rect else self.rect
        if not self.columns or not rect:
            self.render_gap = self.gap
            return
        content_w       = sum(self.col_widths)
        gap_count       = max(1, len(self.columns) - 1)
        available       = rect.width
        extra           = available - content_w
        self.render_gap = max(self.gap, extra // gap_count) if extra > 0 else self.gap
        self.render_gap = self.render_gap * .95

    def header_label(self, col_idx):
        name = str(self.columns[col_idx])
        if col_idx == self.sort_col:
            return name + (" ^" if self.sort_asc else " v")
        return name

    # ══════════════════════════════════════════════════════════════
    # CELL FORMATTING
    # ══════════════════════════════════════════════════════════════

    def format_cell(self, value, col_idx):
        if value is None:
            return "—"
        if CellFormatter.is_numeric(value):
            precision = self.col_precision[col_idx] if col_idx < len(self.col_precision) else -1
            return CellFormatter.format_number(CellFormatter.to_number(value), precision)
        return str(value)

    # ══════════════════════════════════════════════════════════════
    # HOVER — suppress hover brightening on the grid
    # ══════════════════════════════════════════════════════════════

    def resolve_bg(self):
        return self.color_bg

    # ══════════════════════════════════════════════════════════════
    # COMPOSITE — build surfaces, assign to child widgets
    # ══════════════════════════════════════════════════════════════

    def composite(self, rows):
        if not self.columns:
            self.grid_header.my_surface = None
            self.grid_body.my_surface   = None
            return
        self.row_height = self.font.get_height() + self.gap
        gap_total       = self.render_gap * max(0, len(self.columns) - 1)
        total_w         = sum(self.col_widths) + gap_total
        self.grid_header.my_surface = self.render_header(total_w)
        self.grid_body.my_surface   = self.render_rows(rows, total_w)

    # ── Header ────────────────────────────────────────────────────

    def render_header(self, total_w):
        surf = pygame.Surface((total_w, self.row_height), pygame.SRCALPHA)
        self.header_col_rects = []
        x = 0
        for i in range(len(self.columns)):
            label    = self.header_label(i)
            txt_surf = self.font.render(label, True, self.color_header)
            col_w    = self.col_widths[i]
            tx       = self.align_x(x, col_w, txt_surf.get_width(), self.col_aligns[i])
            surf.blit(txt_surf, (tx, 0))
            self.header_col_rects.append(pygame.Rect(x, 0, col_w, self.row_height))
            x += col_w + self.render_gap
        return surf

    # ── Data Rows ─────────────────────────────────────────────────

    def render_rows(self, rows, total_w):
        total_h = self.row_height * len(rows)
        if total_h <= 0:
            return None
        surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        y = 0
        for row_idx, row in enumerate(rows):
            bg = self.color_row_odd if row_idx % 2 else self.color_row_even
            if bg:
                pygame.draw.rect(surf, bg, pygame.Rect(0, y, total_w, self.row_height))
            self.render_one_row(surf, row, y)
            y += self.row_height
        return surf

    def render_one_row(self, surf, row, y):
        x = 0
        for i in range(len(self.columns)):
            val      = row[i] if i < len(row) else ""
            text     = self.format_cell(val, i)
            col_w    = self.col_widths[i]
            txt_surf = self.font.render(text, True, self.color_txt)
            tx       = self.align_x(x, col_w, txt_surf.get_width(), self.col_aligns[i])
            surf.blit(txt_surf, (tx, y))
            x += col_w + self.render_gap

    @staticmethod
    def align_x(x, col_w, text_w, align):
        if align == 'r':
            return x + col_w - text_w
        return x

    # ══════════════════════════════════════════════════════════════
    # CLICK HANDLING
    # ══════════════════════════════════════════════════════════════

    def process_click(self):
        if not self.rect:
            return super().process_click()
        mx, my = pygame.mouse.get_pos()
        if self.hit_test_header(mx, my):
            return True
        if self.row_click_callback:
            return self.hit_test_row(mx, my)
        return super().process_click()

    def hit_test_header(self, mx, my):
        hr = self.grid_header.rect
        if not hr or not hr.collidepoint(mx, my):
            return False
        local_x = mx - hr.left
        local_y = my - hr.top
        for i, rect in enumerate(self.header_col_rects):
            if rect.collidepoint(local_x, local_y):
                self.toggle_sort(i)
                return True
        return False

    def hit_test_row(self, mx, my):
        sr = self.grid_scroller.rect
        if not sr or not sr.collidepoint(mx, my):
            return False
        if self.row_height <= 0:
            return False
        local_y    = my - self.grid_body.rect.top
        row_idx    = int(local_y // self.row_height)
        rows       = self.rows_page()
        if row_idx < 0 or row_idx >= len(rows):
            return False
        self.fire_row_click(row_idx)
        return True

    def fire_row_click(self, row_idx):
        rows = self.rows_page()
        row  = rows[row_idx]
        data = self.build_row_dict(row)
        val  = self.extract_click_value(data, row)
        self.row_click_callback(val)

    def build_row_dict(self, row):
        result = {}
        for i, col_name in enumerate(self.columns):
            result[col_name] = row[i] if i < len(row) else None
        return result

    def extract_click_value(self, data, row):
        col = self.row_click_column
        if col is None:
            return data
        if isinstance(col, int):
            if col < 0 or col >= len(self.columns):
                raise ValueError(
                    f"Column index {col} out of range. "
                    f"Grid has {len(self.columns)} columns: {', '.join(str(c) for c in self.columns)}"
                )
            return row[col] if col < len(row) else None
        if isinstance(col, str):
            if col not in data:
                raise ValueError(
                    f'Column "{col}" not found. '
                    f"Available columns: {', '.join(str(c) for c in self.columns)}"
                )
            return data[col]
        raise TypeError(f"column must be None, int, or str — got {type(col).__name__}")


# ══════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════

class RowClickValidator:
    """Validates on_row_click callback at registration time."""

    @staticmethod
    def validate_callback(callback):
        if not callable(callback):
            raise TypeError(
                f"on_row_click expects a callable, got {type(callback).__name__}. "
                f"Usage: grid.on_row_click(my_handler) or grid.on_row_click(my_handler, 'column_name')"
            )
        param_count = RowClickValidator.count_params(callback)
        if param_count != 1:
            raise ValueError(
                f"on_row_click callback must accept exactly 1 parameter, got {param_count}. "
                f"Your callback receives either a dict (full row) or a single value (if column specified)."
            )

    @staticmethod
    def count_params(callback):
        try:
            sig    = inspect.signature(callback)
            params = [p for p in sig.parameters.values()
                      if p.default is inspect.Parameter.empty
                      and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)]
            return len(params)
        except (ValueError, TypeError):
            return -1


# ══════════════════════════════════════════════════════════════════
# NORMALIZER
# ══════════════════════════════════════════════════════════════════

class Normalizer:
    """Converts any of the three input formats to (columns, rows)."""

    @staticmethod
    def normalize(data, columns):
        if isinstance(data, dict):    return Normalizer.from_dict_of_lists(data)
        if not data:                  return (columns or [], [])
        if isinstance(data[0], dict): return Normalizer.from_list_of_dicts(data)
        return Normalizer.from_list_of_lists(data, columns)

    @staticmethod
    def from_dict_of_lists(data):
        cols   = list(data.keys())
        length = max((len(v) for v in data.values()), default=0)
        rows   = []
        for i in range(length):
            rows.append([data[c][i] if i < len(data[c]) else None for c in cols])
        return (cols, rows)

    @staticmethod
    def from_list_of_dicts(data):
        cols = list(data[0].keys())
        rows = [[row.get(c) for c in cols] for row in data]
        return (cols, rows)

    @staticmethod
    def from_list_of_lists(data, columns):
        if columns:
            return (columns, data)
        if len(data) > 1:
            return (data[0], data[1:])
        return (data[0], [])


# ══════════════════════════════════════════════════════════════════
# SORT HELPER
# ══════════════════════════════════════════════════════════════════

class SortHelper:
    """Provides a stable sort key that handles None, numbers, and strings."""


    @staticmethod
    def sort_key(row, col):
        val = row[col] if col < len(row) else None
        if val is None:                   return (2, "")
        if CellFormatter.is_numeric(val): return (0, CellFormatter.to_number(val))
        return (1, str(val).lower())


# ══════════════════════════════════════════════════════════════════
# CELL FORMATTER
# ══════════════════════════════════════════════════════════════════

class CellFormatter:
    """Formats cell values for display with decimal alignment support."""

    @staticmethod
    def is_numeric(value):
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def to_number(value):
        if isinstance(value, (int, float)):
            return value
        return float(value)

    @staticmethod
    def needs_scientific(value):
        if value == 0:
            return False
        return abs(value) < 1e-4 or abs(value) >= 1e8

    @staticmethod
    def natural_decimals(value):
        if isinstance(value, int):
            return 0
        if value == int(value):
            return 0
        text = f"{value:.6f}".rstrip('0')
        if '.' not in text:
            return 0
        return len(text.split('.')[1])

    @staticmethod
    def format_number(value, precision=-1):
        if CellFormatter.needs_scientific(value):
            return f"{value:.2e}"
        if precision < 0:
            return CellFormatter.format_raw(value)
        if precision == 0:
            return f"{int(round(value)):,}"
        return f"{value:,.{precision}f}"

    @staticmethod
    def format_raw(value):
        if value == 0:
            return "0"
        formatted = f"{value:.6f}".rstrip('0').rstrip('.')
        if '.' in formatted and len(formatted.split('.')[1]) > 4:
            return f"{value:.2e}"
        return formatted