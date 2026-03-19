from ipui import *                     # <======This is the only import you need for framework files.

class FormQuickStart(BaseForm):
    TAB_LAYOUT = {                     # This dict sets up your tabs and panes
        "Hello" : ["world"         ],  # Dictionary Key is tab name.  Values are panes.
        "Tab2"  : ["pane1", "pane2"],  # Ipui scaffolds a file matching tab name Hello.py
        "Tab3"  : ["pane3", "pane4"],  # (run and click a tab with no file)
    }                                  # IPUI searches same folder as 'Form' file
                                       # (and all descendant folders automatically)
