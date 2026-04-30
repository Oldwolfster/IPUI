# _BaseForm.py  Update: ip service portal with geometry context
import pygame
from ipui.engine.NotNP_HardHug  import NotNP_HardHug
from ipui.Style import Style
from ipui.engine.WidgetsDict import WidgetsDict
from ipui.engine.NotNP_HardLayout import NotNP_HardLayout
from ipui.engine.NotNP_HardWrap import NotNP_HardWrap
from ipui.engine.Pipeline import Pipeline
from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.IPUI import IPUI
from ipui.utils.EZ import EZ
from ipui.widgets.TabStrip import TabStrip
import math
import time
from ipui.engine.MgrSanity import MgrSanity

class _BaseForm(_BaseWidget):
    """
    name:        _BaseForm
    desc:        Root container for an IPUI application. Manages render cycle, events, modals, and optional auto-TabStrip.
    when_to_use: Every screen in your app. Subclass it, override build(), done.
    best_for:    Top-level application _forms with or without tabs.
    example:     class MyApp(_BaseForm):TAB_LAYOUT = {"Home": ["welcome"], "Log": ["log"]}\n                 def build(self): self.build_header()
    api:         switch_tab(name), set_pane(tab, idx, builder), hide_tab(name), show_tab(name), get_tab(name), prepare(name), show_modal(msg, fn), pipeline_set(k, v), pipeline_read(k)
    declares:    TAB_LAYOUT(dict), tab_early_load(list), tab_on_change(str), tab_hidden(list), tab_border(int)
    """

    private_allow_init  = True
    THINK_ALWAYS        = False
    RESERVED = {            #These cannot be used as pane names.
        "build", "draw", "measure",
        "setup", "update", "render",
        "apply_scroll", "clear_children",
        "draw_children", "draw_chrome", "draw_chrome_rounded",
        "draw_inboard_glow", "draw_overlay",
        "draw_scrollbar", "draw_scroll_handle",
        "resolve_bg", "set_text", "set_disabled",
        "set_enabled", "validate", "tap",
        "on_click_me", "register_derives",
        "swap_pane", "hide_extra_panes",
        "ip_setup", "ip_think", "ip_draw",
        "ip_draw_hud", "ip_activated",
        "show_modal",
    }
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__ and not cls.__dict__.get('private_allow_init', False):
            EZ.err(f"{cls.__name__}: Don't override __init__, use build() instead\nThis removes the burden of you needing to feed parameters to the superclass.",
               locate="def __init__", locate_in=cls, exc_type=TypeError)

    def __init__(self, title=None):
        self.title          = title
        self.ip             = IPUI.ip
        self.widgets        = WidgetsDict()
        self.widget_registry= {}
        self.pipeline       = Pipeline(self.widgets, self.widget_registry)
        self.pipeline.debug = getattr(self.__class__, 'pipeline_debug', False)
        self.form           = self
        self                . seed_pipeline_defaults()
        self.modal_msg      = None
        self.tab_strip      = None
        self.pinned_tooltip = None
        super().__init__    ( parent=None)
        self                . setup()
        self                . build_footer()
        # commented 4/30 cjf self.layout_engine  = NotNP_HardWrap(self)


    def seed_pipeline_defaults(self):
        defaults = getattr(self.__class__, 'PIPELINE_DEFAULTS', None)
        if not defaults:
            return
        for key, value in defaults.items():
            self.pipeline.set(key, value)

    def render(self, surface):
        self.sane_layout()
        self.draw(surface)
        self.draw_overlays(surface)
        self.draw_tooltips(surface)
        if getattr(self, 'show_diagnostics', False): self.draw_diagnostics(surface)
        self.draw_pulse(surface)

    def sane_layout(self):
        NotNP_HardLayout(self).RunLayout()  # Pass 1
        if NotNP_HardWrap(self).RunLayout():  # Pass 2 — True if surfaces changed
            NotNP_HardLayout(self).RunLayout()  # Pass 3
        NotNP_HardHug(self).RunLayout()  # Pass 4
        MgrSanity.check_tree(self)
        self.dirty = False

    def draw_pulse(self, surface):
        from ipui.engine.IPUI import IPUI
        widget = IPUI.pulse_widget
        if not widget or not widget.rect:       return
        elapsed = time.time() - IPUI.pulse_start
        if elapsed > 3.0:
            IPUI.pulse_widget = None
            if IPUI.pulse_return:
                form_class = IPUI.pulse_return
                IPUI.pulse_return = None
                IPUI.show(form_class)
            return
        t       = elapsed * 4
        alpha   = int(80 + 80 * abs(math.sin(t)))
        grow    = int(6 * abs(math.sin(t)))
        r       = widget.rect.inflate(grow * 2, grow * 2)
        surf    = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        color   = (0, 200, 255, alpha)
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=4)
        pygame.draw.rect(surf, (0, 200, 255, min(alpha + 40, 255)), surf.get_rect(), width=2, border_radius=4)
        surface.blit(surf, r.topleft)

    def draw_overlays(self, surface: pygame.Surface) -> None:
        self.walk_overlays(surface, self)

    def walk_overlays(self, surface: pygame.Surface, widget) -> None:
        for child in widget.children:
            self.walk_overlays(surface, child)
        widget.draw_overlay(surface)

    def draw_tooltips(self, surface):
        if self.pinned_tooltip:
            self.pinned_tooltip.draw_docked(surface)
            return
        tooltip = self.find_hovered_tooltip()
        if tooltip:
            tooltip.show_me(surface)
        else:
            short = self.find_hovered_short_desc()
            if short:
                self.draw_short_tooltip(surface, short)

    def draw_short_tooltip(self, surface, text):
        font    = Style.FONT_DETAIL
        lines   = text.split("\n")
        surfs   = [font.render(l, True, Style.COLOR_TEXT) for l in lines]
        tw      = max(s.get_width() for s in surfs)
        th      = sum(s.get_height() for s in surfs)
        pad     = Style.TOKEN_PAD
        box_w   = tw + pad * 2
        box_h   = th + pad * 2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        sw, sh  = surface.get_size()
        if mouse_x < sw // 2:  x = mouse_x + 15
        else:                   x = mouse_x - box_w - 15
        x       = max(10, min(x, sw - box_w - 10))
        y       = mouse_y - box_h - 10
        if y < 10:              y = mouse_y + 20
        pygame.draw.rect(surface, Style.COLOR_CARD_BG, (x, y, box_w, box_h))
        pygame.draw.rect(surface, Style.COLOR_BORDER,  (x, y, box_w, box_h), 1)
        cy = y + pad
        for s in surfs:
            surface.blit(s, (x + pad, cy))
            cy += s.get_height()

    def mark_dirty(self):
        self.dirty = True

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS
    # ══════════════════════════════════════════════════════════════
    def ip_think(self, ip):       pass

    def ip_draw(self, ip):        pass

    def ip_draw_hud(self, ip):    pass

    def ip_activated(self, ip):       pass

    def ip_setup(self, ip ):      pass #available to be overwritten by base class.

    # ══════════════════════════════════════════════════════════════
    # HOOK DISPATCH — routes to tabs with geometry context
    # ══════════════════════════════════════════════════════════════

    def dispatch_ip_think(self, ip):
        if self.dispatch_tabs_think(ip): return
        self.dispatch_form_think(ip)

    def dispatch_tabs_think(self, ip):
        """active-tab only, THINK_ALWAYS opt-in"""
        #if not self.tab_strip:   return False
        if self.tabless_mode: return False
        active_name    = self.tab_strip.active_tab
        cache          = self.tab_strip.tab_cache
        content_widget = self.tab_strip.content
        for name, tab in cache.items():
            is_active  = (name == active_name)
            if is_active or tab.THINK_ALWAYS:
                ip.set_tab_context(tab, name, is_active, content_widget)
                ip.state.tick(ip.dt)
                if hasattr(tab, 'ip_think'):tab.ip_think(ip)
        return True

    def dispatch_form_think(self, ip):
        if not hasattr(type(self), 'ip_think'):
            return
        ip.set_tab_context(self, type(self).__name__, True, self)
        ip.state.tick(ip.dt)
        self.ip_think(ip)

    def dispatch_ip_render(self, ip, hook_name):
        if self.dispatch_tabs_render(ip, hook_name): return
        self.dispatch_form_render(ip, hook_name)

    def dispatch_tabs_render(self, ip, hook_name):
        #print(f"in render - hook_name={hook_name}")
        if self.form.tabless_mode: return False
        active_name    = self.tab_strip.active_tab
        tab            = self.tab_strip.tab_cache.get(active_name)
        content_widget = self.tab_strip.content if self.tab_strip else None
        if tab:
            ip.set_tab_context(tab, active_name, True, content_widget)
            getattr(tab, hook_name)(ip)
        return True

    def dispatch_form_render(self, ip, hook_name):
        if not hasattr(type(self), hook_name):
            return
        ip.set_tab_context(self, type(self).__name__, True, self)
        getattr(self, hook_name)(ip)



    # ══════════════════════════════════════════════════════════════
    # TOOLTIP HELPERS — called by MgrInput, not by widgets
    # ══════════════════════════════════════════════════════════════

    def handle_tooltip_click(self, pos):
        if self.pinned_tooltip:
            tt = self.pinned_tooltip
            if tt.hit_test_close(pos):
                tt.unpin()
                self.pinned_tooltip = None
                return True
            if tt.hit_test_move(pos):
                tt.toggle_dock_side()
                return True
            if tt.hit_test_docked(pos):
                return True
            if tt.hit_test_copy(pos):
                tt.copy_content()
                return True
            tt.unpin()
            self.pinned_tooltip = None
            return False
        tt = self.find_hovered_tooltip()
        if tt and tt.hit_test_pin(pos):
            tt.pin()
            self.pinned_tooltip = tt
            return True
        return False

    def handle_tooltip_scroll(self, pos, button):
        if not self.pinned_tooltip:
            return False

        if self.pinned_tooltip.content_rect and self.pinned_tooltip.content_rect.collidepoint(pos):
            self.pinned_tooltip.handle_pin_scroll(button)
            return True
        return False

    def update(self):
        pass

    def pipeline_set(self, key, value):    self.pipeline.set(key, value)
    def pipeline_read(self, key):          return self.pipeline.read(key)

    # ============================================================
    # Modal handling
    # ============================================================

    def show_modal(self, msg, min_seconds=2, work_func=None):
        import time
        self.modal_msg = msg
        self.force_render_modal()
        start = time.time()
        if work_func is not None: work_func()
        elapsed = time.time() - start
        if elapsed < min_seconds:
            time.sleep(min_seconds - elapsed)
        self.modal_msg = None

    def force_render_modal(self):
        surface = IPUI.screen
        surface.fill(Style.COLOR_BACKGROUND)
        self.render(surface)
        self.draw_modal(surface)
        pygame.display.flip()

    def draw_modal(self, surface):
        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        font = Style.FONT_TITLE
        text_surf = font.render(self.modal_msg, True, Style.COLOR_TEXT)
        tw, th = text_surf.get_size()
        pad = Style.TOKEN_PAD * 4
        box_w = tw + pad * 2
        box_h = th + pad * 2
        box_x = (sw - box_w) // 2
        box_y = (sh - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(surface, Style.COLOR_CARD_BG, box_rect)
        pygame.draw.rect(surface, Style.COLOR_BEVEL_LIGHT, box_rect, 2)
        surface.blit(text_surf, (box_x + (box_w - tw) // 2, box_y + (box_h - th) // 2))

    # ============================================================
    # Diagnostic
    # ============================================================

    def draw_diagnostics(self, surface):
        self.draw_diagnostic_widget(surface, self)

    def draw_diagnostic_widget(self, surface, widget):
        if widget.rect is None:
            return
        r = widget.rect
        if (widget.width_flex > 0
        or widget.height_flex > 0):         color = (255, 160, 40)
        elif r.width == 0 or r.height == 0: color = (255, 40, 40)
        elif widget.children:               color = (80, 140, 255)
        else:                               color = (80, 220, 80)
        pygame.draw.rect(surface, color, r, 1)
        if widget.frame_x > 0 or widget.frame_y > 0:  # NEW
            inner = r.inflate(-widget.frame_x, -widget.frame_y)  # NEW
            pygame.draw.rect(surface, (color[0] // 2, color[1] // 2, color[2] // 2), inner, 1)
        font = Style.FONT_DETAIL or pygame.font.SysFont("monospace", 11)
        label = font.render(widget.display_name, True, color)
        surface.blit(label, (r.left + 2, r.top + 1))
        size_text = f"{r.width}x{r.height}"
        size_surf = font.render(size_text, True, color)
        surface.blit(size_surf, (r.right - size_surf.get_width() - 2, r.bottom - size_surf.get_height() - 1))
        for child in widget.children:
            self.draw_diagnostic_widget(surface, child)

    def setup(self):
        self.pad = 0 #otherwise pad creats monster border
        if hasattr(self.__class__, 'TAB_LAYOUT'):  self.setup_tabs()
        if hasattr(type(self), 'ip_setup') :  self.ip_setup(self.ip )

    def setup_tabs(self):
        import copy
        cls = self.__class__
        if not hasattr(cls, 'TAB_LAYOUT'):
            return
        self.TAB_LAYOUT = copy.deepcopy(cls.TAB_LAYOUT)
        self.validate_pane_names()
        on_change = None
        method_name = getattr(cls, 'tab_on_change', None)
        if method_name:
            on_change = lambda name, current, m=method_name: getattr(self, m)(name, current)
        self.tab_strip = TabStrip(self,
                                  data=self.TAB_LAYOUT,
                                  early_load=getattr(cls, 'tab_early_load', None),
                                  on_change=on_change,
                                  #border=getattr(cls, 'tab_border', -5),

                                  )
        for name in getattr(cls, 'tab_hidden', []):
            self.tab_strip.hide_tab(name)


    def validate_pane_names(self):
        for tab_name, entries in self.TAB_LAYOUT.items():
            for entry in entries:
                name = entry[0] if isinstance(entry, tuple) else entry
                if isinstance(name, str) and name in _BaseForm.RESERVED:
                    EZ.err(
                        f"Tab '{tab_name}': pane name '{name}' is a reserved framework method.\n"
                        f"FIX: Rename it to something descriptive like '{name}_view' or '{name}_pane'.")

    def build_footer(self):
        pass

    def switch_tab(self, name):
        self.tab_strip.switch_tab(name)

    def set_pane(self, index, builder, *args, tab_name=None, weight=None, **kwargs):
        self.tab_strip.set_pane(index, builder, *args, tab_name=tab_name, weight=weight, **kwargs)

    def refresh_pane(self,index):
        self.tab_strip.refresh_pane(index)

    def hide_tab(self, name):
        self.tab_strip.hide_tab(name)

    def show_tab(self, name):
        self.tab_strip.show_tab(name)

    def get_tab(self, name):
        return self.tab_strip.get_tab(name)

    def prepare(self, name):
        return self.tab_strip.prepare(name)

    def register_derive(self, control_name, property, compute, triggers):
        self.pipeline.register_derive(control_name, property, compute, triggers)

    @property
    def tabless_mode(self):
        return self.tab_strip is None