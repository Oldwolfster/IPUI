from ipui import *


class NewTab(_BaseTab):
    """Three-pane tab template — rename methods to match your tab_data strings."""

    def the_name_from_dict(self,parent):
        pass
        #TODO add content here!

    def welcome(self, parent):
        card = CardCol(parent, width_flex=True, height_flex=True)
        Title(card, "Welcome to IPUI", glow=True)

        sub = CardCol(card)
        Heading(sub, "Easy to get right:", glow=True)
        Heading(sub, "Hard to get wrong:", glow=True)
        Body(sub, "This pane was auto-generated.")
        Body(sub, "Edit the methods below to build your tab.")

    def select_project(self, parent):
        Title(parent, "Details", glow=True)

        sub = CardCol(parent)
        Body(sub, "Each method here becomes a pane.")
        Body(sub, "Name them to match your tab_data dict.")

        sub = CardCol(parent, height_flex=True, scrollable=True)
        Heading(sub, "Scrollable area:")
        for i in range(20):
            Body(sub, f"Item {i}")

    def metaphor(self, parent):
        header = Row(parent, justify_spread=True)
        Title(header, "Actions", glow=True)
        btn = Button(header, "Do Something", color_bg=Style.COLOR_PAL_GREEN_DARK)
        btn.on_click = lambda: print("clicked!")

        sub = CardCol(parent)
        Body(sub, "Buttons, inputs, lists —")
        Body(sub, "all go here.")