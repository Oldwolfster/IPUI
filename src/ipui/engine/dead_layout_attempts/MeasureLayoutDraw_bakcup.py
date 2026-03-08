import pygame
from ipui.Style import Style
from ipui.engine import _BaseWidget
from ipui.engine._BaseWidget import _BaseWidget

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

class MeasureAndLayout:
    def __init__(self, myTrunk):
        self.myTrunk = myTrunk

    def dump_tree(self, w, depth=0):
        indent = "  " * depth
        name = getattr(w, 'name', None) or getattr(w, 'my_name', '?')
        text = getattr(w, 'text', '') or ''
        rect = w.rect if w.rect else 'None'
        print(f"depth={depth}\twidth_minimum={w.width_minimum} {indent}{type(w).__name__:15} name={name:20} text={text!r:20} rect={rect}")
        for child in w.children:
            self.dump_tree(child, depth + 1)

    def Runallthree(self):
        self.MeasureAndLayout(self.myTrunk)
        self.dump_tree(self.myTrunk)

    #this better be my longest function
    def MeasureAndLayout(self,trunk):
        self.measure_minimums(trunk)    #   1. Measure all children to get their minimums.
                                        #   2. Calculate fair share per flex weight from remaining space.
                                        #   3. Find violators: flex children whose minimum > their fair share.
                                        #   4. Lock the BIGGEST violator at its minimum, remove from flex pool.
                                        #   5. Repeat until no violators remain.
                                        #   6. Remaining pool members get their (now larger) fair share.
                                        #   7, MEET GOAL:  SET RECT


    def measure_minimums(self,trunk):
        self.clear_minimums(trunk)
        self.get_nodes_min(trunk)

    def clear_minimums(self, node):
        node.x_min = None
        node.y_min = None
        for child in node.children:
            self.clear_minimums(child)

    def get_nodes_min(self, node):
        """Set width_min and height_min on node after ensuring all children are known."""
        while True:
            unknown = self.any_child_unknown(node)
            if not unknown: break
            self.get_nodes_min(unknown) #get min for any unknown child

        myown_x, myown_y = self.get_my_min_from_surface(node)
        width_of_children, height_of_children = self.get_my_min_from_children(node)
        node.width_minimum       = max (myown_x, width_of_children)
        node.height_minimum       = max (myown_y, height_of_children)

    # MeasureAndLayout method: get_my_min_from_children  NEW: Sum children mins
    def get_my_min_from_children(self, node) -> tuple[int, int]:
        """Return sum of all children's minimums."""
        total_x = 0
        total_y = 0
        for child in node.children:
            if not child.visible or child.do_not_allocate:
                continue
            total_x += child.x_min
            total_y += child.y_min
        return (total_x, total_y)

    def get_my_min_from_surface(self, node) -> tuple[int, int]:
        """Return (width, height) of this widget's own surface plus frame, ignoring children."""
        if not node.my_surface:
            return (0, 0)
        my_x, my_y = node.my_surface.get_size()
        frame = (node.pad + node.border) * 2
        return (my_x + frame, my_y + frame)

    def any_child_unknown(self, node: _BaseWidget) -> _BaseWidget:
        """Return True if all descendants have width_min and height_min set."""
        for child in node.children:
            if child.x_min == None: return child
        return None
