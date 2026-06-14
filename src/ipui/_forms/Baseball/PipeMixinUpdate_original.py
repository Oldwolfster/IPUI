from ipui._forms.Baseball.BbDB import BbDB
from ipui._forms.Baseball.MgrDT import MgrDT
from ipui.utils.EZ import EZ


class MixinUpdate:
    """
    This mixin is meant to contain all the logic for the ETL process
    """
    # ══════════════════════════════════════════════════════════════
    # Loop through all tasks in he ETL process
    # ══════════════════════════════════════════════════════════════

    # MixinUpdate.py method: update_all  New: entry point, defers to after_paint
    def update_all(self):
        self.btn_refresh_all.text = "Working..."
        self.ip.after_paint(self.update_all_now)

    def run_one_task(self):
        if not self.task_queue: return
        label, task = self.task_queue.pop(0)
        BbDB.log("pipeline", label)
        self.ip.after_paint(task)



    def update_all_now(self):
        dates = self.get_start_and_end_dates()
        if dates is None: return
        self.run_raw_layer(           dates[0], dates[1])
        self.update_layer("etl",      dates[0], dates[1])
        self.update_layer("feet",     dates[0], dates[1])
        self.update_layer("forest",   dates[0], dates[1])
        self.task_queue.append(("train XGBoost", lambda: self.train_xgb()))
        self.task_queue.append(("refresh",       lambda: self.refresh_pane()))
        self.ip.after_paint(self.run_one_task)



    def run_one_task(self):
        if not self.task_queue: return
        label, task = self.task_queue.pop(0)
        #BbDB.log("pipeline", label)
        self.ip.after_paint(self.execute_and_continue, task)

    def execute_and_continue(self, task):
        task()
        self.ip.after_paint(self.run_one_task)


    def run_raw_layer(self, start_date, end_date):
        """raw tables use sync_ methods"""
        for tbl in BbDB.tables_for_layer("raw"):
            method = getattr(self, f"sync_{tbl}", None)
            if method:
                #method(start_date, end_date)
                #BbDB.update_summary(tbl)
                self.task_queue.append((f"sync {tbl}", lambda m=method, t=tbl, s=start_date, e=end_date: (m(s, e), BbDB.update_summary(t))))
            else:  BbDB.log(tbl, "no sync method found")


    def update_layer(self, layer, start_date, end_date):
        """loop tables, dispatch each"""
        for tbl in BbDB.tables_for_layer(layer):
            #self.update_table(tbl, start_date, end_date)
            self.task_queue.append((f"update {tbl}",lambda t=tbl, s=start_date, e=end_date: self.update_table(t, s, e)))


    def update_table(self, tbl, start_date, end_date):
        """Steps for updating a derived table"""
        BbDB.log(tbl, f"updateing {tbl}")
        BbDB.upsert_from_view(tbl, start_date, end_date)
        self.roll_up_ts(tbl)
        self.run_update_views(tbl)
        BbDB.update_summary(tbl)


    # ══════════════════════════════════════════════════════════════
    # TS ROLL-UP
    # ══════════════════════════════════════════════════════════════
    def roll_up_ts(self, tbl):
        """Roll up a single table by time slice"""
        if not self.has_ts(tbl): return
        keys, metrics = self.feet_grain(tbl)
        entity        = [k for k in keys if k not in ("GD", "TS")]
        BbDB.execute(f"DELETE FROM {tbl} WHERE TS != 1")
        for ts in self.TIME_SLICES:  BbDB.execute(self.rollup_sql(tbl, ts, entity, metrics))
        BbDB.log(tbl, f"rolled up TS {self.TIME_SLICES} over {len(metrics)} metric cols")


    def has_ts(self, tbl):
        """check for TS in primary key"""
        cols = BbDB.query(f"PRAGMA table_info({tbl})")
        return any(c[1] == "TS" and c[5] > 0 for c in cols)


    def feet_grain(self, tbl):
        """"""
        cols    = BbDB.query(f"PRAGMA table_info({tbl})")
        keys    = [c[1] for c in cols if c[5] > 0]
        metrics = [c[1] for c in cols if c[5] == 0]
        if "TS" not in keys:  EZ.err(f"{tbl} has no TS in its primary key — cannot roll up")
        return keys, metrics


    def rollup_sql(self, tbl, ts, entity, metrics):
        """Create SQL to create the TS Rollup records"""
        cols     = ", ".join(["GD", "TS"] + entity + metrics)
        ent_csv  = ", ".join(entity)
        sums     = ", ".join(f"SUM({m}) AS {m}" for m in metrics)
        max_gd   = f"(SELECT MAX(GD) FROM {tbl} WHERE TS = 1)"
        floor    = self.gd_minus_days(max_gd, ts)
        sql      = f"""
            INSERT INTO {tbl} ({cols})
            SELECT 0, {ts} AS TS, {ent_csv}, {sums}
            FROM {tbl}
            WHERE TS = 1
              AND GD > {floor}
            GROUP BY {ent_csv}
        """
        #print(f"Sql={sql}")
        return sql


    # Move me to MgrDt
    def gd_minus_days(self, gd_expr, days):
        iso = (f"substr(cast({gd_expr} as text),1,4)||'-'||"
               f"substr(cast({gd_expr} as text),5,2)||'-'||"
               f"substr(cast({gd_expr} as text),7,2)")
        return f"cast(replace(date({iso}, '-{days} days'), '-', '') as integer)"


    # ══════════════════════════════════════════════════════════════
    # Update fields in derived tables
    # ══════════════════════════════════════════════════════════════
    def run_update_views(self, tbl):
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
            sql   = f"UPDATE {tbl} SET {sets} FROM {view} v WHERE {joins}"
            BbDB.execute(sql)
            BbDB.log(tbl, f"updated {set_cols} from {view}")


# ═══════════════════════════════════════════════════════════════
# Ready for next
# ═══════════════════════════════════════════════════════════════


