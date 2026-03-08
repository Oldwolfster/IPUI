import pygame
from ipui.Style import Style
from ipui.engine import _BaseWidget
from ipui.engine._BaseWidget import _BaseWidget

## ──────────────────────────────────────────────────────────────────
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
# ITERATIVE FLEX ALLOCATION - Goal Set Rect for each widget in tree
# ──────────────────────────────────────────────────────────────────
# Flex layout is an NP-hard adjacent constraint satisfaction problem.
# CSS spent 20 years on it.
# We use a greedy iterative algorithm that# handles real-world cases perfectly:
# Priority 1: width_min / height_min is king. Nothing renders smaller.#
# Priority 2: Symmetry of flex weights honored when space allows.

## Algorithm (resolve_flex):
#   1. Measure all children to get their minimums.
#   2. Calculate fair share per flex weight from remaining space.
#   3. Find violators: flex children whose minimum > their fair share.
#   4. Lock the BIGGEST violator at its minimum, remove from flex pool.
#   5. Repeat until no violators remain.
#   6. Remaining pool members get their (now larger) fair share.
#   7, MEET GOAL:  SET RECT
# ══════════════════════════════════════════════════════════════════
# MeasureAndLayout.py  NEW: Layout engine — sets rect on every widget in tree
#
# Three phases, all top-down except measure (bottom-up):
#   1. MEASURE   — cache width_minimum / height_minimum on every widget
#   2. LAYOUT    — iterative flex solver, sets rect
#   3. DRAW      — unchanged, stays on _BaseWidget
#
# The engine does NOT own draw. It just sets rects.
# Widgets with custom layout (PowerGrid, NetworkDiagram) override
# layout(rect) and handle their own children — the engine skips them.

import pygame


class MeasureAndLayout:

    def __init__(self, trunk):
        self.trunk = trunk

    # ══════════════════════════════════════════════════════════════
    # PUBLIC — called by _BaseForm.render()
    # ══════════════════════════════════════════════════════════════

    def Runallthree(self):
        self.measure_tree(self.trunk)
        root = self.compute_root_rect()
        self.layout_node(self.trunk, root)
       # self.dump_tree()

    def compute_root_rect(self):
        screen = pygame.display.get_surface().get_rect()
        margin = Style.TOKEN_GAP
        return screen.inflate(-margin * 2, -margin * 2)


    # ══════════════════════════════════════════════════════════════
    # PHASE 1: MEASURE — bottom-up, cache width_minimum / height_minimum
    # ══════════════════════════════════════════════════════════════

    def measure_tree(self, node):
        """Recursively measure all descendants, then this node."""
        for child in node.visible_children:
            self.measure_tree(child)
        self.measure_node(node)

    def measure_node2(self, node):
        width_of_surface, height_of_surface = self.measure_surface(node)
        width_of_children, height_of_children = self.measure_children(node)
        if node.width_flex > 0: width_of_children = 0
        if node.height_flex > 0: height_of_children = 0
        node.width_minimum = max(width_of_surface, width_of_children)
        node.height_minimum = max(height_of_surface, height_of_children)

    def measure_node(self, node):
        """Set width_minimum / height_minimum on one node. Children already measured."""
        width_of_surface, height_of_surface   = self.measure_surface(node)
        width_of_children, height_of_children = self.measure_children(node)
        node.width_minimum        = max(width_of_surface, width_of_children)
        node.height_minimum        = max(height_of_surface, height_of_children)

    def measure_surface(self, node):
        """Min size from this widget's own surface + frame."""
        if not node.my_surface:
            return (0, 0)
        w, h  = node.my_surface.get_size()
        frame = node.frame_size
        return (w + frame, h + frame)

    def measure_children(self, node):
        """Min size needed to hold all visible children."""
        kids = node.visible_children
        if not kids:
            return (0, 0)
        main  = 0
        cross = 0
        for child in kids:
            if node.horizontal:
                main  += child.width_minimum
                cross  = max(cross, child.height_minimum)
            else:
                main  += child.height_minimum
                cross  = max(cross, child.width_minimum)
        main += node.gap * max(0, len(kids) - 1)
        frame = node.frame_size
        if node.horizontal:
            return (main + frame, cross + frame)
        return (cross + frame, main + frame)

    # ══════════════════════════════════════════════════════════════
    # PHASE 2: LAYOUT — top-down, iterative flex, sets rect
    # ══════════════════════════════════════════════════════════════

    def layout_nodeOld(self, node, rect):
        """Assign rect to node, then lay out its children."""
        if rect is None:                          # NEW
            return
        node.rect = rect
        kids      = node.visible_children
        if not kids:
            return
        inner = self.compute_inner(node, rect)
        if node.scrollable:
            inner = self.apply_scroll(node, inner)
        self.layout_kids(node, kids, inner)

    def layout_node(self, node, rect):
        """Assign rect to node, then lay out its children.""" #  ty Grok
        if rect is None:  # NEW
            return
        node.rect = rect
        kids = node.visible_children
        if not kids:
            return
        inner = self.compute_inner(node, rect)
        if node.scrollable:
            inner = self.apply_scroll(node, inner)  # first pass (uses min_ as fallback)
        self.layout_kids(node, kids, inner)

        if node.scrollable:
            inner = self.apply_scroll(node, inner)  # second pass — now has real content size
            # re-assign rects if you shrunk the inner (rarely needed, but safe)
            # self.layout_kids(...) again is optional unless you hit weird cases

    def compute_inner(self, node, rect):
        """Content area inside pad + border."""
        frame = node.frame_size
        return rect.inflate(-frame, -frame)

    def layout_kids(self, node, kids, inner):
        """Solve flex, compute rects, recurse into children."""
        sizes = self.resolve_flex(node, kids, inner)

        # FIXED: True content size for scrolling (calculated from actual sizes, BEFORE scroll_offset)
        if node.scrollable:
            gap_total = node.gap * max(0, len(kids) - 1)
            if node.horizontal:
                node.content_w = sum(s for s in sizes if s is not None) + gap_total
                node.content_h = inner.height
            else:
                node.content_h = sum(s for s in sizes if s is not None) + gap_total
                node.content_w = inner.width

        self.assign_rects(node, kids, inner, sizes)

    def apply_scroll(self, node, inner):
        """Adjust inner rect for scroll state — NOW uses real content size after layout."""
        # First layout pass already happened — we have real rects
        self.update_content_size(node)                    # ← NEW

        content_main = node.content_h if not node.horizontal else node.content_w
        main_size    = inner.height if not node.horizontal else inner.width

        node.scroll_active = content_main > main_size #ty grok
        if not node.scroll_active:
            node.scroll_offset = 0
            return inner

        bar_w = Style.TOKEN_SCROLLBAR
        if node.horizontal:
            # horizontal scroll (rare in your current UI)
            inner = pygame.Rect(inner.left, inner.top, inner.width, inner.height - bar_w)
        else:
            # vertical scroll (your particle widgets case)
            inner = pygame.Rect(inner.left, inner.top, inner.width - bar_w, inner.height)

        max_scroll = max(0, content_main - main_size)
        node.scroll_offset = max(0, min(node.scroll_offset, max_scroll))
        return inner

    def apply_scrollOld(self, node, inner):
        """Adjust inner rect for scroll state."""
        content   = node.height_minimum if not node.horizontal else node.width_minimum
        main_size = inner.width if node.horizontal else inner.height
        #print(f"SCROLL: {node.my_name} content={content} main_size={main_size} kids={len(node.visible_children)}")    # NEW
        node.scroll_active = content > main_size
        if not node.scroll_active:
            node.scroll_offset = 0
            return inner
        bar_w      = Style.TOKEN_SCROLLBAR
        inner      = pygame.Rect(inner.left, inner.top, inner.width - bar_w, inner.height)
        max_scroll = max(0, content - inner.height)
        node.scroll_offset = max(0, min(node.scroll_offset, max_scroll))
        return inner

    def update_content_size(self, node):
        """Fallback only — real content size is now set in layout_kids."""
        if not hasattr(node, 'content_h') or node.content_h is None:
            node.content_h = node.rect.height
        if not hasattr(node, 'content_w') or node.content_w is None:
            node.content_w = node.rect.width

    def update_content_sizeOld(self, node):
        """Called AFTER children are laid out. Computes real content bounds from final rects.
           This is what makes dynamic widgets + wrapping actually scroll."""
        if not node.visible_children:
            node.content_w = node.rect.width
            node.content_h = node.rect.height
            return

        max_right = max((c.rect.right for c in node.visible_children), default=node.rect.left)
        max_bottom = max((c.rect.bottom for c in node.visible_children), default=node.rect.top)

        node.content_w = max_right - node.rect.left
        node.content_h = max_bottom - node.rect.top

    # ──────────────────────────────────────────────────────────────
    # FLEX SOLVER — iterative greedy algorithm
    # ──────────────────────────────────────────────────────────────

    def resolve_flex(self, node, kids, inner):
        """Return list of sizes (one per kid) along the main axis."""
        horiz     = node.horizontal
        budget    = inner.width if horiz else inner.height
        gap_total = node.gap * max(0, len(kids) - 1)
        budget   -= gap_total
        sizes     = [None] * len(kids)
        # Lock non-flex children at their minimum
        for i, child in enumerate(kids):
            flex = child.width_flex if horiz else child.height_flex
            if flex == 0:
                sizes[i] = child.width_minimum if horiz else child.height_minimum
                budget   -= sizes[i]
        # Iterative flex resolution
        budget = max(0, budget)
        self.solve_flex_iterative(node, kids, sizes, budget)
        return sizes

    def solve_flex_iterative(self, node, kids, sizes, budget):
        """Lock violators one at a time until fair shares hold."""
        horiz = node.horizontal
        while True:
            pool = self.flex_pool(node, kids, sizes, horiz)
            if not pool:
                break
            total_flex = sum(pool.values())
            fair_unit  = budget / total_flex if total_flex > 0 else 0
            violator   = self.find_violator(node, kids, pool, fair_unit, horiz)
            if not violator:
                self.assign_fair_shares(kids, sizes, pool, fair_unit)
                break
            idx, minimum = violator
            sizes[idx]   = minimum
            budget      -= minimum

    def flex_pool(self, node, kids, sizes, horiz):
        """Return {index: flex_weight} for unsolved flex children."""
        pool = {}
        for i, child in enumerate(kids):
            if sizes[i] is not None:
                continue
            flex = child.width_flex if horiz else child.height_flex
            if flex > 0:
                pool[i] = flex
        return pool

    def find_violator(self, node, kids, pool, fair_unit, horiz):
        """Find the flex child whose minimum most exceeds its fair share."""
        worst_idx  = None
        worst_over = 0
        for idx, flex in pool.items():
            child   = kids[idx]
            minimum = child.width_minimum if horiz else child.height_minimum
            share   = fair_unit * flex
            over    = minimum - share
            if over > worst_over:
                worst_over = over
                worst_idx  = idx
        if worst_idx is None:
            return None
        child = kids[worst_idx]
        return (worst_idx, child.width_minimum if horiz else child.height_minimum)

    def assign_fair_shares(self, kids, sizes, pool, fair_unit):
        """Give remaining pool members their fair share."""
        for idx, flex in pool.items():
            sizes[idx] = max(0, int(fair_unit * flex))

    # ──────────────────────────────────────────────────────────────
    # RECT ASSIGNMENT
    # ──────────────────────────────────────────────────────────────

    def assign_rects(self, node, kids, inner, sizes):
        """Position children along main axis, recurse layout."""
        horiz  = node.horizontal
        pos    = (inner.left if horiz else inner.top) - node.scroll_offset
        offset, extra = self.compute_justify(node, kids, inner, sizes)
        pos   += offset
        for i, child in enumerate(kids):
            if i > 0:
                pos += node.gap + extra
            rect = self.build_child_rect(horiz, inner, pos, sizes[i])
            self.layout_node(child, rect)
            pos += sizes[i]

    def compute_justify(self, node, kids, inner, sizes):
        """Return (initial_offset, extra_gap) for justify modes."""
        horiz    = node.horizontal
        total    = sum(s for s in sizes if s)
        gap_total = node.gap * max(0, len(kids) - 1)
        space    = (inner.width if horiz else inner.height)
        leftover = space - total - gap_total
        if leftover <= 0:
            return (0, 0)
        if node.justify_spread and len(kids) > 1:
            return (0, leftover / (len(kids) - 1))
        if node.justify_center:
            return (leftover / 2, 0)
        return (0, 0)

    def build_child_rect(self, horiz, inner, pos, size):
        """Build a pygame.Rect for one child."""
        if horiz:
            return pygame.Rect(int(pos), inner.top, int(size), inner.height)
        return pygame.Rect(inner.left, int(pos), inner.width, int(size))

    # ══════════════════════════════════════════════════════════════
    # DEBUG
    # ══════════════════════════════════════════════════════════════

    def dump_tree(self, node=None, depth=0):
        """Print the widget tree with cached min sizes and rects."""
        if node is None:
            node = self.trunk
        indent = "  " * depth
        name   = node.name or node.my_name
        rect   = node.rect if node.rect else 'None'
        width_minimum  = getattr(node, 'width_minimum', '?')
        height_minimum  = getattr(node, 'height_minimum', '?')
        print(f"{indent}{type(node).__name__:15} {name:20} min=({width_minimum},{height_minimum})  rect={rect}")
        for child in node.children:
            self.dump_tree(child, depth + 1)