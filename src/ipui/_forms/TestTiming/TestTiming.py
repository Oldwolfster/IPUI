# Test_Timing.py  New: timing observation harness — tab tier
from ipui import *


class TestTimingTab(_BaseTab):
    """
    Tab-tier counterpart to TestTiming form.
    Pane builder + tab hooks all instrument timing.
    """

    BINDINGS = {
        "lbl_form_setup"        : {"property": "text", "compute": "fmt_form_setup"      , "triggers": ["form_setup_count"     ]},
        "lbl_form_activated"    : {"property": "text", "compute": "fmt_form_activated"  , "triggers": ["form_activated_count" ]},
        "lbl_tab_setup"         : {"property": "text", "compute": "fmt_tab_setup"       , "triggers": ["tab_setup_count"      ]},
        "lbl_tab_activated"     : {"property": "text", "compute": "fmt_tab_activated"   , "triggers": ["tab_activated_count"  ]},
        "lbl_pane_built"        : {"property": "text", "compute": "fmt_pane_built"      , "triggers": ["pane_built_count"     ]},
    }

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDER
    # ══════════════════════════════════════════════════════════════

    def test_timing(self, parent):
        print("[PANE] test_timing builder ran")
        self.bump("pane_built_count")

        Title   (parent, "Lifecycle Timing Counters", glow=True)
        Spacer  (parent)

        card = Card(parent)
        Heading (card, "Form-tier hooks")
        Body    (card, "form.ip_setup       called: 0", name="lbl_form_setup"     )
        Body    (card, "form.ip_activated   called: 0", name="lbl_form_activated" )

        Spacer  (parent)
        card = Card(parent)
        Heading (card, "Tab-tier hooks")
        Body    (card, "tab.ip_setup        called: 0", name="lbl_tab_setup"      )
        Body    (card, "tab.ip_activated    called: 0", name="lbl_tab_activated"  )

        Spacer  (parent)
        card = Card(parent)
        Heading (card, "Pane builder")
        Body    (card, "test_timing()       called: 0", name="lbl_pane_built"     )

        Spacer  (parent)
        card = Card(parent)
        Heading (card, "Expected on cold boot")
        Body    (card, "Each counter SHOULD read 1.")
        Body    (card, "If any reads 2 — that hook fires twice.")

    # ══════════════════════════════════════════════════════════════
    # TAB-TIER HOOKS
    # ══════════════════════════════════════════════════════════════

    def ip_setup(self, ip):
        print("[TAB ] ip_setup")
        self.bump("tab_setup_count")

    def ip_activated(self, ip):
        print("[TAB ] ip_activated")
        self.bump("tab_activated_count")

    # ══════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════

    def bump(self, key):
        current = self.form.pipeline_read(key) or 0
        self.form.pipeline_set(key, current + 1)

    # ══════════════════════════════════════════════════════════════
    # Compute formatters for BINDINGS
    # ══════════════════════════════════════════════════════════════

    def fmt_form_setup     (self, form_setup_count    ): return f"form.ip_setup       called: {form_setup_count    }"
    def fmt_form_activated (self, form_activated_count): return f"form.ip_activated   called: {form_activated_count}"
    def fmt_tab_setup      (self, tab_setup_count     ): return f"tab.ip_setup        called: {tab_setup_count     }"
    def fmt_tab_activated  (self, tab_activated_count ): return f"tab.ip_activated    called: {tab_activated_count }"
    def fmt_pane_built     (self, pane_built_count    ): return f"test_timing()       called: {pane_built_count    }"