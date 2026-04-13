# IPContext.py  NEW: Frame context for ip_think / ip_draw / ip_draw_hud
#
# ╔══════════════════════════════════════════════════════════════╗
# ║  DRAW IN ip_think AT YOUR OWN RISK                         ║
# ║                                                             ║
# ║  ip_think    = THINK.  State, math, physics, logic.        ║
# ║  ip_draw  = Draw your world BEFORE the UI paints.     ║
# ║  ip_draw_hud = Draw overlays AFTER the UI paints.        ║
# ║                                                             ║
# ║  The surface is on ctx for all three, but ip_think runs    ║
# ║  before the screen is cleared. Anything you draw there     ║
# ║  gets painted over. You have been warned.                  ║
# ╚══════════════════════════════════════════════════════════════╝


class IPContext:
    """Per-frame context passed to every ip_ lifecycle hook.

    Attributes:
        dt         (float):  Seconds since last frame.
        fps        (int):    Current frames per second.
        frame_id   (int):    Monotonically increasing frame counter.
        surface    (Surface): The pygame draw surface.
        events     (list):   All pygame events this frame.
        unhandled  (list):   Events the UI did not consume.
    """

    def __init__(self):
        self.___current_root = None
        self.dt         = 0.0
        self.fps        = 0
        self.frame_id   = 0
        self.surface    = None
        self.events     = []
        self.unhandled  = []
