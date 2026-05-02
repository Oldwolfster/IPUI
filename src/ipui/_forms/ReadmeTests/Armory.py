# Armory.py  New: cross-tab pane sharing source (README L911)
from ipui import *

class Armory(_BaseTab):

    def match_hints(self, parent):
        Title(parent, "Match Hints (Armory)")
        Body (parent, "Hints pane — referenced by another tab via dot notation")

    def match_settings(self, parent):                          # README L911-913
        Title(parent, "Match Settings (Armory)")
        Body (parent, "Referenced as 'Armory.match_settings'")
