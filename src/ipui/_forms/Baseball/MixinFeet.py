# MixinFeet.py — TS roll-up for the feet (feature-store) layer
from ipui._forms.Baseball.BbDB import BbDB


class MixinFeet:

    # Trailing CALENDAR-day windows. TS=1 is the atom (already built); these sum up from it.
    TSLICE = [7, 30, 200]

    # ══════════════════════════════════════════════════════════════
    # TS ROLL-UP
    #   Sum the TS=1 atoms into trailing calendar windows, write back
    #   as TS=7/30/200. Column- AND key-agnostic: reads the table's
    #   own PK for the grain, sums everything else.
    #   CONTRACT: additive base feet tables only — no ratio columns.
    # ══════════════════════════════════════════════════════════════

    # MixinFeet.py method: roll_up_ts  New: drop derived TS rows, rebuild from all TS=1 atoms
    def roll_up_ts(self, tbl):
        keys, metrics = self.feet_grain(tbl)
        entity        = [k for k in keys if k not in ("GD", "TS")]
        BbDB.execute  ( f"DELETE FROM {tbl} WHERE TS != 1")
        for ts in self.TSLICE: BbDB.execute(self.rollup_sql(tbl, ts, entity, metrics))
        BbDB.log(tbl, f"rolled up TS {self.TSLICE} over {len(metrics)} metric cols")

    # MixinFeet.py method: feet_grain  New: PK columns = grain (keys); the rest = summable metrics
    def feet_grain(self, tbl):
        cols    = BbDB.query(f"PRAGMA table_info({tbl})")
        keys    = [c[1] for c in cols if c[5] > 0]
        metrics = [c[1] for c in cols if c[5] == 0]
        if "TS" not in keys:
            raise ValueError(f"{tbl} has no TS in its primary key — cannot roll up")
        return keys, metrics

    # MixinFeet.py method: rollup_sql  New: build the column-agnostic INSERT for one TS window
    def rollup_sql(self, tbl, ts, entity, metrics):
        cols     = ", ".join(["GD", "TS"] + entity + metrics)
        a_ent    = ", ".join(f"a.{e}"             for e in entity)
        join_ent = " ".join (f"AND b.{e} = a.{e}" for e in entity)
        sums     = ", ".join(f"SUM(b.{m}) AS {m}" for m in metrics)
        ent_csv  = ", ".join(entity)
        floor    = self.gd_minus_days("a.GD", ts)
        sql      = f"""
            INSERT INTO {tbl} ({cols})
            SELECT a.GD, {ts} AS TS, {a_ent}, {sums}
            FROM (SELECT DISTINCT GD, {ent_csv} FROM {tbl} WHERE TS = 1) a
            JOIN {tbl} b ON b.TS = 1 {join_ent}
                        AND b.GD <= a.GD
                        AND b.GD >  {floor}
            GROUP BY a.GD, {a_ent}
        """
        print(f"Sql={sql}")
        return sql

    # MixinFeet.py method: gd_minus_days  New: "GD minus N calendar days" as an integer-GD SQL fragment
    def gd_minus_days(self, gd_expr, days):
        iso = (f"substr(cast({gd_expr} as text),1,4)||'-'||"
               f"substr(cast({gd_expr} as text),5,2)||'-'||"
               f"substr(cast({gd_expr} as text),7,2)")
        return f"cast(replace(date({iso}, '-{days} days'), '-', '') as integer)"