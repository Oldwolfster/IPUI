# Optimizer.py  module: Optimizer  Update: real bench scenes + multi-sample timing
# Three scenes, 5 samples each, reports min/med/max ms.
# For comparing engine changes — run before, change, run after, eyeball deltas.

from time      import perf_counter
from statistics import median
from ipui      import *
from ipui.widgets.Label import Label


class Optimizer(_BaseTab):

    TAB_LAYOUT = {
        "Optimizer": [
            ("bench_flat_wall" , 1),
            ("bench_deep_tree" , 1),
            ("bench_wrap_storm", 1),
            ("bench_target"    , 3),
        ],
    }

    PRESETS_FLAT  = [10, 50, 250, 1000, 5000]
    PRESETS_TREE  = [10, 50, 250, 1000, 5000]
    PRESETS_WRAP  = [10, 25, 50 , 100 , 1000 ]
    TARGET_PANE   = 3
    SAMPLES       = 5

    WRAP_TEXT     = ("The quick brown fox jumps over the lazy dog. "
                     "Pack my box with five dozen liquor jugs. "
                     "How vexingly quick daft zebras jump. "
                     "Sphinx of black quartz, judge my vow. ")

    # ══════════════════════════════════════════════════════════════
    # SETUP
    # ══════════════════════════════════════════════════════════════

    def ip_setup_early(self, ip):
        self.results_flat_wall  = []   # list of (n, times_ms_list, note)
        self.results_deep_tree  = []
        self.results_wrap_storm = []
        self.lbl_status_flat    = None
        self.lbl_status_tree    = None
        self.lbl_status_wrap    = None
        self.log_flat           = None
        self.log_tree           = None
        self.log_wrap           = None
        self.txt_n_flat         = None
        self.txt_n_tree         = None
        self.txt_n_wrap         = None
        self.txt_note_flat      = None
        self.txt_note_tree      = None
        self.txt_note_wrap      = None

    # ══════════════════════════════════════════════════════════════
    # PANE: Flat Wall controls
    # ══════════════════════════════════════════════════════════════

    def bench_flat_wall(self, parent):
        Title( parent, "Flat Wall", glow=True)
        Body ( parent, "N stacked Labels in a Card. Per-widget overhead.")
        Body ( parent, "Layout & render should grow O(N).")

        self.build_preset_row(parent, self.PRESETS_FLAT, self.run_flat_wall)
        self.txt_n_flat, self.txt_note_flat = self.build_custom_row(parent, self.run_flat_wall)
        self.lbl_status_flat = Body(parent, "idle")
        self.log_flat        = Card(parent, scroll_v=True, flex_height=1)
        self.replay_log(self.log_flat, self.results_flat_wall)

    # ══════════════════════════════════════════════════════════════
    # PANE: Deep Tree controls
    # ══════════════════════════════════════════════════════════════

    def bench_deep_tree(self, parent):
        Title( parent, "Wide Tree", glow=True)
        Body(parent, "N sibling Cards under one root. Single Button each.")
        Body ( parent, "Tests breadth scaling — O(N) widget construction.")

        self.build_preset_row(parent, self.PRESETS_TREE, self.run_deep_tree)
        self.txt_n_tree, self.txt_note_tree = self.build_custom_row(parent, self.run_deep_tree)
        self.lbl_status_tree = Body(parent, "idle")
        self.log_tree        = Card(parent, scroll_v=True, flex_height=1)
        self.replay_log(self.log_tree, self.results_deep_tree)

    # ══════════════════════════════════════════════════════════════
    # PANE: Wrap Storm controls
    # ══════════════════════════════════════════════════════════════

    def bench_wrap_storm(self, parent):
        Title( parent, "Wrap Storm", glow=True)
        Body ( parent, "N wrapped Body widgets. Forces Pass 2 (HardWrap).")
        Body ( parent, "Costs the full multi-pass orchestration.")

        self.build_preset_row(parent, self.PRESETS_WRAP, self.run_wrap_storm)
        self.txt_n_wrap, self.txt_note_wrap = self.build_custom_row(parent, self.run_wrap_storm)
        self.lbl_status_wrap = Body(parent, "idle")
        self.log_wrap        = Card(parent, scroll_v=True, flex_height=1)
        self.replay_log(self.log_wrap, self.results_wrap_storm)

    # ══════════════════════════════════════════════════════════════
    # PANE: Target — placeholder, gets swapped during runs
    # ══════════════════════════════════════════════════════════════

    def bench_target(self, parent):
        Body(parent, "Run a bench to see the scene here.", text_align=CENTER)

    # ══════════════════════════════════════════════════════════════
    # HELPERS — input rows, log, status
    # ══════════════════════════════════════════════════════════════

    def build_preset_row(self, parent, presets, on_run):
        row = Row(parent)
        Body(row, "N: ")
        for n in presets:
            Button(row, str(n), on_click=lambda n=n, h=on_run: h(n))

    def build_custom_row(self, parent, on_run):
        row      = Row(parent)
        Body    (row, "N: ")
        txt_n    = TextBox(row, placeholder="custom", flex_width=1,
                            on_submit=lambda v, h=on_run: self.run_from_textbox(v, h))
        txt_note = TextBox(row, placeholder="note",   flex_width=2)
        return txt_n, txt_note

    def run_from_textbox(self, value, on_run):
        try:
            n = int(value.strip())
        except (ValueError, AttributeError):
            return
        if n < 1: return
        on_run(n)

    def format_log_line(self, n, times_ms, note):
        lo  = min   (times_ms)
        md  = median(times_ms)
        hi  = max   (times_ms)
        return f"N={n:>5}   min={lo:7.2f}  med={md:7.2f}  max={hi:7.2f} ms   {note}"

    def replay_log(self, card, results):
        for n, times_ms, note in results:
            Body(card, self.format_log_line(n, times_ms, note))

    def append_result(self, kind, n, times_ms):
        if kind == "flat":
            note = self.txt_note_flat.text.strip()
            self.txt_note_flat.set_text("")
            self.results_flat_wall.append((n, times_ms, note))
            Body(self.log_flat, self.format_log_line(n, times_ms, note))
            self.lbl_status_flat.set_text(f"done — N={n}  med={median(times_ms):.2f} ms")
        elif kind == "tree":
            note = self.txt_note_tree.text.strip()
            self.txt_note_tree.set_text("")
            self.results_deep_tree.append((n, times_ms, note))
            Body(self.log_tree, self.format_log_line(n, times_ms, note))
            self.lbl_status_tree.set_text(f"done — depth={n}  med={median(times_ms):.2f} ms")
        elif kind == "wrap":
            note = self.txt_note_wrap.text.strip()
            self.txt_note_wrap.set_text("")
            self.results_wrap_storm.append((n, times_ms, note))
            Body(self.log_wrap, self.format_log_line(n, times_ms, note))
            self.lbl_status_wrap.set_text(f"done — N={n}  med={median(times_ms):.2f} ms")

    # ══════════════════════════════════════════════════════════════
    # RUNNERS — 5 samples each, set_pane wraps construction + layout
    # ══════════════════════════════════════════════════════════════

    def run_flat_wall(self, n):
        self.lbl_status_flat.set_text(f"running… N={n}")
        times_ms = []
        for _ in range(self.SAMPLES):
            t0 = perf_counter()
            self.form.set_pane(self.TARGET_PANE, self.scene_flat_wall, n=n)
            times_ms.append((perf_counter() - t0) * 1000.0)
        self.append_result("flat", n, times_ms)

    def run_deep_tree(self, n):
        self.lbl_status_tree.set_text(f"running… depth={n}")
        times_ms = []
        for _ in range(self.SAMPLES):
            t0 = perf_counter()
            self.form.set_pane(self.TARGET_PANE, self.scene_deep_tree, n=n)
            times_ms.append((perf_counter() - t0) * 1000.0)
        self.append_result("tree", n, times_ms)

    def run_wrap_storm(self, n):
        self.lbl_status_wrap.set_text(f"running… N={n}")
        times_ms = []
        for _ in range(self.SAMPLES):
            t0 = perf_counter()
            self.form.set_pane(self.TARGET_PANE, self.scene_wrap_storm, n=n)
            times_ms.append((perf_counter() - t0) * 1000.0)
        self.append_result("wrap", n, times_ms)

    # ══════════════════════════════════════════════════════════════
    # SCENES — pure layout cost, no scroll machinery
    # ══════════════════════════════════════════════════════════════

    def scene_flat_wall(self, parent, n=10):
        card = Card(parent)
        for i in range(n):
            Label(card, f"Item {i:04d}")

    def scene_deep_tree(self, parent, n=1):
        root = Card(parent)  # NEW
        for i in range(n):
            branch = Card(root)  # NEW  sibling Cards, not nested
            Button(branch, f"L{i}")  # NEW
        Label(root, f"nodes = {n}")  # NEW  (was: depth = {n})

    def scene_wrap_storm(self, parent, n=10):
        card = Card(parent)
        for _ in range(n):
            Body(card, self.WRAP_TEXT)