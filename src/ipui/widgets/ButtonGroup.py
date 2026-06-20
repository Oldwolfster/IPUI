# ButtonGroup.py  NEW FILE — mutually-exclusive button group (segmented selector). Owns its selection and
#   recolors its own buttons in place (color_bg is read at draw time) so it NEVER triggers a pane rebuild.
from ipui.Style import Style
from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.Button import Button          # widgets live in ipui.widgets (same as CopyButton)


class ButtonGroup(_BaseWidget):
    """A row of buttons where exactly one is selected. The widget owns the selection — the caller keeps
    no shadow state and never calls refresh_pane.

        data           options:  ["Entity","Metric"]   OR   [("readme","ReadMe"), ...]  (value, label)
        initial_value  selected value at build; None → first option
        on_change      callback(value) — fired on USER click only (programmatic .value set is silent)
        name           registry access; get/set the selection via  .value

    Example:
        ButtonGroup(parent, data=Registry.KINDS, on_change=self.set_kind, name="grp_kind")
        kind = self.form.widgets["grp_kind"].value          # read the truth
        self.form.widgets["grp_kind"].value = "Metric"      # set it (no on_change fires)
    """

    COLOR_ON  = Style.COLOR_BUTTON_CTA
    COLOR_OFF = Style.COLOR_BUTTON_BG

    def build(self):
        self.horizontal      = True                              # lay the buttons in a row
        self.options         = self.normalize_options(self.data)
        self.private_buttons = {}                                # value -> Button
        self.private_value   = self.first_value()
        self.build_buttons()
        self.paint_selection()

    def normalize_options(self, data):
        """Accept ['a','b'] or [('a','A'),('b','B')] → [(value, label), ...]."""
        out = []
        for item in (data or []):
            if isinstance(item, (list, tuple)): out.append((item[0], item[1]))
            else:                               out.append((item, item))
        return out

    def first_value(self):
        if self.initial_value is not None: return self.initial_value
        return self.options[0][0] if self.options else None

    def build_buttons(self):
        from ipui import Plate
        from ipui import Row
        plate = Row(Plate(self,pad=2),pad=2)
        for value, label in self.options:
            btn = Button(plate, label, on_click=lambda v=value: self.handle_pick(v))
            self.private_buttons[value] = btn

    def handle_pick(self, value):
        """User clicked a button — select it and notify."""
        self.set_value(value, fire=True)

    def set_value(self, value, fire=False):
        """Select a value. on_change fires only when the user did it (fire=True)."""
        self.private_value = value
        self.paint_selection()
        if fire and self.on_change is not None: self.on_change(value)

    def paint_selection(self):
        """Recolor in place — color_bg is read at draw time, so no rebuild is needed."""
        for value, btn in self.private_buttons.items():
            btn.color_bg = ButtonGroup.COLOR_ON if value == self.private_value else ButtonGroup.COLOR_OFF

    @property
    def value(self):
        """The currently selected value."""
        return self.private_value

    @value.setter
    def value(self, v):
        self.set_value(v, fire=False)                            # programmatic set is silent