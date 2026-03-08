# frmPro.py — new file

from ipui.widgets.Row import CardCol
from ipui.widgets.Label import Title, Heading, Body


class frmPro:

    @staticmethod
    def build(parent):
        card = CardCol(parent, width_flex=True, height_flex=True)
        Title(card, "Pro Tools", glow=True)

        sub = CardCol(card)
        Heading (sub, "Everything. One Screen.")
        Body    (sub, "Armory settings on the left.")
        Body    (sub, "Architecture workbench in the middle.")
        Body    (sub, "Live network preview on the right.")

        sub = CardCol(card)
        Heading (sub, "For Power Users:")
        Body    (sub, "Once you're comfortable with the\nArmory and Workbench tabs separately,\nPro puts it all together.")

        sub     = CardCol(card)
        Heading (sub, "Default Architecture:")
        Body    (sub, "8 → 4 → 1")
        Body    (sub, "A solid starting point for most problems.")

        sub = CardCol(card)
        Heading(sub, "Coming Soon!", glow=True)