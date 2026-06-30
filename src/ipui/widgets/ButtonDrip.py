# ButtonDrip.py  Update: fix double-wrap by storing callback in DRIP_ACTIVE

from ipui.widgets.Button import Button


class ButtonDrip(Button):
    """
    desc:        Button that auto-swaps text during drip work and reverts when dry.
    when_to_use: Any button that kicks off drip-based async work.
    best_for:    Run All, Train XGB, or any long-running drip operation.
    example:     ButtonDrip(parent, "Run All", data="Working...", on_click=do_work)
    api:         data = busy text shown while drip queue is active
    """
    DRIP_ACTIVE = {}

    def build(self):
        if not self.name:
            self.name = "btn_" + self.text.lower().replace(" ", "_")
            if self.form:
                self.form.widgets[self.name] = self
        active = self.name in ButtonDrip.DRIP_ACTIVE
        if active:
            original_text, original_cb   = ButtonDrip.DRIP_ACTIVE[self.name]
            self.text                    = self.data
            self.private_user_callback   = original_cb
        super().build()
        if self.data and self.on_click:
            if not active:
                self.private_user_callback = self.on_click
            self.on_click = self.drip_click_handler

    def drip_click_handler(self):
        if self.name in ButtonDrip.DRIP_ACTIVE:
            return
        ButtonDrip.DRIP_ACTIVE[self.name] = (self.text, self.on_click)
        self.text       = self.data
        self.my_surface = self.render_multiline(self.data)
        self.private_user_callback()
        self.form.ip.drip_when_dry(self.drip_revert)

    def drip_revert(self):
        entry = ButtonDrip.DRIP_ACTIVE.pop(self.name, None)
        if entry is None:
            return
        original_text = entry[0]
        widget = self.form.widgets.get(self.name)
        if widget:
            widget.text       = original_text
            widget.my_surface = widget.render_multiline(original_text)