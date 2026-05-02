# Forge.py  New: cross-tab pane sharing source (README L912)
from ipui import *

class Forge(_BaseTab):

    def workbench(self, parent):                               # README L912
        Title(parent, "Workbench (Forge)")
        Body (parent, "Referenced as 'Forge.workbench'")

    def preview(self, parent):                                 # README L912
        Title(parent, "Preview (Forge)")
        Body (parent, "Referenced as 'Forge.preview'")
