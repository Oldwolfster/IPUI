# TooltipBaseballTable.py  class: TooltipBaseballTable  NEW: huge-tooltip for baseball schema cards

from ipui.engine._BaseHugeTooltip import _BaseHugeTooltip
from ipui._forms.Baseball.BB     import BB


class TooltipBaseballTable(_BaseHugeTooltip):

    def __init__(self, tbl_name):
        super().__init__()
        self.tbl_name = tbl_name


    def header_text(self):
        return f"{self.tbl_name}:"


    def content_to_display(self):
        info = self.build_info_lines()
        cols = self.build_column_lines()
        return [info + [""] + cols]


    # ══════════════════════════════════════════════════════════════
    # SECTION 1 — schema info (layer, rows, cols, range)
    # ══════════════════════════════════════════════════════════════

    def build_info_lines(self):
        layer        = self.find_layer()
        rows         = BB.row_count(self.tbl_name)
        cols         = BB.col_count(self.tbl_name)
        mn, mx       = BB.date_range(self.tbl_name)
        rng_text     = f"{mn}  →  {mx}" if mn is not None else "—"
        return [
            f"Layer:      {layer}",
            f"Rows:       {rows:,}",
            f"Columns:    {cols}",
            f"GD Range:   {rng_text}",
        ]


    # ══════════════════════════════════════════════════════════════
    # SECTION 2 — column list (raw declarations preserved with V-align)
    # GD is auto-injected by the materializer, not in _tables, so we
    # prepend it explicitly for visibility.
    # ══════════════════════════════════════════════════════════════

    def build_column_lines(self):
        rows  = BB.query("SELECT col FROM _tables WHERE tbl = ? ORDER BY id", (self.tbl_name,))
        lines = ["Columns:", "  PK GD                                          INTEGER  (auto)"]
        if self.is_feet_layer():
            lines.append("  PK TS                                          INTEGER  (auto)")
        for (raw_col,) in rows:
            lines.append(f"  {raw_col}")
        return lines


    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def find_layer(self):
        for layer, tbls in BB.LAYERS.items():
            if self.tbl_name in tbls:
                return layer
        return "?"

    def is_feet_layer(self):
        return self.find_layer() == "feet"