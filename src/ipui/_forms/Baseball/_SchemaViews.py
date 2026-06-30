# _Schema_views.py  NEW FILE  — pull_* views via convention: view_xxx() → CREATE VIEW pull_xxx

import sqlite3


class _SchemaViews:

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
    def view_pull_etl_pitch(cls):
        return """
            SELECT     
                       *
                       ,game_pk                                            AS gameID
                       ,at_bat_number                                      AS pa
                       ,stand AS b_hand
                       ,p_throws p_hand
                       ,CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END  AS home
                       ,CASE WHEN events IS NOT NULL THEN 1 ELSE 0 END     AS pa_flag
                       ,CASE WHEN events IN ('single','double','triple','home_run')
                       THEN 1 ELSE 0 END                             AS h
                       ,CASE WHEN events IN ('walk','hit_by_pitch','sac_bunt','sac_fly'
                       ,'catcher_interf','intent_walk')
            OR         events IS NULL
                       THEN 0 ELSE 1 END                             AS ab
                       ,CASE WHEN events IN ('strikeout','strikeout_double_play')
                       THEN 1 ELSE 0 END                             AS k
                       ,CASE WHEN events IN ('walk','intent_walk')
                       THEN 1 ELSE 0 END                             AS bb
                       ,CASE WHEN events = 'home_run'
                       THEN 1 ELSE 0 END                             AS hr
                       ,CASE events
                       WHEN 'single'   THEN 1
                       WHEN 'double'   THEN 2
                       WHEN 'triple'   THEN 3
                       WHEN 'home_run' THEN 4
                       ELSE 0 END                                    AS tb
            
            FROM       raw_pitches
        """
    @classmethod
    def view_model_log5(cls):
        return """
            SELECT
                r.GD,
                r.batter,
                r.game_pk,
                (r.b * r.p / r.lg)
                / ( (r.b * r.p / r.lg)
                  + ((1 - r.b) * (1 - r.p) / NULLIF(1 - r.lg, 0)) )
                * 3.8                                                    AS predicted
            FROM (
                SELECT
                    f.GD,
                    f.batter,
                    f.game_pk,
                    COALESCE(f.b_ba,         lg.lg_ba)  AS b,
                    COALESCE(f.p_ba_against, lg.lg_ba)  AS p,
                    lg.lg_ba                            AS lg
                FROM       forest f
                CROSS JOIN (
                    SELECT SUM(is_hit) * 1.0 / NULLIF(SUM(is_ab), 0) AS lg_ba
                    FROM etl_pa
                ) lg
            ) r
        """

    @classmethod
    def view_pull_etl_starters(cls):
        return """
            SELECT     GD
                       ,batter
                       ,pitcher
                       ,pa
            
            FROM       (
                       SELECT     GD
                                  ,batter
                                  ,pitcher
                                  ,pa
                                  ,ROW_NUMBER() OVER (PARTITION BY GD, batter ORDER BY pa) AS rn
            
                       FROM       etl_pa
                       ) ranked
            
            WHERE      rn = 1
        """

    @classmethod
    def view_pull_etl_pa(cls):
        return """
            SELECT     GD, batter, pitcher, pa, h, ab,b_hand, p_hand, home, k
            
            FROM       etl_pitch
            
            WHERE      pa_flag = 1
        """
    @classmethod
    def view_pull_feet_batter(cls):
        return """
            SELECT     
                       GD
                       ,1         AS TS
                       ,batter
            -- ,game
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
            
            FROM       etl_pa
            
            GROUP BY   GD, batter
        """
    @classmethod
    def view_update_feet_batter(cls):
        return """
            SELECT     GD, TS, batter
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
            
            FROM       feet_batter
        """

    @classmethod
    def view_pull_feet_pitcher(cls):
        return """
            SELECT     
                       GD
                       ,1         AS TS
                       ,pitcher
                    -- ,game
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
            
            FROM       etl_pa
            
            GROUP BY   GD, pitcher
        """

    @classmethod
    def view_update_feet_pitcher(cls):
        return """
            SELECT     GD, TS, pitcher
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
            
            FROM       feet_pitcher
        """

    @classmethod
    def view_pull_forest_pa(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                                    AS t_h
                       ,pull_forest_pa_mixin_batter.b_ba
                       ,pull_forest_pa_mixin_pitcher.p_ba
                       ,pull_forest_pa_mixin_batter_hand.b_ba_hand
                       ,pull_forest_pa_mixin_pitcher_hand.p_ba_hand
            
            FROM       etl_pa
            
            LEFT JOIN  pull_forest_pa_mixin_batter
            ON         pull_forest_pa_mixin_batter.GD            = etl_pa.GD
            AND        pull_forest_pa_mixin_batter.batter        = etl_pa.batter
            
            LEFT JOIN  pull_forest_pa_mixin_pitcher
            ON         pull_forest_pa_mixin_pitcher.GD           = etl_pa.GD
            AND        pull_forest_pa_mixin_pitcher.pitcher      = etl_pa.pitcher
            
            LEFT JOIN  pull_forest_pa_mixin_batter_hand
            ON         pull_forest_pa_mixin_batter_hand.GD       = etl_pa.GD
            AND        pull_forest_pa_mixin_batter_hand.batter   = etl_pa.batter
            AND        pull_forest_pa_mixin_batter_hand.hand     = etl_pa.p_hand
            
            LEFT JOIN  pull_forest_pa_mixin_pitcher_hand
            ON         pull_forest_pa_mixin_pitcher_hand.GD       = etl_pa.GD
            AND        pull_forest_pa_mixin_pitcher_hand.pitcher  = etl_pa.pitcher
            AND        pull_forest_pa_mixin_pitcher_hand.hand     = etl_pa.b_hand
        """
    @classmethod
    def view_pull_forest_pa_mixin_batter(cls):
        return """
            SELECT     GD, batter
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba
            
            FROM       feet_batter
            
            WHERE      ts=200 -- season numbers
            
            GROUP BY   gd, batter
        """

    @classmethod
    def view_pull_forest_pa_mixin_pitcher(cls):
        return """
            SELECT     GD, pitcher
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba
            
            FROM       feet_pitcher
            
            WHERE      ts=200 -- season numbers
            
            GROUP BY   gd, pitcher
        """

    @classmethod
    def view_pull_forest_batter(cls):
        return """
            SELECT     
                       etl_starters.GD    ,etl_starters.batter --,etl_starters.game
                       ,pull_forest_batter_mixin_batter_game     .h t_h
                       ,pull_forest_batter_mixin_batter_season   .ba b_ba
                       ,pull_forest_batter_mixin_pitcher_season  .ba p_ba
            
            FROM       etl_starters
            
            LEFT JOIN  pull_forest_batter_mixin_batter_game
            ON         pull_forest_batter_mixin_batter_game.GD     = etl_starters.GD
            AND        pull_forest_batter_mixin_batter_game.batter = etl_starters.batter
            --AND        pull_forest_batter_mixin_batter_game.game   = etl_starters.game
            
            LEFT JOIN  pull_forest_batter_mixin_batter_season
            ON         pull_forest_batter_mixin_batter_season.GD                = etl_starters.GD
            AND        pull_forest_batter_mixin_batter_season.batter            = etl_starters.batter
            
            LEFT JOIN  pull_forest_batter_mixin_pitcher_season
            ON         pull_forest_batter_mixin_pitcher_season.GD             = etl_starters.GD
            AND        pull_forest_batter_mixin_pitcher_season.pitcher        = etl_starters.pitcher
        """
    @classmethod
    def view_pull_forest_batter_mixin_batter_game(cls):
        return """
            SELECT     
                       GD
                       ,batter
            --,game
                       ,SUM(h) AS h
            
            FROM       
                       etl_pa
            
            GROUP BY   
                       GD, batter--, game
        """
    @classmethod
    def view_pull_forest_batter_mixin_batter_season(cls):
        return """
            SELECT     GD, batter, ab, h, ba
            
            FROM       feet_batter
            
            WHERE      TS = 200
        """

    @classmethod
    def view_pull_forest_batter_mixin_pitcher_season(cls):
        return """
            SELECT     GD, pitcher, ab, h, ba
            
            FROM       feet_pitcher
            
            WHERE      TS = 200
        """

    @classmethod
    def view_pull_feet_batter_hand(cls):
        return """
            SELECT     
                       GD                       ,1         AS TS
                       ,batter                  ,p_hand AS hand
            -- ,game
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
            
            FROM       etl_pa
            
            GROUP BY   GD, batter,p_hand
        """
    @classmethod
    def view_update_feet_batter_hand(cls):
        return """
            SELECT     GD, TS, batter, hand
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
            
            FROM       feet_batter_hand
        """

    @classmethod
    def view_pull_feet_pitcher_hand(cls):
        return """
            SELECT     
                                   GD
                                   ,1         AS TS
                                   ,pitcher, b_hand AS hand
                        -- ,game
                                   ,COUNT(*)  AS pa
                                   ,SUM(ab)   AS ab
                                   ,SUM(h)    AS h
                        
                        FROM       etl_pa
                        
                        GROUP BY   GD, pitcher, b_hand
        """
    @classmethod
    def view_update_feet_pitcher_hand(cls):
        return """
            SELECT     GD, TS, pitcher,hand
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
            
            FROM       feet_pitcher_hand
        """

    @classmethod
    def view_pull_forest_pa_mixin_batter_hand(cls):
        return """
            SELECT     GD, batter, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand
            
            FROM       feet_batter_hand
            
            WHERE      ts = 200
            
            GROUP BY   GD, batter, hand
        """

    @classmethod
    def view_pull_forest_pa_mixin_pitcher_hand(cls):
        return """
            SELECT     GD, pitcher, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand
            
            FROM       feet_pitcher_hand
            
            WHERE      ts = 200
            
            GROUP BY   GD, pitcher, hand
        """

    @classmethod
    def view_pull_forest_pa_both(cls):
        return """
            SELECT     
                                   etl_pa.GD, etl_pa.batter, etl_pa.pa
                                   ,etl_pa.pitcher
                                   ,etl_pa.h                                    AS t_h
                                   ,pull_forest_pa_both_mixin_batter.b_ba
                                   ,pull_forest_pa_both_mixin_pitcher.p_ba
                                   ,pull_forest_pa_both_mixin_batter_hand.b_ba_hand
                                   ,pull_forest_pa_both_mixin_pitcher_hand.p_ba_hand
                        
                        FROM       etl_pa
                        
                        LEFT JOIN  pull_forest_pa_both_mixin_batter
                        ON         pull_forest_pa_both_mixin_batter.GD            = etl_pa.GD
                        AND        pull_forest_pa_both_mixin_batter.batter        = etl_pa.batter
                        
                        LEFT JOIN  pull_forest_pa_both_mixin_pitcher
                        ON         pull_forest_pa_both_mixin_pitcher.GD           = etl_pa.GD
                        AND        pull_forest_pa_both_mixin_pitcher.pitcher      = etl_pa.pitcher
                        
                        LEFT JOIN  pull_forest_pa_both_mixin_batter_hand
                        ON         pull_forest_pa_both_mixin_batter_hand.GD       = etl_pa.GD
                        AND        pull_forest_pa_both_mixin_batter_hand.batter   = etl_pa.batter
                        AND        pull_forest_pa_both_mixin_batter_hand.hand     = etl_pa.p_hand
                        
                        LEFT JOIN  pull_forest_pa_both_mixin_pitcher_hand
                        ON         pull_forest_pa_both_mixin_pitcher_hand.GD       = etl_pa.GD
                        AND        pull_forest_pa_both_mixin_pitcher_hand.pitcher  = etl_pa.pitcher
                        AND        pull_forest_pa_both_mixin_pitcher_hand.hand     = etl_pa.b_hand
        """
    @classmethod
    def view_pull_forest_pa_both_mixin_batter(cls):
        return """
            SELECT     GD, batter
                                   ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba
                        
                        FROM       feet_batter
                        
                        WHERE      ts=200 -- season numbers
                        
                        GROUP BY   gd, batter
        """

    @classmethod
    def view_pull_forest_pa_both_mixin_pitcher(cls):
        return """
            SELECT     GD, pitcher
                                   ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba
                        
                        FROM       feet_pitcher
                        
                        WHERE      ts=200 -- season numbers
                        
                        GROUP BY   gd, pitcher
        """

    @classmethod
    def view_pull_forest_pa_both_mixin_batter_hand(cls):
        return """
            SELECT     GD, batter, hand
                                   ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand
                        
                        FROM       feet_batter_hand
                        
                        WHERE      ts = 200
                        
                        GROUP BY   GD, batter, hand
        """

    @classmethod
    def view_pull_forest_pa_both_mixin_pitcher_hand(cls):
        return """
            SELECT     GD, pitcher, hand
                                   ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand
                        
                        FROM       feet_pitcher_hand
                        
                        WHERE      ts = 200
                        
                        GROUP BY   GD, pitcher, hand
        """

    @classmethod
    def view_pull_forest_pa_hand(cls):
        return """
            SELECT     
                                   etl_pa.GD, etl_pa.batter, etl_pa.pa
                                   ,etl_pa.pitcher
                                   ,etl_pa.h                                    AS t_h
                                   ,pull_forest_pa_hand_mixin_batter_hand.b_ba_hand
                                   ,pull_forest_pa_hand_mixin_pitcher_hand.p_ba_hand
                        
                        FROM       etl_pa
                        
                        LEFT JOIN  pull_forest_pa_hand_mixin_batter_hand
                        ON         pull_forest_pa_hand_mixin_batter_hand.GD       = etl_pa.GD
                        AND        pull_forest_pa_hand_mixin_batter_hand.batter   = etl_pa.batter
                        AND        pull_forest_pa_hand_mixin_batter_hand.hand     = etl_pa.p_hand
                        
                        LEFT JOIN  pull_forest_pa_hand_mixin_pitcher_hand
                        ON         pull_forest_pa_hand_mixin_pitcher_hand.GD       = etl_pa.GD
                        AND        pull_forest_pa_hand_mixin_pitcher_hand.pitcher  = etl_pa.pitcher
                        AND        pull_forest_pa_hand_mixin_pitcher_hand.hand     = etl_pa.b_hand
        """
    @classmethod
    def view_pull_forest_pa_hand_mixin_batter_hand(cls):
        return """
            SELECT     GD, batter, hand
                                                                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand
                                                            
                                                            FROM       feet_batter_hand
                                                            
                                                            WHERE      ts = 200
                                                            
                                                            GROUP BY   GD, batter, hand
        """

    @classmethod
    def view_pull_forest_pa_hand_mixin_pitcher_hand(cls):
        return """
            SELECT     GD, pitcher, hand
                                                                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand
                                                            
                                                            FROM       feet_pitcher_hand
                                                            
                                                            WHERE      ts = 200
                                                            
                                                            GROUP BY   GD, pitcher, hand
        """

    @classmethod
    def view_pull_feet_batter_home(cls):
        return """
            SELECT     
                       GD
                       ,1         AS TS
                       ,batter, home
            -- ,game
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
            
            FROM       etl_pa
            
            GROUP BY   GD, batter, home
        """

    @classmethod
    def view_update_feet_batter_home(cls):
        return """
            SELECT     GD, TS, batter, home
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
            
            FROM       feet_batter_home
        """

    @classmethod
    def view_pull_feet_pitcher_home(cls):
        return """
            SELECT     
                       GD
                       ,1         AS TS
                       ,pitcher, home
            -- ,game
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
            
            FROM       etl_pa
            
            GROUP BY   GD, pitcher, home
        """

    @classmethod
    def view_update_feet_pitcher_home(cls):
        return """
            SELECT     GD, TS, pitcher, home
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
            
            FROM       feet_pitcher_home
        """

    @classmethod
    def view_pull_forest_pa_home(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                                    AS t_h
                       ,pull_forest_pa_home_mixin_batter_home.b_ba_home
                       ,pull_forest_pa_home_mixin_pitcher_home.p_ba_home
            
            FROM       etl_pa
            
            LEFT JOIN  pull_forest_pa_home_mixin_batter_home
            ON         pull_forest_pa_home_mixin_batter_home.GD       = etl_pa.GD
            AND        pull_forest_pa_home_mixin_batter_home.batter   = etl_pa.batter
            AND        pull_forest_pa_home_mixin_batter_home.home     = etl_pa.home
            
            LEFT JOIN  pull_forest_pa_home_mixin_pitcher_home
            ON         pull_forest_pa_home_mixin_pitcher_home.GD       = etl_pa.GD
            AND        pull_forest_pa_home_mixin_pitcher_home.pitcher  = etl_pa.pitcher
            AND        pull_forest_pa_home_mixin_pitcher_home.home     = etl_pa.home
        """
    @classmethod
    def view_pull_forest_pa_home_mixin_batter_home(cls):
        return """
            SELECT     GD, batter, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_home
            
            FROM       feet_batter_home
            
            WHERE      ts = 200
            
            GROUP BY   GD, batter, home
        """

    @classmethod
    def view_pull_forest_pa_home_mixin_pitcher_home(cls):
        return """
            SELECT     GD, pitcher, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_home
            
            FROM       feet_pitcher_home
            
            WHERE      ts = 200
            
            GROUP BY   GD, pitcher, home
        """


    # ══════════════════════════════════════════════════════════════
    # _SchemaViews.py  — ADD all methods below
    # ══════════════════════════════════════════════════════════════

    # ── forest_pa_home: 2 mixins + pull ──────────────────────────

    # _SchemaViews.py method: view_pull_forest_pa_home_mixin_batter_home  NEW
    @classmethod
    def view_pull_forest_pa_home_mixin_batter_home(cls):
        return """
            SELECT     GD, batter, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_home

            FROM       feet_batter_home

            WHERE      ts = 200

            GROUP BY   GD, batter, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_home_mixin_pitcher_home  NEW
    @classmethod
    def view_pull_forest_pa_home_mixin_pitcher_home(cls):
        return """
            SELECT     GD, pitcher, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_home

            FROM       feet_pitcher_home

            WHERE      ts = 200

            GROUP BY   GD, pitcher, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_home  NEW
    @classmethod
    def view_pull_forest_pa_home(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                                    AS t_h
                       ,mx_bhome.b_ba_home
                       ,mx_phome.p_ba_home

            FROM       etl_pa

            LEFT JOIN  pull_forest_pa_home_mixin_batter_home mx_bhome
            ON         mx_bhome.GD          = etl_pa.GD
            AND        mx_bhome.batter      = etl_pa.batter
            AND        mx_bhome.home        = etl_pa.home

            LEFT JOIN  pull_forest_pa_home_mixin_pitcher_home mx_phome
            ON         mx_phome.GD          = etl_pa.GD
            AND        mx_phome.pitcher     = etl_pa.pitcher
            AND        mx_phome.home        = etl_pa.home
        """

    # ── forest_pa_all: 6 mixins + pull ───────────────────────────

    # _SchemaViews.py method: view_pull_forest_pa_all_mixin_batter  NEW
    @classmethod
    def view_pull_forest_pa_all_mixin_batter(cls):
        return """
            SELECT     GD, batter
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba

            FROM       feet_batter

            WHERE      ts = 200

            GROUP BY   GD, batter
        """

    # _SchemaViews.py method: view_pull_forest_pa_all_mixin_pitcher  NEW
    @classmethod
    def view_pull_forest_pa_all_mixin_pitcher(cls):
        return """
            SELECT     GD, pitcher
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba

            FROM       feet_pitcher

            WHERE      ts = 200

            GROUP BY   GD, pitcher
        """

    # _SchemaViews.py method: view_pull_forest_pa_all_mixin_batter_hand  NEW
    @classmethod
    def view_pull_forest_pa_all_mixin_batter_hand(cls):
        return """
            SELECT     GD, batter, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand

            FROM       feet_batter_hand

            WHERE      ts = 200

            GROUP BY   GD, batter, hand
        """

    # _SchemaViews.py method: view_pull_forest_pa_all_mixin_pitcher_hand  NEW
    @classmethod
    def view_pull_forest_pa_all_mixin_pitcher_hand(cls):
        return """
            SELECT     GD, pitcher, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand

            FROM       feet_pitcher_hand

            WHERE      ts = 200

            GROUP BY   GD, pitcher, hand
        """

    # _SchemaViews.py method: view_pull_forest_pa_all_mixin_batter_home  NEW
    @classmethod
    def view_pull_forest_pa_all_mixin_batter_home(cls):
        return """
            SELECT     GD, batter, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_home

            FROM       feet_batter_home

            WHERE      ts = 200

            GROUP BY   GD, batter, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_all_mixin_pitcher_home  NEW
    @classmethod
    def view_pull_forest_pa_all_mixin_pitcher_home(cls):
        return """
            SELECT     GD, pitcher, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_home

            FROM       feet_pitcher_home

            WHERE      ts = 200

            GROUP BY   GD, pitcher, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_all  NEW
    @classmethod
    def view_pull_forest_pa_all(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                          AS t_h
                       ,mx_b.b_ba
                       ,mx_p.p_ba
                       ,mx_bh.b_ba_hand
                       ,mx_ph.p_ba_hand
                       ,mx_bhome.b_ba_home
                       ,mx_phome.p_ba_home

            FROM       etl_pa

            LEFT JOIN  pull_forest_pa_all_mixin_batter mx_b
            ON         mx_b.GD              = etl_pa.GD
            AND        mx_b.batter          = etl_pa.batter

            LEFT JOIN  pull_forest_pa_all_mixin_pitcher mx_p
            ON         mx_p.GD              = etl_pa.GD
            AND        mx_p.pitcher         = etl_pa.pitcher

            LEFT JOIN  pull_forest_pa_all_mixin_batter_hand mx_bh
            ON         mx_bh.GD             = etl_pa.GD
            AND        mx_bh.batter         = etl_pa.batter
            AND        mx_bh.hand           = etl_pa.p_hand

            LEFT JOIN  pull_forest_pa_all_mixin_pitcher_hand mx_ph
            ON         mx_ph.GD             = etl_pa.GD
            AND        mx_ph.pitcher        = etl_pa.pitcher
            AND        mx_ph.hand           = etl_pa.b_hand

            LEFT JOIN  pull_forest_pa_all_mixin_batter_home mx_bhome
            ON         mx_bhome.GD          = etl_pa.GD
            AND        mx_bhome.batter      = etl_pa.batter
            AND        mx_bhome.home        = etl_pa.home

            LEFT JOIN  pull_forest_pa_all_mixin_pitcher_home mx_phome
            ON         mx_phome.GD          = etl_pa.GD
            AND        mx_phome.pitcher     = etl_pa.pitcher
            AND        mx_phome.home        = etl_pa.home
        """


    @classmethod
    def view_update_feet_batter_hand_home(cls):
        return """
            SELECT     GD, TS, batter, hand, home
                       ,h * 1.0 / NULLIF(ab, 0) AS ba

            FROM       feet_batter_hand_home
        """

    # ── feet_pitcher_hand_home: pull + update ────────────────────

    # _SchemaViews.py method: view_pull_feet_pitcher_hand_home  NEW
    @classmethod
    def view_pull_feet_pitcher_hand_home(cls):
        return """
            SELECT     GD
                       ,1         AS TS
                       ,pitcher
                       ,b_hand    AS hand
                       ,home
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h

            FROM       etl_pa

            GROUP BY   GD, pitcher, b_hand, home
        """

    # _SchemaViews.py method: view_update_feet_pitcher_hand_home  NEW
    @classmethod
    def view_update_feet_pitcher_hand_home(cls):
        return """
            SELECT     GD, TS, pitcher, hand, home
                       ,h * 1.0 / NULLIF(ab, 0) AS ba

            FROM       feet_pitcher_hand_home
        """

    # ── forest_pa_hand_home: 2 mixins + pull ─────────────────────

    # _SchemaViews.py method: view_pull_forest_pa_hand_home_mixin_batter_hand_home  NEW
    @classmethod
    def view_pull_forest_pa_hand_home_mixin_batter_hand_home(cls):
        return """
            SELECT     GD, batter, hand, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand_home

            FROM       feet_batter_hand_home

            WHERE      ts = 200

            GROUP BY   GD, batter, hand, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_hand_home_mixin_pitcher_hand_home  NEW
    @classmethod
    def view_pull_forest_pa_hand_home_mixin_pitcher_hand_home(cls):
        return """
            SELECT     GD, pitcher, hand, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand_home

            FROM       feet_pitcher_hand_home

            WHERE      ts = 200

            GROUP BY   GD, pitcher, hand, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_hand_home  NEW
    @classmethod
    def view_pull_forest_pa_hand_home(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                              AS t_h
                       ,mx_bhh.b_ba_hand_home
                       ,mx_phh.p_ba_hand_home

            FROM       etl_pa

            LEFT JOIN  pull_forest_pa_hand_home_mixin_batter_hand_home mx_bhh
            ON         mx_bhh.GD          = etl_pa.GD
            AND        mx_bhh.batter      = etl_pa.batter
            AND        mx_bhh.hand        = etl_pa.p_hand
            AND        mx_bhh.home        = etl_pa.home

            LEFT JOIN  pull_forest_pa_hand_home_mixin_pitcher_hand_home mx_phh
            ON         mx_phh.GD          = etl_pa.GD
            AND        mx_phh.pitcher     = etl_pa.pitcher
            AND        mx_phh.hand        = etl_pa.b_hand
            AND        mx_phh.home        = etl_pa.home
        """

    # ── forest_pa_all2: 8 mixins + pull ──────────────────────────

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_batter  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_batter(cls):
        return """
            SELECT     GD, batter
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba

            FROM       feet_batter

            WHERE      ts = 200

            GROUP BY   GD, batter
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_pitcher  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_pitcher(cls):
        return """
            SELECT     GD, pitcher
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba

            FROM       feet_pitcher

            WHERE      ts = 200

            GROUP BY   GD, pitcher
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_batter_hand  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_batter_hand(cls):
        return """
            SELECT     GD, batter, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand

            FROM       feet_batter_hand

            WHERE      ts = 200

            GROUP BY   GD, batter, hand
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_pitcher_hand  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_pitcher_hand(cls):
        return """
            SELECT     GD, pitcher, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand

            FROM       feet_pitcher_hand

            WHERE      ts = 200

            GROUP BY   GD, pitcher, hand
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_batter_home  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_batter_home(cls):
        return """
            SELECT     GD, batter, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_home

            FROM       feet_batter_home

            WHERE      ts = 200

            GROUP BY   GD, batter, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_pitcher_home  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_pitcher_home(cls):
        return """
            SELECT     GD, pitcher, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_home

            FROM       feet_pitcher_home

            WHERE      ts = 200

            GROUP BY   GD, pitcher, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_batter_hand_home  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_batter_hand_home(cls):
        return """
            SELECT     GD, batter, hand, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba_hand_home

            FROM       feet_batter_hand_home

            WHERE      ts = 200

            GROUP BY   GD, batter, hand, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2_mixin_pitcher_hand_home  NEW
    @classmethod
    def view_pull_forest_pa_all2_mixin_pitcher_hand_home(cls):
        return """
            SELECT     GD, pitcher, hand, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba_hand_home

            FROM       feet_pitcher_hand_home

            WHERE      ts = 200

            GROUP BY   GD, pitcher, hand, home
        """

    # _SchemaViews.py method: view_pull_forest_pa_all2  NEW
    @classmethod
    def view_pull_forest_pa_all2(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                          AS t_h
                       ,mx_b.b_ba
                       ,mx_p.p_ba
                       ,mx_bh.b_ba_hand
                       ,mx_ph.p_ba_hand
                       ,mx_bhome.b_ba_home
                       ,mx_phome.p_ba_home
                       ,mx_bhh.b_ba_hand_home
                       ,mx_phh.p_ba_hand_home

            FROM       etl_pa

            LEFT JOIN  pull_forest_pa_all2_mixin_batter mx_b
            ON         mx_b.GD              = etl_pa.GD
            AND        mx_b.batter          = etl_pa.batter

            LEFT JOIN  pull_forest_pa_all2_mixin_pitcher mx_p
            ON         mx_p.GD              = etl_pa.GD
            AND        mx_p.pitcher         = etl_pa.pitcher

            LEFT JOIN  pull_forest_pa_all2_mixin_batter_hand mx_bh
            ON         mx_bh.GD             = etl_pa.GD
            AND        mx_bh.batter         = etl_pa.batter
            AND        mx_bh.hand           = etl_pa.p_hand

            LEFT JOIN  pull_forest_pa_all2_mixin_pitcher_hand mx_ph
            ON         mx_ph.GD             = etl_pa.GD
            AND        mx_ph.pitcher        = etl_pa.pitcher
            AND        mx_ph.hand           = etl_pa.b_hand

            LEFT JOIN  pull_forest_pa_all2_mixin_batter_home mx_bhome
            ON         mx_bhome.GD          = etl_pa.GD
            AND        mx_bhome.batter      = etl_pa.batter
            AND        mx_bhome.home        = etl_pa.home

            LEFT JOIN  pull_forest_pa_all2_mixin_pitcher_home mx_phome
            ON         mx_phome.GD          = etl_pa.GD
            AND        mx_phome.pitcher     = etl_pa.pitcher
            AND        mx_phome.home        = etl_pa.home

            LEFT JOIN  pull_forest_pa_all2_mixin_batter_hand_home mx_bhh
            ON         mx_bhh.GD            = etl_pa.GD
            AND        mx_bhh.batter        = etl_pa.batter
            AND        mx_bhh.hand          = etl_pa.p_hand
            AND        mx_bhh.home          = etl_pa.home

            LEFT JOIN  pull_forest_pa_all2_mixin_pitcher_hand_home mx_phh
            ON         mx_phh.GD            = etl_pa.GD
            AND        mx_phh.pitcher       = etl_pa.pitcher
            AND        mx_phh.hand          = etl_pa.b_hand
            AND        mx_phh.home          = etl_pa.home
        """

    @classmethod
    def view_pull_feet_batter_hand_home(cls):
        return """
            SELECT     GD
                       ,1         AS TS
                       ,batter
                       ,p_hand    AS hand
                       ,home
                       ,COUNT(*)  AS pa
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
            
            FROM       etl_pa
            
            GROUP BY   GD, batter, p_hand, home
        """





    # ══════════════════════════════════════════════════════════════
    # _SchemaViews.py  — True_dmg track)
    # ══════════════════════════════════════════════════════════════

    # ── etl_agg: pull ────────────────────────────────────────────

    # _SchemaViews.py method: view_pull_etl_agg  NEW

    @classmethod
    def view_pull_etl_agg(cls):
        return """
            SELECT     GD, batter  AS player, p_hand AS hand, home
                       ,SUM(ab) AS ab
                       ,SUM(h)  AS h
                       ,SUM(k) AS k
            
            FROM       etl_pa
            
            GROUP BY   GD, batter, p_hand, home
            
            UNION      ALL
            
            SELECT     GD, pitcher AS player, b_hand AS hand, 1 - home
                       ,SUM(ab) AS ab
                       ,SUM(h)  AS h
                       ,SUM(k) AS k
            
            FROM       etl_pa
            
            GROUP BY   GD, pitcher, b_hand, home
        """

    @classmethod
    def view_pull_feet_atom(cls):
        return """
            SELECT     GD
                       ,1         AS TS
                       ,player
                       ,hand
                       ,home
                       ,ab
                       ,h
                       ,k
            
            FROM       etl_agg
        """

    @classmethod
    def view_update_feet_atom(cls):
        return """
            SELECT     GD, TS, player, hand, home
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
                       ,k * 1.0 / NULLIF(ab, 0) AS k_rate
            
            FROM       feet_atom
        """

    @classmethod
    def view_pull_feet_fast(cls):
        return """
            SELECT     GD
                       ,1         AS TS
                       ,player
                       ,SUM(ab)   AS ab
                       ,SUM(h)    AS h
                       ,SUM(k) AS k
            
            FROM       etl_agg
            
            GROUP BY   GD, player
        """

    @classmethod
    def view_update_feet_fast(cls):
        return """
            SELECT     GD, TS, player
                       ,h * 1.0 / NULLIF(ab, 0) AS ba
                       , k * 1.0 / NULLIF(ab, 0) AS k_rate
            
            FROM       feet_fast
        """

    @classmethod
    def view_pull_forest_pa_dmg_mixin_overall(cls):
        return """
            SELECT     GD, player
                       ,ba
                       ,k_rate
            
            FROM       feet_fast
            
            WHERE      ts = 200
        """
    @classmethod
    def view_pull_forest_pa_dmg_mixin_hand(cls):
        return """
            SELECT     GD, player, hand
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS ba
                       ,SUM(k) * 1.0 / NULLIF(SUM(ab), 0) AS  k_rate
            
            FROM       feet_atom
            
            WHERE      ts = 200
            
            GROUP BY   GD, player, hand
        """

    @classmethod
    def view_pull_forest_pa_dmg_mixin_home(cls):
        return """
            SELECT     GD, player, home
                       ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS ba
                       ,SUM(k) * 1.0 / NULLIF(SUM(ab), 0) AS k_rate
            
            FROM       feet_atom
            
            WHERE      ts = 200
            
            GROUP BY   GD, player, home
        """
    @classmethod
    def view_pull_forest_pa_dmg_mixin_hand_home(cls):
        return """
            SELECT     GD, player, hand, home
                       ,ba
                       , k_rate
            
            FROM       feet_atom
            
            WHERE      ts = 200
        """

    @classmethod
    def view_pull_forest_pa_dmg(cls):
        return """
            SELECT     
                       etl_pa.GD, etl_pa.batter, etl_pa.pa
                       ,etl_pa.pitcher
                       ,etl_pa.h                          AS t_h
                       ,mx_b.ba                           AS b_ba
                       ,mx_p.ba                           AS p_ba
                       ,mx_bh.ba                          AS b_ba_hand
                       ,mx_ph.ba                          AS p_ba_hand
                       ,mx_bhome.ba                       AS b_ba_home
                       ,mx_phome.ba                       AS p_ba_home
                       ,mx_bhh.ba                         AS b_ba_hand_home
                       ,mx_phh.ba                         AS p_ba_hand_home
                       ,mx_b.k_rate                      AS b_k_rate
                       ,mx_p.k_rate                      AS p_k_rate
                       ,mx_bh.k_rate                     AS b_k_rate_hand
                       ,mx_ph.k_rate                     AS p_k_rate_hand
                       ,mx_bhome.k_rate                  AS b_k_rate_home
                       ,mx_phome.k_rate                  AS p_k_rate_home
                       ,mx_bhh.k_rate                    AS b_k_rate_hand_home
                       ,mx_phh.k_rate                    AS p_k_rate_hand_home
            
            FROM       etl_pa
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_overall mx_b
            ON         mx_b.GD              = etl_pa.GD
            AND        mx_b.player          = etl_pa.batter
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_overall mx_p
            ON         mx_p.GD              = etl_pa.GD
            AND        mx_p.player          = etl_pa.pitcher
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_hand mx_bh
            ON         mx_bh.GD             = etl_pa.GD
            AND        mx_bh.player         = etl_pa.batter
            AND        mx_bh.hand           = etl_pa.p_hand
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_hand mx_ph
            ON         mx_ph.GD             = etl_pa.GD
            AND        mx_ph.player         = etl_pa.pitcher
            AND        mx_ph.hand           = etl_pa.b_hand
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_home mx_bhome
            ON         mx_bhome.GD          = etl_pa.GD
            AND        mx_bhome.player      = etl_pa.batter
            AND        mx_bhome.home        = etl_pa.home
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_home mx_phome
            ON         mx_phome.GD          = etl_pa.GD
            AND        mx_phome.player      = etl_pa.pitcher
            AND        mx_phome.home        = 1 - etl_pa.home
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_hand_home mx_bhh
            ON         mx_bhh.GD            = etl_pa.GD
            AND        mx_bhh.player        = etl_pa.batter
            AND        mx_bhh.hand          = etl_pa.p_hand
            AND        mx_bhh.home          = etl_pa.home
            
            LEFT JOIN  pull_forest_pa_dmg_mixin_hand_home mx_phh
            ON         mx_phh.GD            = etl_pa.GD
            AND        mx_phh.player        = etl_pa.pitcher
            AND        mx_phh.hand          = etl_pa.b_hand
            AND        mx_phh.home          = 1 - etl_pa.home
        """
