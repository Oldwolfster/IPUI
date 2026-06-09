from ipui import *
from ipui._forms.Baseball.BbDB import BbDB


class WorkshopMixinBuildView:
    VIEW_TYPES = ["For Insert", "Update After"]

    # ── navigation ──────────────────────────────────────────────
    def start_build_view(self):
        self.private_building_view = True
        self.private_build_type    = WorkshopMixinBuildView.VIEW_TYPES[0]
        self.private_build_source  = None
        self.set_pane(1, self.source)
        self.view_name        = " "
        self.view_name_suffix = " "

    def cancel_build_view(self):
        self.private_building_view = False
        self.private_build_source  = None
        self.set_pane(1, self.source)

    # ── main builder layout ─────────────────────────────────────
    def build_view_builder(self, parent):
        """Build New View"""
        self.build_banner_plate(parent)
        self.build_view_naming(parent)
        row = Row(parent, flex_height=1)
        self.build_view_targets(CardCol(row, flex_width=1, flex_height=1, pad=2))
        self.build_view_sources(CardCol(row, flex_width=1, flex_height=1, pad=2))
        #self.build_view_prose(parent)
        self.build_view_actions(parent)

    def build_banner_plate(self, parent):
            self.banner_plate(f"CREATE VIEW: pull_...k", parent, buttons=[
                # We build full update_ or pull_ primary_view_suffix per keystroke in update_name
                ("Ask Claude", lambda: self.form.show_modal("Coming Soon"), Style.COLOR_BUTTON_CTA),
                #("Ask ChatGPT", lambda: self.form.show_modal("Coming Soon"), Style.COLOR_BUTTON_CTA),
                #("DO NOT ASK GROK", lambda: self.form.show_modal("DO NOT TRUST"), Style.COLOR_BUTTON_DANGER),
                ("Cancel", self.cancel_build_view), ]
                )
    # ── naming row ──────────────────────────────────────────────
    def build_view_naming(self, parent):
        card = Card(parent, pad=2)  #flex_height =1 makes it very tall... but text area expand.. think constrained by the row
        row  = Row(card)
        TextBox(row, name="txt_build_suffix", flex_width=33333.369, placeholder="Name", on_change=self.update_name) #In tree, it shows flex width at 1, so maybe the 33k is getting stomped?
        Spacer(row,flex_width=.1)

        for t in self.VIEW_TYPES:
            active = (t == self.private_build_type)
            color  = Style.COLOR_BUTTON_ACCENT if active else Style.COLOR_TAB_BG
            Button(row, t, color_bg=color, on_click=lambda c=t: self.set_build_type(c))
        Spacer(row,flex_width=.1)
        self.build_view_prose(row)

        #Spacer(row, flex_width=.1)
        #Button(row,"yo")

    # ── prose description ───────────────────────────────────────
    def build_view_prose(self, parent):
        ph_text= "Describe what this view should accomplish:"
        TextArea(parent, "", name="txt_build_prose", flex_height=969.9,placeholder=ph_text)

    def update_name(self):
        """Update the bannerPane's create view name as they type or click."""
        pass

    def set_build_type(self, chosen):
        self.private_build_type = chosen
        self.set_pane(1, self.source)

    # ── target columns (the shopping list) ──────────────────────
    def build_view_targets(self, parent):

        Body(parent, "Target Columns - from primary view")
        cols = self.private_staged_columns
        if not cols:
            Body(parent, "— no columns —")
            return
        SelectionList(parent,
            data        = {c['name']: {} for c in cols},
            flex_height = 1,
        )

    # ── source picker ───────────────────────────────────────────
    def build_view_sources(self, parent):
        #Title(parent, "Available Sources")
        TextBox(parent, name="txt_build_filter",placeholder="Filter")
        sources = self.fetch_build_sources()
        SelectionList(parent,
            data          = {s: {} for s in sources},
            single_select = True,
            flex_height   = 1,
            on_change     = self.on_build_source_selected,
        )

    def fetch_build_sources(self):
        rows = BbDB.query(
            "SELECT name FROM sqlite_master "
            "WHERE type IN ('table', 'view') "
            "AND name NOT LIKE '\\_%' ESCAPE '\\' "
            "ORDER BY name"
        )
        return [r[0] for r in rows]

    def on_build_source_selected(self, picks):
        if not picks: return
        self.private_build_source = picks[0]
        self.set_pane(2, self.build_source_detail)


    def build_source_detail(self, parent):
        self.banner_plate(f"Columns: {self.private_build_source}", parent,
                          buttons=[("Bac121211k", lambda: self.set_pane(2, self.columns))])
        cols = BbDB.query(f"PRAGMA table_info({self.private_build_source})")
        if not cols:
            Body(parent, "— no columns —")
            return
        SelectionList(parent,
            data        = {c[1]: {} for c in cols},
            flex_height = 1,
        )

    # ── action buttons ──────────────────────────────────────────
    def build_view_actions(self, parent):
        pass
        self.private_clone_layer        = None
        self.private_building_view      = False
        self.private_build_type         = WorkshopMixinBuildView.VIEW_TYPES[0]
        self.private_build_source       = None


    def build_mixin_area(self, parent):
        if   self.private_building_view:     self.build_view_builder(parent)   # NEW
        elif self.private_editing_mixin:     self.build_mixin_editor(parent)
        elif self.private_selected_view:     self.build_mixin_detail(parent)
        else:                                self.build_mixin_list(parent)

