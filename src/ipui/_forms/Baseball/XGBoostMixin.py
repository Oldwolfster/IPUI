
import numpy   as np
from ipui._forms.Baseball.BB import BB


class XGBoostMixin:

    XGB_MODEL_NAME  = "xgb_v1"                                          # matches predict_xgb_v1 table
    XGB_TABLE       = "predict_xgb_v1"
    XGB_THROWS_MAP  = {"L": 0, "R": 1, "": -1}                         # encode handedness
    XGB_STAND_MAP   = {"L": 0, "R": 1, "S": 2, "": -1}                 # encode stance; S=switch

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — wired to Train XGBoost button on Pipe header.
    # ══════════════════════════════════════════════════════════════

    def train_xgb(self):

        BB.log(self.XGB_TABLE, "INFO",  "loading forest")
        rows = self.load_forest()
        if not rows:
            BB.log(self.XGB_TABLE, "WARN",  "forest is empty — run Update All first")
            return
        BB.log(self.XGB_TABLE, "INFO",  f"training on {len(rows)} rows")
        model = self.fit_model(rows)
        BB.log(self.XGB_TABLE, "INFO",  "writing predictions")
        self.write_predictions(model, rows)
        BB.log(self.XGB_TABLE, "DONE",  "model_xgb_v1 ready")

    # ══════════════════════════════════════════════════════════════
    # LOAD — pull forest rows; skip rows with NULL features.
    # ══════════════════════════════════════════════════════════════

    def load_forest(self):
        return BB.query("""
            SELECT GD, batter, game_pk, hits,
                   b_ba, p_ba_against, p_throws, b_stand
            FROM   forest
            WHERE  hits          IS NOT NULL
              AND  b_ba          IS NOT NULL
              AND  p_ba_against  IS NOT NULL
              AND  p_throws      IS NOT NULL
              AND  b_stand       IS NOT NULL
        """)

    # ══════════════════════════════════════════════════════════════
    # FEATURES — encode categoricals, return X matrix and y vector.
    # ══════════════════════════════════════════════════════════════

    def build_xy(self, rows):
        X = np.array([
            [
                r[4],                                                    # b_ba
                r[5],                                                    # p_ba_against
                self.XGB_THROWS_MAP.get(r[6], -1),                      # p_throws encoded
                self.XGB_STAND_MAP .get(r[7], -1),                      # b_stand encoded
            ]
            for r in rows
        ], dtype=float)
        y = np.array([r[3] for r in rows], dtype=float)                 # hits = target
        return X, y

    # ══════════════════════════════════════════════════════════════
    # TRAIN — fit XGBoost regressor with conservative defaults.
    # Small dataset — keep trees shallow to avoid overfit.
    # ══════════════════════════════════════════════════════════════

    def fit_model(self, rows):
        import xgboost as xgb
        X, y        = self.build_xy(rows)
        model       = xgb.XGBRegressor(
            n_estimators    = 50,                                        # few trees — tiny dataset
            max_depth       = 3,                                         # shallow — avoid overfit
            learning_rate   = 0.1,
            subsample       = 0.8,
            random_state    = 42,
            verbosity       = 0,
        )
        model.fit(X, y)
        return model

    # ══════════════════════════════════════════════════════════════
    # WRITE — upsert predictions into predict_xgb_v1.
    # ══════════════════════════════════════════════════════════════

    def write_predictions(self, model, rows):
        X, _   = self.build_xy(rows)
        preds  = model.predict(X)
        for row, pred in zip(rows, preds):
            BB.execute("""
                INSERT INTO predict_xgb_v1 (GD, batter, game_pk, predicted)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(GD, batter, game_pk) DO UPDATE SET
                    predicted = excluded.predicted
            """, (row[0], row[1], row[2], float(pred)))
