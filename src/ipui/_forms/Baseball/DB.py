# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# DB.py  NEW FILE — the "DB" tab (next-gen Registry). Pane 0 Database Browser · Pane 1 Fld Registry (+Key) ·
#   Pane 2 The Object · Pane 3 The Inspector. CSR clean-slate: panes 0–1 re-admitted BY HAND from the old
#   Registry, swapping the retired banner_plate() method for the BannerPlate widget (its debut). Panes 2–3 are
#   anchor-1 stubs. Vocab is read DB-direct (never off a filtered grid). DB is the ONLY _BaseTab subclass in
#   this file on purpose — the tab resolver returns the first one it finds.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════
from ipui import *
from ipui._forms.Baseball.MgrSchema import MgrSchema
from ipui.widgets.BannerPlate import BannerPlate
from ipui._forms.Baseball.BbDB      import BbDB
from ipui._forms.Baseball.MgrDT     import MgrDT
from ipui._forms.Baseball.MgrBackup import MgrBackup
from ipui.utils.MgrClipboard        import MgrClipboard





# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# DB.py  NEW FILE — the "DB" tab (next-gen Registry). Pane 0 Database Browser · Pane 1 Fld Registry (+Key) ·
#   Pane 2 The Object · Pane 3 The Inspector. CSR clean-slate: panes 0–1 re-admitted BY HAND from the old
#   Registry, swapping the retired banner_plate() method for the BannerPlate widget (its debut). Panes 2–3 are
#   anchor-1 stubs. Vocab is read DB-direct (never off a filtered grid). DB is the ONLY _BaseTab subclass in
#   this file on purpose — the tab resolver returns the first one it finds.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════
from ipui import *
from ipui._forms.Baseball.MgrSchema import MgrSchema
from ipui.widgets.BannerPlate import BannerPlate
from ipui._forms.Baseball.BbDB      import BbDB
from ipui._forms.Baseball.MgrDT     import MgrDT
from ipui.utils.MgrClipboard        import MgrClipboard


class DB(_BaseTab):
    """Next-gen Registry. Controlled vocabulary in; garbage names unreachable.
       Panes: 0 Database Browser · 1 Fld Registry (+Key) · 2 The Object · 3 The Inspector."""

    KINDS  = ["Entity", "Metric", "Context", "Key"]                     # Key is the new 4th kind — carries a dtype, like Metric
    DTYPES = ["TEXT", "INTEGER", "REAL", "NUMERIC", "BLOB"]
    VIEW_NAME_TRIM = 12
    # ── lifecycle ───────────────────────────────────────────────────────────────────
    def ip_setup_early(self, ip):
        """Init every pane's state: browser filter/selection, registry filter, selected object,
           edit/clone mode + proposed-columns + selected-row, and the Inspector's facet/layer/suffix."""
        self.private_db_filter      = "all"                                # browser:  all | table | view
        self.private_db_selected    = None                                 # browser:  drilled-into object (detail view)
        self.private_reg_filter     = None                                 # registry: kind filter (None = all)
        self.current_table          = None                                 # object selected for Pane 2

        # For DB
        self.private_mode           = "browse"                             # browse | edit | clone
        self.private_proposed       = []                                   # proposed columns (seeded from Original on edit/clone)
        self.private_sel_row        = None                                 # selected Proposed row index
        # For Alter
        self.private_facet          = "Identity"                           # Identity | Keys | Metrics
        self.private_layer          = None                                 # clone: chosen layer
        self.private_suffix         = ""                                   # clone: free-text suffix
        self.private_metric_picks   = {}                                  # NEW
        self.private_show_tracks    = False                                 # NEW

    def ip_activated(self, ip):
        """Fill the registry grid; inherit table context from sibling tab if needed."""
        self.load_grid(self.private_reg_filter)
        if self.current_table is None and getattr(self.form, 'last_viewed_table', None):  # NEW
            self.load_table(self.form.last_viewed_table)

    # ════════════════════════════════════════════════════════════════════════════════
    # PANE 0 — Database Browser  (re-admitted by hand; banner_plate → BannerPlate)
    # ════════════════════════════════════════════════════════════════════════════════
    def database_browser(self, parent):
        """Pane-0 root: show the objects list, or a drilled-into object's field list."""
        if self.private_db_selected is None: self.build_db_list(parent)
        else:                                self.build_db_detail(parent)

    def build_db_list(self, parent):
        """Title banner + All/Tables/Views filter buttons + the grid of matching DB objects."""
        BannerPlate(parent, "Database", text_align=CENTER)
        self.build_db_filter_buttons(parent)
        card = CardCol(parent, name="card_db_objects", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_db_objects")
        self.populate_db_objects_grid(grid)

    def build_db_filter_buttons(self, parent):
        """All / Tables / Views row; the active filter's button is painted as the CTA color."""
        row = Row(parent)
        for caption, kind in (("All", "all"), ("Tables", "table"), ("Views", "view")):
            active = kind == self.private_db_filter
            color  = Style.COLOR_BUTTON_CTA if active else Style.COLOR_TAB_BG
            Button(row, caption, color_bg=color, flex_width=1, on_click=lambda k=kind: self.set_db_filter(k))

    def set_db_filter(self, kind):
        """Switch the browser's object-kind filter and repaint Pane 0."""
        self.private_db_filter = kind
        self.set_pane(0, self.database_browser)

    def populate_db_objects_grid(self, grid):
        """Load the filtered objects into the grid; single-click loads The Object, double-click drills fields."""
        grid.set_data(BbDB.list_objects(self.private_db_filter), columns=["Type", "Name"])
        grid.on_row_click(self.on_db_object_clicked, "Name")
        grid.on_row_double_click(self.on_db_object_dbl_clicked, "Name")

    def on_db_object_dbl_clicked(self, name):
        """Double-click drills into the object's field list (Pane 0 detail view)."""
        self.private_db_selected = name
        self.set_pane(0, self.database_browser)

    def build_db_detail(self, parent):
        """Drilled-into object: name banner + its field-name grid + a Back button."""
        BannerPlate(parent, self.private_db_selected, text_align=CENTER)
        card = CardCol(parent, name="card_db_fields", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_db_fields")
        grid.set_data([[n] for n in BbDB.field_names(self.private_db_selected)], columns=["Field"])
        grid.on_row_double_click(self.on_db_field_dbl_clicked, "Field")
        Button(parent, "<- Back", on_click=self.back_to_db_list, flex_width=1)

    def back_to_db_list(self):
        """Clear the drilled-into selection and return to the objects list."""
        self.private_db_selected = None
        self.set_pane(0, self.database_browser)

    def load_table(self, name):
        """Remember the clicked object as the current table and repaint The Object pane."""
        self.current_table = name
        self.form.last_viewed_table = name
        self.set_pane(2, self.the_object)

    # ════════════════════════════════════════════════════════════════════════════════
    # PANE 1 — Fld Registry  (re-admitted; +Key kind, dtype kept for Metric & Key)
    # ════════════════════════════════════════════════════════════════════════════════
    def fld_registry(self, parent):
        """Pane-1 root: vocab header/grid on top, the add/edit editor below."""
        self.build_registry_header(parent)
        self.build_registry_editor(parent)

    def build_registry_header(self, parent):
        """Title + kind-filter buttons + the vocab grid; clicking a row loads it for editing."""
        head = Row(Plate(Card(parent, pad=3), pad=5))
        Title(head, "Fld Registry", glow=True)
        Spacer(head)
        self.registry_filter_buttons(head)
        card = Card(parent, flex_height=1, pad=3)
        grid = PowerGrid(card, name="grid_db_reg", flex_height=1)
        grid.on_row_click(self.load_for_edit)
        self.load_grid(self.private_reg_filter)

    def registry_filter_buttons(self, parent):
        """All + one button per KINDS entry (Entity / Metric / Context / Key)."""
        Button(parent, "All", on_click=lambda: self.load_grid(None))
        for kind in DB.KINDS:
            Button(parent, kind, on_click=lambda k=kind: self.load_grid(k))

    def load_grid(self, kind=None):
        """Repopulate the vocab grid DB-direct from _registry, optionally filtered by kind."""
        self.private_reg_filter = kind
        #all_rows = BbDB.query("SELECT kind, token, definition FROM _registry ORDER BY kind, token")
        all_rows = BbDB.query("SELECT kind, token, seq, definition FROM _registry ORDER BY kind, token")
        rows     = [list(r) for r in all_rows if kind is None or r[0] == kind]

        grid     = self.form.widgets.get("grid_db_reg")
        if grid is not None: grid.set_data(rows, columns=["Type", "Token", "Definition"])
        if grid is not None: grid.set_data(rows, columns=["Type", "Token", "Seq", "Definition"])

    def build_registry_editor(self, parent):
        """Kind selector + token/definition text boxes + dtype picker + Save/New/Delete buttons."""
        head = Row(Plate(Card(parent, pad=3), pad=5))
        row  = Row(head)
        Title(row, "Add / Edit           ", glow=True)
        ButtonGroup(row, data=DB.KINDS, name="grp_db_kind", hug_parent=True, pad=0)
        body = Card(parent, pad=5)
        TextBox(body, name="txt_db_token", placeholder="Token (e.g. ba):")
        TextBox(body, name="txt_db_def",   placeholder="Definition:")
        TextBox(body, name="txt_db_seq", placeholder="Seq (sort order):")
        Detail(body, "Data type (metrics / keys):")
        ButtonGroup(body, data=DB.DTYPES, initial_value="INTEGER", name="grp_db_dtype")
        self.build_registry_buttons(body)

    def build_registry_buttons(self, body):
        """Save / New / Delete row for the registry editor."""
        btns = Row(body)
        Button(btns, "Save",   color_bg=Style.COLOR_BUTTON_CTA,    flex_width=1, on_click=self.save_entry)
        Button(btns, "New",    flex_width=1,                       on_click=self.new_entry)
        Button(btns, "Delete", color_bg=Style.COLOR_BUTTON_DANGER, flex_width=1, on_click=self.delete_entry)

    def save_entry(self):
        """Upsert the editor's (kind, token) row into _registry, carrying dtype and seq."""
        kind  = self.form.widgets["grp_db_kind"].value
        token = self.form.widgets["txt_db_token"].text.strip()
        defn  = self.form.widgets["txt_db_def"].text.strip()
        dtype = self.form.widgets["grp_db_dtype"].value
        seq_t = self.form.widgets["txt_db_seq"].text.strip()
        seq   = int(seq_t) if seq_t.isdigit() else None
        MgrSchema.flds_upsert(kind, token, defn, dtype, seq)
        self.load_grid(self.private_reg_filter)

    def new_entry(self):
        """Clear the token/definition/seq fields for a fresh add."""
        for n in ("txt_db_token", "txt_db_def", "txt_db_seq"): self.set_widget_text(n, "")

    def delete_entry(self):
        """Delete the (kind, token) row that matches the editor's current fields."""
        kind  = self.form.widgets["grp_db_kind"].value
        token = self.form.widgets["txt_db_token"].text.strip()
        if not kind or not token:
            BbDB.log("registry", "select a row to delete"); return
        MgrSchema.flds_delete(kind, token)
        self.new_entry()
        self.load_grid(self.private_reg_filter)

    def load_for_edit(self, row):
        """Seed the editor's fields from a clicked vocab row (dtype + seq re-read DB-direct)."""
        self.form.widgets["grp_db_kind"].value  = row["Type"]
        self.form.widgets["grp_db_dtype"].value = self.dtype_for(row["Type"], row["Token"])
        self.set_widget_text("txt_db_token", row["Token"])
        self.set_widget_text("txt_db_def",   row["Definition"])
        self.set_widget_text("txt_db_seq",   str(MgrSchema.seq_for(row["Type"], row["Token"])))

    def dtype_for(self, kind, token):
        """The stored dtype for a (kind, token) pair, defaulting to INTEGER if unset."""
        rows = BbDB.query("SELECT dtype FROM _registry WHERE kind=? AND token=?", (kind, token))
        return rows[0][0] if rows and rows[0][0] else "INTEGER"

    def set_widget_text(self, name, text):
        """set_text on a registry-looked-up widget, no-op if the name isn't found."""
        w = self.form.widgets.get(name)
        if w is not None: w.set_text(text)

    # ════════════════════════════════════════════════════════════════════════════════
    # PANE 2 — The Object  (browse / edit / clone of a table's columns)
    # ════════════════════════════════════════════════════════════════════════════════
    def the_object(self, parent):
        """Pane-2 root: nothing selected → placeholder; browse mode vs edit/clone editor otherwise."""
        if not self.current_table:
            BannerPlate(parent, "Table: (none selected)", text_align=CENTER); return
        if self.private_mode == "browse": self.build_object_browse(parent)
        else:                             self.build_object_editor(parent)

    def build_object_browse(self, parent):
        """Browse mode: banner with Edit/Clone/Delete + the read-only columns grid."""
        BannerPlate(parent, f"Table: {self.trim_view_name(self.current_table)}",
                    data=[("Edit", self.handle_edit), ("Clone", self.handle_clone),("Tracks", self.handle_tracks), ("Delete", self.handle_delete)])
        card = CardCol(parent, name="card_db_obj", flex_height=1, pad=0)
        grid = PowerGrid(card, name="grid_db_obj")
        grid.set_data(self.cols_to_rows(self.read_columns(self.current_table)), columns=["#", "Name", "Type", "PK"])

    def build_object_editor(self, parent):
        """Edit/clone mode: named banner (carries the live name preview) + Original | Proposed side-by-side grids."""
        BannerPlate(parent, self.object_banner_text(), name="bnr_object", data=[("Cancel", self.handle_cancel)])
        grids = Row(parent, flex_height=1)
        self.build_side_grid(grids, "Original (reference)", "grid_db_original",
                             self.read_columns(self.current_table), clickable=False)
        self.build_side_grid(grids, "Proposed (editable)", "grid_db_proposed",
                             self.private_proposed, clickable=True)

    def object_banner_text(self):
        """Banner text: 'Editing: x' in edit mode, 'Building: layer_suffix' in clone mode."""
        if self.private_mode == "edit": return f"Editing: {self.current_table}"
        return f"Building: {self.proposed_name() or '…'}"

    def build_side_grid(self, parent, label, grid_name, cols, clickable):
        """One labelled column-grid half (Original or Proposed); restores the row selection,
           then forces a rebuild so the restored highlight actually paints."""
        col  = CardCol(parent, flex_width=1, pad=0)
        Detail(col, label)
        card = CardCol(col, flex_height=1, pad=0)
        grid = PowerGrid(card, name=grid_name)
        grid.set_data(self.cols_to_rows(cols), columns=["#", "Name", "Type", "Key"])
        if clickable:
            grid.on_row_click(self.on_proposed_row_clicked, "#")
            if self.private_sel_row is not None:
                grid.selected_row = self.private_sel_row
                grid.rebuild()

    def read_columns(self, tbl):
        """A table/view's columns DB-direct via PRAGMA; GD/TS are flagged locked."""
        info = BbDB.query(f"PRAGMA table_info({tbl})")                  # (cid, name, type, notnull, dflt, pk)
        return [{"name": r[1], "type": r[2], "pk": bool(r[5]),
                 "locked": r[1] in ("GD", "TS")} for r in info]

    def cols_to_rows(self, cols):
        """Column dicts → grid rows (🔒 = locked, ✓ = pk), with a placeholder row if empty."""
        rows = [[i + 1, c["name"], c["type"], "🔒" if c["locked"] else ("✓" if c["pk"] else "")]
                for i, c in enumerate(cols)]
        return rows or [["—", "", "", ""]]

    def handle_edit(self):
        """Enter edit mode on the current table."""
        self.enter_editor("edit")

    def handle_clone(self):
        """Enter clone mode on the current table."""
        self.enter_editor("clone")

    def enter_editor(self, mode):
        """Seed Proposed as a copy of Original, seed identity state (layer/suffix/facet),
           enforce layer-required keys, and repaint both Pane 2 and Pane 3."""
        self.private_mode     = mode
        self.private_proposed = self.read_columns(self.current_table)
        self.private_sel_row  = None
        self.private_facet    = "Identity"
        self.private_layer    = BbDB.layer_of(self.current_table)
        self.private_suffix   = ""
        self.enforce_layer_keys()
        self.set_pane(2, self.the_object)
        self.set_pane(3, self.the_inspector)

    def handle_cancel(self):
        """Drop back to browse mode and repaint Pane 2 and Pane 3."""
        self.private_mode = "browse"
        self.set_pane(2, self.the_object)
        self.set_pane(3, self.the_inspector)

    def handle_delete(self):
        """Confirm before deleting the current table, its schema entry, and all associated views."""
        if not self.current_table: return
        MgrMsgBox.show(self.form,
                       f"Delete {self.current_table} and all its ETL views?",
                       MSG_BTNS_YES_NO | MSG_ICON_WARNING,
                       "Confirm Delete",
                       self.confirm_delete)

    def confirm_delete(self, result):
        """If confirmed, delete table + views + schema, reset all state, refresh UI."""
        if result != MSG_RESULT_YES: return
        MgrSchema.delete_table_entrypoint(self.current_table)
        self.current_table        = None
        self.private_show_tracks  = False
        self.private_mode         = "browse"
        pipe = self.form.tab_strip.resolve_tab("Pipe")
        if pipe: pipe.private_stale = True
        self.set_pane(0, self.database_browser)
        self.set_pane(2, self.the_object)
        self.set_pane(3, self.the_inspector)

    def on_proposed_row_clicked(self, row_num):
        """Remember the clicked Proposed row, switch the Inspector to the matching facet (Keys vs Metrics)."""
        self.private_sel_row = int(row_num) - 1
        col = self.sel_col()
        if col is not None: self.private_facet = "Keys" if col["pk"] else "Metrics"
        self.set_pane(3, self.the_inspector)

    def noop(self):
        """Inert modal callback placeholder."""
        pass

    def on_db_object_clicked(self, name):
        """Single-click loads the object into Pane 2, but only while browsing (not mid edit/clone)."""
        if self.private_mode != "browse": return
        self.load_table(name)

    def on_db_field_dbl_clicked(self, field):
        """Browsing: copy the field name to the clipboard. Editing/cloning: add it to Proposed instead."""
        if self.private_mode == "browse": MgrClipboard.copy(field); return
        self.add_field_to_proposed(field)

    def add_field_to_proposed(self, field):
        """Add a drilled-into field to Proposed: keys insert above the metrics, metrics append at the end."""
        if any(c["name"] == field for c in self.private_proposed): return
        col = {c["name"]: c for c in self.read_columns(self.private_db_selected)}.get(field)
        if col is None: return
        is_key = col["pk"] or field in self.all_key_tokens()
        new    = {"name": field, "type": col["type"], "pk": is_key, "locked": field in self.locked_keys()}
        if is_key: self.private_proposed.insert(self.first_metric_index(), new)
        else:      self.private_proposed.append(new)
        self.refresh_editor()

    # ════════════════════════════════════════════════════════════════════════════════
    # PANE 3 — The Inspector  (facet editor for the Proposed column under edit/clone)
    # ════════════════════════════════════════════════════════════════════════════════
    def the_inspector(self, parent):
        """Pane-3 root: tracks view, browse hint, or full facet editor."""
        if self.private_show_tracks:            self.build_track_inspector(parent); return
        if self.private_mode == "browse":
            BannerPlate(parent, "Inspector", text_align=CENTER)
            Body(parent, "Edit or Clone a table, then pick a field."); return
        self.build_inspector_banner(parent)
        self.build_facet_editor(parent)
        self.build_constant_controls(parent)
        self.build_action_bar(parent)

    def build_inspector_banner(self, parent):
        """Three plain facet buttons (Identity/Keys/Metrics), the active one painted as the CTA color."""
        data = [(f, (lambda x=f: self.set_facet(x)), self.facet_color(f)) for f in ("Identity", "Keys", "Metrics")]
        BannerPlate(parent, "Inspector", data=data)

    def facet_color(self, facet):
        """CTA color for the active facet, tab-bg color for the others."""
        return Style.COLOR_BUTTON_CTA if facet == self.private_facet else Style.COLOR_TAB_BG

    def set_facet(self, facet):
        """Switch the active facet and repaint the Inspector."""
        self.private_facet = facet
        self.set_pane(3, self.the_inspector)

    # ── Plate A — facet editor (Identity / Keys / Metrics, swaps by self.private_facet) ──
    def build_facet_editor(self, parent):
        """Dispatch Plate A to the editor matching the active facet."""
        plate = Plate(parent, pad=5, flex_height=1)
        if   self.private_facet == "Identity": self.build_identity_facet(plate)
        elif self.private_facet == "Keys":     self.build_keys_facet(plate)
        else:                                   self.build_metrics_facet(plate)

    def build_identity_facet(self, parent):
        """Identity facet: read-only display in edit mode, editable layer/suffix picker in clone mode."""
        if self.private_mode == "edit": self.build_identity_edit(parent)
        else:                           self.build_identity_clone(parent)

    def build_identity_edit(self, parent):
        """Edit mode's Identity facet: layer and name shown, both locked (can't rename/relayer a live table)."""
        Detail(parent, "Layer (locked in Edit)")
        Body  (parent, BbDB.layer_of(self.current_table))
        Detail(parent, "Name (locked in Edit)")
        Body  (parent, self.current_table)

    def build_identity_clone(self, parent):
        """Clone mode's Identity facet: layer picker + suffix box, pre-selected/pre-filled from
           the remembered pick so re-opening the facet doesn't lose state."""
        Detail(parent, "Layer")
        sl = SelectionList(parent, data={l: {} for l in BbDB.all_layers()},
                           single_select=True, flex_height=.4, pad=0, on_change=self.on_layer_selected)
        for item in sl.items:
            if item.text == self.private_layer:
                item.is_selected = True
                item.apply_selection_visual()
        Detail(parent, "Suffix")
        TextBox(parent, self.private_suffix, name="txt_db_suffix", on_change=self.on_suffix_changed)

    def on_layer_selected(self, picks):
        """Store the picked layer, re-enforce its required keys, refresh the banner's name preview."""
        self.private_layer = picks[0] if picks else self.private_layer
        self.enforce_layer_keys()
        self.set_widget_text("bnr_object", self.object_banner_text())
        self.refresh_validity()

    def on_suffix_changed(self, *a):
        """Store the suffix text, refresh the banner's name preview."""
        w = self.form.widgets.get("txt_db_suffix")
        self.private_suffix = w.text.strip() if w else ""
        self.set_widget_text("bnr_object", self.object_banner_text())
        self.refresh_validity()

    def build_keys_facet(self, parent):
        """Keys facet: locked keys listed as text; the rest as a SelectionList, pre-checked
           (selection visual applied) from whichever of them are already in Proposed."""
        locked  = self.locked_keys()
        Detail(parent, "Locked keys: " + (", ".join(locked) if locked else "none"))
        options = [t for t in self.all_key_tokens() if t not in locked]
        sl      = SelectionList(parent, data={t: {} for t in options}, flex_height=1, pad=0, on_change=self.on_keys_changed)
        current = {c["name"] for c in self.private_proposed if c["pk"]}
        for item in sl.items:
            item.is_selected = item.text in current
            item.apply_selection_visual()

    def on_keys_changed(self, selected):
        """Toggling the Keys SelectionList only touches the tokens it governs — every Proposed
           column outside that option set (locked keys, metrics, anything like p_throws) survives untouched."""
        options  = set(self.all_key_tokens()) - set(self.locked_keys())     # only these are toggleable here
        selected = set(selected)
        kept     = [c for c in self.private_proposed if c["name"] not in options or c["name"] in selected]
        present  = {c["name"] for c in kept}
        for tok in selected:
            if tok not in present:
                kept.insert(self.first_metric_index_of(kept), self.key_col(tok, self.locked_keys()))
        self.private_proposed = kept
        self.sort_proposed()
        self.set_pane(2, self.the_object)

    def sort_proposed(self):
        """Sort Proposed columns by registry seq. GD is hardcoded to 0."""
        for c in self.private_proposed:
            if c["name"] == "GD":       c["seq"] = 0
            elif "seq" not in c:        c["seq"] = MgrSchema.seq_for("Key", c["name"])
        self.private_proposed.sort(key=lambda c: c["seq"])


    def build_metrics_facet(self, parent):
        """Metric assembler: 4 pick lists + live preview + Add button."""
        lists = Row(parent, flex_height=1)
        self.build_metric_list(lists, "Entity",    "Entity",  True)
        self.build_metric_list(lists, "Metric",    "Metric",  True)
        self.build_metric_list(lists, "TimeSlice", None,       True)
        self.build_metric_list(lists, "Context",   "Context",  False)
        Detail(parent, self.assembled_metric_name(), name="detail_metric_preview")
        Button(parent, "Add to Proposed", on_click=self.add_assembled_metric,
               flex_width=1, color_bg=Style.COLOR_BUTTON_CTA)
    # DB.py method: build_metric_list  New: one labeled SelectionList column
    def build_metric_list(self, parent, label, kind, single):
        """Build a labeled SelectionList for one grammar component, restoring prior picks."""
        col = CardCol(parent, flex_width=1, pad=0)
        Detail(col, label)
        if kind:
            tokens = [r[0] for r in BbDB.query(
                "SELECT token FROM _registry WHERE kind=? ORDER BY token", (kind,))]
        else:
            from ipui._forms.Baseball.Pipe import Pipe
            tokens = [str(ts) for ts in Pipe.TIME_SLICES]
        sl = SelectionList(col, data={t: {} for t in tokens},
                           single_select=single, flex_height=1, pad=0,
                           on_change=lambda picks, lbl=label: self.on_metric_changed(lbl, picks))
        current = self.private_metric_picks.get(label, [])
        for item in sl.items:
            if item.text in current:
                item.is_selected = True
                item.apply_selection_visual()

    # ── Plate B — constant controls (act on the selected Proposed row) ───────────────
    def build_constant_controls(self, parent):
        """Move Up/Down, Remove, conditionally Mark as Target (forest only), plus the validity readout."""
        plate = Plate(parent, pad=5)
        row   = Row(plate)
        Button(row, "Move Up",   flex_width=1, on_click=self.move_up)
        Button(row, "Move Down", flex_width=1, on_click=self.move_down)
        Button(row, "Remove",    flex_width=1, color_bg=Style.COLOR_BUTTON_DANGER, on_click=self.remove_sel)
        if self.active_layer() == "forest":
            Button(plate, "Mark as Target", flex_width=1, on_click=self.mark_target)
        Detail(plate, self.validity_text(), name="detail_validity")

    def refresh_validity(self):
        """Update the validity readout and commit button to match current name/key state."""
        self.set_widget_text("detail_validity", self.validity_text())
        self.private_commit_btn.enabled = self.is_valid()

    def move_up(self):
        """Nudge the selected row one slot earlier."""
        self.move(-1)

    def move_down(self):
        """Nudge the selected row one slot later."""
        self.move(1)

    def move(self, d):
        """Swap the selected Proposed row with its neighbor d slots away, if that slot exists."""
        i, p = self.private_sel_row, self.private_proposed
        if i is None: return
        j = i + d
        if not (0 <= j < len(p)): return
        p[i], p[j] = p[j], p[i]
        self.private_sel_row = j
        self.refresh_editor()

    def remove_sel(self):
        """Drop the selected column from Proposed; locked columns are protected from removal."""
        c = self.sel_col()
        if c is None or c["locked"]: return
        self.private_proposed.pop(self.private_sel_row)
        self.private_sel_row = None
        self.refresh_editor()

    def mark_target(self):
        """Mark the selected column as the forest's single t_ target, stripping the prefix from any prior one."""
        c = self.sel_col()
        if c is None: return
        for col in self.private_proposed:
            if col["name"].startswith("t_"): col["name"] = col["name"][2:]
        c["name"] = "t_" + c["name"]
        self.refresh_editor()

    # ── Plate C — action bar (constant; Cancel + commit, greyed until valid) ─────────
    def build_action_bar(self, parent):
        """Cancel + the mode-appropriate commit button (Drop & Rebuild / Build New), disabled until valid."""
        plate = Plate(parent, pad=5)
        Button(plate, "Cancel", flex_width=1, on_click=self.handle_cancel)
        verb = "Drop & Rebuild" if self.private_mode == "edit" else "Build New"
        #btn  = Button(plate, verb, flex_width=1, color_bg=Style.COLOR_BUTTON_CTA, on_click=self.handle_commit)
        self.private_commit_btn = Button(plate, verb, flex_width=1, color_bg=Style.COLOR_BUTTON_CTA,on_click=self.handle_commit)
        self.private_commit_btn .enabled = self.is_valid()

    def handle_commit(self):
        """Route to commit_edit or commit_clone by mode (validity is already gated by the button)."""
        if not self.is_valid(): return
        if self.private_mode == "edit": self.commit_edit()
        else:                           self.commit_clone()

    def commit_clone(self):
        """Build a brand-new table from Proposed via MgrSchema, then switch Pane 2 onto it."""
        name = self.clone_full_name()
        if not name: return
        MgrSchema.create_table(name, self.bare_cols())
        MgrSchema.clone_etl_views_ENTRYPOINT(self.current_table, name)
        self.form.tab_strip.resolve_tab("Pipe").private_stale = True
        self.current_table = name
        self.form.show_modal(f"Built {name}", 1.5, self.after_commit)


    def commit_edit(self):
        """Rewrite the current table's schema and drop/rebuild it in place via MgrSchema."""
        MgrSchema.update_tbl_schema(self.current_table, self.bare_cols())
        MgrSchema.drop_and_rebuild_table(self.current_table)
        self.form.tab_strip.resolve_tab("Pipe").private_stale = True
        self.form.show_modal("Table rebuilt", 1.5, self.after_commit)

    def clone_full_name(self):
        """layer_suffix, must be non-empty on both parts and must not already exist in the schema."""
        if not self.private_layer or not self.private_suffix:
            BbDB.log("clone", "Need a layer and a suffix"); return None
        full = f"{self.private_layer}_{self.private_suffix}"
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl
        if full in {t for t, _ in _SchemaTbl.SCHEMA}:
            BbDB.log("clone", f"{full} already exists"); return None
        return full

    def bare_cols(self):
        """Proposed reduced to the commit shape (name/type/pk), minus GD/TS — MgrSchema re-injects those."""
        return [{"name": c["name"], "type": c["type"], "pk": c["pk"]}
                for c in self.private_proposed if c["name"] not in ("GD", "TS")]

    def after_commit(self):
        """Back to browse mode; repaint Pane 0, Pane 2, and Pane 3."""
        self.private_mode = "browse"
        self.set_pane(0, self.database_browser)
        self.set_pane(2, self.the_object)
        self.set_pane(3, self.the_inspector)

    # ════════════════════════════════════════════════════════════════════════════════
    # Shared helpers
    # ════════════════════════════════════════════════════════════════════════════════
    def refresh_editor(self):
        """Repaint the Proposed grid (Pane 2) and the Inspector (Pane 3)."""
        self.set_pane(2, self.the_object)
        self.set_pane(3, self.the_inspector)

    def sel_col(self):
        """The selected Proposed column dict, or None if there's no valid selection."""
        i = self.private_sel_row
        if i is None or not (0 <= i < len(self.private_proposed)): return None
        return self.private_proposed[i]

    def active_layer(self):
        """The layer governing the current edit: the picked layer in clone mode, the table's own layer in edit mode."""
        if self.private_mode == "clone": return self.private_layer
        return BbDB.layer_of(self.current_table)

    def locked_keys(self):
        """Keys that can't be toggled off: GD always, game_pk on forest, TS if already present."""
        locked = ["GD"]
        if self.active_layer() == "forest": locked.append("game_pk")
        if any(c["name"] == "TS" for c in self.private_proposed): locked.append("TS")
        return locked

    def enforce_layer_keys(self):
        """Forest tables must carry game_pk — add it to Proposed if it's missing."""
        if self.active_layer() == "forest" and not any(c["name"] == "game_pk" for c in self.private_proposed):
            self.private_proposed.append(self.key_col("game_pk", self.locked_keys()))

    def all_key_tokens(self):
        """Every registered Key-kind token, read DB-direct from _registry."""
        return [r[0] for r in BbDB.query("SELECT token FROM _registry WHERE kind='Key' ORDER BY token")]

    def key_col(self, name, locked):
        """Build a key column dict for a token, with dtype and seq pulled from the registry."""
        return {"name": name, "type": self.dtype_for("Key", name), "pk": True,
                "locked": name in locked, "seq": MgrSchema.seq_for("Key", name)}

    def proposed_name(self):
        """The in-progress table name: layer_suffix while cloning, the current table's name while editing."""
        if self.private_mode == "clone":
            return f"{self.private_layer}_{self.private_suffix}" if (self.private_layer and self.private_suffix) else ""
        return self.current_table

    def n_keys(self):
        """Count of Proposed columns flagged as primary key."""
        return sum(1 for c in self.private_proposed if c["pk"])

    def n_metrics(self):
        """Count of Proposed columns not flagged as primary key."""
        return sum(1 for c in self.private_proposed if not c["pk"])

    def is_valid(self):
        """A commit is valid once there's a name and at least one key."""
        return bool(self.proposed_name()) and self.n_keys() > 0

    def validity_text(self):
        """The greyed-commit explainer: what's missing, or a ✓ summary once valid."""
        if not self.proposed_name(): return "✗ needs a name"
        if self.n_keys() == 0:       return "✗ no keys yet"
        return f"✓ {self.proposed_name()} · {self.n_keys()} keys · {self.n_metrics()} metrics"

    def first_metric_index_of(self, cols):
        """Index where keys end in a given column list (first non-key, or the list's length)."""
        return next((i for i, c in enumerate(cols) if not c["pk"]), len(cols))

    def first_metric_index(self):
        """Index where keys end in Proposed — delegates to the list-taking version."""
        return self.first_metric_index_of(self.private_proposed)


    # DB.py method: on_metric_changed  New: unified handler for all 4 lists
    def on_metric_changed(self, label, picks):
        """Store picks for this grammar component and refresh the preview."""
        self.private_metric_picks[label] = picks
        self.refresh_metric_preview()

    # DB.py method: refresh_metric_preview  New: poke the preview text
    def refresh_metric_preview(self):
        """Update the assembled name preview without rebuilding the pane."""
        self.set_widget_text("detail_metric_preview", self.assembled_metric_name())

    # DB.py method: assembled_metric_name  New: build name from current picks
    def assembled_metric_nameOLD_RULES__(self):
        """Entity_Metric[_TimeSlice][_Context...] from current selections."""
        p       = self.private_metric_picks
        entity  = p["Entity"][0]    if p.get("Entity")    else None
        metric  = p["Metric"][0]    if p.get("Metric")    else None
        if not entity or not metric: return "(pick Entity + Metric)"
        parts   = [entity, metric]
        ts      = p["TimeSlice"][0] if p.get("TimeSlice") else None
        if ts: parts.append(ts)
        parts.extend(sorted(p.get("Context", [])))
        return "_".join(parts)

    def assembled_metric_name(self):
        """Assemble column name from whatever grammar components are selected."""
        p     = self.private_metric_picks
        parts = []
        if p.get("Entity"):    parts.append(p["Entity"][0])
        if p.get("Metric"):    parts.append(p["Metric"][0])
        if p.get("TimeSlice"): parts.append(p["TimeSlice"][0])
        parts.extend(sorted(p.get("Context", [])))
        return "_".join(parts) if parts else "(pick something)"

    def add_assembled_metric(self):
        """Add the assembled metric name to Proposed with its registry dtype and seq."""
        name = self.assembled_metric_name()
        if name.startswith("("): return
        if any(c["name"] == name for c in self.private_proposed): return
        metric_token = self.private_metric_picks["Metric"][0]
        dtype = self.dtype_for("Metric", metric_token)
        seq   = MgrSchema.seq_for("Metric", metric_token)
        self.private_proposed.append({"name": name, "type": dtype, "pk": False, "locked": False, "seq": seq})
        self.sort_proposed()
        self.refresh_editor()




    # ════════════════════════════════════════════════
    ################## HANDLE TRACKS
    # ════════════════════════════════════════════════
    def handle_tracks(self):
        """Show the track assignment panel in the Inspector."""
        self.private_show_tracks = True
        self.set_pane(3, self.the_inspector)

    def trim_view_name(self, name):
        """Trim long view names, keeping the right (significant) end."""
        if len(name) <= self.VIEW_NAME_TRIM: return name
        return "…" + name[-(self.VIEW_NAME_TRIM - 1):]

    # DB.py method: build_track_inspector  New: track assignment UI
    def build_track_inspector(self, parent):
        """Multi-select of tracks + new track input."""
        BannerPlate(parent, f"Tracks: {self.trim_view_name(self.current_table)}",
                    data=[("Done", self.handle_tracks_done)])
        all_tracks = self.all_tracks()
        current    = self.tracks_for_table(self.current_table)
        if all_tracks:
            sl = SelectionList(parent, data={t: {} for t in all_tracks},
                               flex_height=1, pad=0, on_change=self.on_tracks_changed)
            for item in sl.items:
                if item.text in current:
                    item.is_selected = True
                    item.apply_selection_visual()
        else:
            Body(parent, "No tracks yet — create one below.")
        row = Row(parent)
        TextBox(row, name="txt_new_track", placeholder="New track name:", flex_width=1)
        Button(row, "Add", on_click=self.add_new_track, color_bg=Style.COLOR_BUTTON_CTA)

    # DB.py method: handle_tracks_done  New: close track assignment
    def handle_tracks_done(self):
        """Return to browse mode from track assignment."""
        self.private_show_tracks = False
        self.set_pane(3, self.the_inspector)

    def on_tracks_changed(self, selected):
        """Full replace: delete all assignments for this table, re-insert selected."""
        MgrSchema.tracks_replace_table(self.current_table, selected)

    def add_new_track(self):
        """Create a new track from the textbox and assign the current table to it."""
        w    = self.form.widgets.get("txt_new_track")
        name = w.text.strip() if w else ""
        if not name: return
        MgrSchema.track_add_table(name, self.current_table)
        self.set_pane(3, self.the_inspector)

    # DB.py method: all_tracks  New: distinct track names
    def all_tracks(self):
        """Every known track name."""
        return [r[0] for r in BbDB.query("SELECT DISTINCT track FROM _track_tables ORDER BY track")]

    # DB.py method: tracks_for_table  New: which tracks a table belongs to
    def tracks_for_table(self, tbl):
        """Set of track names this table is assigned to."""
        return {r[0] for r in BbDB.query("SELECT track FROM _track_tables WHERE tbl=?", (tbl,))}

