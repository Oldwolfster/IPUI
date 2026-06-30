# Predict.py  class: Predict  Update: N-pane comparison via Add Pane button + per-pane state
import sqlite3
from datetime import date, timedelta, datetime
from pathlib import Path

from ipui import *
from ipui._forms.Baseball.BbDB import BbDB


class Predict(_BaseTab):

    DB_PATH      = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")
    MODEL_PREFIX = "model_"
    NEW_PANE_WEIGHT = 0.75
    ABs_PER_GAME = 3.8

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ══════════════════════════════════════════════════════════════

    def ip_setup_early(self, ip):
        self.pane_state = {}        # {index: {"model": str, "day": str}}

    def ip_activated(self, ip):
        if not self.list_models():
            self.set_pane(1, self.no_models)

    # ══════════════════════════════════════════════════════════════
    # PANE 0 — Controls
    # ══════════════════════════════════════════════════════════════

    def controls(self, parent):
        card = CardCol(parent, flex_height=1)
        Title(card, "Predict Hits", glow=True)
        Body(card, "Pick a model per pane. Click + to compare more.")

        row1 = Row(card)
        Body(row1, "From:")
        TextBox(row1, initial_value="2026-03-27", #self.default_start_date(),
                name="txt_predict_start",
                on_submit=lambda val: self.on_dates_changed())

        row2 = Row(card)
        Body(row2, "To:  ")
        TextBox(row2, initial_value=self.default_end_date(),
                name="txt_predict_end",
                on_submit=lambda val: self.on_dates_changed())

        Spacer(card)
        Button(card, "+ Add Pane", color_bg=Style.COLOR_BUTTON_CTA,
               on_click=self.add_pane)

        Title(card, "Status")
        self.lbl_status = Body(card, "Ready.")

    def add_pane(self):
        next_index = len(self.form.tab_strip.tab_layout[self.form.tab_strip.active_tab])
        self.set_pane(next_index, self.by_model, pane_index=next_index, weight=self.NEW_PANE_WEIGHT)

    def on_dates_changed(self):
        for index, state in self.pane_state.items():
            if state.get("day"):
                self.set_pane(index, self.by_dude, pane_index=index)
            elif state.get("model"):
                self.set_pane(index, self.by_day, pane_index=index)

    # ══════════════════════════════════════════════════════════════
    # STATE: by_model (picker)
    # ══════════════════════════════════════════════════════════════

    def by_model(self, parent, pane_index=1):
        self.pane_state[pane_index] = {"model": None, "day": None}

        Title(parent, f"Pane {pane_index} — Pick a Model", glow=True)
        SelectionList(parent,
            data          = self.list_models_dict(),
            single_select = True,
            flex_height   = 1,
            on_change     = lambda picks, i=pane_index: self.on_model_picked(i, picks),
        )

    # Predict.py method: on_model_picked  UPDATE: selected model is now model_run.model_name
    def on_model_picked(self, pane_index, picks):
        if not picks:
            return
        self.pane_state[pane_index]["model"] = picks[0]
        self.set_pane(pane_index, self.by_day, pane_index=pane_index)


    # ══════════════════════════════════════════════════════════════
    # STATE: by_day (days grid)
    # ══════════════════════════════════════════════════════════════


    # Predict.py method: by_day  UPDATE: use model tables instead of model_* view name
    def by_day(self, parent, pane_index=1):
        model_name = self.pane_state[pane_index]["model"]
        if model_name is None:
            self.set_pane(pane_index, self.by_model, pane_index=pane_index)
            return

        start_str, end_str = self.read_dates()
        if start_str is None:
            return

        days = self.query_daily_summary(model_name, start_str, end_str)

        header = Row(parent, justify_spread=True)
        Title(header, f"{model_name}  —  Daily Summary", glow=True)
        Button(header, "← Back", color_bg=Style.COLOR_TAB_BG,
               on_click=lambda i=pane_index: self.back_to_models(i))

        grid = PowerGrid(parent, flex_height=1)
        grid.set_data(self.format_days_rows(days))
        grid.on_row_click(lambda gd, i=pane_index: self.on_day_clicked(i, gd), "gd")

        if days:
            self.show_status(
                f"Pane {pane_index} — {model_name}  "
                f"MAE {self.overall_mae(days):.3f}  "
                f"({sum(d[1] for d in days):,} preds across {len(days)} days)"
            )
        else:
            self.show_status(f"Pane {pane_index} — no predictions in range for {model_name}.")



    def back_to_models(self, pane_index):
        self.set_pane(pane_index, self.by_model, pane_index=pane_index)

    def on_day_clicked(self, pane_index, gd):
        self.pane_state[pane_index]["day"] = gd
        self.set_pane(pane_index, self.by_dude, pane_index=pane_index)

    # ══════════════════════════════════════════════════════════════
    # STATE: by_dude (per-batter detail)
    # ══════════════════════════════════════════════════════════════

    # Predict.py method: by_dude  UPDATE: use model tables instead of model_* view name
    def by_dude(self, parent, pane_index=1):
        model_name = self.pane_state[pane_index]["model"]
        gd         = self.pane_state[pane_index]["day"]
        if model_name is None or gd is None:
            self.set_pane(pane_index, self.by_day, pane_index=pane_index)
            return

        rows = self.query_predictions_for(model_name, gd)

        header = Row(parent, justify_spread=True)
        Title(header, f"{model_name}  —  {gd}  ({len(rows)} batters)", glow=True)
        Button(header, "← Back", color_bg=Style.COLOR_TAB_BG,
               on_click=lambda i=pane_index: self.back_to_days(i))

        grid = PowerGrid(parent, flex_height=1)
        grid.set_data(self.format_preds_rows(rows))




    def back_to_days(self, pane_index):
        self.pane_state[pane_index]["day"] = None
        self.set_pane(pane_index, self.by_day, pane_index=pane_index)

    # ══════════════════════════════════════════════════════════════
    # STATE: no_models (empty registry)
    # ══════════════════════════════════════════════════════════════

    # Predict.py method: no_models  UPDATE: model_run is now the registry
    def no_models(self, parent, pane_index=1):
        card = CardCol(parent, flex_height=1)
        Title(card, "No Models Defined", glow=True)
        Body(card, "No rows found in model_run.")
        Body(card, "")
        Body(card, "Run the Pipe tab, train selected forest tables,")
        Body(card, "then return here.")



    # ══════════════════════════════════════════════════════════════
    # MODEL DISCOVERY
    # ══════════════════════════════════════════════════════════════


    # Predict.py method: list_models  UPDATE: read model registry table
    def list_models(self):
        rows = BbDB.query("""
            SELECT model_name
            FROM model_run
            ORDER BY model_name
        """)
        return [r[0] for r in rows]

    def list_models_dict(self):
        return {name: {} for name in self.list_models()}

    # ══════════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════════


    # Predict.py method: query_daily_summary  UPDATE: read model_day
    def query_daily_summary(self, model_name, start_str, end_str):
        start_gd = int(start_str.replace("-", ""))
        end_gd   = int(end_str.replace("-", ""))
        sql = """
            SELECT
                GD             AS gd,
                predictions    AS predictions,
                mae            AS mae,
                min_err        AS min_err,
                max_err        AS max_err
            FROM model_day
            WHERE model_name = ?
              AND GD BETWEEN ? AND ?
            ORDER BY GD
        """
        return BbDB.query(sql, (model_name, start_gd, end_gd))

    def query_predictions_for(self, model_name, gd):
        gd_int = int(str(gd).replace("-", ""))
        sql = """
            SELECT
                mp.batter                                               AS batter_id,
                COALESCE(p.full_name, '#' || mp.batter)                 AS name,
                COALESCE(t.abbreviation, '???')                         AS team,
                p.position                                              AS pos,
                --mp.game                                                 AS game,
                mp.actual                                               AS actual,
                ROUND(mp.predicted, 2)                                  AS predicted,
                ROUND(mp.error, 2)                                      AS error
            FROM       model_prediction   mp
            LEFT JOIN  raw_players        p
                   ON  p.player_id = mp.batter
                  AND  p.GD = (
                        SELECT MAX(p2.GD)
                        FROM raw_players p2
                        WHERE p2.player_id = mp.batter
                  )
            LEFT JOIN  raw_teams          t
                   ON  t.team_id = p.team_id
                  AND  t.GD = (
                        SELECT MAX(t2.GD)
                        FROM raw_teams t2
                        WHERE t2.team_id = p.team_id
                  )
            WHERE      mp.model_name = ?
              AND      mp.GD = ?
            ORDER BY   mp.actual DESC, mp.predicted DESC
        """
        return BbDB.query(sql, (model_name, gd_int))
    def overall_mae(self, days):
        scored      = [d for d in days if d[2] is not None]
        total_preds = sum(d[1] for d in scored)
        if not total_preds:
            return 0.0
        total_err   = sum(d[1] * d[2] for d in scored)
        return total_err / total_preds

    # ══════════════════════════════════════════════════════════════
    # FORMATTING
    # ══════════════════════════════════════════════════════════════

    def format_days_rows(self, days):
        return [
            {
                "gd"          : d[0],
                "predictions" : d[1],
                "mae"         : round(d[2], 3) if d[2] is not None else None,
                "min_err"     : round(d[3], 2) if d[3] is not None else None,
                "max_err"     : round(d[4], 2) if d[4] is not None else None,
            }
            for d in days
        ]

    def format_preds_rows(self, rows):
        return [
            {
                "name"      : r[1],
                "team"      : r[2],
                "pos"       : r[3],
                #"game"   : r[4],
                "actual"    : r[4],
                "predicted" : r[5],
                "error"     : r[6],
            }
            for r in rows
        ]

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def show_status(self, text):
        print(f"predict: {text}")
        if self.lbl_status is not None:
            self.lbl_status.set_text(text)

    def read_dates(self):
        start_str = self.form.widgets["txt_predict_start"].text.strip()
        end_str   = self.form.widgets["txt_predict_end"].text.strip()
        if not self.is_valid_date(start_str) or not self.is_valid_date(end_str):
            self.show_status("Bad date format. Use YYYY-MM-DD.")
            return (None, None)
        if start_str > end_str:
            self.show_status("Start date must be on or before end date.")
            return (None, None)
        return (start_str, end_str)

    def default_end_date(self):
        return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    def default_start_date(self):
        return (date.today() - timedelta(days=8)).strftime("%Y-%m-%d")

    def is_valid_date(self, text):
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def open_db(self):
        return sqlite3.connect(self.DB_PATH)


    ################NEW CODE









