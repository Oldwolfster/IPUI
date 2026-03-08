# LayoutEngine.py — NEW: Measure + Layout orchestration extracted from _BaseWidget
#
# ══════════════════════════════════════════════════════════════════
# IPUI WIDGET LIFECYCLE — SINGLE-PASS: BUILD → MEASURE → LAYOUT → DRAW
# ══════════════════════════════════════════════════════════════════
#
# Every frame, the widget tree executes four phases top-down:
#
# 1. BUILD    Constructor calls build(). Each widget creates its own
#             content (surfaces, child widgets). Runs once at creation,
#             and again on set_text() or other state changes.
#
# 2. MEASURE  Parent asks each child: "how big do you want to be?"
#             Returns (width, height) based on the surface built in step 1.
#             Flex children (width_flex/height_flex > 0) skip this —
#             their size comes from leftover space, not intrinsic content.
#
# 3. LAYOUT   Parent assigns each child a rect. For vertical stacks:
#             width = parent's inner width, height = measured or flex.
#             This is where measure_after_wrap() enables text wrapping —
#             the ONLY place a child learns its actual width. See the
#             text wrapping comment block below for details.
#
# 4. DRAW     Each widget draws itself into its assigned rect, then
#             recurses into children. Clipping ensures nothing leaks.
#
# This is NOT a virtual DOM. There's no diffing, no reconciliation.
# Each phase runs once per frame in a single top-down pass.
# State changes (set_text, pipeline updates) just re-run build() on
# the affected widget. The next frame's layout pass picks up the new
# measurements automatically.
#
# ──────────────────────────────────────────────────────────────────
# TEXT WRAPPING — HOW IT AVOIDS THE CHICKEN-AND-EGG PROBLEM
# ──────────────────────────────────────────────────────────────────
# Problem:  Text wrapping needs a width to wrap to.
#           build() creates the surface BEFORE layout assigns the width.
#           So at build-time, we don't know the wrap width. Classic deadlock.
#
# Solution: We DON'T wrap at build-time. build() creates a single-line surface
#           as always. The wrapping happens later, inside layout_children(),
#           which is the first moment the parent knows the child's actual width.
#
#           layout_children() calls measure_after_wrap(max_width) instead of
#           measure(). For most widgets this just returns measure() — no change.
#           But a Label with wrap=True uses that width to rebuild its surface
#           with word-wrapping, then returns the new (wrapped) dimensions.
#
#           The key insight: layout_children already knows the child's width
#           (it's inner.width for vertical stacks). It just wasn't telling
#           the child. Now it does, through measure_after_wrap().
#
# Timeline: build()   → surface = single-line (no width known yet)
#           measure() → returns single-line dimensions (used by flex budget)
#           layout_children() calls measure_after_wrap(inner.width)
#               → Label rebuilds surface wrapped to that width
#               → returns new (narrower, taller) dimensions
#           layout()  → child gets rect using the wrapped height
#           draw()    → draws the wrapped surface
#
# ──────────────────────────────────────────────────────────────────
# ITERATIVE FLEX ALLOCATION
# ──────────────────────────────────────────────────────────────────
# Flex layout is an NP-hard adjacent constraint satisfaction problem.
# CSS spent 20 years on it. We use a greedy iterative algorithm that
# handles real-world cases perfectly:
#
# Priority 1: width_min / height_min is king. Nothing renders smaller.
# Priority 2: Symmetry of flex weights honored when space allows.
#
# Algorithm (resolve_flex):
#   1. Measure all children to get their minimums.
#   2. Calculate fair share per flex weight from remaining space.
#   3. Find violators: flex children whose minimum > their fair share.
#   4. Lock the BIGGEST violator at its minimum, remove from flex pool.
#   5. Repeat until no violators remain.
#   6. Remaining pool members get their (now larger) fair share.
# ══════════════════════════════════════════════════════════════════

import pygame
from ipui.Style import Style


class LayoutEngine:
    """Stateless layout orchestration. All methods operate on widget attributes directly."""

    # ==============================================================
    # MEASURE
    # ==============================================================

    @staticmethod
    def measure(w) -> tuple[int, int]:
        """Return (width, height) minimum space needed."""
        if w.my_surface: return LayoutEngine.measure_surface(w)
        if w.children  : return LayoutEngine.measure_children(w)
        return (0, 0)

    @staticmethod
    def measure_surface(w) -> tuple[int, int]:
        """Space needed for content surface plus frame."""
        if not w.my_surface: return (0, 0)
        cw, ch = w.my_surface.get_size()
        frame  = (w.pad + w.border) * 2
        return (cw + frame, ch + frame)


    @staticmethod
    def measure_children(w) -> tuple[int, int]:
        """Sum children along main axis, max along cross axis."""
        kids        = LayoutEngine.visible_kids(w)
        if not kids : return (0, 0)
        total_main  = 0
        max_cross   = 0
        for child in kids:
            cx, cy = LayoutEngine.measure(child)
            if w.horizontal:
                total_main += cx
                max_cross   = max(max_cross, cy)
            else:
                total_main += cy
                max_cross   = max(max_cross, cx)
        gap_total    = w.gap * max(0, len(kids) - 1)
        total_main  += gap_total
        frame        = (w.pad + w.border) * 2
        if w.horizontal: return (total_main + frame, max_cross + frame)
        else:            return (max_cross + frame, total_main + frame)
    @staticmethod
    def compute_min_size(w) -> None:
        """Set width_min and height_min. Handles wrap=True text specially."""
        if getattr(w, 'wrap', False) and w.text and w.font:
            frame        = (w.pad + w.border) * 2
            words        = w.text.split()
            w.width_min  = max(
                (w.font.size(word)[0] for word in words),
                default=0
            ) + frame
            w.height_min = w.font.get_height() + frame
        else:
            mw, mh       = LayoutEngine.measure(w)
            w.width_min  = mw
            w.height_min = mh

    @staticmethod
    def measure_after_wrap(w, max_width: int) -> tuple[int, int]:
        """Re-measure a widget given a width constraint. Rebuilds wrapped text surface."""
        if not getattr(w, 'wrap', False): return LayoutEngine.measure(w)
        if not w.text or not w.font:      return LayoutEngine.measure(w)
        if getattr(w, 'glow', False):
            w.my_surface = w.composite_glow_wrapped(max_width)
        else:
            w.my_surface = LayoutEngine.render_wrapped(w, w.text, max_width)
        return LayoutEngine.measure_surface(w)

    # ==============================================================
    # TEXT RENDERING (wrap support)
    # ==============================================================

    @staticmethod
    def wrap_lines(w, text: str, max_width: int) -> list[str]:
        """Split text into lines that fit within max_width, honoring existing newlines."""
        frame     = (w.pad + w.border) * 2
        max_width = max_width - frame
        if max_width <= 0: return text.split("\n") if text else [""]
        result    = []
        for paragraph in (text or "").split("\n"):
            words = paragraph.split()
            if not words:
                result.append("")
                continue
            current = words[0]
            for word in words[1:]:
                test = current + " " + word
                if w.font.size(test)[0] <= max_width:
                    current = test
                else:
                    result.append(current)
                    current = word
            result.append(current)
        return result

    @staticmethod
    def render_wrapped(w, text: str, max_width: int):
        """Render text with word-wrapping to fit within max_width."""
        lines         = LayoutEngine.wrap_lines(w, text, max_width)
        line_surfaces = [w.font.render(line, True, w.color_txt) for line in lines]
        if not line_surfaces: return None
        width  = max(s.get_width()  for s in line_surfaces)
        height = sum(s.get_height() for s in line_surfaces)
        surf   = pygame.Surface((width, height), pygame.SRCALPHA)
        y      = 0
        for s in line_surfaces:
            if   w.text_align == 'c': x = (width - s.get_width()) // 2
            elif w.text_align == 'r': x = width - s.get_width()
            else:                     x = 0
            surf.blit(s, (x, y))
            y += s.get_height()
        return surf

    # ==============================================================
    # LAYOUT
    # ==============================================================

    @staticmethod
    def layout(w, rect: pygame.Rect) -> None:
        """Receive rect from parent, lay out children within it."""

        w.rect = rect
        if not w.children: return
        frame  = (w.pad + w.border) * 2
        inner  = rect.inflate(-frame, -frame)
        if w.scrollable:
            inner = LayoutEngine.apply_scroll(w, inner)
            print(f"LAYOUT SCROLLABLE: {w.my_name:20} type={type(w).__name__:15} has_children={bool(w.children)}")
        LayoutEngine.layout_children(w, inner)

    @staticmethod
    def apply_scroll(w, inner: pygame.Rect) -> pygame.Rect:
        """Adjust inner rect for scroll state; always reserve scrollbar space."""
        bar_w          = Style.TOKEN_SCROLLBAR
        inner          = pygame.Rect(inner.left, inner.top, inner.width - bar_w, inner.height)

        content = LayoutEngine.compute_content_size(w)
        main_size = inner.width if w.horizontal else inner.height
        # LayoutEngine.py method: apply_scroll  Update: Show class type too
        print(          f"SCROLL DEBUG: {w.my_name:20} type={type(w).__name__:15} content={content:5} viewport={main_size:5} kids={len(LayoutEngine.visible_kids(w))} scrollable={w.scrollable}")
        #print(            f"SCROLL DEBUG: {w.my_name:20} content={content:5} viewport={main_size:5} kids={len(LayoutEngine.visible_kids(w))}")
        #for c in LayoutEngine.visible_kids(w):
            #print(                f"  child: {getattr(c, 'my_name', '?'):20} text={getattr(c, 'text', '')!r:20} fh={c.height_flex} measure={LayoutEngine.measure(c)}")

        w.scroll_active = content > main_size
        if w.scroll_active:
            max_scroll     = max(0, content - inner.height)
            w.scroll_offset = max(0, min(w.scroll_offset, max_scroll))
        else:
            w.scroll_offset = 0
        return inner

    @staticmethod
    def layout_children(w, inner: pygame.Rect) -> None:
        """Position children within inner rect, distributing flex space."""
        kids          = LayoutEngine.visible_kids(w)
        horiz         = w.horizontal
        total_space   = inner.width if horiz else inner.height
        for child in kids:
            LayoutEngine.compute_min_size(child)
        share         = LayoutEngine.resolve_flex(w, kids, total_space)
        surplus       = LayoutEngine.compute_surplus(w, kids, total_space, share)
        offset, extra = LayoutEngine.compute_justify_offset(w, surplus, kids)
        pos           = (inner.left if horiz else inner.top) + offset - w.scroll_offset
        for i, child in enumerate(kids):
            if i > 0  : pos += w.gap + extra
            fill      = child.width_flex_actual if horiz else child.height_flex_actual
            if fill > 0:
                size  = share * fill
            else:
                size  = child.width_min if horiz else child.height_min
                if not horiz and getattr(child, 'wrap', False):
                    x, y = LayoutEngine.measure_after_wrap(child, inner.width)
                    size = y
            LayoutEngine.layout(child, LayoutEngine.child_rect(w, child, inner, pos, size))
            pos      += size

    @staticmethod
    def resolve_flex(w, kids, total_space) -> float:
        """Iterative flex allocation respecting minimum sizes.
        Returns share_per_weight for final pixel assignment."""
        horiz = w.horizontal
        for child in kids:
            if horiz: child.width_flex_actual  = child.width_flex
            else:     child.height_flex_actual = child.height_flex

        pool         = [c for c in kids if (c.width_flex if horiz else c.height_flex) > 0]
        locked_space = 0
        for c in kids:
            if (c.width_flex if horiz else c.height_flex) == 0:
                locked_space += c.width_min if horiz else c.height_min
        locked_space += w.gap * max(0, len(kids) - 1)

        share_per_weight = 0
        while pool:
            remaining    = total_space - locked_space
            total_weight = sum(c.width_flex if horiz else c.height_flex for c in pool)
            if total_weight <= 0: break
            share_per_weight = remaining / total_weight

            violators = [
                c for c in pool
                if (c.width_min if horiz else c.height_min)
                    > share_per_weight * (c.width_flex if horiz else c.height_flex)
            ]
            if not violators: break

            v = max(violators, key=lambda c: c.width_min if horiz else c.height_min)
            if horiz: v.width_flex_actual  = 0
            else:     v.height_flex_actual = 0
            locked_space += v.width_min if horiz else v.height_min
            pool.remove(v)

        return share_per_weight

    # ==============================================================
    # LAYOUT HELPERS
    # ==============================================================

    @staticmethod
    def compute_surplus(w, kids, total_space, share_per_weight) -> int:
        """Return unused space after all children are assigned sizes."""
        horiz = w.horizontal
        used  = w.gap * max(0, len(kids) - 1)
        for child in kids:
            fill = child.width_flex_actual if horiz else child.height_flex_actual
            if fill > 0: used += share_per_weight * fill
            else:        used += child.width_min if horiz else child.height_min
        return max(0, int(total_space - used))

    @staticmethod
    def compute_justify_offset(w, surplus: int, kids: list) -> tuple[int, int]:
        """Return (initial_offset, extra_gap) for justify modes."""
        if surplus <= 0: return 0, 0
        if w.justify_spread:
            extra = surplus / max(1, len(kids) - 1) if len(kids) > 1 else 0
            return 0, extra
        if w.justify_center: return surplus / 2, 0
        return 0, 0

    @staticmethod
    def child_rect(w, child, inner: pygame.Rect, pos: float, size: float) -> pygame.Rect:
        """Build a rect for one child along the main axis."""
        if w.horizontal: return pygame.Rect(pos, inner.top,  size, inner.height)
        else:            return pygame.Rect(inner.left, pos, inner.width, size)

    @staticmethod
    def compute_content_size(w) -> int:
        """Total size of children along main axis (for scroll calculation)."""
        kids = LayoutEngine.visible_kids(w)
        total = 0
        for child in kids:
            LayoutEngine.compute_min_size(child)
            total += child.width_min if w.horizontal else child.height_min
        total += w.gap * max(0, len(kids) - 1)
        return total

    @staticmethod
    def visible_kids(w) -> list:
        """Children that participate in layout and drawing."""
        return [c for c in w.children if c.visible and not c.do_not_allocate]