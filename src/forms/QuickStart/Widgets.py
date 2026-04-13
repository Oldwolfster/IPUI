from ipui import *

class Widgets(_BaseTab):
    def demo(self, parent):
        Title(parent, "Widget Playground")
        Button(parent, "Test Me", 
               on_click=lambda: self.form.show_modal("Nice!"))