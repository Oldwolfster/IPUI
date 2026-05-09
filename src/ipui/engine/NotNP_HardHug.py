# NotNP_HardHug.py  Update: split into single-purpose methods; symmetric shrink keeps parent centered
from pygame import Rect
from ipui.engine.NotNP_HardWrap import NotNP_HardWrap


class NotNP_HardHug:
    """
    Pass 4 of 4: the hug pass.

    Bottom-up walk. Any child with hug_parent=True asks its parent to symmetrically
    shrink its rect to the bounding box of all visible siblings, plus the parent's
    own pad + border. Children never move; the parent stays centered on its
    original center, both edges crawling inward equally.

    Bounds:
        Floor   — never below the parent's min_width / min_height.
        Ceiling — never beyond the rect NotNP_HardLayout settled on. Hug only
                  shrinks; it never grows.

    Scope:
        - Mutates parent.rect only (x, y, width, height).
        - Does NOT touch surfaces, mins, flex weights, or scrollbar state.
        - Runs after Layout and Wrap have fully settled, so the rects it shrinks
          reflect final wrapped surface sizes.

    Orchestration lives in _BaseForm.sane_layout, not here.
    """

    def __init__(self, trunk):
        self.trunk  = trunk
        #self.engine = NotNP_HardWrap(trunk)

    def RunLayout(self):
        #self.engine.RunLayout()
        self.hug_walk(self.trunk)

    def hug_walk(self, node):
        if node is None: return
        for child in self.kids(node):
            self.hug_walk(child)
        if getattr(node, "hug_parent", False) and node.parent is not None:
            self.hug_child(node.parent)

    def hug_child(self, parent):
        #print("in hug")
        if parent.rect is None: return
        rect = self.kids_bbox(parent)
        #print(f"kids_bbox rect={rect}")
        if rect is None: return
        rect = self.add_parent_chrome(parent, rect)
        #print(f"add_parent_chrome rect={rect}")
        rect = self.clamp_to_ceiling(parent, rect)
        #print(f"clamp_to_ceiling rect={rect}")
        rect = self.clamp_to_floor(parent, rect)
        #print(f"clamp_to_floor rect={rect}")
        rect = self.recenter(parent, rect)
        #print(f"recenter rect={rect}")
        self.apply(parent, rect)


    def kids_bbox(self, parent):
        kids = [k for k in self.kids(parent) if k.rect is not None]
        if not kids: return None
        rects = [self.kid_visible_rect(k) for k in kids]
        min_x = min(r.left for r in rects)
        min_y = min(r.top for r in rects)
        max_x = max(r.right for r in rects)
        max_y = max(r.bottom for r in rects)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)



    def kid_visible_rect(self, kid):
        if kid.my_surface is None:
            return kid.rect
        x, y = kid.compute_content_position()
        w, h = kid.my_surface.get_size()
        return Rect(x, y, w, h)

    def add_parent_chrome(self, parent, rect):
        return rect.inflate(2 * (parent.pad_x + parent.border),
                            2 * (parent.pad_y + parent.border))

    def clamp_to_ceiling(self, parent, rect):
        rect.width  = min(rect.width,  parent.rect.width)
        rect.height = min(rect.height, parent.rect.height)
        return rect

    def clamp_to_floor(self, parent, rect):
        rect.width  = max(rect.width,  parent.min_width  or 0)
        rect.height = max(rect.height, parent.min_height or 0)
        return rect

    def recenter(self, parent, rect):
        rect.center = parent.rect.center
        return rect

    def apply(self, parent, rect):
        #print(f"[HUG] {type(parent).__name__} wid={parent.widget_id}: "
        #      f"({parent.rect.x},{parent.rect.y},{parent.rect.width}x{parent.rect.height}) "
        #      f"→ ({rect.x},{rect.y},{rect.width}x{rect.height})")
        parent.rect.x      = rect.x
        parent.rect.y      = rect.y
        parent.rect.width  = rect.width
        parent.rect.height = rect.height

    def kids(self, node):
        return getattr(node, "visible_children", []) or []