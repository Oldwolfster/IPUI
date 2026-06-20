# BannerPlate.py  NEW FILE — pane header bar. Raised double-Plate, glowing Title, optional right-aligned
#   action buttons (pushed over by a Spacer). text_align=CENTER → a lone centered title with buttons
#   suppressed by design. Replaces the hand-rolled banner_plate() that was copy-pasted across the baseball
#   tabs. Construction IS Attachment: BannerPlate(parent, "Title") and it's wired. Rename live via  .text
#   (the property proxies the inner Title, so only the header re-renders — never the whole banner).
from ipui import CENTER
from ipui.engine._BaseWidget import _BaseWidget


class BannerPlate(_BaseWidget):
    """A pane header bar: glowing title on the left, optional action buttons on the right.

        text         the caption (positional, like any Label). Re-assign  .text  to rename it live.
        data         buttons:  [("Caption", action)]  or  [("Caption", action, color_bg)]
        text_align   CENTER → centered title, NO buttons (by design); default (left) → title + buttons
        name         registry access

    Example:
        BannerPlate(parent, "Database", text_align=CENTER)
        BannerPlate(parent, title, data=[("Clone Table", self.clone_table_on_click)])
        bp = BannerPlate(parent, "CREATE VIEW: ...", data=[("Run", self.run, Style.COLOR_BUTTON_CTA)])
        bp.text = f"CREATE VIEW: {name}"             # updates in place, no pane rebuild
    """

    private_title = None                                     # inner Title handle; class default keeps the .text setter safe before build()

    # BannerPlate.py  method: build  NEW: text_align picks the layout — centered title, or left title + buttons
    def build(self):
        if self.text_align == CENTER: self.build_centered()
        else:                         self.build_left_with_buttons()

    # BannerPlate.py  method: build_centered  NEW: lone centered title (buttons intentionally suppressed)
    def build_centered(self):
        from ipui import Plate, Title
        banner             = Plate(Plate(self, pad=2), pad=2)
        self.private_title = Title(banner, self.private_caption, glow=True, pad=2, text_align=CENTER)

    # BannerPlate.py  method: build_left_with_buttons  NEW: left title, Spacer, then the action buttons
    def build_left_with_buttons(self):
        from ipui import Plate, Row, Title, Spacer
        banner             = Row(Plate(Plate(self, pad=2), pad=2))
        self.private_title = Title(banner, self.private_caption, glow=True, pad=2)
        Spacer(banner)
        self.add_buttons(banner)

    # BannerPlate.py  method: add_buttons  NEW: one Button per (caption, action[, color_bg]) spec in data
    def add_buttons(self, banner):
        from ipui import Button
        for caption, action, *extra in (self.data or []):
            Button(banner, caption, on_click=action, color_bg=(extra[0] if extra else None))

    # BannerPlate.py  method: text  NEW (getter): report the inner Title's caption — the live truth
    @property
    def text(self):
        if self.private_title is not None: return self.private_title.text
        return getattr(self, "private_caption", None)

    # BannerPlate.py  method: text  NEW (setter): rename in place — proxy to the inner Title, never rebuild the banner
    @text.setter
    def text(self, value):
        self.private_caption = value
        if self.private_title is not None: self.private_title.set_text(value)