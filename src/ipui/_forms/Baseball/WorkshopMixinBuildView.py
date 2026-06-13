# ════════════════════════════════════════════════════════════════
# WorkshopMixinBuildView.py  COMPLETE NEW FILE
# ════════════════════════════════════════════════════════════════
from ipui import *
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrSchema import MgrSchema


class WorkshopMixinBuildView:
    VIEW_TYPES = ["For Insert", "Update After"]

    # ── navigation ──────────────────────────────────────────────

    def start_build_view(self):
        print("I AM RUNNING")
        self.private_building_view  = True
        self.private_build_type     = WorkshopMixinBuildView.VIEW_TYPES[0]
        self.private_build_suffix   = ""
        self.private_build_targets  = []
        self.private_build_title    = None
        self.set_pane(1, self.source)

    def cancel_build_view(self):
        self.private_building_view  = False
        self.set_pane(1, self.source)

    # ── main layout ─────────────────────────────────────────────

    def build_view_builder(self, parent):
        self.private_build_title = self.banner_plate(
            f"CREATE VIEW: {self.generate_view_name()}", parent,
            buttons=[
                ("Create", self.create_new_view, Style.COLOR_BUTTON_CTA),
                ("Ask Claude", lambda: self.form.show_modal("Coming Soon"), Style.COLOR_BUTTON_CTA),
                ("Cancel", self.cancel_build_view),
            ])
        self.build_view_naming(parent)
        row = Row(parent,flex_height=1)
        self.build_view_prose(row)
        self.build_view_targets(row)

    # ── naming + prose row ──────────────────────────────────────

    def build_view_naming(self, parent):
        card = Card(parent, pad=2)
        row  = Row(card)
        TextBox(row, name="txt_build_suffix", flex_width=1,
                initial_value = self.private_build_suffix,
                placeholder   = "Name",
                on_change     = self.update_name)
        Spacer(row, flex_width=.1)
        for t in self.VIEW_TYPES:
            active = (t == self.private_build_type)
            color  = Style.COLOR_BUTTON_ACCENT if active else Style.COLOR_TAB_BG
            Button(row, t, color_bg=color, on_click=lambda c=t: self.set_build_type(c))
        #Spacer(row, flex_width=.1)
        #TextArea(row, "", name="txt_build_prose", flex_height=1,                 placeholder="Describe what this view should accomplish:")

    # ── name generation ─────────────────────────────────────────

    def generate_view_name(self):
        tbl    = self.current_table or ""
        suffix = self.private_build_suffix or ""
        if self.private_build_type == "For Insert":
            return f"pull_{tbl}_mixin_{suffix}" if suffix else f"pull_{tbl}_mixin_"
        return f"update_{tbl}_{suffix}" if suffix else f"update_{tbl}_"

    def update_name(self,new_letter):

        txt = self.form.widgets.get("txt_build_suffix")
        if txt: self.private_build_suffix = txt.text.strip()
        if self.private_build_title:
            self.private_build_title.text = f"CREATE VIEW: {self.generate_view_name()}"

    def set_build_type(self, chosen):
        self.update_name('doh')
        self.private_build_type = chosen
        self.set_pane(1, self.source)

    def build_view_prose(self,parent):
        prose=CardCol(parent,flex_width=1)
        Body(prose, "What this view accomplishes:")
        TextArea(prose, "", name="txt_build_prose", flex_height=969.9)


    # ── target columns ──────────────────────────────────────────

    def build_view_targets(self, parent):
        targ = CardCol(parent, flex_width=1)
        Body(targ, "Select target columns this view should produce:")
        cols = self.private_staged_columns
        if not cols:
            Body(parent, "— no columns —")
            return
        SelectionList(targ,
            data      = {c['name']: {} for c in cols},
            flex_height = 1,
                      pad=0,
            on_change = self.on_targets_changed,
        )

    def on_targets_changed(self, picks):
        self.private_build_targets = picks if picks else []

    # ── create ──────────────────────────────────────────────────

    def create_new_view(self):
        if not self.private_build_suffix:
            self.form.show_modal("C'mon bro... name your view!")
            return
        if not self.private_build_targets:
            self.form.show_modal("Pick at least one target column!")
            return
        view_name = self.generate_view_name()
        stub_sql  = self.generate_sentinel_sql()
        error     = MgrSchema.test_sql(view_name, stub_sql)
        if error:
            BbDB.log(view_name, error)
            return
        MgrSchema . save_view(view_name, stub_sql)
        self.private_building_view  = False
        self.private_editor_sql     = stub_sql
        self.private_selected_view  = view_name
        self.private_editing_mixin  = True
        self.set_pane(1, self.source)
        self.set_pane(2, self.columns)

    def generate_sentinel_sql(self):
        cols = ",\n       ".join(f"369 AS {c}" for c in self.private_build_targets)
        return f"SELECT {cols}"

    # ── dispatcher (lives here, called from Workshop.source) ────

    def build_mixin_area(self, parent):
        if   self.private_building_view:     self.build_view_builder(parent)
        elif self.private_editing_mixin:     self.build_mixin_editor(parent)
        elif self.private_selected_view:     self.build_mixin_detail(parent)
        else:                                self.build_mixin_list(parent)
