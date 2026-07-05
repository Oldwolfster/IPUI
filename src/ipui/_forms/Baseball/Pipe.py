import pygame

from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.DbResults import DbResults
from ipui._forms.Baseball.FieldLineage import FieldLineage
from ipui._forms.Baseball.PipeMixinRawPull import MixinRawPull
from ipui._forms.Baseball.PipeMixinXGBoost import MixinXGBoost
from ipui._forms.Baseball.MgrDT import MgrDT
from ipui import *
from ipui._forms.Baseball.PipeMixinUpdate import PipeMixinUpdate
from ipui.engine.DisplayArrow import DisplayArrow
from ipui.utils.EZ import EZ
from ipui._forms.Baseball.PipeMixinModelResults import MixinModelResults

class Pipe(_BaseTab, MixinRawPull, MixinXGBoost, PipeMixinUpdate,MixinModelResults):#, MixinXGBoost):
    TIME_SLICES = [27,15,28,30,200,9999]
    TIME_SLICES = [2, 3, 8, 200, 9999]
    GUYS_LINE   = 0.77
    ROLLUP_EXCLUDE = {"GD", "TS", "game", "game_pk", "pa", "at_bat_number"}
    FOREST_TABLES_TO_TRAIN = []
    LAYERS = ["Raw", "ETL", "Feet", "Forest", "Predict"]
    PITCH_BUCKETS = {
        "FF": "fastball", "SI": "fastball", "FC": "fastball", "FA": "fastball",
        "SL": "breaking", "ST": "breaking", "CU": "breaking", "KC": "breaking", "SV": "breaking", "CS": "breaking",
        "CH": "offspeed", "FS": "offspeed", "SP": "offspeed", "FO": "offspeed",
    }


    def ip_setup_early(self,ip):
        self.task_queue             = []
        self.private_stale          = False     # not sure if this ended up being needed
        self.private_track_filter   = None
        self.card_mode              = "detail"           # detail | field  (toggled in the header)
        self.btn_run_all_txt        = "Run All"
        self.btn_train_xgb          = "Train XGB"
        self.btn_walk_up            = "Walk Up"

        self.start_date             = "2026-03-27"       # instance state, seeded once — survives rebuilds like card_mode
        self.end_date               = "2026-03-30"
        self.active_table           = None
        self.private_lineage_path   = None
        self.private_field_bodies   = {}

    def ip_activated(self,ip):          # called by TabSystem when user switches here
        #print("Am i firing")
        if self.private_stale:
            self.private_stale = False
            self.refresh_pane()

    def ip_think(self, ip):
        """#Drift warning ip_think  NEW: detect right-click on fields"""
        if self.card_mode != "field":
            self.private_lineage_path = None
            return
        for event in ip.unhandled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.handle_field_right_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.private_lineage_path = None
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
        Title(header, "Pipeline", glow=True)
        Spacer(header)

        Button(header, self.btn_run_all_txt, color_bg=Style.COLOR_BUTTON_CTA, on_click=self.run_all)


        TextBox(header, initial_value=self.start_date, name="txt_start_date")
        Body(header, "to:")
        TextBox(header, initial_value=self.end_date, name="txt_end_date")
        Button(header, self.btn_walk_up, color_bg=Style.COLOR_BUTTON_CTA, on_click=self.walk_all)
        Spacer(header)
        #Button(header, "Train XGB"  , on_click=lambda: self.train_xgb("forest"))
        Button(header, self.btn_train_xgb, on_click=self.train_xgb_clicked)

        Button(header, "Refresh"       , on_click=self.refresh_pane)
        Button(header, self.toggle_label(), on_click=self.toggle_card_mode)
        #btn.on_click = lambda: (btn.set_text("Working..."))

        Button(header, "Phoenix"    , on_click=self.nuke_clicked, color_bg=Style.COLOR_BUTTON_DANGER)
        #Button(header, "Clear Cache", on_click=self.clear_cache_clicked)


        # Just a test - delete me
        #DropDown(header, placeholder="Pick one...", border=0, pad=0, flex_width=1, data={"Alpha": {}, "Bravo": {}, "Charlie": {}, "Delta": {}, "Echo": {}, "Foxtrot": {}, "Foxtrot2": {}, "Foxtrot3": {}, "Foxtrot4": {}, "Foxtrot5": {}, "Foxtrot6": {}})
        #DropDown(header, placeholder="All", border=0, pad=0, flex_width=1,  data=self.track_dropdown_data(), on_change=self.on_track_changed)
        dd = DropDown(header, placeholder="All", border=0, pad=0, flex_width=1,  data=self.track_dropdown_data(), on_change=self.on_track_changed)
        if self.private_track_filter: dd.textbox.set_text(self.private_track_filter)

    def clear_cache_clicked(self):

        self.clear_cache()
        self.refresh_pane()

    def commit_dates(self):
        self.start_date = self.form.widgets["txt_start_date"].text
        self.end_date   = self.form.widgets["txt_end_date"].text

    def refresh_pane(self):
        self.commit_dates()
        self.set_pane(0, self.all_in_one)


    def train_xgb_clicked(self):
        start_gd, target_gd = self.get_start_and_end_dates()
        self.btn_train_xgb="Working..."
        self.refresh_pane()
        self.run_predict_layer(target_gd)
        self.ip.drip_when_dry(self.reset_run_btn)

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



    def select_forest_table(self, tbl):
        print(f"select_forest_table  tbl={tbl}")
        if tbl in Pipe.FOREST_TABLES_TO_TRAIN: Pipe.FOREST_TABLES_TO_TRAIN.remove(tbl)
        else:                                  Pipe.FOREST_TABLES_TO_TRAIN.append(tbl)
        self.refresh_pane()


    def toggle_label(self):
        return "Fields" if self.card_mode == "detail" else "Details"

    def toggle_card_mode(self):
        self.card_mode = "field" if self.card_mode == "detail" else "detail"
        self.refresh_pane()

    # Pipe.py method: nuke_clicked  Update: msgbox now warns full-file delete
    def nuke_clicked(self):
        self.form.msgbox(
            "PHOENIX — delete the ENTIRE database file?\n\n"
            "Every layer (raw included) and the .db file itself\n"
            "will be deleted, then rebuilt fresh from schema.\n"
            "Same as your drop-bat + restart.",
            MSG_BTNS_YES_NO + MSG_ICON_QUESTION + MSG_DEFAULT_2,
            "Phoenix — full reset",
            on_result=self.do_nuke,
        )

    # Pipe.py method: do_nuke  Update: hard reset via BbDB.phoenix(), then refresh
    def do_nuke(self, result):
        if result != MSG_RESULT_YES: return
        BbDB.phoenix()
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
        for tbl in self.tables_for_layer_filtered(layer):
            self.build_one_card(parent, tbl)

    def build_one_card(self, parent, tbl):
        summary  = BbDB.get_summary(tbl)
        selected = BbDB.layer_of(tbl) == "forest" and tbl in Pipe.FOREST_TABLES_TO_TRAIN
        color    = self.card_color(tbl, selected)
        card     = Card(parent, pad=5, color_bg=color) if color else Card(parent, pad=5)
        if BbDB.layer_of(tbl) == "forest": card.on_click_me(lambda t=tbl: self.select_forest_table(t))
        self.build_card_header(card, tbl, summary)
        refs     = self.build_card_body(card, tbl, summary)
        self.build_card_buttons(card, tbl, refs)

    def card_color(self, tbl, selected):
        if tbl == self.active_table: return Style.COLOR_TAB_STATUS_LINKED  # ← PICK THIS COLOR (distinct from the green)
        if selected:                 return Style.COLOR_BUTTON_CTA
        return None

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
        Body(card, f"{rng} ")
        return body_rows, body_range

    def build_field_list(self, card, tbl):
        body = Body(card, "\n".join(BbDB.field_names(tbl)),
                    on_right_click=lambda t=tbl: self.handle_field_lineage(t))
        self.private_field_bodies[tbl] = body

    # Pipe.py method: handle_field_lineage  NEW: right-click → trace → store path
    def handle_field_lineage(self, tbl):
        import pygame
        pos   = pygame.mouse.get_pos()
        field = self.field_at_click(tbl, pos[1])
        if field is None: return
        backward, forward = FieldLineage.trace(field, tbl)
        path = [(hop.table, hop.field) for hop in reversed(backward)]
        path.append((tbl, field))
        path.extend((hop.table, hop.field) for hop in forward)
        self.private_lineage_path = path

    # Pipe.py method: ip_draw_hud  NEW: draw lineage arrows
    def ip_draw_hud(self, ip):
        if not self.private_lineage_path: return
        path = self.private_lineage_path
        for i in range(len(path) - 1):
            src_tbl, src_field = path[i]
            dst_tbl, dst_field = path[i + 1]
            src_body = self.form.widgets.get(f"fields_{src_tbl}")
            dst_body = self.form.widgets.get(f"fields_{dst_tbl}")
            if src_body is None or dst_body is None: continue
            src_fields = BbDB.field_names(src_tbl)
            dst_fields = BbDB.field_names(dst_tbl)
            if src_field not in src_fields or dst_field not in dst_fields: continue
            lh    = Style.FONT_BODY.get_height()
            src_i = src_fields.index(src_field)
            dst_i = dst_fields.index(dst_field)
            start = (src_body.abs_rect.right, src_body.abs_rect.top + src_i * lh + lh // 2)
            end   = (dst_body.abs_rect.left,  dst_body.abs_rect.top + dst_i * lh + lh // 2)
            DisplayArrow(
                start, end,
                screen     = ip.surface,
                color      = Style.COLOR_MOLTEN,
                thickness  = 2,
                arrow_size = 10,
            ).draw()




    def field_at_click(self, tbl, click_y):
        body = self.private_field_bodies.get(tbl)                  # DELETE form.widgets line
        if body is None: return None
        fields      = BbDB.field_names(tbl)
        if not fields: return None
        line_height = Style.FONT_BODY.get_height()
        line_index  = (click_y - body.rect.top) // line_height
        if line_index < 0 or line_index >= len(fields): return None
        return fields[line_index]


    # Pipe.py method: field_coords  NEW: field name → screen (x, y) midpoint
    def field_coords(self, tbl, field_name, side='right'):
        body = self.form.widgets.get(f"fields_{tbl}")
        if body is None: return None
        fields = BbDB.field_names(tbl)
        if field_name not in fields: return None
        line_height = Style.FONT_BODY.get_height()
        index       = fields.index(field_name)
        y           = body.rect.top + (index * line_height) + (line_height // 2)
        x           = body.rect.right if side == 'right' else body.rect.left
        return (x, y)
    def build_card_buttonsOLD(self, card, tbl, refs):
        body_rows, body_range = refs if refs else (None, None)
        btns = Row(Plate(Plate(Plate(card,pad=2),pad=2),pad=4))
        Button(btns, "Run"      , flex_width=1, on_click=lambda t=tbl, br=body_rows, bg=body_range: self.refresh_table(t, br, bg))
        Button(btns, "DB"       , flex_width=1, on_click=lambda t=tbl: self.view_in_db(t))
        Button(btns, "WS"       , flex_width=1, on_click=lambda t=tbl: self.view_in_workbench(t))  # NEW
        Button(btns, "SQL"      , flex_width=1, on_click=lambda t=tbl: self.view_in_sql(t))  # NEW

    def build_card_buttons(self, card, tbl, refs):
        body_rows, body_range = refs if refs else (None, None)
        plate_color = self.guys_line_color(tbl)
        plate = Plate(Plate(Plate(card, pad=2, color_bg=plate_color), pad=2), pad=4)   # DELETE old line 217
        btns  = Row(plate)
        Button(btns, "Run"      , flex_width=1, on_click=lambda t=tbl, br=body_rows, bg=body_range: self.refresh_table(t, br, bg))
        Button(btns, "DB"       , flex_width=1, on_click=lambda t=tbl: self.view_in_db(t))
        Button(btns, "WB"       , flex_width=1, on_click=lambda t=tbl: self.view_in_workbench(t))
        Button(btns, "SQL"      , flex_width=1, on_click=lambda t=tbl: self.view_in_sql(t))
        Button(btns, "SQL"      , flex_width=1, on_click=lambda t=tbl: self.trace_table(t))

    def view_in_db(self, tbl):
        self.form.switch_tab("DB")
        db_tab = self.form.get_tab("DB")
        if db_tab is None:
            BbDB.log("view_in_db", "DB tab not found after switch")
            return
        db_tab.load_table(tbl)

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

    def refresh_table_nowOLD(self, tbl, dates, body_rows, body_range):
        start_gd, end_gd = dates
        layer = BbDB.layer_of(tbl)
        if layer == "raw":
            method = getattr(self, f"sync_{tbl}", None)
            if method:
                for gd in MgrDT.gd_range(start_gd, end_gd):
                    method(gd)
            else:
                BbDB.log(tbl, "no sync method found")
            BbDB.update_summary(tbl)
        else:
            for gd in MgrDT.gd_range(start_gd, end_gd):
                self.update_table(tbl, gd)
        s = BbDB.get_summary(tbl)
        if not body_rows: return
        body_rows.text  = f"Rows: {s.rows:,}"
        rng = f"{MgrDT.gd_to_iso(s.min_gd)}  to  {MgrDT.gd_to_iso(s.max_gd)}" if s.min_gd else "—  to  —"
        body_range.text = f"Range: {rng}"


    def refresh_table_now(self, tbl, dates, body_rows, body_range):
        start_gd, end_gd = dates
        layer = BbDB.layer_of(tbl)
        if layer == "raw":
            method = getattr(self, f"sync_{tbl}", None)
            if method:
                for gd in MgrDT.gd_range(start_gd, end_gd):
                    self.ip.drip(method, gd)
            else:
                BbDB.log(tbl, "no sync method found")
            self.ip.drip(BbDB.update_summary, tbl)
        else:
            for gd in MgrDT.gd_range(start_gd, end_gd):
                self.ip.drip(self.logthe_table, tbl, gd)
                self.ip.drip(self.update_table, tbl, gd)
        self.ip.drip(self.refresh_card_stats, tbl, body_rows, body_range)

    def refresh_card_stats(self, tbl, body_rows, body_range):
        s = BbDB.get_summary(tbl)
        if not body_rows: return
        body_rows.text  = f"Rows: {s.rows:,}"
        rng = f"{MgrDT.gd_to_iso(s.min_gd)}  to  {MgrDT.gd_to_iso(s.max_gd)}" if s.min_gd else "—  to  —"
        body_range.text = rng

    def parse_textbox_date_to_gd(self, name): return MgrDT.str_to_gd(self.form.widgets[name].text)

    def get_start_and_end_dates(self):
        try:
            start_gd = self.parse_textbox_date_to_gd("txt_start_date")
            end_gd   = self.parse_textbox_date_to_gd("txt_end_date")
        except (ValueError, KeyError) as e:
            BbDB.log("dates", f"bad input: {e}")
            EZ.err(f"Bad dates: {e}")
        if start_gd > end_gd:
            msg=f"start {start_gd} > end {end_gd}; aborting"
            BbDB.log("dates", f"start {start_gd} > end {end_gd}; aborting")
            EZ.err(msg)
        self.commit_dates()
        return start_gd, end_gd



    # ════════════════════════════════════════════════
    # Managing Track                              ═══
    # ════════════════════════════════════════════════
    # Pipe.py method: track_dropdown_data  New: build DropDown data from _track_tables
    def track_dropdown_data(self):
        """All known tracks plus an 'All' entry for unfiltered view."""
        tracks = BbDB.query("SELECT DISTINCT track FROM _track_tables ORDER BY track")
        data   = {"All": {}}
        for (t,) in tracks: data[t] = {}
        return data

    # Pipe.py method: on_track_changed  New: filter pipeline cards by track
    def on_track_changed(self, selected):
        """Store the selected track (None = All) and rebuild the card area."""
        pick = selected[0] if selected else "All"
        self.private_track_filter = None if pick == "All" else pick
        self.refresh_pane()

    # Pipe.py method: tables_in_track  New: set of tables belonging to a track
    def tables_in_track(self, track):
        """All table names assigned to this track."""
        rows = BbDB.query("SELECT tbl FROM _track_tables WHERE track=?", (track,))
        return {r[0] for r in rows}

    def tables_for_layer_filteredOLD(self, layer):
        """Tables for a layer, filtered by active track if one is selected."""
        tables = BbDB.tables_for_layer(layer)
        if self.private_track_filter is None: return tables
        track_set = self.tables_in_track(self.private_track_filter)
        return [t for t in tables if t in track_set]

    def tables_for_layer_filtered(self, layer):
        """Tables for a layer, filtered by active track if one is selected."""
        tables = [t for t in BbDB.tables_for_layer(layer) if BbDB.table_exists(t)]
        if self.private_track_filter is None: return tables
        track_set = self.tables_in_track(self.private_track_filter)
        return [t for t in tables if t in track_set]

    # ════════════════════════════════════════════════
    # Widget Tree                                  ═══
    # ════════════════════════════════════════════════


    def build_card_buttons(self, card, tbl, refs):
        body_rows, body_range = refs if refs else (None, None)
        plate_color = self.guys_line_color(tbl)
        plate = Plate(Plate(Plate(card, pad=2, color_bg=plate_color), pad=2), pad=4)   # DELETE old line 217
        btns  = Row(plate)
        Button(btns, "Run"      , flex_width=1, on_click=lambda t=tbl, br=body_rows, bg=body_range: self.refresh_table(t, br, bg))
        Button(btns, "DB",        flex_width=1, on_click=lambda t=tbl: self.view_in_db(t))
        Button(btns, "WB"       , flex_width=1, on_click=lambda t=tbl: self.view_in_workbench(t))
        Button(btns, "SQL"      , flex_width=1, on_click=lambda t=tbl: self.view_in_sql(t))

    # Pipe.py method: guys_line_color  NEW: MAE → red/yellow/green spectrum
    def guys_line_color(self, tbl):
        layer = BbDB.layer_of(tbl)
        if not tbl.startswith("predict_"):     return None
        forest = tbl.replace("predict_", "") if layer == "predict" else tbl
        row = BbDB.query("SELECT total_mae FROM model_run WHERE forest_table = ? ORDER BY GD DESC LIMIT 1",            (forest,)        )
        if not row or row[0][0] is None:            return None
        mae   = row[0][0]
        ratio = mae / Pipe.GUYS_LINE
        return Pipe.spectrum_color(ratio)

    # Pipe.py method: spectrum_color  NEW: ratio → RGB
    @staticmethod
    def spectrum_color(ratio):
        # 0.8 or below = green, 1.0 = yellow, 1.2+ = red
        ratio  = max(0.8, min(1.2, ratio))
        t      = (ratio - 0.8) / 0.4        # 0.0 = green, 0.5 = yellow, 1.0 = red
        if t <= 0.5:
            r = int(255 * (t * 2))
            g = 255
        else:
            r = 255
            g = int(255 * (1 - (t - 0.5) * 2))
        return (r, g, 0)

    ####################FIELD LINEAGE #######################
    ####################FIELD LINEAGE #######################

    def ip_draw_hud(self, ip):
        if not self.private_lineage_path: return
        path = self.private_lineage_path
        for i in range(len(path) - 1):
            src_tbl, src_field = path[i]
            dst_tbl, dst_field = path[i + 1]
            src_body = self.private_field_bodies.get(src_tbl)      # DELETE form.widgets line
            dst_body = self.private_field_bodies.get(dst_tbl)      # DELETE form.widgets line
            if src_body is None or dst_body is None: continue
            src_fields = BbDB.field_names(src_tbl)
            dst_fields = BbDB.field_names(dst_tbl)
            if src_field not in src_fields or dst_field not in dst_fields: continue
            lh    = Style.FONT_BODY.get_height()
            src_i = src_fields.index(src_field)
            dst_i = dst_fields.index(dst_field)
            start = (src_body.rect.right, src_body.rect.top + src_i * lh + lh // 2)
            end   = (dst_body.rect.left,  dst_body.rect.top + dst_i * lh + lh // 2)
            DisplayArrow(
                start, end,
                screen     = ip.surface,
                color      = Style.COLOR_MOLTEN,
                thickness  = 2,
                arrow_size = 10,
            ).draw()

    ########################### WALK UP ###########################
    ########################### WALK UP ###########################

    def walk_all(self):
        self.btn_walk_up = "Walking..."
        self.refresh_pane()
        BbDB.log("walk", "preparing to walk up")
        self.ip.drip(self.queue_walk_folds)
        self.ip.drip_when_dry(self.reset_run_btn)

    def queue_walk_folds(self):
        start_gd, target_gd = self.get_start_and_end_dates()
        tables              = self.valid_forest_tables_for_predict_layer()   # snapshot — mid-walk clicks can't mutate
        base_id             = DbResults.next_run_id()
        for i, table in enumerate(tables):
            self.ip.drip(self.set_walk_run, base_id + i)
            for gd in MgrDT.gd_range(start_gd, target_gd):
                if gd == start_gd: continue                                  # day one has nothing to train on
                self.ip.drip(self.walk_one_fold, table, gd)
        self.ip.drip(self.clear_walk_run)

    # Pipe.py  method: walk_one_fold  NEW: one fold = the literal production path with a cut
    def walk_one_fold(self, table, gd):
        self.train_xgb(table, cut_date=gd)

    # Pipe.py  method: clear_walk_run  NEW: back to normal minting
    def clear_walk_run(self):
        self.walk_run_id = None

    def set_walk_run(self, run_id):
        self.walk_run_id = run_id