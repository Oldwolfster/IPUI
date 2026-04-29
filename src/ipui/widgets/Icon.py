from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style

class Icon(_BaseWidget):
    """
    desc:        Displays a small icon from the icons folder.
    when_to_use: Visual accent next to text in cards, titles, rows.
    best_for:    Feature lists, toolbars, buttons, navigation.
    example:     Icon(parent, "debug")
    api:         (display only — no custom methods)
    """
    def build(self):
        from ipui.utils.IconCache import IconCache
        size            = self.font.get_height() if self.font else Style.FONT_BODY.get_height()
        self.my_surface = IconCache.get(self.text, size)
