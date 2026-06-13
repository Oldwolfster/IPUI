from ipui import *
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrSchema import MgrSchema


class WorkshopMixinBuildTable:

    def clone_table_on_click(self):
        self.set_pane(2, self.clone_ui)

    def clone_ui(self, par):

        self.banner_plate("Clone Table",par,[( "Cancel", self.cancel_clone)])
        parent = Card(par, pad=Style.TOKEN_PAD/2, flex_height=1,border=0)
        Spacer(parent, flex_height=.0369)

        card = Card(parent, pad_x=Style.TOKEN_PAD, flex_height=.3)
        Body(card, "New Table Name (prefix added automatically):")
        TextBox(card, name="txt_clone_name")
        Spacer(parent, flex_height=.0669)
        Body(parent, "Select layer :")
        layers = BbDB.all_layers()
        default_layer = BbDB.layer_of(self.current_table) if self.current_table else None
        self.private_clone_layer = default_layer
        SelectionList(parent,
            data          = {l: {} for l in layers},
            single_select = True,
            on_change     = self.on_clone_layer_selected,
            flex_height   =.669,

        )

        Spacer(parent, flex_height=.0699)
        Button(Plate(parent, pad=20, border=5), "Confirm Clone", color_bg=Style.COLOR_BUTTON_CTA, flex_width=1, on_click=self.confirm_clone)
        #Spacer(parent, flex_height=.0369)


    # Workbench.py  method: on_clone_layer_selected  NEW: store layer pick
    def on_clone_layer_selected(self, picks):
        self.private_clone_layer = picks[0] if picks else None


    # Workbench.py  method: cancel_clone  NEW: return to controls pane
    def cancel_clone(self):
        self.refresh_all_panes()

    # Workbench.py  method: validate_clone_inputs  NEW: clean + check name
    def validate_clone_inputs(self):
        layer = self.private_clone_layer
        if not layer:
            BbDB.log("clone", "No layer selected"); return None
        name_w = self.form.widgets.get("txt_clone_name")
        if not name_w or not name_w.text.strip():
            BbDB.log("clone", "Enter a table name"); return None
        raw       = name_w.text.strip().lower()
        prefix    = f"{layer}_"
        if raw.startswith(prefix): raw = raw[len(prefix):]
        full_name = f"{layer}_{raw}"
        from ipui._forms.Baseball._SchemaTbl import _SchemaTbl
        if full_name in {t for t, _ in _SchemaTbl.SCHEMA}:
            BbDB.log("clone", f"{full_name} already exists"); return None
        return full_name


    def confirm_clone(self):
        full_name = self.validate_clone_inputs()
        if not full_name: return
        columns = self.parse_schema_for_table(self.current_table)
        MgrSchema.create_table(full_name, columns)
        self.load_table(full_name)
        self.refresh_all_panes()