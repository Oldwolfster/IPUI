# PipeMixinXGBoost.py  FULL REWRITE — column-agnostic trainer; all feature logic lives in forest
import pandas as pd
from ipui._forms.Baseball.BbDB import BbDB


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
    XGB_ID_COLS    = ("GD", "batter", "game_pk", "pitcher")   # bookkeeping — never features

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — wired to Train XGBoost button.
    # Column-agnostic: forest col 0 = target, ID cols = bookkeeping,
    # everything else = feature. Add a feature to forest → no change here.
    # ══════════════════════════════════════════════════════════════
    def train_xgb(self):
        BbDB.log(self.XGB_TABLE, "loading forest")
        df = self.load_forest()
        if df.empty:
            BbDB.log(self.XGB_TABLE, "forest has no labeled rows — run Update All first")
            return
        if df.columns[0] in self.XGB_ID_COLS:                                   # pit-of-success guard
            BbDB.log(self.XGB_TABLE, f"WARNING: col 0 is '{df.columns[0]}' — is the target first in forest?")
        BbDB.log(self.XGB_TABLE, f"training on {len(df)} rows, {df.shape[1]} cols")
        model = self.fit_model(df)
        self.write_predictions(model, df)
        BbDB.log(self.XGB_TABLE, "model_xgb_v1 ready")

    # ══════════════════════════════════════════════════════════════
    # LOAD — whatever forest holds. Drop only LABEL-less rows;
    # NULL *features* (cold starts) are KEPT — XGBoost handles them.
    # ══════════════════════════════════════════════════════════════
    def load_forest(self):
        cols = [c[1] for c in BbDB.query("PRAGMA table_info(forest)")]
        rows = BbDB.query("SELECT * FROM forest")
        df   = pd.DataFrame(rows, columns=cols)
        return df[df.iloc[:, 0].notna()]                                        # col 0 = target

    # ══════════════════════════════════════════════════════════════
    # SPLIT — col 0 = target; ID cols dropped; the rest = features.
    # ══════════════════════════════════════════════════════════════
    def split_xy(self, df):
        target   = df.columns[0]
        ids      = [c for c in self.XGB_ID_COLS if c in df.columns]
        features = [c for c in df.columns if c != target and c not in ids]
        return df[features], df[target], features

    # ══════════════════════════════════════════════════════════════
    # TRAIN — Poisson: hits-per-game is count data, not Gaussian.
    # Shallow + few trees: tiny dataset, guard overfit.
    # ══════════════════════════════════════════════════════════════
    def fit_model(self, df):
        import xgboost as xgb
        X, y, features = self.split_xy(df)
        BbDB.log(self.XGB_TABLE, f"features: {features}")
        model = xgb.XGBRegressor(
            objective     = "count:poisson",
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
    def write_predictions(self, model, df):
        X, _, _ = self.split_xy(df)
        preds   = model.predict(X)
        for gd, batter, game_pk, pred in zip(df["GD"], df["batter"], df["game_pk"], preds):
            BbDB.execute("""
                INSERT INTO predict_xgb_v1 (GD, batter, game_pk, predicted)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(GD, batter, game_pk) DO UPDATE SET
                    predicted = excluded.predicted
            """, (int(gd), int(batter), int(game_pk), float(pred)))
        BbDB.update_summary(self.XGB_TABLE)
        self.refresh_pane()