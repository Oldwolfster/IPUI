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
    "_BaseForm",
    "_BaseWidget",
    "_BaseHugeTooltip",
    "_BaseTab",
    "WidgetsDict",
    # Managers
    "MgrColor", "MgrFont", "Log",
    # Input constants
    "Key", "Mouse",
    # Widgets
    "Button", "Card", "ChartWidget", "DropDown",
    "NetworkDiagram", "NeuronCell", "PowerGrid",
    "ProjectListItem", "Row", "CardCol", "CardRow", "Col",
    "SelectableListItem", "SelectionList", "Spacer",
    "TabStrip", "TextBox", "TextArea",
    # Label family
    "Title", "Heading", "Body", "Banner", "Detail",
    # Utilities
    "smart_format", "WidgetCatalog", "CodeBox","RecordSelector",
    "LEFT", "CENTER", "RIGHT",
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
from ipui.engine._BaseTab               import _BaseTab
from ipui.engine._BaseWidget            import _BaseWidget
from ipui.engine._BaseHugeTooltip       import _BaseHugeTooltip
from ipui.engine.MgrColor               import MgrColor
from ipui.engine.MgrFont                import MgrFont
from ipui.engine.Key                    import Key
from ipui.engine.Mouse                  import Mouse
from ipui.engine.WidgetsDict            import WidgetsDict

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
from ipui.widgets.CodeBox               import CodeBox
from ipui.widgets.TextBox               import TextBox
from ipui.widgets.TextArea              import TextArea
from ipui.widgets.RecordSelector        import RecordSelector
from ipui.utils.general_text            import smart_format
from ipui.utils.WidgetCatalog           import WidgetCatalog
from ipui.utils.general_text            import parse_int_list
from ipui.utils.MgrFileManager          import FileManager
from ipui.utils.Align                   import Align, LEFT,CENTER,RIGHT
from forms.NeuroForge.custom_widgets.Logger import Log