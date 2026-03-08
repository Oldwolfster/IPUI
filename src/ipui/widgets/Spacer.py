from ipui.engine._BaseWidget import _BaseWidget


class Spacer(_BaseWidget):
    """
    desc:        Invisible flex filler. Eats remaining space so siblings can breathe.
    when_to_use: Pushing widgets apart, right-aligning buttons, vertical breathing room.
    best_for:    The gap between a title and an action button in a header row.
    example:     Row(parent); Heading(row, "Title"); Spacer(row); Button(row, "Action")
    api:         (no methods — it's a spacer)
    """
    def build(self):
        self.width_flex     = self.width_flex or 1
        self.height_flex    = self.height_flex or 1
        self.my_name        = f"Spacer"
        self.pad            = 0
        self.gap            = 0
        self.border         = 0