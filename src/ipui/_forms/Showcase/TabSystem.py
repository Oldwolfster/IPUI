from ipui import *
import inspect

class TabSystemShowcase(_BaseTab):
    """The tab that sells tabs."""
    # ══════════════════════════════════════════════════════════════
    #  LEFT PANE — Explain and demo with a simple example
    # ══════════════════════════════════════════════════════════════

    def explain(self, parent):
        scroller = CardCol(parent, scroll_v=True)
        self.explain_header   (scroller)
        #self.explain_concept  (scroller)
        self.explain_example  (scroller)
        self.explain_pane    (scroller)
        #self.explain_discovery(scroller)

    def explain_header(self, parent):
        card = Col(parent)
        row = Row(card)
        Icon(row, "tab_system")
        Heading(row, "TAB_LAYOUT is the blueprint of your app!")
        Spacer(card)
        row = Row(card)
        #Icon(row, "muscle")
        # Heading(row, "To keep it simple - The key does double duty")
        row2 = CardRow(card)
        c1 = Plate(row2, width_flex=1,name="myplate")
        c2 = Plate(row2, width_flex=1)
        Heading(c1, "Each key is a tab\nin your form", text_align=CENTER)
        Heading(c2, "Each list item\nis a pane in that tab", text_align=CENTER)
        #Body(card, "No IMPORT REQUIRED!  No Circular Import Baloney!", text_align=CENTER)

    def explain_example(self, parent):
        card  = CardCol(parent)
        row   = Row(card)
        Icon  ( row, "fire")
        Heading(row, "Example: Pet Volcano", glow=True)
        Spacer (row, width_flex=1)
        Heading(row, "4 Tabs, Status, Record, Training, Care ")
        CodeBox(card, data=VOLCANO_EXAMPLE)
        #Body  ( card, "Because someone has to keep an eye on these things.")

    def explain_pane(self, parent):
        card = Col(parent)
        row = Row(card)
        #Icon(row, "tab_system")
        #Title(row, "TAB_LAYOUT is the blueprint of your app!", glow=True)
        #Spacer(card)
        #row = Row(card)
        #Icon(row, "selfdoc")
        #Title(row, "")



        card = Col(parent)
        row = Row(card)
        #Icon(row, "tab_system")
        #Title(row, "TAB_LAYOUT is the blueprint of your app!", glow=True)
        #Spacer(card)
        row = Row(card)
        Icon(row, "selfdoc")
        Heading(row, "Each pane builds one branch of the widget tree")
        #row2 = CardRow(card)
        #c1 = Card(row2, width_flex=1)
        #c2 = Card(row2, width_flex=1)
        #Heading(c1, "Each Pane is like a\n'branch' from the widget tree", text_align=CENTER)
        #Heading(c2, "IPUI will auto-scaffold\nthe class and pane method stubs", text_align=CENTER)
        #Body(card, "No IMPORT REQUIRED!  No Circular Import Baloney!", text_align=CENTER)


        CodeBox(card, data=STATUS_EXAMPLE)

    # ══════════════════════════════════════════════════════════════
    #  RIGHT PANE — The showcase eating its own dog food
    # ══════════════════════════════════════════════════════════════

    def showcase(self, parent):
        scroller = CardCol(parent, scroll_v=True)
        self.showcase_header   (scroller)
        #self.showcase_live_tabs(scroller)
        Spacer(scroller)
        self.showcase_codebox  (scroller)
        Spacer(scroller)

    def showcase_header(self, parent):
        card  = CardCol(parent)
        row   = Row(card)
        Icon  ( row, "boom")
        Title ( row, "This App, Right Now", glow=True)
        Spacer(parent,width_flex=0.2)
        card = CardCol(parent)
        Body  ( card, "Everything you see in this showcase: "
                      "every tab, every pane, every layout,\n"
                      "is driven by the TAB_LAYOUT below.")
        Body(card, "No routing code. No navigation stack. Just the dictionary.")
        Spacer(parent, width_flex=0.2)
        card  = CardCol(parent)
        #Body(card, "Note: You can give panes a 'flex number' to change how space is allocated to panes within the tab.  By default it's equal")
        row = Row(card)
        Icon(row, "boom")
        Title(row, "Check out the left column below.  Notice,", glow=True)
        Title(card, "it matches the tabs at the top off this app.")


    def showcase_live_tabs(self, parent):
        card    = CardCol(parent)
        layout  = self.form.TAB_LAYOUT
        Heading ( card, f"{len(layout)} Tabs · {self.count_panes(layout)} Panes", glow=True)
        Spacer  ( card, height_flex=0.2)
        for tab_name, panes in layout.items():
            self.showcase_tab_card(card, tab_name, panes)

    def showcase_tab_card(self, parent, tab_name, panes):
        is_current = (self.form.tab_strip.active_tab == tab_name)
        bg         = Style.COLOR_TAB_ROW_CURRENT  if is_current else None
        card       = CardCol(parent, color_bg=bg, on_click=lambda tn=tab_name: self.form.switch_tab(tn))
        row        = Row(card)
        Heading   ( row, tab_name, glow=is_current)
        Spacer    ( row)
        Detail    ( row, f"{len(panes)} pane{'s' if len(panes) != 1 else ''}")
        pane_row  = Row(card)
        for p in panes:
            self.showcase_pane_chip(pane_row, p)

    def showcase_pane_chip(self, parent, pane_spec):
        if pane_spec is None:
            label  = "None (canvas)"
            bg     = Style.COLOR_TAB_STATUS_ERROR
        elif isinstance(pane_spec, tuple):
            name   = pane_spec[0] if pane_spec[0] else "None (canvas)"
            weight = pane_spec[1]
            label  = f"{name} ×{weight}"
            bg     = Style.COLOR_TAB_STATUS_LINKED  if pane_spec[0] else Style.COLOR_TAB_STATUS_ERROR
        else:
            label  = pane_spec
            bg     = Style.COLOR_TAB_STATUS_LINKED
        chip = Card(parent, color_bg=bg, width_flex=1, border=2)
        Body ( chip, label, text_align=CENTER)

    def showcase_codebox(self, parent):
        form_file = inspect.getfile(self.form.__class__)
        card      = Card(parent)
        CodeBox   ( card, data=form_file, start="STATUS_EXAMPLE", end="}")

    def count_panes(self, layout):
        return sum(len(v) for v in layout.values())


# ══════════════════════════════════════════════════════════════
#  Example code shown in the left pane CodeBox
# ══════════════════════════════════════════════════════════════

VOLCANO_EXAMPLE = '''
class FormPetVolcano(_BaseForm):  
    TAB_LAYOUT = {                                              
        # Tabs       Panes in each tab 
        "Status":   ["mood"      ,"lava_level"   ,"smoking"  ], 
        "Alerts":   ["meltdown"  ,"evacuation"               ],
        "Care":     ["walks"     ,"lava_bath"    ,"feed_goat"],    
        "Profile":  ["nameplate" ,"adoption_papers"          ],
    }
'''


STATUS_EXAMPLE = '''
class Status(_BaseTab):                            # Status (tab) from the dict key

    def mood(self, parent):                        # mood (pane) from Status' list.
        Heading(parent, "Filename: Status.py")     # parent parameter is the 'branch'
        Heading(parent, "Method: is_it_growling")  # Add widgets to parent
        Heading(parent, "Add content here!")       # you can do a whole branch from it 
    
    def lava_level(self, parent):                  # lava_level (pane) from Status' list.
        Heading(parent, "Filename: Status.py")     # Tabs and Panes 
        Heading(parent, "Method: lava_level")      # Easy Peasy! :)
        Heading(parent, "Add content here!")       # What are you going to build?

    def smoking(self, parent):                     # smoking (pane) from Status' list.
        Heading(parent, "Filename: Status.py")     # Wanna get crazy and try a button??
        Heading(parent, "Method: smoke")
        Heading(parent, "Add content here!")    
'''