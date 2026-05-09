from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style

class Icon(_BaseWidget):
    """
    desc:        Displays a small icon from the icons folder.
    when_to_use: Visual accent next to text in cards, titles, rows.
    best_for:    Feature lists, toolbars, buttons, navigation.
    example:     Icon(parent, "debug")
    api:         scale by setting data, data=1 is no change.  data = .5 cuts size in half
    """
    def build(self):
        from ipui.utils.IconCache import IconCache
        if self.data    ==None: self.data=1
        size            = self.font.get_height() if self.font else Style.FONT_BODY.get_height()
        size            = int(size * self.data / 1) if self.data else size   # NEW
        self.my_surface = IconCache.get(self.text, size)
