# WidgetExplorer.py  New: self-documenting widget cookbook
from ipui import *
import inspect

from ipui.utils.MgrClipboard import MgrClipboard


class ShowcaseTemplate(_BaseTab):

    #COMMENT OR DELETE THIS TO PREVENT THE COOKBOOK FROM Hijacking the 2nd and 3rd pane.
    def ip_activated(self,ip):
        self.set_pane(1, self.cookbook_menu, weight=.6)
        self.set_pane(2, self.cookbook_demo, weight=1.3)

    # PUT YOUR CONTENT HERE
    def left_pane22(self,parent):
        # self.ensure_cookbook() #Remove this to access your other panes.
        Title   ( parent, "Your Pane", glow=True)
        Body    ( parent, "This is your first pane — the one you defined in TAB_LAYOUT.")
        Body    ( parent, "Right now it's empty, and that's the point.")
        Spacer  ( parent)
        Heading ( parent, "How to get moving fast:")
        card    = CardCol(parent)
        Body    ( card,   "1. Browse the the Cookbook to the right")
        Body    ( card,   "2. Click any pattern to see it live with source code")
        Body    ( card,   "3. Hit the Copy button on the code block")
        Body    ( card,   "4. Paste it into your tab file and tweak it")
        Body    ( card,   "5. Save the file and re-run to see your changes")
        Spacer  ( parent)

        Heading ( parent, "Your _BaseTab file:",text_align=CENTER)
        r = Row ( parent)
        Spacer  ( r)
        c=Card  ( r)
        file    = self.form.pipeline_read("missing_tab_path") or "YourTab.py"
        file    = __file__
        c2=CardCol(parent)
        Detail ( c2, file)
        Button(c2, "Copy full path", on_click=lambda: MgrClipboard.copy(file))
        Spacer  ( r)
        Spacer  ( parent)
        Detail  ( parent, "When you're done exploring, delete the WidgetExplorer pane")
        Detail  ( parent, "from your _BaseTab file and build out the other panes.")
        Spacer  ( parent)

    def proud_features(self, parent): pass

    def detail(self, parent): pass

    def ensure_cookbook(self):
        print("in cookbook")
        self.set_pane(1,self.cookbook_menu,weight=.6)
        self.set_pane(2, self.cookbook_demo, weight=1.3)

    def cookbook_menu(self, parent):
        Title(parent, "Cookbook", glow=True)
        Body(parent, "Pick a pattern to see it live")
        card = Card(parent, scrollable=True, height_flex=1)
        for name, label in self.discover_demos():
            Button(card, label, on_click=lambda n=name: self.show_demo(n),width_flex=1,text_align='l')

    def cookbook_demo(self, parent):
        Title(parent, "Source Code", glow=True)
        Body(parent, "Pick something from the menu",
             name="explorer_placeholder")

    def show_demo(self, method_name):
        method = getattr(self, method_name)
        def wrapped(parent):
            card    = Card(parent, scrollable=True)
            method  ( card)
            #Spacer  ( card)
            c2=Card (card)
            CodeBox (c2, data=method)
            #Spacer  ( card)
        self.form.set_pane(2, wrapped)

    def discover_demos(self):
        demos = []
        for name in dir(self):
            if name.startswith("demo_"):
                label = name[5:]
                label = self.strip_sort_prefix(label)
                label = label.replace("_", " ").title()
                demos.append((name, label))
        return sorted(demos, key=lambda d: d[0])  # sort by method name (keeps numbering)

    def strip_sort_prefix(self, label):
        parts = label.split("_", 1)
        if len(parts) > 1 and parts[0].isdigit():
            return parts[1]
        return label

    # ══════════════════════════════════════════════════════════════
    # DEMOS — add a method, it appears in the menu
    # ══════════════════════════════════════════════════════════════

    def demo_010_text_hierarchy(self, parent):
        Title   ( parent, "Text Hierarchy", glow=True)
        Body    ( parent, "Five semantic levels - pick the role, not the size:")
        card    = CardCol(parent)
        Banner  ( card,   "Banner")
        Title   ( card,   "Title")
        Heading ( card,   "Heading")
        Body    ( card,   "Body")
        Detail  ( card,   "Detail")

    def demo_020_buttons(self, parent):
        Title   ( parent, "Buttons", glow=True)
        Body    ( parent, "Click handlers, colors, and states:")
        Button  ( parent, "Default Button"  , on_click=self.click_me)
        Button  ( parent, "Call To Action"  , on_click=self.click_me, color_bg=Style.COLOR_BUTTON_CTA)
        Button  ( parent, "Danger"          , on_click=self.click_me, color_bg=Style.COLOR_BUTTON_DANGER)
        Button  ( parent, "Secondary"       , on_click=self.click_me, color_bg=Style.COLOR_BUTTON_SECONDARY)
        Button  ( parent, "Warning"         , on_click=self.click_me, color_bg=Style.COLOR_BUTTON_WARNING)
        Button  ( parent, "Please Hover").set_disabled("I am disabled. Use set_disabled(reason)")

    def click_me(self):        self.show_modal("I've been clicked")

    def demo_030_textbox(self, parent):
        Title   ( parent, "TextBox", glow=True)
        Body    ( parent, "Text input with placeholder, submit, and pipeline:")
        TextBox ( parent, placeholder="Type here...")
        TextBox ( parent, placeholder="Hit enter...",  on_submit=lambda t: self.show_modal(f"You said: {t}"))
        TextBox ( parent, initial_value="Pre-filled",  width_flex=1)

    def demo_040_cards_and_layout(self, parent):
        Title   ( parent, "Cards & Layout", glow=True)
        Body    ( parent, "Vertical and horizontal grouping:")
        row     = Row(parent, width_flex=1)
        left    = CardCol(row, width_flex=1)
        Heading ( left,   "Left Column")
        Body    ( left,   "Cards stack vertically by default.")
        right   = CardCol(row, width_flex=1)
        Title   ( right,  "Right Column")
        Body    ( right,  "Use Row to go horizontal.")

    def demo_050_flex_layout(self, parent):
        Title   ( parent, "Flex Layout", glow=True)
        Body    ( parent, "width_flex controls proportional sizing:")
        row     = Row(parent, width_flex=1)
        CardCol ( row, width_flex=1).tap(lambda c: Title(c, "flex=1"))
        CardCol ( row, width_flex=2).tap(lambda c: Title(c, "flex=2"))
        CardCol ( row, width_flex=1).tap(lambda c: Title(c, "flex=1"))
        Body    ( parent, "The middle column gets 50% of the space.")

    def demo_060_spacer(self, parent):
        Title   ( parent, "Spacer", glow=True)
        Body    ( parent, "Push widgets apart with invisible flex:")
        row     = Row(parent, width_flex=1)
        Button  ( row,    "Left")
        Spacer  ( row)
        Button  ( row,    "Right")
        Body    ( parent, "Also works vertically between cards.")

    def demo_070_scrollable_card(self, parent):
        Title   ( parent, "Scrollable Card", glow=True)
        Body    ( parent, "Any Card becomes scrollable with one parameter:")
        card    = Card(parent, scrollable=True, height_flex=1)
        for i in range(20):
            Body( card,   f"Row {i + 1} — scroll me!")

    def demo_080_grid(self, parent):
        Title   ( parent, "PowerGrid", glow=True)
        Body    ( parent, "Feed it lists, dicts, or SQL — it just works:")
        data    = [
            {"Name": "Alice",   "Score": 95,  "Grade": "A"},
            {"Name": "Bob",     "Score": 82,  "Grade": "B"},
            {"Name": "Charlie", "Score": 71,  "Grade": "C"},
            {"Name": "Diana",   "Score": 98,  "Grade": "A"},
        ]
        grid    = PowerGrid(parent, height_flex=1)
        grid.set_data(data)
        grid.on_row_click(lambda row: self.show_modal(f"{row['Name']}: {row['Score']}"))

    def demo_085_codebox(self, parent):
        Title   ( parent, "CodeBox", glow=True)
        Body    ( parent, "Display source code — pass a method or a file path:")
        Body    ( parent, "This CodeBox is showing its own demo method:")

    def demo_090_swap_pane(self, parent):
        Title   ( parent, "Swap Pane", glow=True)
        Body    ( parent, "Replace pane content on the fly with set_pane:")
        Button  ( parent, "Show Version A", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.form.set_pane(2, self.swap_example_a))
        Button  ( parent, "Show Version B", color_bg=Style.COLOR_BUTTON_SECONDARY,
                  on_click=lambda: self.form.set_pane(2, self.swap_example_b))
        Button  ( parent, "Back to this demo", color_bg=Style.COLOR_BUTTON_WARNING,
                  on_click=lambda: self.form.set_pane(2, self.demo_90_swap_pane))

    def swap_example_a(self, parent):
        Title   ( parent, "Version A", glow=True)
        Body    ( parent, "You swapped to A! Click back in the menu to return.")

    def swap_example_b(self, parent):
        Title   ( parent, "Version B", glow=True)
        Body    ( parent, "You swapped to B! This is a completely different pane.")

    def demo_095_master_detail(self, parent):
        Title   ( parent, "Master / Detail", glow=True)
        Body    ( parent, "Click a row — detail updates in the same pane:")
        row     = Row(parent, width_flex=1, height_flex=1)
        items   = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]
        card    = CardCol(row, width_flex=1)
        for item in items:
            Button( card,  item, on_click=lambda i=item: self.show_detail(i))
        self.detail_card = CardCol(row, width_flex=2)
        Body    ( self.detail_card, "Click an item on the left.")

    def show_detail(self, item):
        self.detail_card.clear_children()
        Title   ( self.detail_card, item, glow=True)
        Body    ( self.detail_card, f"You selected: {item}")
        Body    ( self.detail_card, f"This is the detail view for {item}.")
        Body    ( self.detail_card, "In a real app, load data here.")

    def demo_100_dropdown(self, parent):
        Title   ( parent, "DropDown", glow=True)
        Body    ( parent, "Single-select dropdown with search filtering:")
        items   = {"Red": {}, "Green": {}, "Blue": {}, "Orange": {}, "Purple": {}}
        dd      = DropDown(parent, text="Pick a color", data=items, width_flex=1)
        dd.on_change = lambda sel: self.show_modal(f"Selected: {sel}")

    def demo_110_selection_list(self, parent):
        Title   ( parent, "SelectionList", glow=True)
        Body    ( parent, "Multi-select with toggle and filter:")
        items   = {"Python": {}, "Rust": {}, "Go": {}, "TypeScript": {}, "C++": {}}
        sel     = SelectionList(parent, text="Languages", data=items, height_flex=1)
        Button  ( parent, "Show Selected", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.show_modal(f"Selected: {sel.get_selected()}"))

    def demo_120_single_select(self, parent):
        Title   ( parent, "Single Select List", glow=True)
        Body    ( parent, "Add single_select=True for radio-button behavior:")
        items   = {"Small": {}, "Medium": {}, "Large": {}, "XL": {}}
        sel     = SelectionList(parent, text="Size", data=items,
                                single_select=True, height_flex=1)
        Button  ( parent, "Show Choice", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.show_modal(f"Chose: {sel.get_selected()}"))

    def demo_130_textarea(self, parent):
        Title   ( parent, "TextArea", glow=True)
        Body    ( parent, "Multi-line text input — great for SQL, notes, config:")
        ta      = TextArea(parent, height_flex=1, initial_value="SELECT *\nFROM users\nWHERE active = 1")
        Button  ( parent, "Run", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.show_modal(f"Query:\n{ta.text}"))

    def demo_200_pipeline_reactive(self, parent):
        Title   ( parent, "Pipeline — Reactive", glow=True)
        Body    ( parent, "Type in the box. The label updates automatically:")
        TextBox ( parent, placeholder="Type your name...", pipeline_key="explorer_name")
        Body    ( parent, " ", name="lbl_explorer_greeting")
        Body    ( parent, "No on_change handler. No manual update. The pipeline does it.")

    BINDINGS = {
        "lbl_explorer_greeting": {
            "property": "text",
            "compute":  "compute_greeting",
            "triggers": ["explorer_name"],
        },
    }

    def compute_greeting(self, explorer_name):
        if not explorer_name:
            return "Hello, stranger!"
        return f"Hello, {explorer_name}!"

    def demo_210_pipeline_read_write(self, parent):
        Title   ( parent, "Pipeline — Read & Write", glow=True)
        Body    ( parent, "Share data across panes without passing references:")
        row     = Row(parent, width_flex=1)
        Button  ( row,    "Set Count = 42", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.form.pipeline_set("explorer_count", 42))
        Button  ( row,    "Set Count = 0",  color_bg=Style.COLOR_BUTTON_DANGER,
                  on_click=lambda: self.form.pipeline_set("explorer_count", 0))
        Button  ( row, "Read Count",     color_bg=Style.COLOR_BUTTON_SECONDARY,
                  on_click=lambda: self.show_modal(
                      f"explorer_count = {self.form.pipeline_read('explorer_count')}"))
        Body    ( parent, "pipeline_set writes. pipeline_read reads. Any pane, any tab.")

    def demo_300_state_machine(self, parent):
        Title   ( parent, "State Machine", glow=True)
        Body    ( parent, "Delegate-based states with auto-transitions:")
        Body    ( parent, " ", name="lbl_explorer_state")
        row     = Row(parent, width_flex=1)
        Button  ( row,    "Go IDLE",    on_click=lambda: self.ip.state("explorer").go("IDLE"))
        Button  ( row,    "Go RUNNING", on_click=lambda: self.ip.state("explorer").go("RUNNING"),
                  color_bg=Style.COLOR_BUTTON_CTA)
        Button  ( row,    "Go DONE",    on_click=lambda: self.ip.state("explorer").go("DONE"),
                  color_bg=Style.COLOR_BUTTON_SECONDARY)
        Body    ( parent, "DONE auto-transitions to IDLE after 2 seconds.")
        self.setup_explorer_state_machine()

    def setup_explorer_state_machine(self):
        sm = self.ip.state("explorer")
        if sm.current is not None:
            return
        sm.add("IDLE",    self.explorer_state_idle)
        sm.add("RUNNING", self.explorer_state_running)
        sm.add("DONE",    self.explorer_state_done, "IDLE", 2.0)
        sm.go("IDLE")

    def explorer_state_idle(self):
        lbl = self.form.widgets.get("lbl_explorer_state")
        if lbl: lbl.set_text("State: IDLE — waiting for action")

    def explorer_state_running(self):
        lbl = self.form.widgets.get("lbl_explorer_state")
        if lbl: lbl.set_text(f"State: RUNNING — frame {self.ip.frame}")

    def explorer_state_done(self):
        lbl = self.form.widgets.get("lbl_explorer_state")
        if lbl: lbl.set_text("State: DONE — returning to IDLE in 2s...")

    def demo_310_show_modal(self, parent):
        Title   ( parent, "Modal Messages", glow=True)
        Body    ( parent, "Block the UI briefly to show a message:")
        Button  ( parent, "Simple Message",  color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.show_modal("Hello from a modal!"))
        Button  ( parent, "With Work",       color_bg=Style.COLOR_BUTTON_SECONDARY,
                  on_click=lambda: self.show_modal("Working...", min_seconds=3,
                      work_func=lambda: None))
        Body    ( parent, "show_modal(msg) pauses for 2 seconds by default.")
        Body    ( parent, "Pass work_func to run code while the modal shows.")

    def demo_320_icons(self, parent):
        Title   ( parent, "Icons", glow=True)
        Body    ( parent, "Twemoji PNG icons — use them anywhere:")
        row     = Row(parent, width_flex=1)
        Icon    ( row, "rocket")
        Icon    ( row, "fire")
        Icon    ( row, "star")
        Icon    ( row, "devil")
        Icon    ( row, "microscope")
        Icon    ( row, "laugh")
        Body    ( parent, "Icon(parent, 'rocket') — that's it.")
        Body    ( parent, "Icons scale with resolution. No asset management.")

    def demo_400_grid_sql(self, parent):
        Title   ( parent, "Grid + SQL", glow=True)
        Body    ( parent, "Point PowerGrid at a SQLite database:")
        Body    ( parent, "grid.set_data('path/to/db.sqlite', table='users')")
        Body    ( parent, "grid.set_data('path/to/db.sqlite', query='SELECT ...')")
        Body    ( parent, "Sorting, pagination, and row clicks — all automatic.")
        Body    ( parent, "See the SQL tab for a full interactive example.")

    def demo_410_cross_tab_panes(self, parent):
        Title   ( parent, "Cross-Tab Pane Sharing", glow=True)
        Body    ( parent, "Reuse a pane builder from another tab with dot notation:")
        card    = CardCol(parent)
        Body    ( card,   'TAB_LAYOUT = {')
        Body    ( card,   '    "Main"    : ["dashboard", "chart"],')
        Body    ( card,   '    "Compare" : ["dashboard", "Main.chart"],')
        Body    ( card,   '}')
        Body    ( parent, "Compare tab reuses Main's chart pane. Same code, same state.")
        Body    ( parent, "The dot syntax tells IPUI to look in another tab's file.")

    def demo_420_hide_show_tabs(self, parent):
        Title   ( parent, "Hide & Show Tabs", glow=True)
        Body    ( parent, "Control which tabs are visible at runtime:")
        row     = Row(parent, width_flex=1)
        Button  ( row,    "Hide Designer", color_bg=Style.COLOR_BUTTON_DANGER,
                  on_click=lambda: self.form.hide_tab("Designer"))
        Button  ( row,    "Show Designer", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.form.show_tab("Designer"))
        Body    ( parent, "Useful for progressive disclosure — show tabs as users unlock features.")
        Body    ( parent, "Also: tab_hidden = ['Advanced'] in your Form to start hidden.")

    def demo_500_justify(self, parent):
        Title   ( parent, "Justify Spread & Center", glow=True)
        Body    ( parent, "Distribute children evenly or center them:")
        Body    ( parent, "justify_spread=True:")
        row1    = Row(parent, width_flex=1, justify_spread=True)
        Button  ( row1,   "A")
        Button  ( row1,   "B")
        Button  ( row1,   "C")
        Body    ( parent, "justify_center=True:")
        row2    = Row(parent, width_flex=1, justify_center=True)
        Button  ( row2,   "X")
        Button  ( row2,   "Y")

    def demo_510_fit_content(self, parent):
        Title   ( parent, "Fit Content Width", glow=True)
        Body    ( parent, "Buttons normally stretch. fit_content=True hugs the text:")
        Button  ( parent, "I stretch to fill", width_flex=1)
        Button  ( parent, "I hug my text",     fit_content=True)
        row     = Row(parent, width_flex=1)
        Button  ( row,    "Save",   fit_content=True, color_bg=Style.COLOR_BUTTON_CTA)
        Button  ( row,    "Cancel", fit_content=True)
        Spacer  ( row)
        Button  ( row,    "Delete", fit_content=True, color_bg=Style.COLOR_BUTTON_DANGER)
        Body    ( parent, "Combine with Spacer to push buttons apart.")

    def demo_520_nested_cards(self, parent):
        Title   ( parent, "Nested Cards", glow=True)
        Body    ( parent, "Cards inside cards — natural grouping:")
        outer   = CardCol(parent)
        Title   ( outer,  "User Profile")
        row     = Row(outer, width_flex=1)
        info    = CardCol(row, width_flex=1)
        Heading ( info,   "Contact")
        Body    ( info,   "alice@example.com")
        Body    ( info,   "555-0123")
        stats   = CardCol(row, width_flex=1)
        Heading ( stats,  "Stats")
        Body    ( stats,  "Projects: 12")
        Body    ( stats,  "Commits: 847")

    def demo_530_dynamic_list(self, parent):
        Title   ( parent, "Dynamic List", glow=True)
        Body    ( parent, "Build a list from data — add and remove at runtime:")
        self.demo_list_card = Card(parent, scrollable=True, height_flex=1)
        self.demo_list_items = ["Alpha", "Bravo", "Charlie"]
        self.rebuild_demo_list()
        row     = Row(parent, width_flex=1)
        self.demo_list_input = TextBox(row, placeholder="New item...", width_flex=1,
                                        on_submit=lambda t: self.list_add())
        Button  ( row,    "Add", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=self.list_add)

    def rebuild_demo_list(self):
        self.demo_list_card.clear_children()
        for i, item in enumerate(self.demo_list_items):
            row     = CardRow(self.demo_list_card, width_flex=1, justify_spread=True)
            Body    ( row,    f"{i + 1}. {item}", width_flex=1)
            Button  ( row,    "X", color_bg=Style.COLOR_BUTTON_DANGER, fit_content=True,
                      on_click=lambda idx=i: self.list_remove(idx))

    def list_add(self):
        text    = self.demo_list_input.text.strip()
        if not text:    return
        self.demo_list_items.append(text)
        self.demo_list_input.set_text("")
        self.rebuild_demo_list()

    def list_remove(self, idx):
        self.demo_list_items.pop(idx)
        self.rebuild_demo_list()

    def demo_540_row_col_nesting(self, parent):
        Title   ( parent, "Row & Col Nesting", glow=True)
        Body    ( parent, "Alternate Row and Col to build any layout:")
        row     = Row(parent, width_flex=1, height_flex=1)
        left    = CardCol(row, width_flex=1)
        Title   ( left,   "Sidebar")
        Button  ( left,   "Nav 1")
        Button  ( left,   "Nav 2")
        Button  ( left,   "Nav 3")
        Spacer  ( left)
        Detail  ( left,   "v0.1.0")
        right   = Col(row, width_flex=3)
        top     = CardCol(right, width_flex=1)
        Title   ( top,    "Main Content")
        Body    ( top,    "This is a classic sidebar + main layout.")
        bot     = Row(right, width_flex=1)
        CardCol ( bot, width_flex=1).tap(lambda c: Body(c, "Footer Left"))
        CardCol ( bot, width_flex=1).tap(lambda c: Body(c, "Footer Right"))

    def demo_600_on_click_me(self, parent):
        Title   ( parent, "on_click_me", glow=True)
        Body    ( parent, "Register a click handler after construction:")
        btn     = Button(parent, "Click Me")
        btn.on_click_me(lambda: self.show_modal("on_click_me fired!"))
        Body    ( parent, "Useful when you need the widget reference first,")
        Body    ( parent, "or when wiring clicks in a loop.")

    def demo_610_widget_registry(self, parent):
        Title   ( parent, "Widget Registry", glow=True)
        Body    ( parent, "Name a widget. Find it from anywhere:")
        Body    ( parent, "Hello!", name="lbl_registry_demo")
        row     = Row(parent, width_flex=1)
        Button  ( row,    "Change Text", color_bg=Style.COLOR_BUTTON_CTA,
                  on_click=lambda: self.form.widgets["lbl_registry_demo"].set_text("Changed!"))
        Button  ( row,    "Reset",       color_bg=Style.COLOR_BUTTON_SECONDARY,
                  on_click=lambda: self.form.widgets["lbl_registry_demo"].set_text("Hello!"))
        Body    ( parent, "No reference passing. No globals. Just name it and find it.")

    def demo_620_tab_layout(self, parent):
        Title   ( parent, "TAB_LAYOUT", glow=True)
        Body    ( parent, "Your entire app structure in one dictionary:")
        card    = CardCol(parent)
        Body    ( card,   'TAB_LAYOUT = {')
        Body    ( card,   '    "Home"     : ["welcome"],')
        Body    ( card,   '    "Settings" : ["general", "advanced"],')
        Body    ( card,   '    "Data"     : [("table", 1), ("chart", 2)],')
        Body    ( card,   '    "Game"     : ["hud", None, "controls"],')
        Body    ( card,   '}')
        Body    ( parent, "Keys = tab names. Values = pane builders.")
        Body    ( parent, "Tuples set flex weights. None = pygame canvas.")

    def demo_630_lifecycle_hooks(self, parent):
        Title   ( parent, "Lifecycle Hooks", glow=True)
        Body    ( parent, "Five hooks give you full control of the game loop:")
        card    = CardCol(parent)
        Heading ( card,   "ip_setup(self, ip)")
        Body    ( card,   "Once — when tab is first created. Init state here.")
        Heading ( card,   "ip_activated(self, ip)")
        Body    ( card,   "Once — when tab is first created and when tab is switched back to.")
        Heading ( card,   "ip_think(self, ip)")
        Body    ( card,   "Every frame — state, physics, logic. Before render.")
        Heading ( card,   "ip_draw(self, ip)")
        Body    ( card,   "Every frame — draw BEFORE widgets. Backgrounds.")
        Heading ( card,   "ip_draw_hud(self, ip)")
        Body    ( card,   "Every frame — draw AFTER widgets. Overlays, HUD.")
        Body    ( parent, "All receive ip — the service portal with dt, mouse, keys.")

    def demo_640_ip_service_portal(self, parent):
        Title   ( parent, "The ip Service Portal", glow=True)
        Body    ( parent, "One object, everything you need. Type ip. and explore:")
        card    = CardCol(parent)
        Body    ( card,   "ip.dt           Seconds since last frame")
        Body    ( card,   "ip.fps          Current FPS")
        Body    ( card,   "ip.mouse_x/y    Mouse position")
        Body    ( card,   "ip.mouse_pressed(Mouse.LEFT)")
        Body    ( card,   "ip.key_pressed(Key.SPACE)")
        Body    ( card,   "ip.rect_pane    Your drawing canvas")
        Body    ( card,   "ip.to_screen(nx, ny)  Normalized → pixels")
        Body    ( card,   "ip.state        Per-tab state machine")
        Body    ( parent, "See ip.help() for the full tour.")

    def demo_700_save_load_json(self, parent):
        Title   ( parent, "Save & Load JSON", glow=True)
        Body    ( parent, "Persist state to the user's home folder:")
        card    = CardCol(parent)
        Body    ( card,   "from pathlib import Path")
        Body    ( card,   "import json")
        Body    ( card,   "")
        Body    ( card,   "SAVE_PATH = Path.home() / 'my_app_data.json'")
        Body    ( card,   "")
        Body    ( card,   "def save(self):")
        Body    ( card,   "    data = {'score': self.score, 'level': self.level}")
        Body    ( card,   "    SAVE_PATH.write_text(json.dumps(data, indent=2))")
        Body    ( card,   "")
        Body    ( card,   "def load(self):")
        Body    ( card,   "    if SAVE_PATH.exists():")
        Body    ( card,   "        data = json.loads(SAVE_PATH.read_text())")
        Body    ( card,   "        self.score = data['score']")
        Body    ( parent, "Real example: see Particle Life's save system.")

    def demo_710_construction_is_attachment(self, parent):
        Title   ( parent, "Construction IS Attachment", glow=True)
        Body    ( parent, "No add(). No pack(). Build it inside a container, it's attached:")
        card    = CardCol(parent)
        Body    ( card,   "# Other frameworks:")
        Body    ( card,   "btn = Button('Click')")
        Body    ( card,   "panel.add(btn)          # forget this = invisible widget")
        Body    ( card,   "")
        Body    ( card,   "# IPUI:")
        Body    ( card,   "Button(panel, 'Click')  # done. attached. visible.")
        Body    ( parent, "An entire class of bugs — eliminated by design.",glow=True)

    def demo_900_philosophy(self, parent):
        Title   ( parent, "The IPUI Philosophy", glow=True)
        Body    ( parent, "Every design decision follows one principle:")
        Heading  ( parent, "Easy to get right.\nHard to get wrong.", text_align=CENTER,glow=True)
        card    = CardCol(parent)
        Heading ( card,   "Pit of Success")
        Body    ( card,   "The framework shoves you toward correct usage.")
        Body    ( card,   "Defaults work. Errors are loud and helpful.")
        Body    ( card,   "The wrong thing is harder than the right thing.")
        Heading ( card,   "O(1) Solutions")
        Body    ( card,   "Every problem is solved once, in the framework.")
        Body    ( card,   "Not O(N) times, by every developer, on every project.")
        Heading ( card,   "Construction IS Attachment")
        Body    ( card,   "If you build it inside a container, it's attached.")
        Body    ( card,   "No voids. No leaks. No orphan widgets.")
