# _BaseWidget.py — IPUI Framework Base Widget
# All widgets inherit from this class. No widget should override __init__; use build() instead.

from __future__ import annotations
import time
from typing import Optional, TYPE_CHECKING

import pygame

#from ipui.engine.LayoutEngine import LayoutEngine
from ipui.Style import Style
from ipui.engine.MgrColor import MgrColor
from ipui.engine.MixinScrollH import MixinScrollH
from ipui.utils.EZ import EZ


if TYPE_CHECKING:
    from ipui.engine._BaseForm import _BaseForm


class _BaseWidget(MixinScrollH):
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
    private_next_tab_order=1

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '__init__' in cls.__dict__ and cls.__name__ != '_BaseForm':
            EZ.err(f"{cls.__name__}: Don't override __init__, use build() instead\nThis removes the burden of you needing to feed parameters to the superclass.",
                   locate="def __init__", locate_in=cls, exc_type=TypeError)


    def __init__(self, parent=None, text=None, name=None,
                 width_flex=0, height_flex=0, scroll_h=False,
                 pad=None, pad_x=None, pad_y=None, gap=None,  border=None,justify_center=False, justify_spread=False, visible = True,
                 enabled=True, start= None, end = None, font=None, fit_content=False, border_radius=None,hug_parent=False,
                 text_align=None, wrap=False, color_bg=None, glow=False, data=None, single_select=False,
                 placeholder=None, initial_value=None, on_submit=None, on_change=None, on_click=None, tab_order=None, on_double_click=None,
                 pipeline_key=None, tooltip_class=None, scrollable=False, scroll_glow=.369, early_load =None):

        self.preflight_check(parent, text_align, width_flex, height_flex)

        # Identity
        self.name               = name
        self.widget_type        = None #automatically set after build
        _BaseWidget             ._next_id += 1  # NEW
        self.widget_id          = _BaseWidget._next_id

        # Tree
        self.children           = []

        self.parent             = parent
        self.form               = parent.form if parent else getattr(self, 'form', None)

        # Content
        self.text               = text
        self.my_surface         = None
        self.data               = data

        # Layout
        self.rect               = None
        self.pad_x              = Style.TOKEN_PAD
        self.pad_y              = Style.TOKEN_PAD
        self.gap                = Style.TOKEN_GAP
        self.border             = Style.TOKEN_BORDER


        self.justify_center     = justify_center
        self.justify_spread     = justify_spread
        self.width_flex         = width_flex
        self.width_flex_actual  = width_flex #if there is not enough space to honr the width_flex it may be set to zero (renders at minimum(intrinsic) size)
        self.height_flex        = height_flex
        self.height_flex        = height_flex #if there is not enough space to honor the height_flex it may be set to zero (renders at minimum(intrinsic) size)
        self.fit_content        = fit_content
        self.hug_parent         = hug_parent
        self.horizontal         = False
        self.wrap               = wrap
        self.text_align         = text_align.lower() if text_align is not None else None
        self.width_minimum      = None      #min space needed to render surface of children
        self.height_minimum     = None      #min space needed to render surface of children

        #if text_align.lower() in ('c', 'r') and self.width_flex == 0: self.width_flex = 1

        # Appearance
        self.font               = font
        self.color_bg           = color_bg
        self.color_disabled     = None
        self.color_txt          = Style.COLOR_TEXT
        self.glow               = glow
        self.border_radius      = border_radius
        self.single_select      = single_select
        self.visible            = visible
        self.do_not_allocate    = False         # skip layout allocation
        self.is_overlay         = False         # if do_not_allocate, still receive input (clicks, scroll)

        # Scrolling
        self.scrollable         = scrollable
        self.scroll_offset      = 0
        self.scroll_active      = False
        self.scroll_glow        = scroll_glow
        self.scroll_top_inset       = 0
        self.private_handle_rect    = None             #  handle rect for drag hit-testing
        self.private_track_top      = 0                #  top of scrollbar track
        self.private_track_h        = 0                #  height of scrollbar track
        self.private_handle_h       = 0                #  height of handle
        self.private_max_scroll     = 0                #  max scroll value
        self.private_dragging       = False            #  currently dragging?
        self.private_drag_anchor    = 0                # mouse offset from handle top


        # Events — declare, don't handle. MgrInput reads these.
        self.on_click           = on_click
        self.on_double_click    = on_double_click
        self.on_change          = on_change
        self.on_hover           = None
        self.focusable          = False
        self.early_load         = early_load

        # State
        self.is_hovered         = False
        self.hover_bright       = True
        self.is_pressed         = False
        self.enabled            = enabled
        self.private_enabled    = enabled
        self.is_focused         = False
        self.locked_to_list     = True
        self.tool_tip_huge      = None
        self.hover_start_time   = 0
        self.start              = start
        self.end                = end
        self.tab_order          = tab_order


        # Subclass storage
        self.placeholder        = placeholder
        self.initial_value      = initial_value
        self.on_submit          = on_submit
        self.pipeline_key       = pipeline_key
        self.tooltip_class      = tooltip_class
        if self.scrollable      and self.height_flex == 0: self.height_flex = 1 # must occur before validate
        self.validate()
        if self.form            : self.form.widget_registry[self.widget_id] = self
        if parent               : parent.children.append(self)
        if name and self.form   : self.form.widgets[name] = self
        self.private_build_comp = False                 #Track if build has run at least once

        #=============================================================
        # ================== Hook to Widget' Build  ==================
        self.build()
        # =============================================================
        if pad    is not None: self.pad    = pad      #  if user passed override then overwrite what was set in build
        if pad_x  is not None: self.pad_x  = pad_x                                       # NEW
        if pad_y  is not None: self.pad_y  = pad_y
        if gap    is not None: self.gap    = gap
        if border is not None: self.border = border

        #if scroll_h is not None: self.scroll_h = scroll_h
        self.init_scroll(scroll_h=scroll_h)

        if self.text_align is None: self.text_align = 'l'
        self.text_align = self.text_align.lower()
        if self.text_align in ('c', 'r') and self.width_flex == 0 and not self.fit_content and not self.hug_parent:
            self.width_flex = 1

        if self.tab_order == 0:
            _BaseWidget.private_next_tab_order += 1
            self.tab_order = _BaseWidget.private_next_tab_order
        if self.widget_type is None: self.widget_type =  type(self).__name__
        self.private_build_comp = True

    def build(self): pass #exists to be overwritten

# _BaseWidget.py  Update: preflight_check now calls validate_text_align; new validator added; line 214 block killed

    def preflight_check(self, parent, text_align, width_flex, height_flex):
        """All construction-time input checks live here.
        Runs as the first line of __init__ — before the framework
        touches any of these inputs. Add new validators below."""
        self.validate_parent(parent)
        self.validate_text_align(text_align)
        self.validate_flex('width_flex', width_flex)
        self.validate_flex('height_flex', height_flex)

    def validate_flex(self, name, value):
        """flex must be a number (int or float). Catches the True/False muscle-memory bug."""
        if isinstance(value, bool):                    self.err_flex_bad(name, value)
        if not isinstance(value, (int, float)):        self.err_flex_bad(name, value)

    def err_flex_bad(self, name, value):
        EZ.err(
            f"{type(self).__name__}() got {name}={value!r} — not a valid flex value.\n"
            f"\n"
            f"{name} needs a number: 0 means 'size to content', any positive\n"
            f"number is a flex slot (1, 2, 0.5, etc.). Bigger numbers grab more space.\n"
            f"\n"
            f"You wrote:     {type(self).__name__}(parent, ..., {name}={value!r})\n"
            f"Did you mean:  {type(self).__name__}(parent, ..., {name}=1)"
        )

    def validate_text_align(self, text_align):
        """text_align must be None or one of l/c/r (case-insensitive)."""
        if text_align is None:                                  return
        if isinstance(text_align, str) and text_align.lower() in ('l', 'c', 'r'): return
        EZ.err(
            f"{type(self).__name__}() got text_align={text_align!r} — not a valid alignment.\n"
            f"\n"
            f"text_align needs a direction: LEFT / CENTER / RIGHT (no quotes).\n"
            f"\n"
            f"You wrote:  {type(self).__name__}(parent, ..., text_align={text_align!r})\n"
            f"You meant:  {type(self).__name__}(parent, ..., text_align=CENTER)"
        )

    def validate_parent(self, parent):
        """Catch the two ways parent goes wrong: missing, or not a widget."""
        if parent is None and getattr(self, 'form', None) is None:
            EZ.err(
                f"{type(self).__name__}() was called without a parent.\n"
                f"\n"
                f"ROOT CAUSE: Every IPUI widget's first argument is its parent.\n"
                f"            That's what 'construction IS attachment' means —\n"
                f"            no floating widgets, no add() calls.\n"
                f"\n"
                f"Example 1:  {type(self).__name__}(my_card, ...)\n"
                f"Example 2:  {type(self).__name__}(parent, ...)   # if it's the first widget in a pane"
            )
        if parent is not None and not isinstance(parent, _BaseWidget):
            shown = repr(parent)
            if len(shown) > 40: shown = shown[:37] + "..."
            EZ.err(
                f"{type(self).__name__}() got a {type(parent).__name__} where a parent widget was expected.\n"
                f"\n"
                f"ROOT CAUSE: Looks like you forgot the parent argument.\n"
                f"            Every IPUI widget's first argument is its parent.\n"
                f"\n"
                f"You wrote:  {type(self).__name__}({shown}, ...)\n"
                f"You meant:  {type(self).__name__}(parent, {shown}, ...)\n"
                f"\n"
                f"TIP: 'parent' is whatever container you want this widget to live in\n"
                f"TIP: — usually a Card, Pane, or another widget passed into your method."
            )

    # BELOW IS POST VALIDATE

    def validate(self) -> None:

        self.validate_contradictory_arg()
        self.validate_no_parent()

    def validate_no_parent(self):
        if self.parent is None and self.form is None:
            EZ.err(  # NEW
                f"{type(self).__name__}() has no parent!\n"  
                f"A widget's first arg is always the parent widget.\n"  
                f"Example 1: {type(self).__name__}(my_card, ...)\n"
                f"Example 2: {type(self).__name__}(parent, ...) # if it's the first widget in a pane"
            )

    def validate_contradictory_arg(self):
        """Guard against contradictory constructor arguments."""
        if self.justify_center and self.justify_spread: EZ.err("Cannot set both justify_center and justify_spread\nPlease pick on or the other.",ValueError)
        #if self.text_align not in ('l', 'c', 'r'):      EZ.err(f"text_align must be 'l', 'c', or 'r' — got '{self.text_align}'",ValueError)
        if self.text_align is not None and self.text_align not in ('l', 'c', 'r'): EZ.err(
            f"text_align must be 'l', 'c', or 'r' — got '{self.text_align}'", ValueError)
        if self.parent and self.parent.scrollable and self.height_flex > 0 and 1==3: #1==3 becaues i don't think this is actually wrong
            EZ.err( f"""{type(self).__name__} has height_flex inside scrollable {type(self.parent).__name__}. TO FIX: Remove height_flex from the child, or remove scrollable from the parent.  Flex expands to fill space; scrollable needs content bigger than viewport. Contradictory!""")

    # ==============================================================
    # Reparent if scroller needed
    # ==============================================================




    # ==============================================================
    # PROPERTIES
    # ==============================================================


    @property
    def pad(self):
        # 369 is a deliberate tripwire — pad_x and pad_y are the real source of truth.
        # If you see 369 anywhere in layout math, somebody is reading self.pad and they shouldn't be.
        return 369

    @pad.setter
    def pad(self, value):
        if isinstance(value, tuple):
            self.pad_x, self.pad_y = value
        else:
            self.pad_x = value
            self.pad_y = value


    @property
    def pad_total_x(self):  return self.pad_x * 2     # left + right pad combined

    @property
    def pad_total_y(self):  return self.pad_y * 2     # top + bottom pad combined

    @property
    def frame_size(self) -> int:
        # Legacy — kept for sites we haven't converted yet (MgrSanity, etc.)
        # Returns symmetric value; safe while pad_x == pad_y everywhere.
        return (self.pad_x + self.border) * 2

    @property
    def frame_x(self) -> int:
        return (self.pad_x + self.border) * 2

    @property
    def frame_y(self) -> int:
        return (self.pad_y + self.border) * 2


    @property
    def display_name(self):
        raw = self.name or str(self.text or "")[:30] or self.first_child_text or self.widget_type
        raw = raw.replace("\n", " ")
        return "".join(ch for ch in raw if ch.isalnum() or ch == " ")[:24].strip()

    @property
    def first_child_text(self):
        for child in self.children:
            if child.text:
                return "w/ lbl " + str(child.text)[:24] + "'"
            for grandchild in child.children:
                if grandchild.text:
                    return "w/ lbl " + str(grandchild.text)[:24] + "'"
        return None


    @property
    def frame_size(self) -> int:
        """Total inset from edge to content: (pad + border) × 2."""
        return (self.pad_x + self.border) * 2

    @property
    def visible_children(self) -> list[_BaseWidget]:
        """Children that participate in layout and drawing."""
        return [c for c in self.children if c.visible and not c.do_not_allocate]

    @property
    def interactive_children(self) -> list['_BaseWidget']:
        """Children eligible for input dispatch — visible normals plus overlays.
        Layout uses visible_children (excludes overlays). Input uses this (includes them)."""
        return [c for c in self.children if c.visible and (not c.do_not_allocate or c.is_overlay)]
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
        self.draw_scroll_h_bar(surface)

    def draw_children(self, surface):
        """Draw visible children, clipped to content area."""
        if not self.visible_children: return
        old_clip = surface.get_clip()
        clip = self.rect.inflate(-self.frame_x, -self.frame_y)
        if self.scroll_active:   clip.width -= Style.TOKEN_SCROLLBAR
        #clip = self.shrink_clip_h(clip)  # NEW
        self.translate_children_h()  # NEW
        clip = old_clip.clip(clip)
        surface.set_clip(clip)
        for child in self.visible_children: child.draw(surface)
        self.restore_children_h()  # NEW
        surface.set_clip(old_clip)



    def draw_chrome(self, surface: pygame.Surface, r: pygame.Rect, color_bg: Optional[tuple]) -> None:
        """Draw background fill and bevel borders. Inverts bevel on press."""
        radius = getattr(self, 'border_radius', 0)
        if radius and color_bg and hasattr(self, 'border_top') and self.border_top:
            self.draw_chrome_rounded(surface, r, color_bg, radius)
            return
        if color_bg:
            pygame.draw.rect(surface, color_bg, r)
        if not hasattr(self, 'border_top') or not self.border_top: return
        if self.is_pressed: top, left, bottom, right = self.border_bottom, self.border_right, self.border_top, self.border_left
        else:               top, left, bottom, right = self.border_top,    self.border_left,  self.border_bottom, self.border_right
        w = self.border
        pygame.draw.line(surface, top,    (r.left,      r.top),        (r.right - 1, r.top),        w)
        pygame.draw.line(surface, left,   (r.left,      r.top),        (r.left,      r.bottom - 1), w)
        pygame.draw.line(surface, bottom, (r.left,      r.bottom - 1), (r.right - 1, r.bottom - 1), w)
        pygame.draw.line(surface, right,  (r.right - 1, r.top),        (r.right - 1, r.bottom - 1), w)

    def draw_chrome_rounded(self, surface, r, color_bg, radius):
        """Three overlapping solid rounded plates, all contained within r.
        Highlight at top-left, shadow at bottom-right, face centered. Bevel thickness = self.border."""
        if self.is_pressed: light, dark = self.border_bottom, self.border_top
        else:               light, dark = self.border_top,    self.border_bottom
        b         = self.border
        inner_w   = r.width  - 2 * b
        inner_h   = r.height - 2 * b
        highlight = pygame.Rect(r.left,         r.top,         inner_w, inner_h)
        pygame.draw.rect(surface, light,    highlight, border_radius=radius)
        shadow    = pygame.Rect(r.left + 2*b,   r.top + 2*b,   inner_w, inner_h)
        pygame.draw.rect(surface, dark,     shadow,    border_radius=radius)
        face      = pygame.Rect(r.left + b,     r.top + b,     inner_w, inner_h)
        pygame.draw.rect(surface, color_bg, face,      border_radius=radius)


    def draw_chrome_rounded(self, surface, r, color_bg, radius):
        """Three overlapping solid rounded plates, all contained within r.
        Highlight extends behind the face plate so all face corners land on highlight or shadow — never raw background.
        Bevel thickness = self.border."""
        if self.is_pressed: light, dark = self.border_bottom, self.border_top
        else:               light, dark = self.border_top,    self.border_bottom
        b         = self.border
        inner_w   = r.width  - 2 * b
        inner_h   = r.height - 2 * b
        highlight = pygame.Rect(r.left,         r.top,         inner_w + b*.5, inner_h + b*.5)
        pygame.draw.rect(surface, light,    highlight, border_radius=radius)
        shadow    = pygame.Rect(r.left + 2*b,   r.top + 2*b,   inner_w,     inner_h)
        pygame.draw.rect(surface, dark,     shadow,    border_radius=radius)
        face      = pygame.Rect(r.left + b,     r.top + b,     inner_w,     inner_h)
        pygame.draw.rect(surface, color_bg, face,      border_radius=radius)

    def draw_inboard_glow(self, surface: pygame.Surface) -> None:
        """Draw the bottom-edge glow indicator for active tabs."""
        if not getattr(self, 'show_glow', False): return
        r      = self.rect
        glow_y = r.bottom - 4
        pygame.draw.line(surface, Style.COLOR_TAB_INDICATOR, (r.left + 4, glow_y), (r.right - 4, glow_y), 2)

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
        elif self.text_align == 'r': x = r.right - sw - self.pad_x    # NEW
        else:                        x = r.left  + self.pad_x
        return (x, y)

    def wrap_lines(self, text: str, max_width: int) -> list[str]:
        """Split text into lines that fit within max_width, honoring existing newlines."""
        max_width  = max_width - self.frame_x
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
        if self.enabled is not True                     : return MgrColor.compute_disabled(self.color_bg) #NOTE DO NOT SIMPLIFY
        if not self.is_hovered or self.color_bg is None : return self.color_bg
        if (self.on_click and not self.focusable
                and self.hover_bright)                  : return MgrColor.compute_hover(self.color_bg)
        else                                            : return self.color_bg

    # ==============================================================
    # EVENTS — MgrInput handles all dispatch. Widgets just declare.
    # ==============================================================
    # on_click       → any widget becomes a button
    # focusable      → any widget receives text input
    # scrollable     → any widget scrolls
    # toggle_selected → any widget toggles
    # See MgrInput.py for the single dispatch point.

    def on_click_me(self, callback):
        """Register a validated click handler."""
        if not callable(callback):
            EZ.err (                f"{self.display_name}.on_click_me expects a callable, got {type(callback).__name__}",TypeError            )
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
                    f"{self.display_name}.on_click_me: callback must accept "
                    f"0 parameters, got {len(params)}: "
                    f"{[p.name for p in params]}"
                )
        except (TypeError,):
            pass
        self.on_click = callback

    # ==============================================================
    # HOVER TOOLTIP FINDERS — used by _BaseForm draw pass
    # ==============================================================

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
        if self.is_hovered and isinstance(self.enabled, str):
            if time.time() - self.hover_start_time >= .69: return self.enabled

        if self.is_hovered and self.data and isinstance(self.data, dict):
            if time.time() - self.hover_start_time >= .69:
                desc = self.data.get("short_desc")
                if desc: return desc
        return None

    # ==============================================================
    # EVENTS — Scroll
    # ==============================================================

    def draw_scrollbar(self, surface: pygame.Surface) -> None:
        """Draw a vertical scrollbar track and handle."""
        if not self.scroll_active: return
        inner        = self.rect.inflate(-self.frame_x, -self.frame_y)
        bar_w        = Style.TOKEN_SCROLLBAR
        bar_x        = self.rect.right - bar_w
        bar_x        = self.rect.right - self.border - bar_w
        content      = getattr(self, 'content_size', self.height_minimum)
        track_top    = self.rect.top + self.border + self.scroll_top_inset
        track_h      = self.rect.height - self.border * 2 - self.scroll_top_inset
        track_rect   = pygame.Rect(bar_x, track_top, bar_w, track_h)
        pygame.draw.rect(surface, Style.COLOR_PANEL_BG, track_rect)
        visible_ratio = track_h / content
        handle_h      = max(20, int(track_h * visible_ratio))
        max_scroll    = max(1, content - track_h)
        scroll_ratio  = self.scroll_offset / max_scroll
        handle_y      = track_top + int((track_h - handle_h) * scroll_ratio)
        handle_rect   = pygame.Rect(bar_x, handle_y, bar_w, handle_h)
        self.private_handle_rect = handle_rect
        self.private_track_top   = track_top
        self.private_track_h     = track_h
        self.private_handle_h    = handle_h
        self.private_max_scroll  = max_scroll
        self.draw_scroll_handle(surface, handle_rect)

    def draw_scroll_handle(self, surface, rect):
        if self.scroll_glow <= 0:
            pygame.draw.rect(surface, (120, 120, 120), rect)
            return
        alpha         = self.scroll_glow
        bg            = Style.COLOR_BUTTON_BG
        pygame.draw.rect(surface, bg, rect)
        lt            = Style.COLOR_BEVEL_HOT_LT
        dk            = Style.COLOR_BEVEL_HOT_DK
        if alpha < 1:
            lt = tuple(int(c * alpha + bg[i] * (1 - alpha)) for i, c in enumerate(lt))
            dk = tuple(int(c * alpha + bg[i] * (1 - alpha)) for i, c in enumerate(dk))
        w = 2
        r = rect
        pygame.draw.line(surface, lt, (r.left,      r.top),        (r.right - 1, r.top),        w)
        pygame.draw.line(surface, lt, (r.left,      r.top),        (r.left,      r.bottom - 1), w)
        pygame.draw.line(surface, dk, (r.left,      r.bottom - 1), (r.right - 1, r.bottom - 1), w)
        pygame.draw.line(surface, dk, (r.right - 1, r.top),        (r.right - 1, r.bottom - 1), w)

    # ==============================================================
    # STATE
    # ==============================================================

    def set_text(self, text: str) -> None:
        """Update text and rebuild the widget."""
        self.text = text
        if hasattr(self, 'build'): self.build()

    def set_disabled(self, reason: str = "") -> None:
        """Disable this widget with an optional reason string."""
        self.enabled = reason if reason else False
        self.build()

    def set_enabled(self) -> None:
        """Re-enable this widget."""
        self.enabled = True
        self.build()

    @property
    def enabled(self):
        return self.private_enabled

    @enabled.setter
    def enabled(self, value):
        self.private_enabled = value
        if hasattr(self, 'private_build_comp'):  # REPLACE
            self.build()

    # _BaseWidget.py method: tap  NEW: inline post-construction helper
    def tap(self, func):
        func(self)
        return self


