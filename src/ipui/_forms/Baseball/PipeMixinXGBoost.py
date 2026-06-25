# PipeMixinXGBoost.py  FULL REWRITE — column-agnostic trainer; all feature logic lives in forest
import pandas as pd
from ipui._forms.Baseball.BbDB import BbDB
from ipui.utils.EZ import EZ
from ipui._forms.Baseball.MgrDT import MgrDT

class MixinXGBoost:
    """
    The one test
        Would a bettor setting the line for this exact game have this exact number in hand before first pitch?
        Yes → the column may go in forest. No → it may not. Every rule below is just this test, made concrete. When in doubt, sit on the eve of the game and ask what you'd actually know.
        A column can play exactly one of three roles
        Target — exactly one, and it's column 0.

        The thing you predict: total hits in this game. It is the outcome, so of course it fails the bettor test — that's fine, it's the answer, not an input. It comes from this game day (batter_games.hits). It's NULL on held-out/inference rows (no answer yet). One target, first column, never moves.
        IDs — a small fixed set, never features.

        GD, batter, game_pk, pitcher. They identify which row, they don't describe the matchup's pre-game state. Used for writeback, the chronological split, joins, eyeballing. The trainer drops them from X by name. Rule of thumb: if it answers "which game/who" rather than "what did they bring into it," it's an ID.
        Features — everything else, and every one passes the test.

        This is where the discipline lives. Each feature must be knowable before first pitch.
        What "knowable before first pitch" means, operationally

        Temporal pin: as of the day before. Every rolling/season stat comes from feet.GD < game_day. Nothing from the game day itself (that's the dilute leak), nothing after it (that's the future leak).
        No outcome siblings. The target is total hits, so this game's PA, AB, and hits are all post-game. The label has a family, and the whole family is radioactive as features.
        Opportunity is allowed — but only the pre-game-knowable kind. Rolling PA/game, batting-order slot, starter-vs-bench, home/away: a bettor knows these. The actual PAs this game: he doesn't. Use the proxies, never the realized count.
        Numbers only. Categoricals get encoded in the forest view (CASE → 0/1 for L/R, home/away). The trainer receives numbers and does no encoding.
        NULL is legal — don't fake it. A player's first game has no prior form → NULL feature → fine, XGBoost reads the gap. Never impute, never drop a row for a NULL feature. Only a NULL target drops a row (from training — you can't learn from a labelless example).
        Participant identity is a given, not a feature. You know who is batting and pitching pre-game — that's the matchup, that's why batter/pitcher are IDs. But never feed the raw ID as a feature; the tree would just memorize individuals. Their pre-game stats are the features.

        Column order in forest
        hits (target, col 0) → GD, batter, game_pk, pitcher (IDs) → numeric features. Append new features at the end; the target stays at 0 and the trainer never changes. That ordering is the contract the rewrite reads.
        The five-second bench test, worked

        b_ba = batter season BA through the day before → accept
        b_ba including this game → reject (dilute leak — today's hits hide inside it)
        p_ba_against vs this batter's hand, through the day before → accept
        this game's AB or PA → reject (post-game sibling of the target)
        batting-order slot / starter-or-bench → accept (lineup is posted pre-game)
        home/away → accept
        rolling PA-per-game → accept (his typical opportunity)
        raw batter as a numeric feature → reject (memorization; keep it as an ID only)

    """
    XGB_MODEL_NAME = "xgb_v1"
    XGB_TABLE      = "predict_xgb_v1"

    XGB_ID_COLS  = ("GD", "batter", "game_pk", "pitcher", "at_bat_number")   # never features
    XGB_KEY_COLS = ("GD", "batter", "game_pk", "at_bat_number")              # the prediction grain (PK)

    def key_cols(self, df):        return [c for c in self.XGB_KEY_COLS if c in df.columns]

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — wired to Train XGBoost button.
    # Column-agnostic: forest col 0 = target, ID cols = bookkeeping,
    # everything else = feature. Add a feature to forest → no change here.
    # ══════════════════════════════════════════════════════════════

    def train_xgb(self, forest_table):
        out_table = f"predict_{forest_table}"
        BbDB.log(out_table, f"loading {forest_table}")
        df_all = self.load_forest(forest_table)
        if df_all.empty:
            BbDB.log(out_table, f"{forest_table} is empty")
            return
        if "game_pk" not in df_all.columns:
            return EZ.err(f"{forest_table} missing game_pk — doubleheaders break without it")

        target                     = self.target_col(df_all)
        df_train, df_predict       = self.split_to_train_and_predict(df_all, target)
        if df_train.empty:
            BbDB.log(out_table, "no training rows")
            return
        BbDB.log(out_table,
                 f"train {len(df_train)} | predict {len(df_predict)}")

        model = self.fit_model(df_train, out_table)
        self.ensure_predict_table(df_predict, out_table)
        preds = self.predict_and_write(model, df_predict, out_table)
        self.enrich_predictions(out_table)
        self.evaluate(df_predict, preds, out_table)
        self.load_model_tables(forest_table, out_table, df_train, df_predict, target)
        BbDB.update_summary(out_table)
        BbDB.log(out_table, f"{out_table} ready")
        self.refresh_pane()


    # ══════════════════════════════════════════════════════════════
    # LOAD — whatever forest holds. Drop only LABEL-less rows;
    # NULL *features* (cold starts) are KEPT — XGBoost handles them.
    # ══════════════════════════════════════════════════════════════
    def load_forest(self, forest_table):
        if not forest_table.isidentifier():
            return EZ.err(f"bad forest table name: {forest_table}")
        cols = [c[1] for c in BbDB.query(f"PRAGMA table_info({forest_table})")]
        rows = BbDB.query(f"SELECT * FROM {forest_table}")
        return pd.DataFrame(rows, columns=cols)

    # ══════════════════════════════════════════════════════════════
    # SPLIT — col 0 = target; ID cols dropped; the rest = features.
    # ══════════════════════════════════════════════════════════════
    def split_xy(self, df):
        target = self.target_col(df)
        ids = [c for c in self.XGB_ID_COLS if c in df.columns]
        features = [c for c in df.columns if c != target and c not in ids]
        X = df[features].apply(pd.to_numeric, errors="coerce") # coerce features to numeric
        return X, df[target], features

    def split_to_train_and_predict(self, df_all, target):
        """Train = all labeled rows before last GD.  Predict = last GD (actuals may be NULL for real tomorrow)."""
        max_gd     = df_all["GD"].max()
        df_train   = df_all[(df_all["GD"] <  max_gd) & (df_all[target].notna())]
        df_predict = df_all[ df_all["GD"] == max_gd]
        if df_train.empty:                                         # single day — can't hold out
            return df_all[df_all[target].notna()], pd.DataFrame(columns=df_all.columns)
        return df_train, df_predict



    # ══════════════════════════════════════════════════════════════
    # TRAIN — Poisson: hits-per-game is count data, not Gaussian.
    # Shallow + few trees: tiny dataset, guard overfit.
    # ══════════════════════════════════════════════════════════════
    def fit_model(self, df, out_table):
        import xgboost as xgb
        X, y, features = self.split_xy(df)
        objective      = self.pick_objective(y)                  # the target's own values choose the loss
        BbDB.log(out_table, f"features: {features}  objective: {objective}")
        model = xgb.XGBRegressor(
            objective     = objective,
            n_estimators  = 50,
            max_depth     = 3,
            learning_rate = 0.1,
            subsample     = 0.8,
            random_state  = 42,
            verbosity     = 0,
        )
        model.fit(X, y)
        return model
    # ══════════════════════════════════════════════════════════════
    # WRITE — predict every row, upsert into predict_xgb_v1.
    # Cast to native python so numpy scalars don't get mangled in SQLite.
    # ══════════════════════════════════════════════════════════════

    def pick_objective(self, y):
        vals = set(y.dropna().unique())
        if vals <= {0, 1}:
            return "binary:logistic"                            # is_hit per PA
        if (y.dropna() >= 0).all() and (y.dropna() % 1 == 0).all():
            return "count:poisson"                              # hits per game
        return "reg:squarederror"

    @staticmethod                                            # NEW — convention finds the target, loudly
    def target_col(df):
        hits = [c for c in df.columns if c.startswith("t_")]
        if len(hits) != 1:
            EZ.err(f"forest needs exactly one t_ column — found {hits}")
        return hits[0]


    def ensure_predict_tableOLD(self, df, out_table):
        keys    = [k for k in self.key_cols(df) if k != "GD"]
        columns = [{"name": k, "type": "INTEGER", "pk": True} for k in keys]
        columns.append({"name": "predicted", "type": "REAL", "pk": False})
        columns.append({"name": "actual",    "type": "REAL", "pk": False})
        from ipui._forms.Baseball.MgrSchema import MgrSchema
        MgrSchema.create_table(out_table, columns)


    def ensure_predict_table(self, df, out_table):
        keys    = [k for k in self.key_cols(df) if k != "GD"]
        columns = [{"name": k, "type": "INTEGER", "pk": True} for k in keys]
        columns.append({"name": "predicted",      "type": "REAL",    "pk": False})
        columns.append({"name": "actual",          "type": "REAL",    "pk": False})
        columns.append({"name": "boxscore_name",   "type": "TEXT",    "pk": False})  # NEW
        columns.append({"name": "team",             "type": "TEXT",    "pk": False})  # NEW
        columns.append({"name": "position",         "type": "TEXT",    "pk": False})  # NEW
        from ipui._forms.Baseball.MgrSchema import MgrSchema
        MgrSchema.create_table(out_table, columns)

    def enrich_predictions(self, out_table):
        """Stamp boxscore_name, team abbreviation, and position from raw_players + raw_teams."""
        sql = f"""
            UPDATE {out_table}
            SET boxscore_name = p.boxscore_name
              , team          = t.abbreviation
              , position      = p.position
            FROM raw_players p
            LEFT JOIN raw_teams t ON p.team_id = t.team_id
            WHERE {out_table}.batter = p.player_id
        """
        BbDB.execute(sql)

    # ══════════════════════════════════════════════════════════════
    # PipeMixinXGBoost.py method: predict_and_write  NEW (replaces write_predictions)
    #   Core predict+insert loop only. No table creation, no refresh.
    # ══════════════════════════════════════════════════════════════
    def predict_and_write(self, model, df, out_table):
        target  = self.target_col(df)
        keys    = self.key_cols(df)
        X, _, _ = self.split_xy(df)
        preds   = model.predict(X)
        actuals = df[target].values
        cols    = ", ".join(keys + ["predicted", "actual"])
        marks   = ", ".join("?" * (len(keys) + 2))
        sql     = f"""
            INSERT INTO {out_table} ({cols})
            VALUES ({marks})
            ON CONFLICT({", ".join(keys)}) DO UPDATE
                SET predicted = excluded.predicted
                  , actual    = excluded.actual
        """
        for *kv, pred, act in zip(*[df[k] for k in keys], preds, actuals):
            vals  = [int(v) for v in kv]
            vals += [float(pred)]
            vals += [float(act) if pd.notna(act) else None]
            BbDB.execute(sql, vals)
        return preds


    def evaluate(self, df_infer, preds, out_table):
        target  = self.target_col(df_infer)
        actuals = df_infer[target].values
        n       = len(actuals)
        if n == 0:
            return
        mae = sum(abs(float(a) - float(p)) for a, p in zip(actuals, preds)) / n
        BbDB.log(out_table, f"infer MAE {mae:.4f} across {n} rows")
        vals = set(actuals)
        if vals <= {0, 1}:
            correct = sum(1 for a, p in zip(actuals, preds) if (p >= 0.5) == (a == 1))
            BbDB.log(out_table, f"accuracy {correct}/{n} = {correct/n:.1%}")

