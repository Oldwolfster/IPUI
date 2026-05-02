# TestTiming.py  New: timing observation harness — form tier
from ipui import *


class TestTiming(_BaseForm):
    """
    Timing observation harness. First tab is 'Test Timing' (lives in Test_Timing.py).
    Every lifecycle hook prints to console AND increments a pipeline counter.
    The counters render live on screen so we can see double-fires at a glance.
    """

    TAB_LAYOUT = {
        "Greet" :["welcome"],
        "Test Timing"   : ["test_timing"],
        "Other"         : ["other"      ],
    }

    PIPELINE_DEFAULTS = {
        "form_setup_count"      : 0,
        "form_activated_count"  : 0,
        "tab_setup_count"       : 0,
        "tab_activated_count"   : 0,
        "pane_built_count"      : 0,
    }

    # ══════════════════════════════════════════════════════════════
    # FORM-TIER HOOKS
    # ══════════════════════════════════════════════════════════════

    def ip_setup(self, ip):
        print("[FORM] ip_setup")
        self.bump("form_setup_count")

    def ip_activated(self, ip):
        print("[FORM] ip_activated")
        self.bump("form_activated_count")

    # ══════════════════════════════════════════════════════════════
    # OTHER tab — just so the strip has more than one tab
    # ══════════════════════════════════════════════════════════════

    def other(self, parent):
        Title(parent, "Other Tab")
        Body (parent, "Switch back to 'Test Timing' to test warm-switch counts.")

    # ══════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════

    def bump(self, key):
        current = self.pipeline_read(key) or 0
        self.pipeline_set(key, current + 1)


if __name__ == "__main__": show(TestTiming)