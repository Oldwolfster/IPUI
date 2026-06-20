#PipeMixinModelResults
from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrDT import MgrDT


class MixinModelResults:

    # PipeMixinModelResults.py  method: load_model_tables  NEW: dispatcher after predict table is written
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
        self.update_model_summaries()
        BbDB.log("model", f"{model_name}: model tables loaded")


    # PipeMixinModelResults.py  method: clear_model_rows  NEW: refresh current result rows only
    def clear_model_rows(self, run_id):
        BbDB.execute("DELETE FROM model_prediction WHERE run_id = ?", (run_id,))
        BbDB.execute("DELETE FROM model_day        WHERE run_id = ?", (run_id,))
        BbDB.execute("DELETE FROM model_run        WHERE run_id = ?", (run_id,))


    # PipeMixinModelResults.py  method: load_model_prediction  NEW: standardize predict grain to batter-game
    def load_model_prediction(self, run_id, model_name, predict_table):
        BbDB.execute(f"""
            INSERT INTO model_prediction
                (GD, run_id, batter, game_pk, model_name, predicted, actual, error)
            SELECT
                GD,
                ?,
                batter,
                game_pk,
                ?,
                SUM(predicted),
                SUM(actual),
                SUM(predicted) - SUM(actual)
            FROM {predict_table}
            GROUP BY GD, batter, game_pk
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
        if "batter" in df.columns and "game_pk" in df.columns: return "batter_game"
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


    # PipeMixinModelResults.py method: load_log5_prediction  NEW: materialize log5 batter-game predictions
    def load_log5_prediction(self, run_id, model_name):
        BbDB.execute("""
            INSERT INTO model_prediction
                (GD, run_id, batter, game_pk, model_name, predicted, actual, error)
            SELECT
                r.GD,
                ?,
                r.batter,
                r.game_pk,
                ?,
                r.predicted,
                bg.hits,
                r.predicted - bg.hits
            FROM (
                SELECT
                    f.GD,
                    f.batter,
                    f.game_pk,
                    (
                        (b * p / lg)
                        / (
                            (b * p / lg)
                            + ((1 - b) * (1 - p) / NULLIF(1 - lg, 0))
                        )
                    ) * 3.8 AS predicted
                FROM (
                    SELECT
                        f.GD,
                        f.batter,
                        f.game_pk,
                        COALESCE(f.b_ba,         lg.lg_ba) AS b,
                        COALESCE(f.p_ba_against, lg.lg_ba) AS p,
                        lg.lg_ba                           AS lg
                    FROM       forest f
                    CROSS JOIN (
                        SELECT SUM(is_hit) * 1.0 / NULLIF(SUM(is_ab), 0) AS lg_ba
                        FROM etl_pa
                    ) lg
                ) f
            ) r
            INNER JOIN batter_games bg
                    ON bg.GD      = r.GD
                   AND bg.batter  = r.batter
                   AND bg.game_pk = r.game_pk
        """, (run_id, model_name))


    # PipeMixinModelResults.py method: load_log5_run  NEW: add log5 to Predict picker registry
    def load_log5_run(self, run_id, model_name):
        pred_start, pred_end  = self.model_prediction_bounds(run_id)
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
            "forest",
            "",
            "hits",
            "batter_game",
            None,
            None,
            pred_start,
            pred_end,
            total_preds,
            total_mae,
            3,
            "b_ba, p_ba_against, lg_ba",
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