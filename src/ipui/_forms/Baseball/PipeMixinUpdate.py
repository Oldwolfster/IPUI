from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrDT import MgrDT
from ipui.utils.EZ import EZ


class PipeMixinUpdate:
    """
    This mixin is meant to contain all the logic for the ETL process
    """
    # ══════════════════════════════════════════════════════════════
    # Loop through all tasks in he ETL process
    # ══════════════════════════════════════════════════════════════

    # MixinUpdate.py method: update_all  New: entry point, defers to after_paint
    def run_all(self):
        self.update_btn_txt = "Working..."
        self.refresh_pane()
        self.ip.drip(self.loop_through_dates)
        self.ip.drip_when_dry(self.reset_run_btn)

    def reset_run_btn(self):
        self.update_btn_txt = "Run All"
        self.active_table   = None
        self.refresh_pane()


    def loop_through_dates(self):
        start_gd, target_gd = self.get_start_and_end_dates()
        for gd in MgrDT.gd_range(start_gd, target_gd):
            if gd == target_gd: self.run_target_day(gd)
            else:               self.run_one_day(gd)
        self.ip.drip(self.sync_raw_players, start_gd)               # was direct call
        self.ip.drip(BbDB.update_summary, "raw_players")            # was direct call
        self.run_predict_layer(gd)

    def run_target_day(self,target_date):
        """Eventually we switch this to switchable from in pitches for research to tomorrows matchup for real use"""
        self.run_one_day(target_date)


    def run_one_day(self,gd):
        self.run_raw_layer(gd)
        self.update_layer("etl",      gd)
        self.update_layer("feet",     gd)
        self.update_layer("forest",   gd)
        #self.task_queue.append(("train XGBoost", lambda: self.train_xgb()))

    def update_layer(self, layer, gd):
        """loop tables, dispatch each"""
        for tbl in BbDB.tables_for_layer(layer):
            self.ip.drip(self.logthe_table, tbl, gd)
            self.ip.drip(self.update_table, tbl, gd)

    def logthe_table(self, tbl, gd):
        self.active_table = tbl
        #print(f">>> testing123 logthe_table: {tbl} for GD={gd}")

        BbDB.log(tbl, f"deleting/inserting for GD={gd}")
        self.refresh_pane()

    def update_table(self, tbl, gd):
        """Steps for updating a derived table"""
        row_count = BbDB.execute(f"delete from {tbl} where gd=?",(gd,))
        if row_count: BbDB.log(tbl, f"{tbl}: Records Deleted:{row_count}")
        BbDB.upsert_from_view(tbl, gd)
        self.roll_up_ts(tbl, gd)
        self.run_update_views(tbl, gd)
        BbDB.update_summary(tbl)
        self.refresh_pane()

    def feet_grain(self, tbl):
        cols    = BbDB.query(f"PRAGMA table_info({tbl})")
        keys    = [c[1] for c in cols if c[5] > 0]
        metrics = [c[1] for c in cols if c[5] == 0]
        return keys, metrics

    def roll_up_ts(self, tbl, gd):
        if not BbDB.has_ts(tbl): return
        keys, metrics = self.feet_grain(tbl)
        entity        = [k for k in keys if k not in self.ROLLUP_EXCLUDE]
        for ts in self.TIME_SLICES:
            sql= self.rollup_sql(tbl, gd, ts, entity, metrics)
            #BbDB.log(tbl,f"rollup sql = P{sql}")
            BbDB.execute(sql)

        BbDB.log(tbl, f"rolled TS {self.TIME_SLICES} @ {MgrDT.gd_to_iso(gd)} over {len(metrics)} metrics")

    # PipeMixinUpdate.py method: rollup_sql  Update: simplified, no game_pk hack
    def rollup_sql(self, tbl, gd, ts, entity, metrics):
        """Rollup TS=1 rows into a higher timeslice for the given entity columns."""
        ent_csv = ", ".join(entity)
        sums    = ", ".join(f"SUM({m}) AS {m}" for m in metrics)
        floor   = MgrDT.gd_add_days(gd, -ts)
        return f"""
            INSERT INTO {tbl} (GD, TS, {ent_csv}, {", ".join(metrics)})
            SELECT {gd}, {ts}, {ent_csv}, {sums}
            FROM {tbl}
            WHERE TS = 1
              AND GD >  {floor}
              AND GD < {gd}
            GROUP BY {ent_csv}
        """

    def run_update_views(self, tbl, gd):
        """discover update_{tbl}* views, UPDATE...FROM"""
        views = [r[0] for r in BbDB.query(
            "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE ?",
            (f"update_{tbl}%",)
        )]
        if not views: return
        pk_cols  = [r[1] for r in BbDB.query(f"PRAGMA table_info({tbl})") if r[5] > 0]
        tbl_cols = set(r[1] for r in BbDB.query(f"PRAGMA table_info({tbl})"))
        for view in sorted(views):
            view_cols = [r[1] for r in BbDB.query(f"PRAGMA table_info({view})")]
            set_cols  = [c for c in view_cols if c in tbl_cols and c not in pk_cols]
            if not set_cols:
                BbDB.log(tbl, f"{view} — no matching columns")
                continue
            sets  = ", ".join(f"{c} = v.{c}" for c in set_cols)
            joins = " AND ".join(f"{tbl}.{pk} = v.{pk}" for pk in pk_cols)
            sql   = f"UPDATE {tbl} SET {sets} FROM {view} v WHERE {joins}  AND {tbl}.GD = ?"
            BbDB.execute(sql, (gd,))
            print  (f"sql={sql}")
            BbDB.log(tbl, f"updated {set_cols} from {view}")

    # ══════════════════════════════════════════════════════════════
    # XGB Prediction
    # ══════════════════════════════════════════════════════════════
    def run_predict_layer(self, gd):
        for tbl in self.valid_forest_tables_for_predict_layer():
            self.ip.drip(self.train_forest_table, tbl, gd)
        self.ip.drip(self.load_log5_model)

    def valid_forest_tables_for_predict_layer(self):
        selected  = list(getattr(self, "FOREST_TABLES_TO_TRAIN", []))
        available = BbDB.tables_for_layer("forest")
        missing   = [t for t in selected if t not in available]
        if missing: BbDB.log("predict", f"skipping missing forest table(s): {', '.join(missing)}")
        return [t for t in selected if t in available]


    # PipeMixinUpdate.py method: train_forest_table  NEW: drip-safe XGB wrapper
    def train_forest_table(self, tbl, gd):
        BbDB.log("predict", f"training {tbl} @ {MgrDT.gd_to_iso(gd)}")
        self.train_xgb(tbl)

