from ipui.widgets.Card import Card
from ipui.widgets.CodeBox import CodeBox


class CodeScroller(Card):
    """
    desc:        A scrollable CodeBox. Scrolls vertically and horizontally with no caller setup.
    when_to_use: Showing source or SQL that's too tall or too wide for its pane.
    best_for:    The Workshop source view, long methods, wide CREATE VIEW statements.
    example:     CodeScroller(parent, data=self.my_method)
    api:         set_text(text)
    """

    # CodeScroller.py method: build  NEW: be a both-axis scroll container holding one CodeBox
    def build(self):
        code_bg = self.color_bg                       # capture before Card.build assigns its default
        super().build()                               # Card: background + sunken bevel
        self.scroll_v = True
        self.scroll_h = True
        self.pad      = 0

        if self.flex_height == 0: self.flex_height = 1
        self.private_codebox = CodeBox(self, data=self.data, start=self.start, end=self.end,
                                       initial_value=self.initial_value, color_bg=code_bg)

    # CodeScroller.py method: set_text  NEW: forward content swaps to the inner CodeBox
    def set_text(self, text):
        self.private_codebox.set_text(text)