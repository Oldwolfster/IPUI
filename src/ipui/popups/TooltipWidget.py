from ipui.engine._BaseHugeTooltip import _BaseHugeTooltip
from ipui.Style import Style


class TooltipWidget(_BaseHugeTooltip):
    """Hover tooltip that shows structured docstring fields and full source code."""

    def __init__(self, widget_name, entry):
        super().__init__()
        self.widget_name = widget_name
        self.entry       = entry
        self.font_body   = Style.FONT_DETAIL

    def header_text(self):
        return f"{self.widget_name}  ({self.entry.get('lines', '?')} lines)"

    def content_to_display(self):
        e     = self.entry
        lines = []

        if e.get("desc"):        lines.append(f"  {e['desc']}")
        if e.get("when_to_use"): lines.append(f"  When: {e['when_to_use']}")
        if e.get("best_for"):    lines.append(f"  Best: {e['best_for']}")
        if e.get("example"):     lines.append(f"  Ex:   {e['example']}")
        if e.get("api"):         lines.append(f"  API:  {e['api']}")

        lines.append("")
        lines.append("─── Source ───")
        lines.append("")

        source = e.get("source", "")
        for src_line in source.split("\n"):
            lines.append(src_line)

        return [lines]