# Predict.py  class: Predict  Update: N-pane comparison via Add Pane button + per-pane state
import sqlite3
from datetime import date, timedelta, datetime
from pathlib import Path

from ipui import *


class Predict(_BaseTab):

    DB_PATH      = str(Path.home() / ".neuroforge" / "projects" / "baseball.db")
    MODEL_PREFIX = "model_"
    NEW_PANE_WEIGHT = 0.75

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
        TextBox(row1, initial_value=self.default_start_date(),
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

    def on_model_picked(self, pane_index, picks):
        if not picks:
            return
        self.pane_state[pane_index]["model"] = self.MODEL_PREFIX + picks[0]
        self.set_pane(pane_index, self.by_day, pane_index=pane_index)

    # ══════════════════════════════════════════════════════════════
    # STATE: by_day (days grid)
    # ══════════════════════════════════════════════════════════════

    def by_day(self, parent, pane_index=1):
        model_view = self.pane_state[pane_index]["model"]
        if model_view is None:
            self.set_pane(pane_index, self.by_model, pane_index=pane_index)
            return

        start_str, end_str = self.read_dates()
        if start_str is None:
            return

        days = self.query_daily_summary(model_view, start_str, end_str)
        model_name = model_view[len(self.MODEL_PREFIX):]

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

    def by_dude(self, parent, pane_index=1):
        model_view = self.pane_state[pane_index]["model"]
        gd         = self.pane_state[pane_index]["day"]
        if model_view is None or gd is None:
            self.set_pane(pane_index, self.by_day, pane_index=pane_index)
            return

        rows = self.query_predictions_for(model_view, gd)
        model_name = model_view[len(self.MODEL_PREFIX):]

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

    def no_models(self, parent, pane_index=1):
        card = CardCol(parent, flex_height=1)
        Title(card, "No Models Defined", glow=True)
        Body(card, "No models defined — views searched: model_*")
        Body(card, "")
        Body(card, "Create a model in the SQL tab:")
        Body(card, "  CREATE VIEW model_001_bootstrap AS")
        Body(card, "  SELECT gd, batter, game_pk, <expr> AS predicted")
        Body(card, "  FROM ...")
        Body(card, "")
        Body(card, "Then return to this tab.")

    # ══════════════════════════════════════════════════════════════
    # MODEL DISCOVERY
    # ══════════════════════════════════════════════════════════════

    def list_models(self):
        conn = self.open_db()
        rows = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE  type = 'view'
              AND  name LIKE ?
            ORDER  BY name
        """, (self.MODEL_PREFIX + "%",)).fetchall()
        conn.close()
        return [r[0][len(self.MODEL_PREFIX):] for r in rows]

    def list_models_dict(self):
        return {name: {} for name in self.list_models()}

    # ══════════════════════════════════════════════════════════════
    # QUERIES
    # ══════════════════════════════════════════════════════════════

    def query_daily_summary(self, model_view, start_str, end_str):
        sql = f"""
            SELECT
                bg.gd                                   AS gd,
                COUNT(*)                                AS predictions,
                AVG(ABS(m.predicted - bg.hits))         AS mae,
                MIN(m.predicted - bg.hits)              AS min_err,
                MAX(m.predicted - bg.hits)              AS max_err
            FROM       batter_games   bg
            INNER JOIN {model_view}   m
                       ON  m.gd      = bg.gd
                      AND  m.batter  = bg.batter
                      AND  m.game_pk = bg.game_pk
            WHERE      bg.gd BETWEEN ? AND ?
            GROUP  BY  bg.gd
            ORDER  BY  bg.gd
        """
        conn = self.open_db()
        rows = conn.execute(sql, (start_str, end_str)).fetchall()
        conn.close()
        return rows

    def query_predictions_for(self, model_view, gd):
        sql = f"""
            SELECT
                bg.batter                              AS batter_id,
                COALESCE(b.name, '#' || bg.batter)     AS name,
                bg.game_pk                             AS game_pk,
                bg.hits                                AS actual,
                m.predicted                            AS predicted,
                m.predicted - bg.hits                  AS error
            FROM       batter_games   bg
            INNER JOIN {model_view}   m
                       ON  m.gd      = bg.gd
                      AND  m.batter  = bg.batter
                      AND  m.game_pk = bg.game_pk
            LEFT  JOIN batters        b
                       ON  b.id      = bg.batter
            WHERE      bg.gd = ?
            ORDER  BY  bg.hits DESC, m.predicted DESC
        """
        conn = self.open_db()
        rows = conn.execute(sql, (gd,)).fetchall()
        conn.close()
        return rows

    def overall_mae(self, days):
        total_preds = sum(d[1] for d in days)
        total_err   = sum(d[1] * d[2] for d in days)
        return total_err / total_preds

    # ══════════════════════════════════════════════════════════════
    # FORMATTING
    # ══════════════════════════════════════════════════════════════

    def format_days_rows(self, days):
        return [
            {
                "gd"          : d[0],
                "predictions" : d[1],
                "mae"         : round(d[2], 3),
                "min_err"     : round(d[3], 2),
                "max_err"     : round(d[4], 2),
            }
            for d in days
        ]

    def format_preds_rows(self, rows):
        return [
            {
                "batter_id" : r[0],
                "name"      : r[1],
                "game_pk"   : r[2],
                "actual"    : r[3],
                "predicted" : round(r[4], 2) if r[4] is not None else None,
                "error"     : round(r[5], 2) if r[5] is not None else None,
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