# ════════════════════════════════════════════════════════════════
# NEW FILE: WorkshopMixinDatabaseBrowser.py
# ════════════════════════════════════════════════════════════════
from ipui import *
from ipui._forms.Baseball.BbDB import BbDB
from ipui.utils.MgrClipboard import MgrClipboard                # NEW
from ipui.engine.MgrInput import MgrInput

class WorkshopMixinDatabaseBrowser:
    """Leftmost pane: browse DB objects (master) → fields (detail)."""

    # WorkshopMixinDatabaseBrowser.py method: database_browser  NEW: pane-0 dispatcher, list vs detail
    def database_browser(self, parent):
        if self.private_db_selected is None: self.build_db_list(parent)
        else:                                self.build_db_detail(parent)

    # method: build_db_list  NEW: title + filter buttons + objects grid
    def build_db_list(self, parent):
        self.banner_plate("Database", parent, center=True)
        self.build_db_filter_buttons(parent)
        card = CardCol(parent, name="card_db_objects", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_db_objects")
        self.populate_db_objects_grid(grid)

    # method: build_db_filter_buttons  NEW: All / Tables / Views, active = CTA
    def build_db_filter_buttons(self, parent):
        row = Row(parent)
        for caption, kind in (("All", "all"), ("Tables", "table"), ("Views", "view")):
            active = kind == self.private_db_filter
            color  = Style.COLOR_BUTTON_CTA if active else Style.COLOR_TAB_BG
            Button(row, caption, color_bg=color, flex_width=1, on_click=lambda k=kind: self.set_db_filter(k))

    # method: set_db_filter  NEW: change filter, rebuild pane
    def set_db_filter(self, kind):
        self.private_db_filter = kind
        self.set_pane(0, self.database_browser)

    # method: populate_db_objects_grid  NEW: [Type, Name] rows, row-click → detail
    def populate_db_objects_grid(self, grid):
        rows = BbDB.list_objects(self.private_db_filter)
        grid.set_data(rows, columns=["Type", "Name"])
        grid.on_row_click(self.on_db_object_clicked, "Name")

    # method: on_db_object_clicked  NEW: select object, show detail
    def on_db_object_clicked(self, name):
        self.private_db_selected = name
        self.set_pane(0, self.database_browser)

    # method: build_db_detail  NEW: title=name, fields grid, Back at bottom
    def build_db_detail(self, parent):
        self.banner_plate(self.private_db_selected, parent, center=True)
        card = CardCol(parent, name="card_db_fields", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_db_fields")
        self.populate_db_fields_grid(grid)
        Button(parent, "<- Back", on_click=self.back_to_db_list, flex_width=1)

    # method: populate_db_fields_grid  NEW: one column of field names (tables + views)
    def populate_db_fields_grid(self, grid):
        rows = [[name] for name in BbDB.field_names(self.private_db_selected)]
        grid.set_data(rows, columns=["Field"])
        grid.on_row_double_click(self.on_db_field_dbl_clicked, "Field")

        # method: back_to_db_list  NEW: clear selection, rebuild pane
    def back_to_db_list(self):
        self.private_db_selected = None
        self.set_pane(0, self.database_browser)

        # WorkshopMixinDatabaseBrowser.py method: editor_if_open  NEW: the open view editor, else None
    def editor_if_open(self):
        if not self.private_editing_mixin: return None
        return self.form.widgets.get("txt_wb_mixin_editor")

    # WorkshopMixinDatabaseBrowser.py method: on_db_field_dbl_clicked  NEW: insert + refocus, else copy to clipboard
    def on_db_field_dbl_clicked(self, field):
        editor = self.editor_if_open()
        if editor is None: MgrClipboard.copy(field); return
        editor.insert_text(field)
        MgrInput.focus(editor)


