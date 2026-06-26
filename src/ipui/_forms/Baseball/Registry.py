# Registry.py  NEW FILE — manage the grammar vocabulary (_registry table). Left: filterable PowerGrid.
#   Right: add/edit form. Classmethod accessors are what MgrGrammar will read.
from ipui import *
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrDT import MgrDT
from ipui._forms.Baseball.WorkshopMixinDatabaseBrowser import WorkshopMixinDatabaseBrowser
from ipui.engine.MgrInput import MgrInput
from ipui.utils.MgrClipboard import MgrClipboard
from ipui._forms.Baseball.MgrBackup import MgrBackup

class Registry(_BaseTab,WorkshopMixinDatabaseBrowser):
    """Vocabulary registry for the field grammar {Entity}_{Metric}_{TimeSlice}_{Context}.
       TimeSlice isn't registered — it's just integers (3 = 3 days). Types managed here are
       Entity / Metric / Context (key-types may join later)."""

    KINDS = ["Entity", "Metric", "Context"]

    def ip_setup_early(self, ip):
        self.private_filter             = None
        self.private_clone_layer        = None     # REFERENCE
        self.private_db_filter          = "all"    # NEW
        self.private_db_selected        = None     # NEW
        self.current_table              = None     # NEW — builder: selected table
        self.private_staged_columns     = []       # NEW — builder: parsed columns [{name,type,pk}]
        self.private_selected_row       = None     # NEW — builder: selected column index



    def ip_activated(self, ip):
        self.load_grid(self.private_filter)
    def banner_plate(self, txt, parent, buttons=None, center=False):
        txtbox = None

        if center:
            banner = Plate(Plate(parent, pad=2), pad=2)
            txtbox = Title(banner, txt, glow=True, pad=2, text_align=CENTER)
            return txtbox

        banner = Row(Plate(Plate(parent, pad=2), pad=2))
        txtbox = Title(banner, txt, glow=True, pad=2)
        Spacer(banner)

        if buttons:
            for button in buttons:
                btnText, btnAction, *extra = button
                color_bg = extra[0] if extra else None
                Button(banner, btnText, on_click=btnAction, color_bg=color_bg)

        return txtbox



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

    def parse_schema_for_table(self, tbl):
        if not tbl: return []
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl
        cols = []
        for schema_tbl, col_decl in _SchemaTbl.SCHEMA:
            if schema_tbl != tbl: continue
            decl = col_decl.strip()
            pk   = decl.upper().startswith("PK")
            rest = decl[2:].strip() if pk else decl
            parts    = rest.split()
            name     = parts[0]
            col_type = parts[1] if len(parts) > 1 else "TEXT"
            cols.append({'name': name, 'type': col_type, 'pk': pk})
        return cols

    def load_table(self, tbl):
        self.current_table          = tbl
        self.private_selected_row   = None
        self.private_staged_columns = self.parse_schema_for_table(tbl)
        self.set_pane(2, self.columns)

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




    # ════════════════════════════════════════════════
    # Pane 1 — list + filters
    # ════════════════════════════════════════════════
    def registry_list(self, parent):
        self.header_and_grid( parent)
        self.editor(parent)

    def header_and_grid(self, parent):
        head = Row(Plate(Card(parent, pad=3), pad=5))
        Title(head, "Fld Registry", glow=True)
        Spacer(head)
        self.filter_buttons(head)
        card = Card(parent, flex_height=1, pad=3)
        grid = PowerGrid(card, name="grid_registry", flex_height=1)
        grid.on_row_click(self.load_for_edit)
        self.load_grid()

    def filter_buttons(self, parent):
        Button(parent, "All",     on_click=lambda: self.load_grid(None))
        Button(parent, "Entity",  on_click=lambda: self.load_grid("Entity"))
        Button(parent, "Metric",  on_click=lambda: self.load_grid("Metric"))
        Button(parent, "Context", on_click=lambda: self.load_grid("Context"))

    def editor(self, parent):
        head = Row(Plate(Card(parent, pad=3), pad=5))
        row=Row(head)
        Title(row, "Add / Edit           ", glow=True)
        ButtonGroup(row, data=Registry.KINDS, name="grp_kind",hug_parent=True, pad=0)
        body = Card(parent, pad=5)
        TextBox(body, name="txt_token",placeholder="Token (e.g. ba):")
        TextBox(body, name="txt_def",placeholder="Definition:")

        btns = Row(body)
        Button(btns, "Save",   color_bg=Style.COLOR_BUTTON_CTA,    flex_width=1, on_click=self.save_entry)
        Button(btns, "New",    flex_width=1,                       on_click=self.new_entry)
        Button(btns, "Delete", color_bg=Style.COLOR_BUTTON_DANGER, flex_width=1, on_click=self.delete_entry)

    # ════════════════════════════════════════════════
    # Pane 2 — add / edit
    # ════════════════════════════════════════════════


    # ════════════════════════════════════════════════
    # Handlers
    # ════════════════════════════════════════════════
    def load_grid(self, kind=None):
        """Repopulate the grid, optionally filtered to one kind."""
        self.private_filter = kind
        rows = [list(r) for r in Registry.all_rows() if kind is None or r[0] == kind]
        grid = self.form.widgets.get("grid_registry")
        if grid is not None: grid.set_data(rows, columns=["Type", "Token", "Definition"])
    def on_db_object_clicked(self, name):
        self.load_table(name)
    def load_for_edit(self, row):
        self.form.widgets["grp_kind"].value = row["Type"]
        self.set_widget_text("txt_token", row["Token"])
        self.set_widget_text("txt_def",   row["Definition"])
    def populate_db_objects_grid(self, grid):
        rows = BbDB.list_objects(self.private_db_filter)
        grid.set_data(rows, columns=["Type", "Name"])
        grid.on_row_click(self.on_db_object_clicked, "Name")            # single  → load into builder (columns)
        grid.on_row_double_click(self.on_db_object_dbl_clicked, "Name") # double  → field detail (works for views too)

    # Registry.py  method: on_db_object_dbl_clicked  NEW: drill into the object's field list
    def on_db_object_dbl_clicked(self, name):
        self.private_db_selected = name
        self.set_pane(0, self.database_browser)

    def new_entry(self):
        self.private_edit_kind = None
        for n in ("lbl_kind", "txt_token", "txt_def"): self.set_widget_text(n, "")

    def delete_entry(self):
        kind = self.form.widgets["grp_kind"].value
        token = self.form.widgets["txt_token"].text.strip()
        if not kind or not token:
            BbDB.log("registry", "select a row to delete");
            return
        BbDB.execute("DELETE FROM _registry WHERE kind=? AND token=?", (kind, token))
        self.new_entry()
        self.load_grid(self.private_filter)
        MgrBackup.export_all()

    def set_widget_text(self, name, text):
        """Safe set_text by registry name (no-op if not built yet)."""
        w = self.form.widgets.get(name)
        if w is not None: w.set_text(text)



    # ════════════════════════════════════════════════
    # Accessors — classmethods, DB-backed (MgrGrammar reads these)
    # ════════════════════════════════════════════════
    @classmethod
    def all_rows(cls):
        """Every vocab row as (kind, token, definition)."""
        return BbDB.query("SELECT kind, token, definition FROM _registry ORDER BY kind, token")

    @classmethod
    def tokens_of(cls, kind):
        return [tok for k, tok, _ in cls.all_rows() if k == kind]

    @classmethod
    def entities(cls): return cls.tokens_of("Entity")
    @classmethod
    def metrics(cls):  return cls.tokens_of("Metric")
    @classmethod
    def contexts(cls): return cls.tokens_of("Context")

    @classmethod
    def is_valid(cls, kind, token):
        """True if token is a registered member of kind."""
        return token in cls.tokens_of(kind)

    def columns(self, parent):
        title = f"Table: {self.current_table}" if self.current_table else "Table"
        self.banner_plate(title, parent, center=True)
        card = CardCol(parent, name="card_cols", flex_height=1, pad=0)
        PowerGrid(card, name="grid_cols")
        self.populate_columns_grid()

    # Registry.py  method: populate_columns_grid  NEW: fill grid_cols from staged columns
    def populate_columns_grid(self):
        grid = self.form.widgets.get("grid_cols")
        if grid is None: return
        if not self.current_table:
            grid.set_data([["—"]], columns=["No table selected"]); return
        rows = [[i + 1, c['name'], c['type'], '✓' if c['pk'] else '']
                for i, c in enumerate(self.private_staged_columns)]
        grid.set_data(rows, columns=["#", "Name", "Type", "PK"])
        grid.on_row_click(self.on_column_row_clicked, "#")

    # Registry.py  method: on_column_row_clicked  NEW: remember which column is selected
    def on_column_row_clicked(self, row_num):
        self.private_selected_row = int(row_num) - 1


    ############################ table controls


    # Registry.py  method: tbl_ctrls  NEW: pane 3 — Alter Table form. Type + PK are ButtonGroups (recolor in place)
    def tbl_ctrls(self, parent):
        self.banner_plate("Alter Table", parent, center=True)
        Spacer(parent)
        form = Plate(parent, pad=20, border=5)
        Detail(form, "Name")
        TextBox(form, name="txt_col_name", flex_width=1)
        Detail(form, "Type")
        ButtonGroup(form, data=["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"], initial_value="TEXT", name="grp_col_type")
        Detail(form, "#  (optional position)")
        TextBox(form, name="txt_col_pos", flex_width=1)
        Spacer(form)
        ButtonGroup(form, data=[(False, "☐ Not Key"), (True, "✓ Primary Key")], initial_value=False, name="grp_col_pk")
        Button(form, "Delete Selected", on_click=self.handle_delete_selected, flex_width=1, color_bg=Style.COLOR_BUTTON_DANGER)
        Button(form, "Add to Grid",     on_click=self.handle_add_column,      flex_width=1, color_bg=Style.COLOR_BUTTON_CTA)
        Spacer(parent)
        danger = Plate(parent, pad=20, border=5)
        Button(danger, "Drop And\nRebuild Table", on_click=self.commit_alter_table, flex_width=1, color_bg=Style.COLOR_BUTTON_CTA)
        Spacer(parent)

    # Registry.py  method: handle_add_column  NEW: stage a column, reading type/PK straight off the ButtonGroups
    def handle_add_column(self):
        name = self.form.widgets["txt_col_name"].text.strip()
        if not name: return
        col = {
            'name': name,
            'type': self.form.widgets["grp_col_type"].value,
            'pk'  : self.form.widgets["grp_col_pk"].value,
        }
        pos = self.form.widgets["txt_col_pos"].text.strip()
        if pos.isdigit(): self.private_staged_columns.insert(max(0, int(pos) - 1), col)
        else:             self.private_staged_columns.append(col)
        self.form.widgets["txt_col_name"].set_text('')
        self.form.widgets["txt_col_pos"].set_text('')
        self.refresh_columns_pane()

    # Registry.py  method: handle_delete_selected  NEW: unstage the selected column
    def handle_delete_selected(self):
        idx = self.private_selected_row
        if idx is None: return
        if 0 <= idx < len(self.private_staged_columns):
            self.private_staged_columns.pop(idx)
            self.private_selected_row = None
            self.refresh_columns_pane()

    # Registry.py  method: refresh_columns_pane  NEW: repaint pane 2 from staged columns
    def refresh_columns_pane(self):
        self.set_pane(2, self.columns)

    # Registry.py  method: commit_alter_table  NEW: write staged cols to _SchemaTbl, rebuild table, reload
    def commit_alter_table(self):
        tbl = self.current_table
        if not tbl or not self.private_staged_columns: return
        from ipui._forms.Baseball.MgrSchema import MgrSchema
        MgrSchema.replace_table_schema(tbl, self.private_staged_columns)
        self.form.tab_strip.resolve_tab("Pipe").private_stale = True
        self.form.show_modal("Old table IRRADICATED — rebuilt from staged columns", 1.5, self.after_commit)

    # Registry.py  method: after_commit  NEW: re-parse the now-updated schema back into the grid
    def after_commit(self):
        self.load_table(self.current_table)




    ############TEMP ADD DELETE BELO

    KINDS       = ["Entity", "Metric", "Context"]                          # REFERENCE (already present)
    DTYPES      = ["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"]           # NEW — shared with Alter Table
    RATE_TOKENS = {"ba", "avg", "woba", "obp", "slg", "ops", "era", "whip", "xba"}  # NEW

    # Registry.py  method: editor  Update: + dtype ButtonGroup (reuses the Alter-Table type widget)
    def editor(self, parent):
        head = Row(Plate(Card(parent, pad=3), pad=5))
        row  = Row(head)
        Title(row, "Add / Edit           ", glow=True)
        ButtonGroup(row, data=Registry.KINDS, name="grp_kind", hug_parent=True, pad=0)
        body = Card(parent, pad=5)
        TextBox(body, name="txt_token", placeholder="Token (e.g. ba):")
        TextBox(body, name="txt_def",   placeholder="Definition:")
        Detail(body, "Data type (metrics):")
        ButtonGroup(body, data=Registry.DTYPES, initial_value="INTEGER", name="grp_dtype")
        btns = Row(body)
        Button(btns, "Save",   color_bg=Style.COLOR_BUTTON_CTA,    flex_width=1, on_click=self.save_entry)
        Button(btns, "New",    flex_width=1,                       on_click=self.new_entry)
        Button(btns, "Delete", color_bg=Style.COLOR_BUTTON_DANGER, flex_width=1, on_click=self.delete_entry)


    def save_entry(self):
        kind  = self.form.widgets["grp_kind"].value
        token = self.form.widgets["txt_token"].text.strip()
        defn  = self.form.widgets["txt_def"].text.strip()
        dtype = self.form.widgets["grp_dtype"].value
        if not kind or not token:
            BbDB.log("registry", "pick a Type and enter a token"); return
        BbDB.execute("DELETE FROM _registry WHERE kind=? AND token=?", (kind, token))
        BbDB.execute("INSERT INTO _registry (GD, kind, token, definition, dtype) VALUES (?,?,?,?,?)",
                     (MgrDT.today_gd(), kind, token, defn, dtype))
        self.load_grid(self.private_filter)
        MgrBackup.export_all()

    # Registry.py  method: load_for_edit  Update: seed the dtype selector (stored, or smart default)
    def load_for_edit(self, row):
        self.form.widgets["grp_kind"].value  = row["Type"]
        self.form.widgets["grp_dtype"].value = Registry.dtype_of(row["Token"])
        self.set_widget_text("txt_token", row["Token"])
        self.set_widget_text("txt_def",   row["Definition"])

    # Registry.py  method: dtype_of  NEW: a metric's declared type, else a smart default (composer reads this)
    @classmethod
    def dtype_of(cls, token):
        rows   = BbDB.query("SELECT dtype FROM _registry WHERE kind='Metric' AND token=?", (token,))
        stored = rows[0][0] if rows and rows[0][0] else None
        return stored or cls.default_dtype(token)

    # Registry.py  method: default_dtype  NEW: rate-ish → REAL, else INTEGER (used when dtype is unset)
    @classmethod
    def default_dtype(cls, token):
        t = token.lower()
        if t in cls.RATE_TOKENS or t.endswith("_pct") or t.endswith("_rate") or t.endswith("_ba"):
            return "REAL"
        return "INTEGER"