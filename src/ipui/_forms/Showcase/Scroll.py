from ipui import *


class Scroll(_BaseTab):

    def left_pane(self, parent):
        Body(parent, "Filename: Scroll.py")
        Body(parent, "Method: left_pane")
        Body(parent, "Add content here!")


    def test_here(self, parent):
        Title(parent, "scroll_h shakedown", text_align=CENTER)

        # 1. The naked widget — should show a bar across the bottom
        Card(parent, scroll_h=True)
        #Spacer(parent)
        # 2. A widget with content — bar should still appear at the bottom
        card = Card(parent, scroll_h=True)
        Body(card, "I have content. The bar lives below me.")
        Body(card, "If you can see a bar at the bottom of this card, Step 1 works.")
        #Spacer(parent)

        # 3. A non-Card widget — the cathedral test
        # If the bar shows on a Banner, the mixin truly works on any widget.
        #Banner(parent, "scroll_h on a Banner That's really really big", scroll_h=True, glow=True)
        #Spacer(parent)
        #4.
        row = Row(parent, scroll_h=True,pad=60)
        for i in range (20):
            Button(row,f"I am button {i}",  on_click=lambda i=i: self.form.show_modal(f"You clicked button {i}"))


    def right_pane(self, parent):
        Body(parent, "Filename: Scroll.py")
        Body(parent, "Method: right_pane")
        Body(parent, "Add content here!")
