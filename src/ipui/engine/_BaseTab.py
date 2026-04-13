from ipui.utils.EZ import EZ
from ipui.engine.IPUI import IPUI

class _BaseTab:
    """Base class for pane builders.
    Gives self.form to all methods.
    Override ip_setup_pane() for one-time setup.

    ══════════════════════════════════════════════════════════════
    LIFECYCLE HOOKS — override these in your Pane subclass
    all run when pane is visible - THINK_ALWAYS=True makes think run regardless.
    ══════════════════════════════════════════════════════════════
    ip_think(ctx)      — Recommended uses. State, math, physics, logic, etc.
    ip_draw(ctx)       — Before UI widget tree draws. Game world, backgrounds.
    ip_draw_hud(ctx)   — After UI widget tree draws. Custom cursors, overlays, scores.

    ctx fields:
        ctx.dt         — Seconds since last frame.
        ctx.fps        — Current FPS.
        ctx.frame_id   — Monotonically increasing frame counter.
        ctx.surface    — The pygame draw surface.
        ctx.events     — All pygame events this frame.
        ctx.unhandled  — Events the UI did not consume.

    DRAW IN ip_think AT YOUR OWN RISK.(feels a bit melodramatic)
    """
    THINK_ALWAYS = False

    #  guard against __init__ override
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__:
            raise TypeError(f"{cls.__name__}: Don't override __init__, use ip_setup_pane() instead")

    def __init__(self, form):
        self.form = form
        self.ip = IPUI.ip
        self.register_derives()
        self.ip_setup_pane()

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

    def ip_setup_pane(self):
        pass

    def swap_pane(self, index, builder, *args, **kwargs):
        def do_swap():
            self.form.set_pane(index, builder)
        return do_swap

    def hide_extra_panes(self, keep_count):
        for pane in self.form.tab_strip.panes[keep_count:]:
            pane.visible = False

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS — override in your pane
    # ══════════════════════════════════════════════════════════════

    def ip_think    (self, ctx):
        """Per-frame logic. Override for state, physics, AI."""
        pass

    def ip_draw     (self, ctx):
        """Draw before UI. Override for game worlds, backgrounds."""
        pass

    def ip_draw_hud (self, ctx):
        """Draw after UI. Override for overlays, cursors, effects."""
        pass


