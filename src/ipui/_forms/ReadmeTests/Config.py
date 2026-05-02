# Config.py  New: external _BaseTab two-pane example (README L867-877)
from ipui import *

class Config(_BaseTab):

    def settings(self, parent):                  # README L870
        Title(parent, "Settings")                # README L871
        Body (parent, "Settings live here")

    def hyperparams(self, parent):               # README L874
        Title(parent, "Hyperparameters")         # README L875
        Body (parent, "Hyperparams live here")
