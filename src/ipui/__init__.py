# ipui/__init__.py  NEW: Package entry point
#
# import ipui
# ipui.show(MyForm, "caption")
# ipui.docs()


__all__ = [
    # Public API functions
    "show", "docs", "back", "destroy", "active",
    # Core engine
    "IPUI", "Style",
    "_BaseForm", "BaseForm",
    "_BaseWidget",
    "_BaseHugeTooltip",
    "_basePane",
    "WidgetsDict",
    # Managers
    "MgrColor", "MgrFont", "Log",
    # Widgets
    "Button", "Card", "ChartWidget", "DropDown",
    "NetworkDiagram", "NeuronCell", "PowerGrid",
    "ProjectListItem", "Row", "CardCol", "CardRow", "Col",
    "SelectableListItem", "SelectionList", "Spacer",
    "TabStrip", "TextBox", "TextArea",
    # Label family
    "Title", "Heading", "Body", "Banner", "Detail",
    # Utilities
    "smart_format", "WidgetCatalog",
]
from ipui.engine.IPUI import IPUI
from ipui.Style        import Style

# ── Public API ──────────────────────────────────────────

def show(form_class, title=None):
    """Launch a form. The one function you need."""
    IPUI.show(form_class, title)

def docs():
    """Open the built-in showcase and documentation."""
    from forms.Showcase.FormShowcase import FormShowcase
    IPUI.show(FormShowcase, "IPUI Documentation Guide")
    
def back():                                                          
    """Navigate to the previous form."""                              
    IPUI.back()                                                      

def destroy(form_class):                                             
    """Remove a form from the stack and cache."""                     
    IPUI.destroy(form_class)                                         

def active():                                                        
    """Return the currently active form instance."""                  
    return IPUI.active()                                             

# ── Re-exports (so users can do: from ipui import Button) ──

from ipui.engine._BaseForm              import _BaseForm
from ipui.engine._BasePane              import _basePane
BaseForm =                              _BaseForm               # alias to preventexception
BasePane =                              _basePane               # alias so `from ipui import *` grabs it
from ipui.engine._BaseWidget            import _BaseWidget
from ipui.engine._BaseHugeTooltip       import _BaseHugeTooltip
from ipui.engine.MgrColor               import MgrColor
from ipui.engine.MgrFont                import MgrFont
from ipui.engine.WidgetsDict            import WidgetsDict
from ipui.engine.Log                    import Log
from ipui.widgets.Button                import Button
from ipui.widgets.Card                  import Card
from ipui.widgets.ChartWidget           import ChartWidget
from ipui.widgets.DropDown              import DropDown
from ipui.widgets.NetworkDiagram        import NetworkDiagram
from ipui.widgets.NeuronCell            import NeuronCell
from ipui.widgets.PowerGrid             import PowerGrid
from ipui.widgets.ProjectListItem       import ProjectListItem
from ipui.widgets.Row                   import Row,  CardRow, CardCol, Col
from ipui.widgets.SelectableListItem    import SelectableListItem
from ipui.widgets.SelectionList         import SelectionList
from ipui.widgets.Spacer                import Spacer
from ipui.widgets.TabStrip              import TabStrip
from ipui.widgets.Label                 import Title, Heading, Body, Banner, Detail
#from ipui.widgets.TextBox               import TextBox
from ipui.widgets.TextBox               import TextBox
from ipui.widgets.TextArea               import TextArea
from ipui.utils.general_text            import smart_format
from ipui.utils.WidgetCatalog           import WidgetCatalog
