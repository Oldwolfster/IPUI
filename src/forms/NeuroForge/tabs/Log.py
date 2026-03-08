# Log.py  NEW FILE  (replaces frmLog.py — _basePane migration)

from ipui.engine.Log      import Logger
from ipui.engine.MgrColor  import MgrColor
from ipui.engine._BasePane import _basePane
from ipui.widgets.Button   import Button
from ipui.widgets.Row      import Row, CardCol
from ipui.widgets.Label     import Title, Body
from ipui.widgets.TextBox  import TextBox


class EZ_Pane(_basePane):
    """Log tab — searchable, filterable log viewer."""

    # ══════════════════════════════════════════════════════════════
    # TAB PANE  (name must match string in FormNeuroForge.tab_data)
    # ══════════════════════════════════════════════════════════════

    def log(self, parent) -> None:
        """Sinmngle pane — log viewer with filters and severity toggles."""
        Title(parent, "Log", glow=True)
        self.build_filters(parent)
        self.build_list(parent)
        if Logger.instance:
            Logger.instance.ui_callback = lambda: self.refresh()  # TODO: NIP — Logger callback
        self.refresh()

    # ══════════════════════════════════════════════════════════════
    # FILTERS
    # ══════════════════════════════════════════════════════════════

    def build_filters(self, parent) -> None:
        """Search box, category filter, and severity toggle buttons."""
        self.form.log_severities = set(Logger.SEVERITIES)
        row = Row(parent)

        TextBox(row,
            placeholder = "Search messages...",
            name        = "txt_log_keyword",
            width_flex  = True,
            on_change   = lambda text: self.refresh(),  # TODO: NIP — TextBox callback
        )
        TextBox(row,
            placeholder = "Filter category...",
            name        = "txt_log_category",
            on_change   = lambda text: self.refresh(),  # TODO: NIP — TextBox callback
        )

        for sev in Logger.SEVERITIES:
            btn = Button(row, sev[0], name=f"btn_sev_{sev}")
            btn.on_click_me(self.make_severity_toggle(sev))

    def make_severity_toggle(self, severity: str) -> callable:
        """Return a zero-arg callable that toggles one severity filter."""
        def do_toggle():
            self.toggle_severity(severity)
        return do_toggle

    # ══════════════════════════════════════════════════════════════
    # LOG DISPLAY
    # ══════════════════════════════════════════════════════════════

    def build_list(self, parent) -> None:
        """Scrollable log body."""
        sub = CardCol(parent, height_flex=True, scrollable=True)
        Body(sub, "(no log entries)", name="lbl_log")

    # ══════════════════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════════════════

    def toggle_severity(self, severity: str) -> None:
        """Toggle a severity filter on/off and refresh the log."""
        form = self.form
        if severity in form.log_severities:
            form.log_severities.discard(severity)
        else:
            form.log_severities.add(severity)
        btn   = form.widgets.get(f"btn_sev_{severity}")
        style = "sunken" if severity not in form.log_severities else "raised"
        if btn:
            MgrColor.apply_bevel(btn, style)
        self.refresh()

    def refresh(self) -> None:
        """Re-filter and update the log display label."""
        if not Logger.instance:
            return
        form       = self.form
        keyword    = form.widgets.get("txt_log_keyword")
        cat_filter = form.widgets.get("txt_log_category")
        keyword    = keyword.text    if keyword    else ""
        cat_filter = cat_filter.text if cat_filter else ""
        severities = getattr(form, 'log_severities', None)

        entries = Logger.instance.filtered(keyword, cat_filter, severities)
        text    = "\n".join(e.display_text() for e in entries) if entries else "(no matching entries)"

        lbl = form.widgets.get("lbl_log")
        if lbl:
            lbl.set_text(text)