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
        self.ip.after_paint(self.loop_through_dates)


    def loop_through_dates(self):
        start_gd, target_gd = self.get_start_and_end_dates()   # raises on bad range — no None check needed
        for gd in MgrDT.gd_range(start_gd, target_gd):
            if gd == target_gd: self.run_target_day(gd)        # the held-out day
            else:               self.run_one_day(gd)           # normal training day

    def run_target_day(self,target_date):  BbDB.log("pipeline", "need to add handling for target day")

    def run_one_day(self,gd):
        BbDB.log("pipeline", f"Running Day {MgrDT.gd_to_iso(gd)}")
        self.run_raw_layer(gd)
        self.update_layer("etl",      gd)
        self.update_layer("feet",     gd)
        self.update_layer("forest",   gd)
        #self.task_queue.append(("train XGBoost", lambda: self.train_xgb()))
        #self.task_queue.append(("refresh",       lambda: self.refresh_pane()))
        self.refresh_pane()
        #self.ip.after_paint(self.run_one_task)

    def update_layer(self, layer, gd):
        """loop tables, dispatch each"""
        for tbl in BbDB.tables_for_layer(layer):
            self.update_table(tbl, gd)
            #self.task_queue.append((f"update {tbl}",lambda t=tbl, s=start_date, e=end_date: self.update_table(t, s, e)))


    def update_table(self, tbl, gd):
        """Steps for updating a derived table"""
        BbDB.log(tbl, f"updating {tbl}")
        row_count = BbDB.execute(f"delete from {tbl} where gd=?",(gd,))
        if row_count: BbDB.log(tbl, f"{tbl}: Records Deleted:{row_count}")
        BbDB.upsert_from_view(tbl, gd)
        self.roll_up_ts(tbl, gd)
        self.run_update_views(tbl, gd)
        BbDB.update_summary(tbl)


    def roll_up_ts(self, tbl, gd):
        if not BbDB.has_ts(tbl): return
        keys, metrics = self.feet_grain(tbl)
        entity        = [k for k in keys if k not in ("GD", "TS")]
        for ts in self.TIME_SLICES:  BbDB.execute(self.rollup_sql(tbl, gd, ts, entity, metrics))
        BbDB.log(tbl, f"rolled TS {self.TIME_SLICES} @ {MgrDT.gd_to_iso(gd)} over {len(metrics)} metrics")

    def feet_grain(self, tbl):
        cols    = BbDB.query(f"PRAGMA table_info({tbl})")
        keys    = [c[1] for c in cols if c[5] > 0]
        metrics = [c[1] for c in cols if c[5] == 0]
        return keys, metrics

    def rollup_sql(self, tbl, gd, ts, entity, metrics):
        cols    = ", ".join(["GD", "TS"] + entity + metrics)
        ent_csv = ", ".join(entity)
        sums    = ", ".join(f"SUM({m}) AS {m}" for m in metrics)
        floor   = MgrDT.gd_add_days(gd, -ts)               # window lower edge (exclusive)
        sql     = f"""
            INSERT INTO {tbl} ({cols})
            SELECT {gd}, {ts}, {ent_csv}, {sums}
            FROM {tbl}
            WHERE TS = 1
              AND GD >  {floor}
              AND GD <= {gd}                            
            GROUP BY {ent_csv}
        """
        #print(f"sql={sql}")
        return sql

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
    # RAW LAYER
    # ══════════════════════════════════════════════════════════════
    def run_raw_layer(self, gd):
        """raw tables use sync_ methods"""
        for tbl in BbDB.tables_for_layer("raw"):
            if self.raw_table_already_loaded(tbl,gd): continue
            method = getattr(self, f"sync_{tbl}", None)
            if method:
                method(gd)
                BbDB.update_summary(tbl)
                #self.task_queue.append((f"sync {tbl}", lambda m=method, t=tbl, s=start_date, e=end_date: (m(s, e), BbDB.update_summary(t))))
            #else:  BbDB.log(tbl, f"no sync method found for {tbl}")

    def raw_table_already_loaded(self, tbl, gd):
        if tbl=="raw_pitches": return BbDB.has_rows_on_or_past(tbl,gd)
        else:                  return  BbDB.has_rows_on_or_past(tbl)


    def BELOW_HERE_IS_OLD(self,dates):
        if dates is None: return
        self.run_raw_layer(           dates[0], dates[1])




    def run_one_task(self):
        if not self.task_queue: return
        label, task = self.task_queue.pop(0)
        #BbDB.log("pipeline", label)
        self.ip.after_paint(self.execute_and_continue, task)

    def execute_and_continue(self, task):
        task()
        self.ip.after_paint(self.run_one_task)








    # ══════════════════════════════════════════════════════════════
    # TS ROLL-UP
    # ══════════════════════════════════════════════════════════════











    # Move me to MgrDt
    def gd_minus_days(self, gd_expr, days):
        iso = (f"substr(cast({gd_expr} as text),1,4)||'-'||"
               f"substr(cast({gd_expr} as text),5,2)||'-'||"
               f"substr(cast({gd_expr} as text),7,2)")
        return f"cast(replace(date({iso}, '-{days} days'), '-', '') as integer)"


    # ══════════════════════════════════════════════════════════════
    # Update fields in derived tables
    # ══════════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════════
# Ready for next
# ═══════════════════════════════════════════════════════════════


