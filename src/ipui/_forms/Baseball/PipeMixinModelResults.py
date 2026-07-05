#PipeMixinModelResults
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.DbResults import DbResults
from ipui._forms.Baseball.MgrDT import MgrDT



class MixinModelResults:
    RUN_LABEL = "ortho"  # edit per experiment: "baseline+pitchtype" etc.
    walk_run_id = None

    def load_model_tables(self, forest_table, predict_table, df_train, df_predict, target):
        if df_predict.empty:
            BbDB.log("model", f"{forest_table}: no prediction rows to load")
            return
        run_id     = forest_table
        model_name = forest_table
        features   = self.model_feature_cols(df_train)
        self.clear_model_rows(run_id)
        self.load_model_prediction(run_id, model_name, predict_table)
        self.load_model_day(run_id, model_name)
        self.load_model_run(run_id, model_name, forest_table, predict_table, target, features, df_train, df_predict)
        self.load_results_gd(run_id, model_name, forest_table, predict_table, target, features, df_train)  # NEW
        self.update_model_summaries()



    # PipeMixinModelResults.py  method: clear_model_rows  NEW: refresh current result rows only
    def clear_model_rows(self, run_id):
        BbDB.execute("DELETE FROM model_prediction WHERE run_id = ?", (run_id,))
        BbDB.execute("DELETE FROM model_day        WHERE run_id = ?", (run_id,))
        BbDB.execute("DELETE FROM model_run        WHERE run_id = ?", (run_id,))

    def load_model_prediction(self, run_id, model_name, predict_table):
        BbDB.execute(f"""
            INSERT INTO model_prediction
                (GD, run_id, batter, --game,
                 model_name, predicted, actual, error)
            SELECT
                GD,
                ?,
                batter,
                --game,
                ?,
                SUM(predicted),
                SUM(actual),
                SUM(predicted) - SUM(actual)
            FROM {predict_table}
            GROUP BY GD, batter--, game
        """, (run_id, model_name))

    # PipeMixinModelResults.py  method: load_model_day  NEW: materialized day drill level
    def load_model_day(self, run_id, model_name):
        BbDB.execute("""
            INSERT INTO model_day
                (GD, run_id, model_name, predictions, mae, min_err, max_err, actual_total, predicted_total)
            SELECT
                GD,
                ?,
                ?,
                COUNT(*),
                AVG(ABS(error)),
                MIN(error),
                MAX(error),
                SUM(actual),
                SUM(predicted)
            FROM model_prediction
            WHERE run_id = ?
            GROUP BY GD
        """, (run_id, model_name, run_id))


    # PipeMixinModelResults.py  method: load_model_run  NEW: one registry row for Predict tab
    def load_model_run(self, run_id, model_name, forest_table, predict_table, target, features, df_train, df_predict):
        train_start, train_end = self.model_gd_bounds(df_train)
        pred_start,  pred_end  = self.model_gd_bounds(df_predict)
        total_preds, total_mae = self.model_totals(run_id)
        BbDB.execute("""
            INSERT INTO model_run
                (GD, run_id, model_name, forest_table, predict_table, target_field, grain,
                 train_start_gd, train_end_gd, predict_start_gd, predict_end_gd,
                 total_predictions, total_mae, feature_count, features_csv, created_ds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred_end,
            run_id,
            model_name,
            forest_table,
            predict_table,
            target,
            self.model_grain(df_predict),
            train_start,
            train_end,
            pred_start,
            pred_end,
            total_preds,
            total_mae,
            len(features),
            ", ".join(features),
            MgrDT.today_ds(),
        ))


    # PipeMixinModelResults.py  method: model_feature_cols  NEW: reuse XGB split rules
    def model_feature_cols(self, df):
        X, y, features = self.split_xy(df)
        return features


    # PipeMixinModelResults.py  method: model_gd_bounds  NEW: safe dataframe GD bounds
    def model_gd_bounds(self, df):
        if df.empty: return None, None
        return int(df["GD"].min()), int(df["GD"].max())


    # PipeMixinModelResults.py  method: model_grain  NEW: rough source grain label
    def model_grain(self, df):
        if "at_bat_number" in df.columns: return "pa"
        if "batter" in df.columns and ("game" in df.columns or "game_pk" in df.columns): return "batter_game"  # NEW
        return "unknown"


    # PipeMixinModelResults.py  method: model_totals  NEW: weighted MAE from day table
    def model_totals(self, run_id):
        rows = BbDB.query("""
            SELECT
                COALESCE(SUM(predictions), 0),
                SUM(predictions * mae) / NULLIF(SUM(predictions), 0)
            FROM model_day
            WHERE run_id = ?
        """, (run_id,))
        return rows[0] if rows else (0, None)
    def game_col_for(self, table):
        """Return 'game' or 'game_pk' depending on what the table has."""
        cols = {c[1] for c in BbDB.query(f"PRAGMA table_info({table})")}
        if "game" in cols: return "game"
        if "game_pk" in cols: return "game_pk"
        return "game"

    # PipeMixinModelResults.py  method: update_model_summaries  NEW: refresh Pipe cards
    def update_model_summaries(self):
        BbDB.update_summary("model_run")
        BbDB.update_summary("model_day")
        BbDB.update_summary("model_prediction")

    ####################################################
    ######################### LOG 5

    def load_log5_model(self):
        run_id     = "log5"
        model_name = "log5"
        self.clear_model_rows(run_id)
        self.load_log5_prediction(run_id, model_name)
        self.load_model_day(run_id, model_name)
        self.load_log5_run(run_id, model_name)
        self.update_model_summaries()
        BbDB.log("model", "log5: model tables loaded")
    def game_col_for(self, table):
        """Return 'game' or 'game_pk' depending on what the table has."""
        cols = {c[1] for c in BbDB.query(f"PRAGMA table_info({table})")}
        if "game" in cols: return "game"
        if "game_pk" in cols: return "game_pk"
        return "game"



    def load_log5_prediction(self, run_id, model_name):
        BbDB.execute("""
            INSERT INTO model_prediction
                (GD, run_id, batter,  model_name, predicted, actual, error)
            SELECT
                f.GD,
                ?,
                f.batter,
                --f.game,
                ?,
                (b * p / lg)
                / ( (b * p / lg)
                  + ((1 - b) * (1 - p) / NULLIF(1 - lg, 0)) )
                * 3.8,
                f.t_h,
                (b * p / lg)
                / ( (b * p / lg)
                  + ((1 - b) * (1 - p) / NULLIF(1 - lg, 0)) )
                * 3.8 - f.t_h
            FROM (
                SELECT
                    f.GD,
                    f.batter,
                    --f.game,
                    f.t_h,
                    COALESCE(f.b_ba, lg.lg_ba)  AS b,
                    COALESCE(f.p_ba, lg.lg_ba)  AS p,
                    lg.lg_ba                    AS lg
                FROM       forest_batter f                          -- DELETE forest_dart
                JOIN (
                    SELECT
                        d.GD,
                        SUM(e.h) * 1.0 / NULLIF(SUM(e.ab), 0) AS lg_ba
                    FROM (SELECT DISTINCT GD FROM forest_batter) d  -- DELETE forest_dart
                    JOIN etl_pa e ON e.GD < d.GD                    -- DELETE etl_dart_pa
                    GROUP BY d.GD
                ) lg ON lg.GD = f.GD
            ) f
        """, (run_id, model_name))
    def load_log5_run(self, run_id, model_name):
        pred_start, pred_end   = self.model_prediction_bounds(run_id)
        total_preds, total_mae = self.model_totals(run_id)
        if pred_end is None:
            BbDB.log("model", "log5: no rows found")
            return
        BbDB.execute("""
            INSERT INTO model_run
                (GD, run_id, model_name, forest_table, predict_table, target_field, grain,
                 train_start_gd, train_end_gd, predict_start_gd, predict_end_gd,
                 total_predictions, total_mae, feature_count, features_csv, created_ds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred_end,
            run_id,
            model_name,
            "forest_dart",
            "",
            "t_h",
            "batter_game",
            None,
            None,
            pred_start,
            pred_end,
            total_preds,
            total_mae,
            3,
            "b_ba, p_ba, lg_ba",
            MgrDT.today_ds(),
        ))
    # PipeMixinModelResults.py method: model_prediction_bounds  NEW: min/max GD for loaded model rows
    def model_prediction_bounds(self, run_id):
        rows = BbDB.query("""
            SELECT MIN(GD), MAX(GD)
            FROM model_prediction
            WHERE run_id = ?
        """, (run_id,))
        return rows[0] if rows else (None, None)

    def load_results_gd(self, run_key, model_name, forest_table, predict_table, target, features, df_train):
        run_id = self.walk_run_id or DbResults.next_run_id()
        base   = self.results_base_row(run_id, model_name, forest_table, predict_table, target, features, df_train)
        days   = BbDB.query("SELECT GD, predictions, mae, predicted_total, actual_total FROM model_day WHERE run_id = ?", (run_key,))
        for gd, preds, mae, pred_tot, act_tot in days:
            DbResults.insert_run_gd({**base, "GD": gd, "predictions": preds, "mae": mae,"predicted_total": pred_tot, "actual_total": act_tot})


        run_mae = DbResults.update_run_mae(run_id)  # NEW
        self.log_results_line(model_name, days, run_mae, len(df_train))
            # PipeMixinModelResults.py  method: results_base_row  NEW: run-level metadata shared by every GD row
    def log_results_line(self, model_name, days, run_mae, train_rows):
        for gd, preds, mae, pred_tot, act_tot in days:
            BbDB.log(model_name, f"{gd % 10000:04d}  mae {mae:.3f}  run {run_mae:.3f}  preds {preds}  train {train_rows:,}")

    def results_base_row(self, run_id, model_name, forest_table, predict_table,
                         target, features, df_train):
        t_start, t_end = self.model_gd_bounds(df_train)
        return {"run_id": run_id, "model_name": model_name,
                "run_mae": 0.0,
                "seed": self.XGB_SEED, "hyper": str(self.XGB_PARAMS),
                "label": self.run_label(), "forest_table": forest_table,
                "predict_table": predict_table, "target_field": target,
                "grain": self.model_grain(df_train),
                "train_start_gd": t_start, "train_end_gd": t_end,
                "train_rows": len(df_train), "feature_count": len(features),
                "features_csv": ", ".join(features), "created_ds": MgrDT.today_ds()}


    def run_label(self):
        pieces = [self.RUN_LABEL]
        pieces += [f"-{p}" for p in self.ABLATE_COLS]
        if self.XGB_SEED != 42: pieces += [f"s{self.XGB_SEED}"]
        return " ".join(pieces)