# Log.py  NEW FILE  — Baseball "Log" tab: Pipe's top strip (inert) over 3 read-only log panes, left pane filterable
import re
from ipui import *
from ipui._forms.Baseball.BbDB import BbDB


class Log(_BaseTab):
    """Log viewer. Top strip mirrors Pipe for visual consistency (mostly disabled).
       Bottom = three scrollable read-only panes; the left shows BbDB.pipe_log_text,
       filterable by a HH:MM:SS time range and a keyword search."""

    def ip_setup_early(self, ip):
        self.private_start   = ""
        self.private_end     = ""
        self.private_search  = ""
        self.private_log_len = -1          # forces first refresh


    def ip_think(self, ip):
        n = len(BbDB.pipe_log_text or "")
        if n == self.private_log_len: return
        self.private_log_len = n
        self.refresh()
    # ════════════════════════════════════════════════
    # Widget Tree                                  ═══
    # ════════════════════════════════════════════════
    def all_in_one(self, parent):
        self.top_section(parent)
        self.bottom_section(parent)

    # ---- top: identical look to Pipe (inert chrome) + corner log ----
    def top_section(self, parent):
        row   = Row(parent)
        frame = CardCol(row, pad=2, flex_width=3.369)
        self.top_left_section(frame)
        log   = CardCol(row, flex_width=1.669, pad=0)
        Detail(Card(log, scroll_v=True, pad_y=0), BbDB.pipe_log_text or "Greetings earthling!")

    def top_left_section(self, frame):
        header = Card(frame , pad=3)
        header = Plate(header, pad=5)
        header = Plate(header, pad=5)
        header = Row(header)
        Title(header, "Log", glow=True)
        Spacer(header)
        Button(header, "Run All", color_bg=Style.COLOR_BUTTON_CTA, enabled=False)
        TextBox(header, initial_value=self.private_start, name="txt_log_start", placeholder="HH:MM:SS", on_change=self.set_start)
        Body(header, "to:")
        TextBox(header, initial_value=self.private_end, name="txt_log_end", placeholder="HH:MM:SS", on_change=self.set_end)
        Spacer(header)
        Button(header, "Train XGB", enabled=False)
        Button(header, "Filter", color_bg=Style.COLOR_BUTTON_CTA, on_click=self.refresh)   # the one live button
        Button(header, "Details", enabled=False)
        Button(header, "Run TS", enabled=False)
        Button(header, "Phoenix", enabled=False, color_bg=Style.COLOR_BUTTON_DANGER)

    # ---- bottom: slim controls row + three panes ----
    def bottom_section(self, parent):
        self.controls_row(parent)
        self.three_panes(parent)

    def controls_row(self, parent):
        row = Row(Plate(parent, pad=4))
        Body(row, "Search:")
        TextBox(row, initial_value=self.private_search, name="txt_log_search",
                placeholder="keyword...", flex_width=1, on_change=self.set_search)
        Button(row, "First", on_click=self.fill_first)      # start = earliest log time
        Button(row, "Clear", on_click=self.clear_filters)
        Spacer(row)
        Body(row, "", name="lbl_log_count")

    def three_panes(self, parent):
        frame = CardRow(parent, flex_height=1, pad=2)
        self.log_pane(frame, "log_main",  "Log")
        self.log_pane(frame, "log_mid",   "(reserved)")
        self.log_pane(frame, "log_right", "(reserved)")

    def log_pane(self, parent, name, label):
        col  = CardCol(parent, flex_width=1, flex_height=1, pad=2)
        head = Plate(col, pad=5)
        Title(head, label, text_align='c')
        body = Plate(col, scroll_v=True, flex_height=1, pad=3)
        Detail(body, "", name=name)

    # ════════════════════════════════════════════════
    # Filtering                                    ═══
    # ════════════════════════════════════════════════
    def lines(self):
        """All log lines, newest first (as BbDB stores them)."""
        return (BbDB.pipe_log_text or "").splitlines()

    def line_time(self, line):
        """'[HH:MM:SS] ...' -> 'HH:MM:SS', else '' (lines without a leading stamp)."""
        if len(line) >= 10 and line[0] == "[" and line[9] == "]": return line[1:9]
        return ""

    def norm_time(self, raw):
        """Pull a zero-padded HH:MM:SS out of arbitrary text (e.g. a pasted log line); '' if none."""
        m = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", raw or "")
        if not m: return ""
        return f"{int(m.group(1)):02d}:{m.group(2)}:{m.group(3)}"

    def passes(self, line):
        """True if a line clears the active time-range and keyword filters."""
        t = self.line_time(line)
        if self.private_start and (not t or t < self.private_start): return False
        if self.private_end   and (not t or t > self.private_end):   return False
        if self.private_search and self.private_search.lower() not in line.lower(): return False
        return True

    def refresh(self, *_):
        """Re-filter the log and push the result into the left pane + count label."""
        all_lines = self.lines()
        matched   = [ln for ln in all_lines if self.passes(ln)]
        body      = "\n".join(matched) if matched else "(no matching log lines)"
        self.set_widget_text("log_main", body)
        self.set_widget_text("lbl_log_count", f"{len(matched)} of {len(all_lines)}")

    # ════════════════════════════════════════════════
    # Filter inputs                                ═══
    # ════════════════════════════════════════════════
    def set_start(self, text):  self.private_start  = self.norm_time(text); self.refresh()
    def set_end(self, text):    self.private_end    = self.norm_time(text); self.refresh()
    def set_search(self, text): self.private_search = text or "";           self.refresh()

    def fill_first(self):
        """Populate the start box with the earliest log timestamp."""
        times = [t for t in (self.line_time(ln) for ln in self.lines()) if t]
        if not times: return
        self.private_start = min(times)
        self.set_widget_text("txt_log_start", self.private_start)
        self.refresh()

    def clear_filters(self):
        """Reset all three filters and show everything."""
        self.private_start = self.private_end = self.private_search = ""
        for n in ("txt_log_start", "txt_log_end", "txt_log_search"): self.set_widget_text(n, "")
        self.refresh()

    def set_widget_text(self, name, text):
        """Safe set_text by registry name (no-op if the widget isn't built yet)."""
        w = self.form.widgets.get(name)
        if w is not None: w.set_text(text)

