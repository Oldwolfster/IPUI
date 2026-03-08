# _BaseWidget.py — IPUI Framework Base Widget
# All widgets inherit from this class. No widget should override __init__; use build() instead.

from __future__ import annotations
import time
from typing import Optional, TYPE_CHECKING

import pygame

#from ipui.engine.LayoutEngine import LayoutEngine
from ipui.Style import Style
from ipui.engine.MgrColor import MgrColor
from ipui.utils.EZ import EZ

if TYPE_CHECKING:
    from ipui.engine._BaseForm import _BaseForm


class _BaseWidget:
    """Base class for all IPUI widgets.

    Provides the complete widget lifecycle: measure → layout → draw,
    plus event handling, scrolling, hover effects, and overlay support.

    Subclasses should override build() for initialization, never __init__.

    ══════════════════════════════════════════════════════════════════
    IPUI WIDGET LIFECYCLE — SINGLE-PASS: BUILD → MEASURE → LAYOUT → DRAW
    ══════════════════════════════════════════════════════════════════

    Every frame, the widget tree executes four phases top-down:

    1. BUILD    Constructor calls build(). Each widget creates its own
                content (surfaces, child widgets). Runs once at creation,
                and again on set_text() or other state changes.

    2. MEASURE  Parent asks each child: "how big do you want to be?"
                Returns (width, height) based on the surface built in step 1.
                Flex children (width_flex/height_flex > 0) skip this —
                their size comes from leftover space, not intrinsic content.

    3. LAYOUT   Parent assigns each child a rect. For vertical stacks:
                width = parent's inner width, height = measured or flex.
                This is where measure_constrained() enables text wrapping —
                the ONLY place a child learns its actual width. See the
                text wrapping comment block below for details.

    4. DRAW     Each widget draws itself into its assigned rect, then
                recurses into children. Clipping ensures nothing leaks.

    This is NOT a virtual DOM. There's no diffing, no reconciliation.
    Each phase runs once per frame in a single top-down pass.
    State changes (set_text, pipeline updates) just re-run build() on
    the affected widget. The next frame's layout pass picks up the new
    measurements automatically.
    ══════════════════════════════════════════════════════════════════

    """

    # ==============================================================
    # CONSTRUCTION
    # ==============================================================
    _next_id = 0 # For global widget resgistry
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__ and cls.__name__ != '_BaseForm':
            raise TypeError(f"{cls.__name__}: Don't override __init__, use build() instead")

    def __init__(self, parent=None, text=None, name=None,
                 width_flex=0, height_flex=0,
                 pad=None, gap=None, border=None,justify_center=False, justify_spread=False, visible = True,
                 enabled=True, start= None, end = None, font=None,
                 text_align='l', wrap=False, color_bg=None, glow=False, data=None, single_select=False,
                 placeholder=None, initial_value=None, on_submit=None, on_change=None, on_click=None,
                 pipeline_key=None, tooltip_class=None, scrollable=False, early_load =None):

        # Identity
        self.name       = name
        self.my_name    = "unnamed"

        _BaseWidget     ._next_id += 1  # NEW
        self.widget_id  = _BaseWidget._next_id
        # Tree
        self.children = []
        self.parent   = parent
        self.form     = parent.form if parent else getattr(self, 'form', None)

        # Content
        self.text       = text
        self.my_surface = None
        self.data       = data


        # Layout
        self.rect               = None
        self.pad                = pad    if pad    is not None else Style.TOKEN_PAD
        self.gap                = gap    if gap    is not None else Style.TOKEN_GAP
        self.border             = border if border is not None else Style.TOKEN_BORDER
        self.justify_center     = justify_center
        self.justify_spread     = justify_spread
        self.width_flex         = int(width_flex)
        self.width_flex_actual  = int(width_flex) #if there is not enough space to honr the width_flex it may be set to zero (renders at minimum(intrinsic) size)
        self.height_flex        = int(height_flex)
        self.height_flex        = int(height_flex) #if there is not enough space to honor the height_flex it may be set to zero (renders at minimum(intrinsic) size)
        self.horizontal         = False
        self.wrap               = wrap
        self.text_align         = text_align.lower()
        self.width_minimum              = None      #min space needed to render surface of children
        self.height_minimum              = None      #min space needed to render surface of children

        if text_align.lower() in ('c', 'r') and self.width_flex == 0: self.width_flex = 1

        # Appearance
        self.font               = font
        self.color_bg           = color_bg
        self.color_disabled     = None
        self.color_txt          = Style.COLOR_TEXT
        self.glow               = glow
        self.single_select      = single_select
        self.visible            = visible
        self.do_not_allocate    = False

        # Scrolling
        self.scrollable         = scrollable
        self.scroll_offset      = 0
        self.scroll_active      = False

        # Events
        self.on_click           = on_click
        self.on_change          = on_change
        self.on_hover           = None
        self.early_load         = early_load

        # State
        self.is_hovered         = False
        self.hover_bright       = True
        self.is_pressed         = False
        self.enabled            = enabled
        self.is_focused         = False
        self.locked_to_list     = True
        self.tool_tip_huge      = None
        self.hover_start_time   = 0
        self.start              = start
        self.end                = end


        # Subclass storage
        self.placeholder        = placeholder
        self.initial_value      = initial_value
        self.on_submit          = on_submit
        self.pipeline_key       = pipeline_key
        self.tooltip_class      = tooltip_class
        if self.scrollable      and self.height_flex == 0: self.height_flex = 1 # must occur before validate
        self.validate()
        if self.form            : self.form.widget_registry[self.widget_id] = self  # NEW
        if parent               : parent.children.append(self)
        if name and self.form   : self.form.widgets[name] = self
        if hasattr(self,'build'): self.build()

    def validate(self) -> None:
        """Guard against contradictory constructor arguments."""
        if self.justify_center and self.justify_spread:
            EZ.err("Cannot set both justify_center and justify_spread\nPlease pick on or the other.",ValueError)

        if self.text_align not in ('l', 'c', 'r'):
            EZ.err(f"text_align must be 'l', 'c', or 'r' — got '{self.text_align}'",ValueError)

        if self.parent and self.parent.scrollable and self.height_flex > 0 and 1==3:
            EZ.err(
                f"""{type(self).__name__} has height_flex inside scrollable {type(self.parent).__name__}.
    TO FIX: Remove height_flex from the child, or remove scrollable from the parent.
    Flex expands to fill space; scrollable needs content bigger than viewport. Contradictory!"""
            )

    # ==============================================================
    # PROPERTIES
    # ==============================================================

    @property
    def frame_size(self) -> int:
        """Total inset from edge to content: (pad + border) × 2."""
        return (self.pad + self.border) * 2

    @property
    def visible_children(self) -> list[_BaseWidget]:
        """Children that participate in layout and drawing."""
        return [c for c in self.children if c.visible and not c.do_not_allocate]


    # ==============================================================
    # LAYOUT
    # ==============================================================

    def apply_scroll(self, inner: pygame.Rect) -> pygame.Rect:
        """Adjust inner rect for scroll state; activate scrollbar if needed."""
        content    = self.compute_content_size()
        main_size  = inner.width if self.horizontal else inner.height
        self.scroll_active = content > main_size
        if self.scroll_active:
            bar_w      = Style.TOKEN_SCROLLBAR
            inner      = pygame.Rect(inner.left, inner.top, inner.width - bar_w, inner.height)
            max_scroll = max(0, content - inner.height)
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        else:
            self.scroll_offset = 0
        return inner



    def clear_children(self) -> None:
        """Remove all children from this widget."""
        self.children.clear()
    # ==============================================================
    # DRAW
    # ==============================================================
    def draw(self, surface: pygame.Surface) -> None:
        """Draw this widget and its children."""
        if self.rect is None: return
        bg = self.resolve_bg()
        self.draw_chrome(surface, self.rect, bg)
        self.draw_inboard_glow(surface)
        if self.my_surface:
            surface.blit(self.my_surface, self.compute_content_position())
        self.draw_children(surface)
        if self.scroll_active: self.draw_scrollbar(surface)

    def draw_children(self, surface):
        """Draw visible children, clipped to content area."""
        if not self.visible_children: return
        old_clip = surface.get_clip()
        frame = self.frame_size
        clip = self.rect.inflate(-frame, -frame)  # REPLACE: was self.rect
        clip = old_clip.clip(clip)  # NEW: intersect with parent's clip
        surface.set_clip(clip)
        for child in self.visible_children: child.draw(surface)
        surface.set_clip(old_clip)



    def draw_chrome(self, surface: pygame.Surface, r: pygame.Rect, bg_color: Optional[tuple]) -> None:
        """Draw background fill and bevel borders. Inverts bevel on press."""
        if bg_color:
            pygame.draw.rect(surface, bg_color, r)
        if not hasattr(self, 'border_top') or not self.border_top: return
        if self.is_pressed: top, left, bottom, right = self.border_bottom, self.border_right, self.border_top, self.border_left
        else:               top, left, bottom, right = self.border_top,    self.border_left,  self.border_bottom, self.border_right
        w = 2
        pygame.draw.line(surface, top,    (r.left,      r.top),        (r.right - 1, r.top),        w)
        pygame.draw.line(surface, left,   (r.left,      r.top),        (r.left,      r.bottom - 1), w)
        pygame.draw.line(surface, bottom, (r.left,      r.bottom - 1), (r.right - 1, r.bottom - 1), w)
        pygame.draw.line(surface, right,  (r.right - 1, r.top),        (r.right - 1, r.bottom - 1), w)

    def draw_inboard_glow(self, surface: pygame.Surface) -> None:
        """Draw the bottom-edge glow indicator for active tabs."""
        if not getattr(self, 'show_glow', False): return
        r      = self.rect
        glow_y = r.bottom - 4
        pygame.draw.line(surface, Style.COLOR_TAB_INDICATOR, (r.left + 4, glow_y), (r.right - 4, glow_y), 2)

    def draw_scrollbar(self, surface: pygame.Surface) -> None:
        """Draw a vertical scrollbar track and handle."""
        if not self.scroll_active: return
        frame        = self.frame_size
        inner        = self.rect.inflate(-frame, -frame)
        bar_w        = Style.TOKEN_SCROLLBAR
        bar_x        = inner.right - bar_w
        #content      = self.compute_content_size()
        #content = self.height_minimum if not self.horizontal else self.width_minimum
        content = getattr(self, 'content_size', self.height_minimum)
        track_h      = inner.height
        track_rect   = pygame.Rect(bar_x, inner.top, bar_w, track_h)
        pygame.draw.rect(surface, Style.COLOR_PANEL_BG, track_rect)
        visible_ratio = track_h / content
        handle_h      = max(20, int(track_h * visible_ratio))
        max_scroll    = max(1, content - track_h)
        scroll_ratio  = self.scroll_offset / max_scroll
        handle_y      = inner.top + int((track_h - handle_h) * scroll_ratio)
        handle_rect   = pygame.Rect(bar_x, handle_y, bar_w, handle_h)
        pygame.draw.rect(surface, Style.COLOR_BUTTON_BG, handle_rect)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        """Override to draw floating content outside normal layout.

        Called after the main draw pass but before tooltips.
        Used by widgets like DropDown that need to render above siblings.
        """
        pass

    def compute_content_position(self) -> tuple[int, int]:
        """Where to blit my_surface within my rect, respecting text_align."""
        s        = self.my_surface
        r        = self.rect
        sw, sh   = s.get_size()
        y        = r.top + (r.height - sh) // 2
        if   self.text_align == 'c': x = r.left + (r.width - sw) // 2
        elif self.text_align == 'r': x = r.right - sw - self.pad
        else:                        x = r.left + self.pad
        return (x, y)

    def wrap_lines(self, text: str, max_width: int) -> list[str]:
        """Split text into lines that fit within max_width, honoring existing newlines."""
        max_width  = max_width - self.frame_size
        if max_width <= 0: return text.split("\n") if text else [""]
        result     = []
        for paragraph in (text or "").split("\n"):
            words = paragraph.split()
            if not words:
                result.append("")
                continue
            current = words[0]
            for word in words[1:]:
                test = current + " " + word
                if self.font.size(test)[0] <= max_width:
                    current = test
                else:
                    result.append(current)
                    current = word
            result.append(current)
        return result


    def render_multiline_from_lines(self, lines: list[str]) -> Optional[pygame.Surface]:
        """Render a list of text lines to a surface, respecting text_align."""
        line_surfaces = [self.font.render(line, True, self.color_txt) for line in lines]
        if not line_surfaces: return None
        w    = max(s.get_width()  for s in line_surfaces)
        h    = sum(s.get_height() for s in line_surfaces)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        y    = 0
        for s in line_surfaces:
            if   self.text_align == 'c': x = (w - s.get_width()) // 2
            elif self.text_align == 'r': x = w - s.get_width()
            else:                        x = 0
            surf.blit(s, (x, y))
            y += s.get_height()
        return surf


    def render_multiline(self, text: str) -> Optional[pygame.Surface]:
        """Render newline-delimited text to a surface, respecting text_align."""
        lines = text.split("\n") if text else [""]                                              # REPLACE
        return self.render_multiline_from_lines(text.split("\n") if text else [""])

    def render_multiline_wrapped(self, text: str, max_width: int) -> Optional[pygame.Surface]:
        """Render text with word-wrapping to fit within max_width, respecting text_align."""
        return self.render_multiline_from_lines(self.wrap_lines(text, max_width))



    def resolve_bg(self) -> Optional[tuple]:
        """Compute effective background color considering disabled/hover state."""
        if self.enabled is not True                      : return MgrColor.compute_disabled(self.color_bg) #NOTE DO NOT SIMPLIFY
        if not self.is_hovered or self.color_bg is None : return self.color_bg
        if self.on_click                                : return MgrColor.compute_hover(self.color_bg)
        else                                            : return self.color_bg

    # ==============================================================
    # EVENTS — Click
    # ==============================================================


    def on_click_me(self, callback):
        """Register a validated click handler."""
        if not callable(callback):
            raise TypeError(
                f"{self.my_name}.on_click_me expects a callable, "
                f"got {type(callback).__name__}"
            )
        import inspect
        try:
            sig    = inspect.signature(callback)
            params = [p for p in sig.parameters.values()
                      if p.default is inspect.Parameter.empty
                      and p.name != 'self'
                      and p.kind not in (
                          inspect.Parameter.VAR_POSITIONAL,
                          inspect.Parameter.VAR_KEYWORD)]
            if len(params) != 0:
                raise ValueError(
                    f"{self.my_name}.on_click_me: callback must accept "
                    f"0 parameters, got {len(params)}: "
                    f"{[p.name for p in params]}"
                )
        except (TypeError,):
            pass
        self.on_click = callback

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Top-level click entry point: clear focus, then dispatch."""
        self.clear_focus()
        return self.dispatch_click(pos)

    def dispatch_click(self, pos: tuple[int, int]) -> bool:
        """Walk children depth-first; if none claim the click, try self."""
        for child in self.visible_children:
            if child.dispatch_click(pos): return True
        if self.rect and self.rect.collidepoint(pos):
            self.handle_focus(pos)
            return self.process_click()
        return False

    def process_click(self) -> bool:
        """Handle the click action for this widget."""
        if self.enabled is not True: return True
        if hasattr(self, 'toggle_selected'): self.toggle_selected()
        if self.on_click:
            self.is_pressed = True
            self.on_click()
            return True
        return False

    def handle_focus(self, pos: tuple[int, int]) -> bool:
        """Override in focusable widgets (e.g. TextBox)."""
        return False

    def clear_focus(self) -> None:
        """Recursively clear focus state down the tree."""
        self.is_focused = False
        for child in self.children: child.clear_focus()

    def handle_mouse_up(self, pos: tuple[int, int]) -> None:
        """Release press state down the tree."""
        self.is_pressed = False
        for child in self.children: child.handle_mouse_up(pos)

    # ==============================================================
    # EVENTS — Keyboard
    # ==============================================================

    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """Walk children first; if none claim the key, try self."""
        for child in self.children:
            if child.handle_keydown(event): return True
        return self.handle_key(event)

    def handle_key(self, event: pygame.event.Event) -> bool:
        """Override in widgets that handle keyboard input."""
        return False

    # ==============================================================
    # EVENTS — Hover
    # ==============================================================

    def update_hover(self, mouse_pos: tuple[int, int]) -> None:
        """Recursively update hover state for this widget and children."""
        self.was_hovered = self.is_hovered
        self.is_hovered  = self.rect.collidepoint(mouse_pos) if self.rect else False
        if self.is_hovered and not self.was_hovered: self.hover_start_time = time.time()
        if self.is_hovered != self.was_hovered and self.on_hover: self.on_hover(self.is_hovered)
        for child in self.visible_children: child.update_hover(mouse_pos)

    def find_hovered_tooltip(self) -> object:
        """Walk tree to find the deepest hovered widget with a tooltip ready to show."""
        for child in self.visible_children:
            result = child.find_hovered_tooltip()
            if result: return result
        if self.is_hovered and self.tool_tip_huge:
            if time.time() - self.hover_start_time >= 2.69: return self.tool_tip_huge
        return None

    def find_hovered_short_desc(self) -> Optional[str]:
        """Walk tree to find the deepest hovered widget with a short description."""
        for child in self.visible_children:
            result = child.find_hovered_short_desc()
            if result: return result
        if self.is_hovered and self.data and isinstance(self.data, dict):
            if time.time() - self.hover_start_time >= .69:
                desc = self.data.get("short_desc")
                if desc: return desc
        return None

    # ==============================================================
    # EVENTS — Scroll
    # ==============================================================

    def handle_scroll(self, pos: tuple[int, int], button: int) -> bool:
        """Dispatch scroll events to the deepest scrollable widget under pos."""
        for child in self.children:
            if child.handle_scroll(pos, button): return True
        if self.scroll_active and self.rect and self.rect.collidepoint(pos):
            direction         = -1 if button == 4 else 1
            self.scroll_offset += direction * 30
            frame              = self.frame_size
            inner              = self.rect.inflate(-frame, -frame)

            content            = getattr(self, 'content_size', self.height_minimum)
            max_scroll         = max(0, content - inner.height)
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
            return True
        return False

    # ==============================================================
    # STATE
    # ==============================================================

    def set_text(self, text: str) -> None:
        """Update text and rebuild the widget."""
        self.text = text
        if hasattr(self, 'build'): self.build()

    def set_disabled(self, reason: str = "") -> None:
        """Disable this widget with an optional reason string."""
        self.enabled = reason if reason else False         # REPLACE self.is_disabled = reason
        self.build()

    def set_enabled(self) -> None:
        """Re-enable this widget."""
        self.enabled = True                                # REPLACE self.is_disabled = None
        self.build()