# _basePane.py  Update: ip_ lifecycle hooks and IP_LIFECYCLE policy
from ipui.utils.EZ import EZ


class _basePane:
    """Base class for pane builders.
    Gives self.form to all methods.
    Override initialize() for one-time setup.

    ══════════════════════════════════════════════════════════════
    LIFECYCLE HOOKS — override these in your Pane subclass
    ══════════════════════════════════════════════════════════════
    ip_think(ctx)      — Every frame. State, math, physics, logic.
    ip_renderpre(ctx)  — Before UI draws. Game world, backgrounds.
    ip_renderpost(ctx) — After UI draws. Custom cursors, overlays.

    ctx fields:
        ctx.dt         — Seconds since last frame.
        ctx.fps        — Current FPS.
        ctx.frame_id   — Monotonically increasing frame counter.
        ctx.surface    — The pygame draw surface.
        ctx.events     — All pygame events this frame.
        ctx.unhandled  — Events the UI did not consume.

    DRAW IN ip_think AT YOUR OWN RISK.
    ══════════════════════════════════════════════════════════════

    IP_LIFECYCLE controls what happens when the tab is not active:
        "persist"  — ip_think keeps running (default)
        "pause"    — ip_think stops, resumes on return
        "restart"  — ip_think stops, initialize() re-runs on return
        "kill"     — pane destroyed, rebuilt on return
    ══════════════════════════════════════════════════════════════
    """

    IP_LIFECYCLE = "persist"

    # _basePane.py method: __init_subclass__  NEW: guard against __init__ override
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__:
            raise TypeError(f"{cls.__name__}: Don't override __init__, use initialize() instead")

    def __init__(self, form):
        self.form = form
        self.register_derives()
        self.initialize()


# _basePane.py method: register_derives  Update: use EZ.err

    def register_derives(self):
        derives = getattr(self.__class__, 'DECLARATION_UPDATES', None)
        if not derives:
            return
        for control_name, entry in derives.items():
            method_name = entry["compute"]
            method      = getattr(self, method_name, None)
            if method is None:
                EZ.err(
                    f"{self.__class__.__name__}.DECLARATION_UPDATES references '{method_name}'. "
                    f"Create {method_name}() on {self.__class__.__name__} "
                    f"to calculate the value for {control_name}."
                )
            self.form.register_derive(
                control_name = control_name,
                property     = entry["property"],
                compute      = method,
                triggers     = entry["triggers"],
            )
        #self.form.pipeline.fire_all_derives()

    def initialize(self): #If writing documentation DOCUMENT THIS IOC HOOK
        pass

    def swap_pane(self, index, builder, *args, **kwargs):
        def do_swap():
            self.form.set_pane(index, builder)
        return do_swap

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS — override in your pane
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ctx):
        """Per-frame logic. Override for state, physics, AI."""
        pass

    def ip_renderpre(self, ctx):
        """Draw before UI. Override for game worlds, backgrounds."""
        pass

    def ip_renderpost(self, ctx):
        """Draw after UI. Override for overlays, cursors, effects."""
        pass
