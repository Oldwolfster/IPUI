# Designer.py  NEW FILE — Visual form designer

import inspect
from pathlib import Path
from ipui import *


WRITE_FILES = False

class Designer(_BaseTab):

    def ip_setup_pane(self):
        self.selected_tab  = None
        self.selected_pane = None

    # ══════════════════════════════════════════════════════════════
    # LEFT PANE — Tab Map
    # ══════════════════════════════════════════════════════════════



    def tab_map(self, parent):
        Title(parent, "Tab Map", glow=True)
        self.map_card = CardCol(parent, height_flex=True, scrollable=True)
        self.rebuild_tab_map()

        card = CardCol(parent)                                          # NEW
        self.txt_name = TextBox(card, placeholder="Tab or Pane name")   # NEW
        row = Row(card)                                                 # NEW
        Button(row, "+ Tab",  color_bg=Style.COLOR_PAL_GREEN_DARK,      # NEW
            width_flex=1, on_click=self.add_tab)                        # NEW
        Button(row, "- Tab",  color_bg=Style.COLOR_PAL_RED_DARK,        # NEW
            width_flex=1, on_click=self.delete_tab)                     # NEW
        Button(row, "+ Pane", color_bg=Style.COLOR_PAL_GREEN_DARK,      # NEW
            width_flex=1, on_click=self.add_pane)                       # NEW
        Button(row, "- Pane", color_bg=Style.COLOR_PAL_RED_DARK,        # NEW
            width_flex=1, on_click=self.delete_pane)                    # NEW

    def rebuild_tab_map(self):
        self.map_card.clear_children()
        layout = self.form.TAB_LAYOUT
        for tab_name, entries in layout.items():
            self.build_tab_header(tab_name)
            panes = self.normalize_entries(entries)
            for method_name, weight in panes:
                if not isinstance(method_name, str):
                    continue
                self.build_pane_row(tab_name, method_name, weight)

    def build_tab_header(self, tab_name):
        row = Row(self.map_card, justify_spread=True)
        btn = Button(row, tab_name,
            color_bg   = Style.COLOR_TAB_BG,
            width_flex = True)
        is_selected = (tab_name == self.selected_tab and self.selected_pane is None)
        if is_selected:
            btn.set_radiate()
        btn.on_click = lambda n=tab_name: self.select_tab(n)

    def build_pane_row(self, tab_name, method_name, weight):
        row = Row(self.map_card)
        Spacer(row, width_flex=False)
        label       = f"  {method_name}"
        is_selected = (tab_name == self.selected_tab
                       and method_name == self.selected_pane)
        color       = Style.COLOR_PAL_GREEN_DARK if is_selected else Style.COLOR_BUTTON_BG
        btn         = Button(row, label,
            color_bg   = color,
            width_flex = True)
        if is_selected:
            btn.set_radiate()
        btn.on_click = lambda t=tab_name, m=method_name: self.select_pane(t, m)
        Body(row, f"({weight})")

    def normalize_entries(self, entries):
        result = []
        for entry in entries:
            if isinstance(entry, tuple):
                result.append(entry)
            else:
                result.append((entry, 1))
        return result

    # ══════════════════════════════════════════════════════════════
    # MIDDLE PANE — Live Preview
    # ══════════════════════════════════════════════════════════════

    def preview(self, parent):
        Title(parent, "Preview", glow=True)
        Body(parent, "Select a pane from the Tab Map")

    def refresh_preview(self):
        if not self.selected_tab or not self.selected_pane:
            return
        pane = self.form.tab_strip.panes[1]
        pane.children.clear()
        Title(pane, "Preview", glow=True)
        if (self.selected_tab == "Designer"
        and self.selected_pane == "preview"):
            Body(pane, "You're looking at it.")
            return
        preview_area = CardCol(pane, height_flex=True)
        instance = self.form.tab_strip.resolve_pane(self.selected_tab)
        if instance and hasattr(instance, self.selected_pane):
            getattr(instance, self.selected_pane)(preview_area)
        else:
            Body(preview_area, f"Cannot resolve: {self.selected_tab}.{self.selected_pane}")

    # ══════════════════════════════════════════════════════════════
    # RIGHT PANE — Toolbox
    # ══════════════════════════════════════════════════════════════

    def toolbox(self, parent):
        Title(parent, "Tools", glow=True)
        card = CardCol(parent, scrollable=True, height_flex=True)
        Heading(card, "Widgets", glow=True)
        palette = [
            "Title", "Heading", "Body",
            "Button", "CardCol", "CardRow",
            "Row", "Spacer", "TextBox",
            "SelectionList", "PowerGrid",
        ]
        for widget_name in palette:
            Button(card, widget_name,
                color_bg = Style.COLOR_BUTTON_BG,
                on_click = lambda w=widget_name: self.inject_widget(w))

        #Spacer(parent)
        card = CardCol(parent)
        Heading(card, "Status", glow=True)
        Body(card, "Ready.", name="lbl_designer_status")

    # ══════════════════════════════════════════════════════════════
    # SELECTION
    # ══════════════════════════════════════════════════════════════

    def select_tab(self, tab_name):
        self.selected_tab  = tab_name
        self.selected_pane = None
        self.set_status(f"Tab: {tab_name}")
        self.rebuild_tab_map()

    def select_pane(self, tab_name, method_name):
        self.selected_tab  = tab_name
        self.selected_pane = method_name
        self.set_status(f"{tab_name} . {method_name}")
        self.rebuild_tab_map()
        self.refresh_preview()

    # ══════════════════════════════════════════════════════════════
    # ACTIONS — Tab
    # ══════════════════════════════════════════════════════════════

    def add_tab(self):
        name = self.txt_name.text.strip()
        if not name:
            self.set_status("Enter a tab name first.")
            return
        if name in self.form.TAB_LAYOUT:
            self.set_status(f"Tab '{name}' already exists.")
            return
        method = name.lower().replace(" ", "_")
        self.form.TAB_LAYOUT[name] = [method]
        self.form.tab_strip.data[name] = [method]
        self.form.tab_strip.rebuild_tab_buttons()
        self.txt_name.set_text("")
        self.selected_tab  = name
        self.selected_pane = None
        self.save_form_layout()
        self.set_status(f"Added tab: {name}")
        self.rebuild_tab_map()

    def delete_tab(self):
        if not self.selected_tab:
            self.set_status("Select a tab first.")
            return
        if self.selected_tab == "Designer":
            self.set_status("Can't delete Designer. Nice try.")
            return
        name = self.selected_tab
        self.form.TAB_LAYOUT.pop(name, None)
        self.form.tab_strip.data.pop(name, None)
        self.form.tab_strip.pane_cache.pop(name, None)
        self.form.tab_strip.rebuild_tab_buttons()
        self.selected_tab  = None
        self.selected_pane = None
        self.save_form_layout()
        self.set_status(f"Deleted tab: {name}")
        self.rebuild_tab_map()

    # ══════════════════════════════════════════════════════════════
    # ACTIONS — Pane
    # ══════════════════════════════════════════════════════════════

    def add_pane(self):
        if not self.selected_tab:
            self.set_status("Select a tab first.")
            return
        name = self.txt_name.text.strip()
        if not name:
            self.set_status("Enter a pane method name.")
            return
        method = name.lower().replace(" ", "_")
        tab    = self.selected_tab
        self.form.TAB_LAYOUT[tab].append(method)
        self.form.tab_strip.data[tab].append(method)
        self.backup_and_write(tab, method)
        self.form.tab_strip.pane_cache.pop(tab, None)
        self.txt_name.set_text("")
        self.selected_pane = method
        self.save_form_layout()
        self.set_status(f"Added pane: {tab}.{method}")
        self.rebuild_tab_map()

    def delete_pane(self):
        if not self.selected_tab or not self.selected_pane:
            self.set_status("Select a pane first.")
            return
        tab    = self.selected_tab
        method = self.selected_pane
        entries = self.form.TAB_LAYOUT[tab]
        for i, entry in enumerate(entries):
            m = entry[0] if isinstance(entry, tuple) else entry
            if m == method:
                entries.pop(i)
                break
        self.form.tab_strip.data[tab] = entries
        self.form.tab_strip.pane_cache.pop(tab, None)
        if WRITE_FILES:
            file_path = self.get_tab_file_path(tab)
            FileManager.deprecate_method(file_path, method)
        self.save_form_layout()
        self.selected_pane = None
        self.set_status(f"Deprecated: {method}")
        self.rebuild_tab_map()
        if tab == self.form.tab_strip.active_tab:
            self.form.tab_strip.switch_tab(tab)

    # ══════════════════════════════════════════════════════════════
    # ACTIONS — Widget Palette
    # ══════════════════════════════════════════════════════════════

    def inject_widget(self, widget_type):
        if not WRITE_FILES:  return
        if not self.selected_tab or not self.selected_pane:
            self.set_status("Select a pane first.")
            return
        if self.selected_tab == "Designer":
            self.set_status("Can't modify Designer panes.")
            return
        file_path = self.get_tab_file_path(self.selected_tab)
        if not file_path.exists():
            self.set_status(f"File not found: {file_path.name}")
            return
        snippet = self.widget_snippet(widget_type)
        FileManager.inject_into_method(file_path, self.selected_pane, snippet)
        self.form.tab_strip.pane_cache.pop(self.selected_tab, None)
        self.set_status(f"Added {widget_type} to {self.selected_pane}")
        self.refresh_preview()

    def widget_snippet(self, widget_type):
        snippets = {
            "Title":         '        Title(parent, "New Title", glow=True)',
            "Heading":       '        Heading(parent, "New Heading")',
            "Body":          '        Body(parent, "New text")',
            "Button":        '        Button(parent, "Click Me", color_bg=Style.COLOR_PAL_GREEN_DARK)',
            "CardCol":       '        card = CardCol(parent)',
            "CardRow":       '        card = CardRow(parent)',
            "Row":           '        row = Row(parent)',
            "Spacer":        '        Spacer(parent)',
            "TextBox":       '        TextBox(parent, placeholder="Enter text...")',
            "SelectionList": '        SelectionList(parent, data={"Item 1": {}, "Item 2": {}})',
            "PowerGrid":     '        PowerGrid(parent, data=[["Col A", "Col B"], [1, 2]])',
        }
        return snippets.get(widget_type, f'        Body(parent, "{widget_type} placeholder")')

    # ══════════════════════════════════════════════════════════════
    # FILE OPERATIONS
    # ══════════════════════════════════════════════════════════════

    def get_tab_file_path(self, tab_name):
        form_dir = Path(inspect.getfile(self.form.__class__)).parent
        return form_dir / f"{tab_name}.py"

    def backup_and_write(self, tab_name, new_method):
        if not WRITE_FILES:return

        file_path = self.get_tab_file_path(tab_name)
        if file_path.exists():
            FileManager.append_method(file_path, new_method)
        else:
            methods = self.form.TAB_LAYOUT.get(tab_name, [])
            FileManager.generate_pane_file(file_path, tab_name, methods)

    def save_form_layout(self):
        if not WRITE_FILES:  return
        form_file = inspect.getfile(self.form.__class__)
        FileManager.save_TAB_LAYOUT(form_file, self.form.TAB_LAYOUT)

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def set_status(self, msg):
        if "lbl_designer_status" in self.form.widgets:
            self.form.widgets["lbl_designer_status"].set_text(msg)