# Widgets.py  New: external _BaseTab demo (README L194-203, L141-145)
from ipui import *

# README L194-203: "The class name can be anything, as long as it inherits from _BaseTab"
# README L141-145: trimmed Widgets snippet
class TotallyWhateverNameYouWant(_BaseTab):

    def demo(self, parent):                                                  # README L201
        Title (parent, "Hello from Widgets.py")                              # README L202
        Body  (parent, "External _BaseTab file — golden rule: this wins")   # README L209
        Button(parent, "Test Me",                                            # README L144
               on_click=lambda: self.form.show_modal("Nice"))                # README L145

    def demo2(self, parent):                                                 # second pane in Widgets tab
        Heading(parent, "Second pane in the Widgets tab")
        Body   (parent, "Two-pane tab demonstration")
