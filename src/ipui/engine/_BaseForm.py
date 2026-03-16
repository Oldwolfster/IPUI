# _BaseForm.py  Update: ip service portal with geometry context
import pygame

from ipui.Style import Style
from ipui.engine.WidgetsDict import WidgetsDict
from ipui.engine.MeasureAndLayout import MeasureAndLayout
from ipui.engine.MeasureAndWrap import MeasureAndWrap
from ipui.engine.Pipeline import Pipeline
from ipui.engine._BaseWidget import _BaseWidget
from ipui.engine.IPUI import IPUI
from ipui.widgets.TabStrip import TabStrip


class _BaseForm(_BaseWidget):
    """
    name:        _BaseForm
    desc:        Root container for an IPUI application. Manages render cycle, events, modals, and optional auto-TabStrip.
    when_to_use: Every screen in your app. Subclass it, override build(), done.
    best_for:    Top-level application forms with or without tabs.
    example:     class MyApp(_BaseForm):TAB_LAYOUT = {"Home": ["welcome"], "Log": ["log"]}\n                 def build(self): self.build_header()
    api:         switch_tab(name), set_pane(tab, idx, builder), hide_tab(name), show_tab(name), get_tab(name), prepare(name), show_modal(msg, fn), pipeline_set(k, v), pipeline_read(k)
    declares:    TAB_LAYOUT(dict), tab_early_load(list), tab_on_change(str), tab_hidden(list), tab_border(int)
    """

    _allow_init = True
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__ and not cls.__dict__.get('_allow_init', False):
            raise TypeError(f"{cls.__name__}: Don't override __init__, use build() instead")

    def __init__(self, title=None):
        self.title          = title
        self.widgets       = WidgetsDict()
        self.widget_registry= {}
        self.pipeline       = Pipeline(self.widgets, self.widget_registry)
        self.pipeline.debug = getattr(self.__class__, 'pipeline_debug', False)
        self.form           = self
        self.modal_msg      = None
        self.tab_strip      = None
        self.pinned_tooltip = None
        super().__init__    ( parent=None)
        self                . setup_tabs()
        self                . build_footer()
        self.MEASUREDRAWLAY = MeasureAndWrap(self)


    def compute_root_rectHopefullyIamDeprecated(self):
        screen_rect         = pygame.display.get_surface().get_rect()
        margin              = Style.TOKEN_GAP
        return screen_rect  . inflate(-margin * 2, -margin * 2)


    def render(self, surface):
        if 1==1 or self.dirty :
            self.MEASUREDRAWLAY.Runallthree()
            self.dirty = False
        self.draw(surface)
        self.draw_overlays(surface)
        self.draw_tooltips(surface)
        if getattr(self, 'show_diagnostics', False):   self.draw_diagnostics(surface)

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

    def ip_think(self, ip):
        self.dispatch_ip_think(ip)

    def ip_renderpre(self, ip):
        self.dispatch_ip_render(ip, "ip_renderpre")

    def ip_renderpost(self, ip):
        self.dispatch_ip_render(ip, "ip_renderpost")

    # ══════════════════════════════════════════════════════════════
    # HOOK DISPATCH — routes to panes with geometry context
    # ══════════════════════════════════════════════════════════════

    def dispatch_ip_think(self, ip):
        if not self.tab_strip:
            return
        active_name  = self.tab_strip.active_tab
        cache        = self.tab_strip.pane_cache
        content_widget = self.tab_strip.content if self.tab_strip else None
        for name, pane in cache.items():
            policy    = getattr(pane, 'IP_LIFECYCLE', 'persist')
            is_active = (name == active_name)
            ip.set_pane_context(pane, name, is_active, content_widget if is_active else None)
            pane.ip = ip
            if is_active:
                pane.ip_think(ip)
            elif policy == 'persist':
                pane.ip_think(ip)

    def dispatch_ip_render(self, ip, hook_name):
        if not self.tab_strip:
            return
        active_name    = self.tab_strip.active_tab
        pane           = self.tab_strip.pane_cache.get(active_name)
        content_widget = self.tab_strip.content if self.tab_strip else None
        if pane:
            ip.set_pane_context(pane, active_name, True, content_widget)
            getattr(pane, hook_name)(ip)

    # ══════════════════════════════════════════════════════════════
    # EVENT PROCESSING
    # ══════════════════════════════════════════════════════════════

    def process_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_tooltip_click(event.pos):
                return True
            if self.handle_scroll_drag_start(event.pos):
                return True
            self.handle_click(event.pos)
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.handle_scroll_drag_end(event.pos)
            self.handle_mouse_up(event.pos)
            return True
        elif event.type == pygame.MOUSEMOTION:
            self.handle_scroll_drag_move(event.pos)
            self.handle_mouse_move(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            if self.handle_tooltip_scroll(event.pos, event.button):
                return True
            self.handle_scroll(event.pos, event.button)
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.show_diagnostics = not getattr(self, 'show_diagnostics', False)
            elif event.key == pygame.K_ESCAPE and self.pinned_tooltip:
                self.pinned_tooltip.unpin()
                self.pinned_tooltip = None
            elif event.key == pygame.K_F12:
                from forms.Debugger.FormDebugger import FormDebugger
                if isinstance(self, FormDebugger):
                    IPUI.back()
                else:
                    IPUI.debug_target = self
                    IPUI.switch(FormDebugger, "IPUI X-Ray and Diagnostic Tools")
            else:
                self.handle_keydown(event)
            return True
        return False

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
        if self.pinned_tooltip.rect_pane and self.pinned_tooltip.rect_pane.collidepoint(pos):
            self.pinned_tooltip.handle_pin_scroll(button)
            return True
        return False

    def check_hover(self):
        self.update_hover(pygame.mouse.get_pos())

    def update(self):
        pass

    def pipeline_set(self, key, value):    self.pipeline.set(key, value)
    def pipeline_read(self, key):          return self.pipeline.read(key)

    # ============================================================
    # Modal handling
    # ============================================================

    def show_modal(self, msg, work_func=None, min_seconds=0):
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
        if widget.pad > 0 or widget.border > 0:
            inset = widget.pad + widget.border
            inner = r.inflate(-inset * 2, -inset * 2)
            pygame.draw.rect(surface, (color[0]//2, color[1]//2, color[2]//2), inner, 1)
        font = Style.FONT_DETAIL or pygame.font.SysFont("monospace", 11)
        label = font.render(widget.my_name, True, color)
        surface.blit(label, (r.left + 2, r.top + 1))
        size_text = f"{r.width}x{r.height}"
        size_surf = font.render(size_text, True, color)
        surface.blit(size_surf, (r.right - size_surf.get_width() - 2, r.bottom - size_surf.get_height() - 1))
        for child in widget.children:
            self.draw_diagnostic_widget(surface, child)

    def setup_tabs(self):
        import copy
        cls = self.__class__
        if not hasattr(cls, 'TAB_LAYOUT'):
            return
        self.TAB_LAYOUT = copy.deepcopy(cls.TAB_LAYOUT)
        on_change = None
        method_name = getattr(cls, 'tab_on_change', None)
        if method_name:
            on_change = lambda name, current, m=method_name: getattr(self, m)(name, current)
        self.tab_strip = TabStrip(self,
                                  data=self.TAB_LAYOUT,
                                  early_load=getattr(cls, 'tab_early_load', None),
                                  on_change=on_change,
                                  border=getattr(cls, 'tab_border', -5),
                                  )
        for name in getattr(cls, 'tab_hidden', []):
            self.tab_strip.hide_tab(name)

    def build_footer(self):
        pass

    def switch_tab(self, name):
        self.tab_strip.switch_tab(name)

    def set_pane(self, index, builder,  *args, tab_name=None, **kwargs):
        self.tab_strip.set_pane(index, builder,  *args, tab_name=tab_name, **kwargs)

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