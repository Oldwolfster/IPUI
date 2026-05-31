# _Schema_views.py  NEW FILE  — pull_* views via convention: view_xxx() → CREATE VIEW pull_xxx

import sqlite3


class _Schema_views:

    @classmethod
    def create_all(cls, db):
        conn = sqlite3.connect(db)
        for name in sorted(dir(cls)):
            if not name.startswith("view_"): continue
            method = getattr(cls, name)
            if not callable(method):         continue
            tbl    = name[len("view_"):]
            select = method()
            conn.execute(f"CREATE VIEW IF NOT EXISTS {tbl} AS {select}")
        conn.commit()
        conn.close()

    @classmethod
    def view_pull_etl_pa(cls):
        return """
            SELECT
                GD,
                batter,
                game_pk,
                at_bat_number,
                pitcher,
                stand,
                p_throws,
                home_team,
                away_team,
                inning_topbot,
                events,
                launch_speed,
                launch_angle,
                woba_value,
                woba_denom,
                estimated_ba_using_speedangle               AS xba,
                CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END                              AS home,
                CASE WHEN inning_topbot = 'Top' THEN away_team ELSE home_team END              AS bat_team,
                CASE WHEN inning_topbot = 'Top' THEN home_team ELSE away_team END              AS pit_team,
                CASE WHEN events IN ('single','double','triple','home_run')
                     THEN 1 ELSE 0 END                                                         AS is_hit,
                CASE WHEN events IN ('walk','hit_by_pitch','sac_bunt','sac_fly',
                                     'catcher_interf','intent_walk')
                          OR events IS NULL
                     THEN 0 ELSE 1 END                                                         AS is_ab,
                CASE WHEN events IN ('strikeout','strikeout_double_play')
                     THEN 1 ELSE 0 END                                                         AS is_k,
                CASE WHEN events IN ('walk','intent_walk')
                     THEN 1 ELSE 0 END                                                         AS is_bb,
                CASE WHEN events = 'home_run'
                     THEN 1 ELSE 0 END                                                         AS is_hr,
                CASE events
                     WHEN 'single'   THEN 1
                     WHEN 'double'   THEN 2
                     WHEN 'triple'   THEN 3
                     WHEN 'home_run' THEN 4
                     ELSE 0 END                                                                AS total_bases
            FROM raw_pitches
            WHERE events IS NOT NULL;
        """

    @classmethod
    def view_pull_feet_batter(cls):
        return """
            SELECT
        GD,
        1                                                                  AS TS,
        batter,
        COUNT(*)                                                           AS pa,
        SUM(is_ab)                                                         AS ab,
        SUM(is_hit)                                                        AS hits,
        SUM(is_hr)                                                         AS hr,
        SUM(is_bb)                                                         AS bb,
        SUM(is_k)                                                          AS k,
        SUM(total_bases)                                                   AS total_bases,
        SUM(launch_speed)                                                  AS sum_launch_speed,
        SUM(xba)                                                           AS sum_xba,
        SUM(woba_value)                                                    AS sum_woba_value,
        SUM(woba_denom)                                                    AS sum_woba_denom,
        SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END)                AS hard_hit_count
    FROM etl_pa
    GROUP BY GD, batter;
        
    """