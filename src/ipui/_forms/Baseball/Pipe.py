from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.PipeMixinRawPull import MixinRawPull
from ipui._forms.Baseball.PipeMixinXGBoost import MixinXGBoost
from ipui._forms.Baseball.MgrDT import MgrDT
from ipui import *
from ipui._forms.Baseball.PipeMixinUpdate import MixinUpdate


class Pipe(_BaseTab, MixinRawPull, MixinXGBoost, MixinUpdate):#, MixinXGBoost):
    TIME_SLICES = [7,15,28,30,200,9999]
    LAYERS = ["Raw", "ETL", "Feet", "Forest", "Predict"]
    PITCH_BUCKETS = {
        "FF": "fastball", "SI": "fastball", "FC": "fastball", "FA": "fastball",
        "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking", "SV": "breaking", "CS": "breaking",
        "CH": "offspeed", "FS": "offspeed", "SP": "offspeed", "FO": "offspeed",
    }
    start_date = "2026-03-27"
    end_date   = "2026-03-28"

    def ip_setup_early(self,ip):
        self.task_queue    = []
        self.private_stale = False
        self.card_mode     = "detail"           # detail | field  (toggled in the header)

    def ip_activated(self,ip):          # called by TabSystem when user switches here
        #print("Am i firing")
        if self.private_stale:
            self.private_stale = False
            self.refresh_pane()

    # ════════════════════════════════════════════════
    # Widget Tree                                  ═══
    # ════════════════════════════════════════════════
    def all_in_one(self, parent):
        BbDB.configure()
        self.top_section(parent)
        self.bottom_section(parent)

    def passme(self):        pass

    def top_section(self, parent):
        row      = Row(parent)
        frame    = CardCol(row, pad=2, flex_width=3.369)
        self     . top_left_section(frame)
        log      = CardCol(row,flex_width=1.669, pad=0)
        BbDB.pipe_log_display = Detail(Card(log,scroll_v=True,pad_y=0), BbDB.pipe_log_text or "Greetings earthling!")

    def top_left_section(self, frame):
        header   = Card(frame     , pad=3)
        header   = Plate(header   , pad=5)
        header   = Plate(header   , pad=5)
        header   = Row(header)
        Title(header, "Data Pipeline", glow=True)
        Spacer(header)
        self.btn_refresh_all  = Button(header, "Run all", color_bg=Style.COLOR_BUTTON_CTA,  on_click=self.update_all)
        TextBox(header, initial_value=Pipe.start_date, name="txt_start_date")
        Body(header, "to:")
        TextBox(header, initial_value=Pipe.end_date, name="txt_end_date")
        Spacer(header)
        Button(header, "Train XGB"  , on_click=self.train_xgb)
        Button(header, "Refresh"       , on_click=self.refresh_pane)
        Button(header, self.toggle_label(), on_click=self.toggle_card_mode)
        Button(header, "Run TS"     , on_click=lambda: self.roll_up_ts("feet_batter"))
        Button(header, "Phoenix"    , on_click=self.nuke_clicked, color_bg=Style.COLOR_BUTTON_DANGER)

    def refresh_pane(self): self.form.set_pane(0, self.all_in_one)

    def toggle_label(self):
        return "Fields" if self.card_mode == "detail" else "Details"

    def toggle_card_mode(self):
        self.card_mode = "field" if self.card_mode == "detail" else "detail"
        self.refresh_pane()

    # MixinXGBoost.py method: train_xgb  Update: BbDB + summary + refresh


    def train_xgb(self):
        BbDB.log(self.XGB_TABLE, "loading forest")
        rows = self.load_forest()
        if not rows:
            BbDB.log(self.XGB_TABLE, "forest is empty — run 'Run All' first")
            return
        BbDB.log(self.XGB_TABLE, f"training on {len(rows)} rows")
        model = self.fit_model(rows)
        BbDB.log(self.XGB_TABLE, "writing predictions")
        self.write_predictions(model, rows)
        BbDB.log(self.XGB_TABLE, "model_xgb_v1 ready")
        BbDB.update_summary(self.XGB_TABLE)
        self.refresh_pane()

    def nuke_clicked(self):
        self.form.msgbox(
            "Nuke etl + feet + forest layers?\n\n"
            "All derived tables and views will be DROPPED\n"
            "then recreated empty from schema.",
            MSG_BTNS_YES_NO + MSG_ICON_QUESTION + MSG_DEFAULT_2,
            "Nuke derived layers",
            on_result=self.do_nuke,
        )

    def do_nuke(self, result):
        if result != MSG_RESULT_YES: return
        print("nuke confirmed33")
        for layer in ["etl", "feet", "forest"]:
            for tbl in BbDB.tables_for_layer(layer):
                BbDB.drop_table(tbl)
        for v in BbDB.query("SELECT name FROM sqlite_master WHERE type='view'"):
            BbDB.execute(f"DROP VIEW IF EXISTS {v[0]}")
            BbDB.log(v[0], "dropped view")
        BbDB.configure()
        self.refresh_pane()

    # ════════════════════════════════════════════════
    # Widget Tree (bottom section - tbl cards)     ═══
    # ════════════════════════════════════════════════

    def bottom_section(self, parent):
        frame = CardRow(parent, flex_height=1, pad=2)
        for layer in Pipe.LAYERS:
            self.build_a_layer(frame, layer)

    def build_a_layer(self, parent, layer):
        col    = CardCol(parent, flex_width=1, flex_height=1, pad=2)
        header = Plate(col, pad=5)
        Title  ( header, layer.upper(), text_align='c')
        body   = Plate(col, scroll_v=True, flex_height=1, pad=3)
        self   . build_cards_for_layer(body, layer)

    def build_cards_for_layer(self, parent, layer):
        for tbl in BbDB.tables_for_layer(layer):
            self.build_one_card(parent, tbl)

    def build_one_card(self, parent, tbl):
        summary = BbDB.get_summary(tbl)
        card    = Card(parent, pad=5)
        self.build_card_header(card, tbl, summary)
        refs    = self.build_card_body(card, tbl, summary)
        self.build_card_buttons(card, tbl, refs)

    def build_card_header(self, card, tbl, summary):
        head = Row(card)
        Title(head, tbl)
        Spacer(head)
        Body(head, f" {MgrDT.gd_to_iso(summary.gd)}")

    def build_card_body(self, card, tbl, summary):
        if self.card_mode == "field":
            self.build_field_list(card, tbl)
            return None
        return self.build_detail_body(card, summary)

    def build_detail_body(self, card, summary):
        row        = Row(card)
        body_rows  = Body(row, f"Rows:  {summary.rows:,}")
        Spacer(row)
        body_range = Body(row, f"Cols: {summary.cols}")
        rng        = f"{MgrDT.gd_to_iso(summary.min_gd)}  to  {MgrDT.gd_to_iso(summary.max_gd)}" if summary.min_gd else "—  to  —"
        Body(card, f"Range: {rng} ")
        return body_rows, body_range

    def build_field_list(self, card, tbl):
        Body(card, "\n".join(BbDB.field_names(tbl)))

    def build_card_buttons(self, card, tbl, refs):
        body_rows, body_range = refs if refs else (None, None)
        btns = Row(Plate(Plate(card,pad=2),pad=6))
        Button(btns, "Run"      ,flex_width=1, on_click=lambda t=tbl, br=body_rows, bg=body_range: self.refresh_table(t, br, bg))
        Button(btns, "WB", flex_width=1, on_click=lambda t=tbl: self.view_in_workbench(t))  # NEW
        Button(btns, "SQL"      , flex_width=1, on_click=lambda t=tbl: self.view_in_sql(t))  # NEW

    def view_in_workbench(self, tbl):
        self.form.switch_tab("Workshop")                                    # construct if first visit
        wb = self.form.get_tab("Workshop")
        if wb is None:
            BbDB.log("View_InWorkshop", "Workbench tab not found after switch")
            return
        wb.load_table(tbl)

    def view_in_sql(self, tbl):
        dates  = self.get_start_and_end_dates()
        start_gd, end_gd = dates if dates else (None, None)
        self.form.switch_tab("SQL")                                          # construct if first visit
        sql_tab = self.form.get_tab("SQL")
        if sql_tab is None:
            BbDB.log("view_in_sql", "ERROR", "SQL tab not found after switch")
            return
        sql_tab.load_query_for_table(tbl, BbDB.DB_PATH, start_gd, end_gd)

    # ════════════════════════════════════════════════
    # Running Updates                              ═══
    # ════════════════════════════════════════════════

    def refresh_table(self, tbl, body_rows, body_range):
        dates = self.get_start_and_end_dates()
        if dates is None: return
        if body_rows: body_rows.text = "Rows:  refreshing..."     # field mode passes None — nothing to update
        self.ip.after_paint(self.refresh_table_now, tbl, dates, body_rows, body_range)

    def refresh_table_now(self, tbl, dates, body_rows, body_range):
        start_gd, end_gd = dates
        layer = BbDB.layer_of(tbl)
        if layer == "raw":
            method = getattr(self, f"sync_{tbl}", None)
            if method: method(start_gd, end_gd)
            else:      BbDB.log(tbl, "no sync method found")
            BbDB.update_summary(tbl)
        else:
            self.update_table(tbl, start_gd, end_gd)
        s = BbDB.get_summary(tbl)
        if not body_rows: return                                  # field mode: data refreshed, no labels to touch
        body_rows.text  = f"Rows: {s.rows:,}"
        rng = f"{MgrDT.gd_to_iso(s.min_gd)}  to  {MgrDT.gd_to_iso(s.max_gd)}" if s.min_gd else "—  to  —"
        body_range.text = f"Range: {rng}"

    def parse_textbox_date_to_gd(self, name):
        raw = self.form.widgets[name].text
        return MgrDT.str_to_gd(raw)

    def get_start_and_end_dates(self):
        try:
            start_gd = self.parse_textbox_date_to_gd("txt_start_date")
            end_gd = self.parse_textbox_date_to_gd("txt_end_date")
        except (ValueError, KeyError) as e:
            BbDB.log("dates", f"bad input: {e}")
            return None
        if start_gd > end_gd:
            BbDB.log("dates", f"start {start_gd} > end {end_gd}; aborting")
            return None
        Pipe.start_date = self.form.widgets["txt_start_date"].text
        Pipe.end_date = self.form.widgets["txt_end_date"].text
        return start_gd, end_gd



    # ════════════════════════════════════════════════
    # Widget Tree                                  ═══
    # ════════════════════════════════════════════════

    # ════════════════════════════════════════════════
    # Widget Tree                                  ═══
    # ════════════════════════════════════════════════