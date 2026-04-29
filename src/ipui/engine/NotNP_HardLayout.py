import pygame
from ipui.Style import Style
from ipui.engine import _BaseWidget
from ipui.engine._BaseWidget import _BaseWidget

# ──────────────────────────────────────────────────────────────────
# ITERATIVE FLEX ALLOCATION — Goal: set rect for each widget in tree
# ──────────────────────────────────────────────────────────────────
# Pussies call flex layout np-hard adjacent... the first thing that
# should scare you about that is there is no such thing as np-hard adjacent.
# there is np, p, np complete, np hard.... hmm  don't see adjacent anywhere.
# Flex layout is a combinatorial constraint problem. CSS spent 20 years
# on it. We use a greedy iterative algorithm that handles real-world
# cases perfectly:
#
#   Priority 1:  width_min / height_min is king. Nothing renders smaller.
#   Priority 2:  Symmetry of flex weights honored when space allows.
#
# Algorithm (resolve_flex):
#   1. Lock non-flex children at their minimum.
#   2. Calculate fair share per flex weight from remaining budget.
#   3. Find violators: flex children whose minimum > their fair share.
#   4. Lock the BIGGEST violator at its minimum, remove from flex pool.
#   5. Repeat until no violators remain.
#   6. Remaining pool members get their (now larger) fair share.
#   7. Set rect on every kid; recurse.
# ══════════════════════════════════════════════════════════════════
# Two phases:
#   MEASURE — bottom-up. Cache width_minimum / height_minimum.
#   LAYOUT  — top-down.  Resolve flex, assign rect.
#
# DRAW is NOT a phase of this engine — _BaseWidget owns drawing,
# called from _BaseForm.render() after sane_layout finishes.
#
# Widgets with custom layout (PowerGrid, NetworkDiagram) override
# layout(rect) and handle their own children — the engine skips them.
import pygame


class MeasureAndLayout:

    """
    Pass 1 of 4 (and Pass 3 conditionally): the layout engine.

    Single source of truth for min sizes, flex resolution, rect assignment, and
    scrollbar math. Two phases internally:

        MEASURE — bottom-up. Cache width_minimum / height_minimum on every node
                  from its surface, its children, frame (pad + border), and gap.
                  Flex children clamp their min to frame_x / frame_y so they
                  agree to be squeezable.

        LAYOUT  — top-down. Iterative greedy flex solver: lock biggest violator
                  at its min, redistribute fair share to the rest, repeat until
                  no violators remain. Then assign rects, recurse into kids.

    Widgets with a custom layout() method handle their own children — the engine
    hands them their rect and steps back.

    Pass 1 establishes rects from single-line surfaces. If MeasureAndWrap then
    re-renders any text-leaf surfaces, _BaseForm.sane_layout calls RunLayout()
    again as Pass 3 with the new surface dimensions. The flex algorithm is
    deterministic given the same inputs, so two calls converge cleanly.

    Orchestration lives in _BaseForm.sane_layout, not here.
    """
    def __init__(self, trunk):
        self.trunk = trunk

    # ══════════════════════════════════════════════════════════════
    # PUBLIC — called by _BaseForm.render()
    # ══════════════════════════════════════════════════════════════

    def RunLayout(self):
        root = self.compute_root_rect()
        self.measure_tree(self.trunk)

        self.layout_node(self.trunk, root)
       # self.dump_tree()

    def compute_root_rect(self):
        screen = pygame.display.get_surface().get_rect()
        margin = Style.TOKEN_GAP
        margin = 2 # Change to new token Style.TOKEN_GAP
        return screen.inflate(-margin * 2, -margin * 2)

    # ══════════════════════════════════════════════════════════════
    # PHASE 1: MEASURE — bottom-up, cache width_minimum / height_minimum
    # ══════════════════════════════════════════════════════════════

    def measure_tree(self, node):
        """Recursively measure all descendants, then this node."""
        for child in node.visible_children:
            self.measure_tree(child)
        self.measure_node(node)


    def measure_node(self, node):
        """Set width_minimum / height_minimum on one node. Children already measured."""
        width_of_surface,   height_of_surface = self.measure_surface(node)
        width_of_children,  height_of_children = self.measure_children(node)
        node.width_minimum  = max(width_of_surface, width_of_children)
        node.height_minimum = max(height_of_surface, height_of_children)
        self.cap_scrollable_min(node)
        if node.width_flex > 0: node.width_minimum   = node.frame_x
        if node.height_flex > 0: node.height_minimum = node.frame_y


    def cap_scrollable_min(self, node):
        """Scrollable containers keep content size for scroll math but report minimal min to flex."""
        if not node.scrollable: return
        if node.horizontal:
            node.content_size  = node.width_minimum
            node.width_minimum = node.frame_x
        else:
            node.content_size   = node.height_minimum
            node.height_minimum = node.frame_y



    def measure_surface(self, node):
        """Min size from this widget's own surface + frame."""
        if not node.my_surface:
            return (0, 0)
        w, h = node.my_surface.get_size()
        return (w + node.frame_x, h + node.frame_y)


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
        if node.horizontal:
            return (main + node.frame_x, cross + node.frame_y)
        return (cross + node.frame_x, main + node.frame_y)

    # ══════════════════════════════════════════════════════════════
    # PHASE 2: LAYOUT — top-down, iterative flex, sets rect
    # ══════════════════════════════════════════════════════════════

    def layout_node(self, node, rect):
        """Assign rect to node, then lay out its children."""
        if rect is None : return                       # NEW
        node.rect       = rect
        if self.check_for_custom_layout(node): return
        kids            = node.visible_children
        if not kids     : return
        inner           = self.compute_inner(node, rect)
        if node.scrollable:
            inner = self.apply_scroll(node, inner)
        self.layout_kids(node, kids, inner)

    # MeasureAndLayout.py method: check_for_custom_layout  Update: use hasattr
    def check_for_custom_layout(self, node):
        """Widget overrides layout() — let it handle its own children."""
        if 'layout' not in type(node).__dict__: return False
        node.layout(node.rect)
        return True


    def compute_inner(self, node, rect):
        """Content area inside pad + border."""
        return rect.inflate(-node.frame_x, -node.frame_y)

    def layout_kids(self, node, kids, inner):
        """Solve flex, compute rects, recurse into children."""
        sizes = self.resolve_flex(node, kids, inner)
        self.assign_rects(node, kids, inner, sizes)



    def apply_scroll(self, node, inner):
        """Adjust inner rect for scroll state."""
        #content   = node.height_minimum if not node.horizontal else node.width_minimum
        content   = getattr(node, 'content_size', node.height_minimum)
        getattr(node, 'content_size', node.height_minimum)
        main_size = inner.width if node.horizontal else inner.height
        #print(f"SCROLL: {node.display_name} content={content} main_size={main_size} kids={len(node.visible_children)}")    # NEW
        node.scroll_active = content > main_size
        if not node.scroll_active:
            node.scroll_offset = 0
            return inner
        bar_w      = Style.TOKEN_SCROLLBAR
        inner      = pygame.Rect(inner.left, inner.top, inner.width - bar_w, inner.height)
        max_scroll = max(0, content - inner.height)
        node.scroll_offset = max(0, min(node.scroll_offset, max_scroll))
        return inner

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
            rect = self.build_child_rect(horiz, inner, pos, sizes[i],child)
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

    def build_child_rect(self, horiz, inner, pos, size, child=None):
        """Build a pygame.Rect for one child."""
        if horiz:
            return pygame.Rect(int(pos), inner.top, int(size), inner.height)
        w = inner.width
        x = inner.left
        if child and getattr(child, 'fit_content', False) and child.width_flex == 0:
            w = min(w, child.width_minimum)
            x = inner.left + (inner.width - w) // 2
        return pygame.Rect(x, int(pos), w, int(size))
    # ══════════════════════════════════════════════════════════════
    # DEBUG
    # ══════════════════════════════════════════════════════════════

    def dump_tree(self, node=None, depth=0):
        """Print the widget tree with cached min sizes and rects."""
        if node is None:
            node = self.trunk
        indent = "  " * depth
        name   = node.name or node.display_name
        rect   = node.rect if node.rect else 'None'
        width_minimum  = getattr(node, 'width_minimum', '?')
        height_minimum  = getattr(node, 'height_minimum', '?')
        print(f"{indent}{type(node).__name__:15} {name:20} min=({width_minimum},{height_minimum})  rect={rect}")
        for child in node.children:
            self.dump_tree(child, depth + 1)