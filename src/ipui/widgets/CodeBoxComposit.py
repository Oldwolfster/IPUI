# CodeBox.py  NEW FILE  Composite that prevents double-scrollbar setups.
# If parent already scrolls vertically, use CodeBoxNoScroll directly.
# Otherwise wrap in a card with both scrollbars (code overflows in both axes).

from ipui.engine._BaseWidget    import _BaseWidget
from ipui.widgets.Card          import Card
from ipui.widgets.CodeBoxNoScroll import CodeBoxNoScroll
# CodeBox.py  Update: method wrap_and_inject  -  default flex_height=1 so the outer composite doesn't collapse

class CodeBox(_BaseWidget):
    """
    desc:        Source code display. Adds scrollers automatically when needed.
    when_to_use: The default for showing code. Just works in any container.
    best_for:    Showcase tabs, Designer source view, README examples.
    example:     CodeBox(parent, data=__file__, initial_value="def my_method")
    api:         Pass-through to CodeBoxNoScroll (data, start, end, initial_value).
    """

    def build(self):
        if self.parent_has_scroller(): CodeBoxNoScroll(self, **self.passthrough())
        else:                          self.wrap_and_inject()

    def parent_has_scroller(self):
        return getattr(self.parent, "scroll_v", False)

    def wrap_and_inject(self):
        self.flex_height = 1  # FIX: was guarded by `is None`, but framework init sets it to 0
        card = Card(self, scroll_v=True, scroll_h=True, flex_height=1, pad=0)
        CodeBoxNoScroll(card, **self.passthrough())

    def passthrough(self):
        return dict(data=self.data, start=self.start, end=self.end, initial_value=self.initial_value)