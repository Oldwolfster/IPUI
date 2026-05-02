# MgrSanity.py  New: Post-layout sanity checker — detects invisible content
#
# Called by _BaseForm.render() right after layout completes.
# Walks the widget tree once looking for "collapsed" containers —
# widgets whose children are invisible because the container
# got no space on either axis. Fires EZ.err with diagnosis and fix.
#
# Design:
#   1. is_starved()  — pure symptom detection, returns "height", "width", or None
#   2. diagnose()    — runs a checklist of known root causes
#   3. Each check_cause_* either fires EZ.err (never returns) or returns silently
#   4. report_unknown() — fallback, always fires
#
# Adding a new root cause = one new check_cause_* method + one line in diagnose().

import inspect
from ipui.utils.EZ import EZ


class MgrSanity:

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — called from _BaseForm.render()
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def check_tree(cls, root):
        """Walk every node. If collapsed, diagnose it."""
        axis = cls.is_starved(root)
        if axis:
            cls.diagnose(root, axis)
        for child in root.children:
            cls.check_tree(child)

    # ══════════════════════════════════════════════════════════════
    # SYMPTOM DETECTION — is this node visually collapsed?
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def is_starved(cls, node):
        """Returns "height", "width", or None."""
        if not node.rect:                       return None
        if not node.visible:                    return None
        if len(node.visible_children) == 0:     return None
        if not cls.has_content_children(node):  return None
        threshold = node.frame_size + 4
        if node.rect.height <= threshold:       return "height"
        if node.rect.width  <= threshold:       return "width"
        return None

    @classmethod
    def has_content_children(cls, node):
        """True if at least one visible child wants real space."""
        for child in node.visible_children:
            if child.height_minimum and child.height_minimum > 0:
                return True
            if child.width_minimum and child.width_minimum > 0:
                return True
        return False

    # ══════════════════════════════════════════════════════════════
    # DIAGNOSIS — run the cause checklist
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def diagnose(cls, node, axis):
        """Try each known root cause. First match fires EZ.err and never returns."""
        ctx = cls.build_context                     (node, axis)
        cls.check_cause_flex_starved_by_sibling     (node, ctx)
        cls.check_cause_scroll_v_no_flex_ancestor (node, ctx)
        cls.check_cause_flex_no_flex_ancestor       (node, ctx)
        cls.check_cause_all_children_flex           (node, ctx)  # NEW
        cls.check_cause_content_siblings_overflow   (node, ctx)
        # ↑ Future causes go here as one-liners ↑
        cls.report_unknown                          (node, ctx)


    @classmethod
    def build_context(cls, node, axis):
        """Gather common info once so check_cause_* methods stay focused."""
        flex_attr = "height_flex" if axis == "height" else "width_flex"
        if axis == "height":
            child_need = max((c.height_minimum for c in node.visible_children if c.height_minimum), default=0)
            got = node.rect.height
        else:
            child_need = max((c.width_minimum for c in node.visible_children if c.width_minimum), default=0)
            got = node.rect.width
        return {
            "label": cls.widget_label(node),
            "child_need": child_need,
            "got": got,
            "origin": cls.find_origin(node),
            "axis": axis,
            "flex_attr": flex_attr,
        }
    # ══════════════════════════════════════════════════════════════
    # ROOT CAUSE #1: Flex child starved by a sibling
    # ══════════════════════════════════════════════════════════════
    # TRIGGER EXAMPLE (height):
    #   card_a = CardCol(parent, height_flex=1)   # gets ~1% — starved
    #   Title(card_a, "I disappear")
    #   card_b = Card(parent, height_flex=99)        # hogs the budget
    # TRIGGER EXAMPLE (width):
    #   col_a = Col(row, width_flex=1)            # gets ~1% — starved
    #   Title(col_a, "I disappear")
    #   col_b = Col(row, width_flex=99)              # hogs the budget
    # FIX: Remove flex from the victim, or increase its weight.

    @classmethod
    def check_cause_flex_starved_by_sibling(cls, node, ctx):
        flex_attr = ctx["flex_attr"]
        node_flex = getattr(node, flex_attr, 0)
        if node_flex <= 0:                          return
        if not node.parent:                         return
        bully = cls.find_bully_sibling(node, flex_attr)
        if not bully:                               return
        bully_flex  = getattr(bully, flex_attr)
        bully_label = cls.widget_label(bully)
        cls.fire(ctx,
            f"ROOT CAUSE: Flex child starved by sibling ({ctx['axis']}).\n"
            f"\n"
            f"{ctx['label']} has {flex_attr}={node_flex}\n"
            f"but its sibling {bully_label} has {flex_attr}={bully_flex}.\n"
            f"The sibling claims {cls.flex_percent(bully_flex, node_flex)}% of the space,\n"
            f"leaving almost nothing.\n"
            f"\n"
            f"FIX: Remove {flex_attr} from {ctx['label']} and let it\n"
            f"size to its content. Or increase its flex weight.\n"
            f"\n"
            f"Example:  "
            f"  {type(node).__name__}(parent)  # sizes to content, no competition"
        )

    @classmethod
    def find_bully_sibling(cls, node, flex_attr):
        """Find a sibling whose flex weight is 10x or more than node's."""
        node_flex = getattr(node, flex_attr, 0)
        siblings  = node.parent.visible_children
        for sib in siblings:
            if sib is node:                         continue
            sib_flex = getattr(sib, flex_attr, 0)
            if sib_flex <= 0:                       continue
            if sib_flex >= node_flex * 10:
                return sib
        return None

    @classmethod
    def flex_percent(cls, bully_flex, victim_flex):
        """What percent of flex budget does the bully claim?"""
        total = bully_flex + victim_flex
        if total == 0:                              return 0
        return round(bully_flex / total * 100)

    # ══════════════════════════════════════════════════════════════
    # ROOT CAUSE #2: Scrollable container under a non-flex ancestor
    # ══════════════════════════════════════════════════════════════
    # TRIGGER Example: 
    #   wrapper = CardCol(parent)                    # no height_flex — content-sizes
    #   scroller = CardCol(wrapper, scroll_v=True) # scroll_v collapses min-height
    #   Title(scroller, "I disappear")
    # FIX: Add height_flex=1 to the wrapper.

    @classmethod
    def check_cause_scroll_v_no_flex_ancestor(cls, node, ctx):
        if not node.scroll_v:                     return
        flex_attr = ctx["flex_attr"]
        blocker   = cls.find_non_flex_ancestor(node, flex_attr)
        if not blocker:                             return
        blocker_label = cls.widget_label(blocker)
        cls.fire(ctx,
            f"ROOT CAUSE: Scrollable container under non-flex ancestor ({ctx['axis']}).\n"
            f"\n"
            f"{ctx['label']} is scroll_v, which collapses its minimum\n"
            f"{ctx['axis']} to zero. But its ancestor {blocker_label} has no\n"
            f"{flex_attr}, so it content-sizes to zero and collapses\n"
            f"the scroll_v child.\n"
            f"\n"
            f"FIX: Add {flex_attr}=1 to {blocker_label}.\n"
            f"\n"
            f"Example:  "
            f"  {type(blocker).__name__}(parent, {flex_attr}=1)"
        )

    # ══════════════════════════════════════════════════════════════
    # ROOT CAUSE #3: Flex child under a non-flex ancestor
    # ══════════════════════════════════════════════════════════════
    # TRIGGER Example: 
    #   wrapper = CardCol(parent)                    # no height_flex — content-sizes
    #   inner   = CardCol(wrapper, height_flex=1)    # wants flex space
    #   Title(inner, "I disappear")                  # but wrapper has none to give
    # FIX: Add height_flex=1 to the wrapper.

    @classmethod
    def check_cause_flex_no_flex_ancestor(cls, node, ctx):
        flex_attr = ctx["flex_attr"]
        node_flex = getattr(node, flex_attr, 0)
        if node_flex <= 0:                          return
        blocker = cls.find_non_flex_ancestor(node, flex_attr)
        if not blocker:                             return
        blocker_label = cls.widget_label(blocker)
        cls.fire(ctx,
            f"ROOT CAUSE: Flex child under non-flex ancestor ({ctx['axis']}).\n"
            f"\n"
            f"{ctx['label']} has {flex_attr}={node_flex} but its\n"
            f"ancestor {blocker_label} has no {flex_attr}, so there is\n"
            f"no space to distribute.\n"
            f"\n"
            f"FIX: Add {flex_attr}=1 to {blocker_label}.\n"
            f"\n"
            f"Example:  "
            f"  {type(blocker).__name__}(parent, {flex_attr}=1)"
        )

    # ══════════════════════════════════════════════════════════════
    # ROOT CAUSE #4: All children are flex, parent has no flex to give them.
    # ══════════════════════════════════════════════════════════════

    # TRIGGER Example: 
    #   row = Row(parent)
    #   box = CardCol(row)                        # no width_flex — content-sizes
    #   Banner(box, "IPUI", text_align=CENTER)    # text_align=CENTER auto-sets width_flex=1
    #   # box asks children "how wide are you?" — they all say 0 (flex). Box collapses.
    # FIX: Add width_flex to the parent container.

    @classmethod
    def check_cause_all_children_flex(cls, node, ctx):
        flex_attr = ctx["flex_attr"]
        if getattr(node, flex_attr, 0) > 0:             return  # node already has flex — not this cause
        all_flex = all(getattr(c, flex_attr, 0) > 0 for c in node.visible_children)
        if not all_flex:                                 return
        cls.fire(ctx,
                 f"ROOT CAUSE: All children want flex but parent has none ({ctx['axis']}).\n"
                 f"\n"
                 f"{ctx['label']} has no {flex_attr}, so it sizes to content.\n"
                 f"But all its children have {flex_attr}, so they report zero\n"
                 f"minimum {ctx['axis']}. The parent collapses to nothing.\n"
                 f"\n"
                 f"FIX: Add {flex_attr}=1 to {ctx['label']}.\n"
                 f"\n"
                 f"Example:  "
                 f"  {type(node).__name__}(parent, {flex_attr}=1)"
                 )


    # TRIGGER Example: 
    #   def my_pane(self, parent):
    #       CardCol(parent)  # big content
    #       CardCol(parent)  # big content
    #       CardCol(parent)  # big content
    #       Card(parent, scroll_v=True, height_flex=1)  # gets nothing — siblings ate it all
    # FIX: Wrap the content siblings in a scroll_v container, or reduce content.

    # MgrSanity.py method: check_cause_content_siblings_overflow  Update: check leftover vs node frame
    @classmethod
    def check_cause_content_siblings_overflow(cls, node, ctx):
        flex_attr = ctx["flex_attr"]
        node_flex = getattr(node, flex_attr, 0)
        if node_flex <= 0:                          return
        if not node.parent:                         return
        siblings = node.parent.visible_children
        content_total = 0
        for sib in siblings:
            if sib is node:                         continue
            if getattr(sib, flex_attr, 0) > 0:      continue
            min_attr = "height_minimum" if ctx["axis"] == "height" else "width_minimum"
            content_total += getattr(sib, min_attr, 0) or 0
        parent_size = node.parent.rect.height if ctx["axis"] == "height" else node.parent.rect.width
        if content_total <= 0:                      return
        available = parent_size - node.parent.frame_size - content_total
        if available > node.frame_size + 4:         return
        cls.fire(ctx,
                 f"ROOT CAUSE: Content siblings consumed all available space ({ctx['axis']}).\n"
                 f"\n"
                 f"{ctx['label']} has {flex_attr}={node_flex} and wants leftover space,\n"
                 f"but its content-sized siblings need {content_total}px total,\n"
                 f"which leaves only {available}px — not enough to display anything.\n"
                 f"\n"
                 f"FIX: Reduce the content above, or wrap the sibling content\n"
                 f"in a scroll_v container so it doesn't consume all the space."
                 )

    # ══════════════════════════════════════════════════════════════
    # FALLBACK — unknown cause
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def report_unknown(cls, node, ctx):
        flex_attr = ctx["flex_attr"]
        cls.fire(ctx,
            f"Unknown root cause — please report this!\n"
            f"\n"
            f"Axis: {ctx['axis']}\n"
            f"Widget: {ctx['label']}\n"
            f"Type: {type(node).__name__}\n"
            f"{flex_attr}: {getattr(node, flex_attr, 0)}, scroll_v: {node.scroll_v}\n"
            f"Parent: {cls.widget_label(node.parent) if node.parent else 'None'}\n"
            f"\n"
            f"This helps us add a new root cause classifier."
        )

    # ══════════════════════════════════════════════════════════════
    # SHARED HELPERS
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def fire(cls, ctx, cause_text):
        """Build the full message and fire EZ.err. Never returns."""
        msg = (
            f"A widget collapsed and cannot display its children.\n"
            f"\n"
            f"{cause_text}\n"
            f"TIP: If you can't figure out which widget is the problem\n"
            f"TIP: Add name='anyname' to widgets in the area\n"
            f"TIP: That name will be listed in this error\n"
        )
        EZ.err(msg, origin=ctx["origin"])

    @classmethod
    def find_non_flex_ancestor(cls, node, flex_attr):
        """Walk up from parent. Return the first ancestor with no flex on this axis.
           Stop at the root (parent is None). Return None if all ancestors flex."""
        walker = node.parent
        while walker:
            if walker.parent is None:               return None   # root — stop
            if getattr(walker, flex_attr, 0) <= 0:  return walker
            walker = walker.parent
        return None

    @classmethod
    def widget_label(cls, node):
        name = node.name or node.display_name
        return f"{type(node).__name__}('{name}')"

    # ══════════════════════════════════════════════════════════════
    # ORIGIN TRACING — find PyCharm-clickable link to user's code
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def find_origin(cls, node):
        pane_owner, method_name = cls.find_pane_builder(node)
        if pane_owner and method_name:
            return cls.build_origin_link(pane_owner, method_name)
        return "Unknown location — could not trace to a pane builder"

    @classmethod
    def find_pane_builder(cls, node):
        from ipui.widgets.Pane import Pane
        walker = node
        while walker:
            if isinstance(walker, Pane):
                return cls.resolve_builder_from_pane(walker)
            walker = walker.parent
        return (None, None)

    @classmethod
    def resolve_builder_from_pane(cls, pane):
        form = pane.form
        if not form or not hasattr(form, 'tab_strip'):
            return (None, None)
        strip = form.tab_strip
        if not strip:
            return (None, None)
        tab_name = strip.active_tab
        entries  = strip.tab_layout.get(tab_name, [])
        for i, entry in enumerate(entries):
            if i < len(strip.panes) and strip.panes[i] is pane:
                builder = entry[0] if isinstance(entry, tuple) else entry
                if isinstance(builder, str) and "." not in builder:
                    instance = strip.tab_cache.get(tab_name, form)
                    return (instance, builder.replace(" ", "_"))
                elif isinstance(builder, str) and "." in builder:
                    source_tab, method = builder.split(".", 1)
                    instance = strip.tab_cache.get(source_tab)
                    return (instance, method)
        return (None, None)

    @classmethod
    def build_origin_link(cls, owner, method_name):
        class_name  = type(owner).__name__
        method      = getattr(owner, method_name, None)
        if not method:
            return f"Class: {class_name}  Method: {method_name}"
        try:
            source_file = inspect.getfile(method)
            lines, start = inspect.getsourcelines(method)
            return f'File: "{source_file}"  Class: {class_name}  Method: {method_name}'
        except (TypeError, OSError):
            pass
        return f"Class: {class_name}  Method: {method_name}"