from ipui.utils.EZ import EZ
from ipui.engine.IPUI import IPUI

class _BaseTab:
    """Base class for tabs. Contains pane builders and lifecycle hooks..
    Gives self.form to all methods.


    ══════════════════════════════════════════════════════════════
    LIFECYCLE HOOKS — override these in your _BaseTab subclass
    all run when tab is visible - THINK_ALWAYS=True makes think run regardless.
    ══════════════════════════════════════════════════════════════
    ip_setup()      — For one-time setup.
    ip_think()      — Recommended uses. State, math, physics, logic, etc.
    ip_draw()       — Before UI widget tree draws. Game world, backgrounds.
    ip_draw_hud()   — After UI widget tree draws. Custom cursors, overlays, scores.

    """
    THINK_ALWAYS = False    # Continues to run ip_think even if tab is not active

    #  guard against __init__ override
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__:
            raise TypeError(f"{cls.__name__}: Don't override __init__, use ip_setup() instead")

    def __init__(self, form):
        self.form               = form
        self.ip                 = IPUI.ip
        self.ip.tab             = self
        self.private_setup_done = False
        self.register_derives()
        # was being called to early  self.ip_setup(self.ip)

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


    def set_pane(self, index, builder, *args, tab_name=None, weight=None, **kwargs):
        self.form.set_pane(index, builder, *args, tab_name=tab_name, weight=weight, **kwargs)

    def swap_pane(self, index, builder, *args, **kwargs):
        def do_swap():
            self.form.set_pane(index, builder)
        return do_swap

    def hide_extra_panes(self, keep_count):
        for pane in self.form.tab_strip.panes[keep_count:]:
            pane.visible = False


    def show_modal(self, msg, min_seconds=2, work_func=None):
        self.form.show_modal(msg, min_seconds, work_func)
    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS — override in your _BaseTab subclass
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

    def ip_setup(self, ip):
        pass

    def ip_activated(self, ip):
        pass


