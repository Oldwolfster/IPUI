# Pipe.py  class: Pipe  ADD near TIME_SLICES
class deleteme:

    FOREST_TABLES_TO_TRAIN = ["forest"]


    # Pipe.py  method: top_left_section  UPDATE: delete forest TextBox after Train XGB
    def top_left_section(self, frame):
        Button(header, "Train XGB", on_click=self.train_xgb_clicked)          # REFERENCE
        TextBox(header, initial_value="forest", name="txt_forest_table")      # DELETE


    # Pipe.py  method: train_xgb_clicked  UPDATE: train selected forest tables sequentially
    def train_xgb_clicked(self):
        print("Training XGB")
        selected = self.valid_forest_tables_to_train()
        if not selected: return
        for table in selected:
            self.train_xgb(table)


    # Pipe.py  method: valid_forest_tables_to_train  NEW: validate selected forest list
    def valid_forest_tables_to_train(self):
        available = BbDB.tables_for_layer("forest")
        missing   = [t for t in Pipe.FOREST_TABLES_TO_TRAIN if t not in available]
        if missing:
            self.form.msgbox(
                f"Invalid forest table(s): {', '.join(missing)}\n\n"
                f"Available: {', '.join(available)}",
                MSG_BTNS_OK + MSG_ICON_WARNING,
                "Invalid Forest Table",
            )
            return []
        if not Pipe.FOREST_TABLES_TO_TRAIN:
            self.form.msgbox(
                "No forest tables selected.\n\nClick a FOREST card to toggle training.",
                MSG_BTNS_OK + MSG_ICON_WARNING,
                "No Forest Tables",
            )
            return []
        return list(Pipe.FOREST_TABLES_TO_TRAIN)


    # Pipe.py  method: select_forest_table  UPDATE: toggle forest table in training list
    def select_forest_table(self, tbl):
        print(f"select_forest_table  tbl={tbl}")
        if tbl in Pipe.FOREST_TABLES_TO_TRAIN: Pipe.FOREST_TABLES_TO_TRAIN.remove(tbl)
        else:                                  Pipe.FOREST_TABLES_TO_TRAIN.append(tbl)
        self.refresh_pane()


    # Pipe.py  method: build_one_card  UPDATE: selected forest cards get green background
    def build_one_card(self, parent, tbl):
        summary  = BbDB.get_summary(tbl)
        selected = BbDB.layer_of(tbl) == "forest" and tbl in Pipe.FOREST_TABLES_TO_TRAIN
        card     = Card(parent, pad=5, color_bg=Style.COLOR_BUTTON_CTA) if selected else Card(parent, pad=5)
        if BbDB.layer_of(tbl) == "forest": card.on_click_me(lambda t=tbl: self.select_forest_table(t))
        self.build_card_header(card, tbl, summary)
        refs     = self.build_card_body(card, tbl, summary)
        self.build_card_buttons(card, tbl, refs)