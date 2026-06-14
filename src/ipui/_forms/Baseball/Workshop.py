import inspect
from ipui import *
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrSchema import MgrSchema
from ipui._forms.Baseball.MgrSqlBeautification  import MgrSqlBeautification
from ipui._forms.Baseball.WorkshopMixinBuildTable import WorkshopMixinBuildTable
from ipui._forms.Baseball.WorkshopMixinBuildView import WorkshopMixinBuildView
from ipui._forms.Baseball.WorkshopMixinDatabaseBrowser import WorkshopMixinDatabaseBrowser
from ipui.utils.EZ import EZ
from ipui.widgets.CodeScroller import CodeScroller


class Workbench(_BaseTab, WorkshopMixinBuildTable, WorkshopMixinBuildView, WorkshopMixinDatabaseBrowser):
    """Per-table command center — inspect columns, see source, (later) add/delete."""

    def ip_setup_early(self, ip):
        self.current_table              = None
        self.analysis_cache             = {}                                             # {col_name: (min, max, avg, nulls)} — populated by Analyze in Phase 2
        self.private_form_type          = "TEXT"
        self.private_form_pk            = False
        self.private_selected_view      = None
        self.private_staged_columns     = []
        self.private_selected_row       = None
        self.private_editing_mixin      = False
        self.private_editing_primary    = False
        self.private_editor_sql         = ""
        self.private_form_pk            = False
        self.private_clone_layer        = None  

        # ── WorkshopMixinBuildView ──────────────────────────────────────────────
        self.private_building_view      = False  
        self.private_build_type         = "mixin"
        self.private_build_source       = None   
        # ── WorkshopMixinBuildView ──────────────────────────────────────────────
        self.private_clone_layer        = None     # REFERENCE
        self.private_db_filter          = "all"    # NEW
        self.private_db_selected        = None     # NEW

    def load_table(self, tbl):
        self.current_table              = tbl
        self.private_selected_view      = None
        self.private_editing_mixin      = False    # NEW
        self.private_editing_primary    = False    # NEW
        self.private_building_view      = False    # NEW
        self.analysis_cache             = {}
        self.private_selected_row       = None
        self.private_staged_columns     = self.parse_schema_for_table(tbl)
        self.refresh_all_panes()
    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def fire(self, cause_text):
        """Build the full message and fire EZ.err. Never returns."""
        msg = (
            f"The 'back' button did not get added to Claude's Banner Plate\n"
            f"EVERYONE IS VERY VERY DISAPPOINTED.\n"

            f"{cause_text}\n"
            f"TIP: If you can't figure out which widget is the problem\n"
            f"TIP: Add name='anyname' to widgets in the area\n"
            f"TIP: That name will be listed in this error\n"
        )
        EZ.err(msg, exc_type=TypeError)

    def banner_plate(self, txt, parent, buttons=None, center=False):
        txtbox=None
        if isinstance(buttons, str):
            msg=            """
ROOT CAUSE:
This code used an outdated banner_plate API signature.
Expected: buttons=[("Caption", action)]
Got: old positional button args.

Claude has been assigned remedial API-awareness training.           
            """
            self.fire(msg)
        if center:
            banner = Plate(Plate(parent, pad=2), pad=2)
            txtbox= Title(banner, txt, glow=True, pad=2, text_align=CENTER)
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

    def passme(self): pass

    def source(self, parent):
        #parent.pad = Style.TOKEN_PAD

        self.banner_plate(f"SOURCE THAT FEEDS TABLE: pull_{self.current_table}", parent,
                          [(f"Edit View: pull_{self.current_table}", self.handle_edit_primary,Style.COLOR_BUTTON_CTA)])
        top_half = CardCol(parent,flex_height=.4,pad=0)
        low_half = CardCol(parent, flex_height=.6,pad=0)
        self.build_source_view_codebox(top_half)
        self.build_mixin_area(low_half)


    def build_source_view_codebox(self, parent):
        """Top half — the view that writes to the table, with Edit button."""
        tbl = self.current_table
        if not tbl:
            CodeBox(parent, "-- No table selected\n")
            return

        layer = BbDB.layer_of(tbl)
        text  = self.fetch_raw_source(tbl) if layer == "raw" else self.fetch_primary_view_source(tbl)
        #CodeBox(Card(parent,pad=2,name="test_card"), data=text)
        #CodeBox(parent, data=text)
        CodeScroller(parent, data=text)


    def fetch_source_text(self):
        tbl = self.current_table
        if not tbl: return "-- No table selected\n"
        layer = BbDB.layer_of(tbl)
        body  = self.fetch_raw_source(tbl) if layer == "raw" else self.fetch_view_source(tbl)
        return body if body.endswith("\n") else body + "\n"


    def fetch_raw_source(self, tbl):
        pipe   = self.form.get_tab("Pipe")                                   # raw pull methods live on Pipe
        prefix = "sync_" if tbl.startswith("raw") else "pull_"
        method = getattr(pipe, f"{prefix}{tbl}", None) if pipe else None
        if not method: return f"-- No pull_{tbl}() method found on Pipe"
        try:               return inspect.getsource(method)
        except Exception as e: return f"-- Could not read source: {e}"


    def columns(self, parent):
        if self.current_table:  title = f"Table: {self.current_table}"
        else:                   title = 'Table'
        self.banner_plate(title, parent, [("Clone Table", self.clone_table_on_click)])
        card = CardCol(parent, name="card_wb_columns_grid", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_wb_columns")
        self.populate_columns_grid()
        if self.private_editing_mixin:
            Title(parent, "Query Results")
            card = CardCol(parent, flex_height=1, pad=0)
            PowerGrid(card, name="grid_wb_editor_results")


    def populate_columns_grid(self):
        grid = self.form.widgets.get("grid_wb_columns")
        if not grid: return
        if not self.current_table:
            grid.set_data([["—"]], columns=["No table selected"])
            return
        rows = []
        for i, col in enumerate(self.private_staged_columns):
            rows.append([i + 1, col['name'], col['type'], '✓' if col['pk'] else ''])
        grid.set_data(rows, columns=["#", "Name", "Type", "PK"])
        grid.on_row_click(self.on_column_row_clicked, "#")


    def on_column_row_clicked(self, row_num):        self.private_selected_row = int(row_num) - 1


    def tbl_ctrls(self, par):
        self.banner_plate("Alter Table", par)
        Spacer(par)
        parent=Plate(par,pad=20,border=5)
        Detail(parent, "Name")
        TextBox(parent, name="txt_wb_new_col_name", flex_width=1)
        Detail(parent, "Type")
        self.build_type_buttons(parent)
        Detail(parent, "#  (optional position)")
        TextBox(parent, name="txt_wb_new_col_pos", flex_width=1)
        Spacer(parent)
        self.build_pk_toggle(parent)
        Button(parent, "Delete Selected", on_click=self.handle_delete_selected, flex_width=1,color_bg=Style.COLOR_BUTTON_DANGER)
        Button(parent, "Refresh",         on_click=self.handle_refresh_clicked, flex_width=1)
        Button(parent, "Add to Grid",     on_click=self.handle_add_column, flex_width=1, color_bg=Style.COLOR_BUTTON_CTA)
        Spacer(par)
        parent = Plate(par, pad=20, border=5)
        Button(parent, "Drop And\nRebuild Table",  on_click=self.commit_alter_table, flex_width=1, color_bg=Style.COLOR_BUTTON_CTA)
        Spacer(par)


    def build_type_buttons(self, parent):
        types = ["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"]
        for t in types:
            is_active = (t == self.private_form_type)
            color     = Style.COLOR_BUTTON_CTA if is_active else Style.COLOR_TAB_BG
            Button(parent, t, color_bg=color, flex_width=1,   on_click=lambda chosen=t: self.set_form_type(chosen))


    def set_form_type(self, chosen):
        self.temp_hold_field  = self.form.widgets.get("txt_wb_new_col_name").text
        #print(f"setformtype= {self.temp_hold_field}")
        self.private_form_type = chosen
        self.handle_add_column()
        self.set_pane(3, self.tbl_ctrls)
        self.form.widgets.get("txt_wb_new_col_name").set_text = self.temp_hold_field
        #print(f"setformtype2 {self.temp_hold_field}")

    def build_pk_toggle(self, parent):
        label = "✓ Primary Key" if self.private_form_pk else "☐ Primary Key"
        color = Style.COLOR_BUTTON_CTA if self.private_form_pk else Style.COLOR_TAB_BG
        Button(parent, label, color_bg=color, flex_width=1, on_click=self.toggle_form_pk)


    def toggle_form_pk(self):
        self.private_form_pk = not self.private_form_pk
        self.set_pane(3, self.tbl_ctrls)


    def handle_refresh_clicked(self):  self.refresh_all_panes()                                             # only one wired today; others land in later phases


    # ══════════════════════════════════════════════════════════════
    # REFRESH ALL — rebuild all three panes via set_pane
    # ══════════════════════════════════════════════════════════════
    def refresh_all_panes(self):

        self.set_pane(1, self.source)
        self.set_pane(2, self.columns)


    # ════════════════════════════════════════════════════════════════════════════
    # Views
    # ════════════════════════════════════════════════════════════════════════════
    def on_view_selected(self, picks):
        """Update source pane to show the selected view's SQL."""
        if not picks: return
        self.private_selected_view = picks[0]
        self.set_pane(1, self.source)


    def fetch_view_source(self, tbl):
        view_name = getattr(self, 'private_selected_view', None)
        if view_name:
            rows = BbDB.query(
                "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
                (view_name,),
            )
            return rows[0][0] + ";" if rows and rows[0][0] else f"-- No SQL for {view_name}"
        rows = BbDB.query(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type='view' AND name LIKE ? ORDER BY name",
            (f"pull_{tbl}%",),
        )
        if not rows:
            return (f"-- No views found matching 'pull_{tbl}%'")
        return ";\n\n".join(r[1] for r in rows if r[1]) + ";"





    def fetch_primary_view_source(self, tbl):
        """Return SQL for the primary pull view only (no mixins)."""
        rows = BbDB.query(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
            (f"pull_{tbl}",),
        )
        if not rows or not rows[0][0]:
            return f"-- No view 'pull_{tbl}' found"
        return rows[0][0] + ";"


    def build_mixin_area(self, parent):
        if   self.private_building_view:     self.build_view_builder(parent)
        elif self.private_editing_mixin:     self.build_mixin_editor(parent)
        elif self.private_selected_view:     self.build_mixin_detail(parent)
        else:                                self.build_mixin_list(parent)


    def build_mixin_list(self, parent):
        """Show clickable list of mixin views for current table."""
        views = self.find_mixin_views()
        if not views:
            #Detail(parent, "No Supporting views.")
            self.banner_plate("Above has no building blocks!.", parent, [("Add a Building Block", self.start_build_view )])

            return
        self.banner_plate("Building Blocks Available For Above View:", parent, [
            ("Add a Building Block", self.start_build_view , Style.COLOR_BUTTON_CTA),
            #("<- Back", self.back_to_mixin_list),
        ])

        SelectionList(parent,
            data          = {v: {} for v in views},
            single_select = True,
            flex_height   = 1,
            on_change     = self.on_view_selected,
        )


    def find_mixin_views(self):
        """Find mixin views for current table (excludes primary pull view)."""
        tbl = self.current_table
        if not tbl: return []
        rows = BbDB.query(
            "SELECT name FROM sqlite_master "
            "WHERE type='view' AND (name LIKE ? or name LIKE ?) "
            "ORDER BY name",
            (f"pull_{tbl}_mixin_%",  f"update_{tbl}%" ),
        )
        return [r[0] for r in rows]

    def build_mixin_detail(self, parent):
        """Show a single mixin view's SQL with Back + Edit buttons."""

        self.banner_plate("Building Block For Above:", parent, [
            (f"Edit View: {self.private_selected_view}",self.handle_edit_mixin,Style.COLOR_BUTTON_CTA),
            ("<- Back", self.back_to_mixin_list),
        ])
        #header = Row(parent)
        #Title(header, self.private_selected_view)
        #Spacer(header)
        #Button(header, f"Edit View {self.private_selected_view}",   color_bg=Style.COLOR_BUTTON_CTA, on_click=self.handle_edit_mixin)
        #Button(header, "<- Back", color_bg=Style.COLOR_TAB_BG,     on_click=self.back_to_mixin_list)
        rows = BbDB.query(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
            (self.private_selected_view,),
        )
        text = rows[0][0] + ";" if rows and rows[0][0] else "-- No SQL found"
        CodeScroller(parent, data=text)


    def back_to_mixin_list(self):
        self.private_selected_view = None
        self.set_pane(1, self.source)


    # ══════════════════════════════════════════════════════════════
    # SCHEMA PARSING — _SchemaTbl.SCHEMA → editable dicts
    # ══════════════════════════════════════════════════════════════
    def parse_schema_for_table(self, tbl):
        """Parse _SchemaTbl.SCHEMA → [{'name', 'type', 'pk'}, ...]"""
        if not tbl: return []
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl
        columns = []
        for schema_tbl, col_decl in _SchemaTbl.SCHEMA:
            if schema_tbl != tbl: continue
            stripped = col_decl.strip()
            if stripped.upper().startswith('PK'):
                pk   = True
                rest = stripped[2:].strip()
            else:
                pk   = False
                rest = stripped
            parts    = rest.split()
            name     = parts[0]
            col_type = parts[1] if len(parts) > 1 else 'TEXT'
            columns.append({'name': name, 'type': col_type, 'pk': pk})
        return columns


    # ══════════════════════════════════════════════════════════════
    # ADD / DELETE — modify staged columns, refresh grid
    # ══════════════════════════════════════════════════════════════
    def handle_add_column(self):
        name_w = self.form.widgets.get("txt_wb_new_col_name")
        pos_w  = self.form.widgets.get("txt_wb_new_col_pos")
        if not name_w: return
        name = name_w.text.strip()
        if not name: return
        col  = {'name': name, 'type': self.private_form_type, 'pk': self.private_form_pk}
        pos_text = pos_w.text.strip() if pos_w else ''
        if pos_text.isdigit():
            self.private_staged_columns.insert(max(0, int(pos_text) - 1), col)
        else:
            self.private_staged_columns.append(col)
        name_w.set_text('')
        if pos_w: pos_w.set_text('')
        self.refresh_columns_pane()


    def handle_delete_selected(self):
        idx = self.private_selected_row
        if idx is None: return
        if 0 <= idx < len(self.private_staged_columns):
            self.private_staged_columns.pop(idx)
            self.private_selected_row = None
            self.refresh_columns_pane()


    def refresh_columns_pane(self):  self.set_pane(2, self.columns)


    # ══════════════════════════════════════════════════════════════
    # SAVE — write staged columns back to _SchemaTbl.py, rebuild
    # ══════════════════════════════════════════════════════════════
    def commit_alter_table(self):
        tbl = self.current_table
        if not tbl or not self.private_staged_columns: return
        MgrSchema.replace_table_schema(tbl, self.private_staged_columns)
        self.form.show_modal("Old table is IRRADICATED", 1.69,self.refresh_after_table_alter)

        self.refresh_all_panes()
        #self.form.tab_strip.resolve_tab("Pipe").refresh_pane(0)

        self.form.tab_strip.resolve_tab("Pipe").private_stale = True


    def refresh_after_table_alter(self):
        self.refresh_all_panes()

    # ══════════════════════════════════════════════════════════════
    # Edit Mixin Views
    # ══════════════════════════════════════════════════════════════
    def handle_edit_mixin(self):
        """Switch to edit mode for the selected mixin view."""
        rows = BbDB.query(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
            (self.private_selected_view,),
        )
        full_sql = rows[0][0] if rows and rows[0][0] else ""
        self.private_editor_sql     = self.strip_create_view(full_sql)
        self.private_editing_mixin  = True
        self.set_pane(1, self.source)
        self.set_pane(2, self.columns)


    def build_mixin_editor(self, parent):
        """Editable SQL editor for the selected mixin view."""


        self.banner_plate(f"EDITING VIEW: {self.private_selected_view}", parent, [
            ("Run View", self.handle_run_mixin_query,Style.COLOR_BUTTON_CTA),
            ("SQL Beau", self.beautify_the_sql),
            ("Save View", self.view_save_selected),
            ("<- Cancel", self.handle_back_from_editor),
        ])


        #orig card = Card(parent, scroll_v=True, pad=2, flex_height=1)
        #orig TextArea(card, self.private_editor_sql, name="txt_wb_mixin_editor", flex_height=1, wrap=False, scroll_h=True)

        card = Card(parent, scroll_v=True, scroll_h=True, pad=2, flex_height=1)
        TextArea(card, self.private_editor_sql, name="txt_wb_mixin_editor", flex_height=0, wrap=False)

    def beautify_the_sql(self):
        beautiful = MgrSqlBeautification.format_sql (self.form.widgets.get("txt_wb_mixin_editor").text)
        self.form.widgets.get("txt_wb_mixin_editor").set_text(beautiful)

    def handle_run_mixin_query(self):
        """Run the editor SQL and populate the results grid."""
        txt = self.form.widgets.get("txt_wb_mixin_editor")
        if not txt: return
        sql         = txt.text.strip()
        cols, rows  = self.execute_editor_query(sql)
        grid        = self.form.widgets.get("grid_wb_editor_results")
        if grid: grid.set_data(rows, columns=cols)


    def execute_editor_query(self, sql):
        """Execute SQL and return (col_names, rows). Catches errors."""
        import sqlite3
        try:
            conn   = sqlite3.connect(BbDB.DB_PATH)
            cur    = conn.execute(sql)
            if not cur.description:
                conn.close()
                return ["status"], [["Statement executed (no results)"]]
            cols = [d[0] for d in cur.description]
            rows = [list(r) for r in cur.fetchall()]
            conn.close()
            return cols, rows if rows else [["No results"]]
        except Exception as e:
            return ["error"], [[str(e)]]

    def view_save_selected(self):
        err = self.view_save(self.private_selected_view, self.form.widgets.get("txt_wb_mixin_editor").text)
        if err:
            grid = self.form.widgets.get("grid_wb_editor_results")
            if grid: grid.set_data([[err]], columns=["error"])
            return
        self.private_editing_mixin = False
        if self.private_editing_primary:
            self.private_editing_primary = False
            self.private_selected_view  = None
        self.set_pane(1, self.source)
        self.set_pane(2, self.columns)


    def view_save(self,view_name, sql_proposed_for_view):
        error    = self.view_validate(view_name, sql_proposed_for_view)
        if error : return error
        MgrSchema. save_view(view_name, sql_proposed_for_view)
        return None


    def view_validate(self, view_name, sql_proposed_for_view):
        if not sql_proposed_for_view: return "C'mon bro... write a select!"
        return MgrSchema.test_sql(view_name, sql_proposed_for_view)  # returns None if check is good

    def replace_view_return(self, file_text, view_name, new_sql):
        """Find view_{name} method, replace its return triple-quote string."""
        method_name = f"def view_{view_name}("
        lines       = file_text.splitlines(keepends=True)

        method_idx  = None
        return_idx  = None
        close_idx   = None

        for i, line in enumerate(lines):
            if method_name in line:
                method_idx = i
            elif method_idx is not None and return_idx is None:
                if 'return """' in line or "return '''" in line:
                    return_idx = i
            elif return_idx is not None and close_idx is None:
                if '"""' in line or "'''" in line:
                    close_idx = i
                    break

        if None in (method_idx, return_idx, close_idx):
            return None

        indent      = "            "
        new_body    = f'        return """\n{indent}{new_sql.strip()}\n        """\n'
        result      = lines[:return_idx] + [new_body] + lines[close_idx + 1:]
        return ''.join(result)

    def handle_back_from_editor(self):
        """Exit edit mode, return to appropriate view."""
        self.private_editing_mixin = False
        if self.private_editing_primary:
            self.private_editing_primary = False
            self.private_selected_view  = None
        self.set_pane(1, self.source)
        self.set_pane(2, self.columns)


    def handle_edit_primary(self):
        """Edit the primary pull view using the bottom editor."""
        tbl = self.current_table
        if not tbl: return
        view_name = f"pull_{tbl}"
        rows = BbDB.query(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
            (view_name,),
        )
        full_sql = rows[0][0] if rows and rows[0][0] else ""
        self.private_editor_sql      = self.strip_create_view(full_sql)
        self.private_selected_view   = view_name
        self.private_editing_mixin   = True
        self.private_editing_primary = True
        self.set_pane(1, self.source)
        self.set_pane(2, self.columns)

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def strip_create_view(self, sql):
        """Strip 'CREATE VIEW xxx AS' prefix, return bare SELECT."""
        import re
        match = re.search(r'\bAS\b\s+', sql, re.IGNORECASE)
        return sql[match.end():].strip() if match else sql.strip()
