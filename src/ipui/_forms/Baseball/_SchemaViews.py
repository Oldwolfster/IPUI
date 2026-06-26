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
                ,game_pk                                            AS game
                ,at_bat_number                                      AS pa
                ,CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END  AS home
                ,CASE WHEN events IS NOT NULL THEN 1 ELSE 0 END     AS pa_flag
                ,CASE WHEN events IN ('single','double','triple','home_run')
                THEN 1 ELSE 0 END                             AS h
                ,CASE WHEN events IN ('walk','hit_by_pitch','sac_bunt','sac_fly'
                ,'catcher_interf','intent_walk')
                OR events IS NULL
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
            FROM raw_pitches
        """
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
                CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END                  AS home,
                CASE WHEN inning_topbot = 'Top' THEN away_team ELSE home_team END AS bat_team,
                CASE WHEN inning_topbot = 'Top' THEN home_team ELSE away_team END AS pit_team,
                CASE WHEN events IN ('single','double','triple','home_run')
                     THEN 1 ELSE 0 END                                            AS is_hit,
                CASE WHEN events IN ('walk','hit_by_pitch','sac_bunt','sac_fly',
                                     'catcher_interf','intent_walk')
                          OR events IS NULL
                     THEN 0 ELSE 1 END                                            AS is_ab,
                CASE WHEN events IN ('strikeout','strikeout_double_play')
                     THEN 1 ELSE 0 END                                            AS is_k,
                CASE WHEN events IN ('walk','intent_walk')
                     THEN 1 ELSE 0 END                                            AS is_bb,
                CASE WHEN events = 'home_run'
                     THEN 1 ELSE 0 END                                            AS is_hr,
                CASE events
                     WHEN 'single'   THEN 1
                     WHEN 'double'   THEN 2
                     WHEN 'triple'   THEN 3
                     WHEN 'home_run' THEN 4
                     ELSE 0 END                                                   AS total_bases
            FROM raw_pitches
            WHERE events IS NOT NULL;
        """

    @classmethod
    def view_pull_feet_batter(cls):
        return """
            SELECT
                GD
                ,1                                                              AS TS
                ,batter
                ,game_pk
                ,p_throws
                ,COUNT(*)                                                       AS pa
                ,SUM(is_ab)                                                     AS ab
                ,SUM(is_hit)                                                    AS hits
                ,SUM(is_hr)                                                     AS hr
                ,SUM(is_bb)                                                     AS bb
                ,SUM(is_k)                                                      AS k
                ,SUM(total_bases)                                               AS total_bases
                ,SUM(CASE WHEN launch_speed IS NOT NULL THEN launch_speed END)  AS launch_speed
                ,SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END)      AS launch_speed_cnt
                ,SUM(CASE WHEN xba          IS NOT NULL THEN xba          END)  AS xba
                ,SUM(CASE WHEN xba          IS NOT NULL THEN 1 ELSE 0 END)      AS xba_cnt
                ,SUM(woba_value)                                                AS woba_value
                ,SUM(woba_denom)                                                AS woba_denom
                ,SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END)            AS hard_hit
                ,SUM(CASE WHEN launch_speed IS NULL THEN 0
                WHEN launch_speed >= 95 THEN 1 ELSE 0 END)             AS barrel
            FROM etl_pa
            GROUP BY GD, batter, game_pk, p_throws
        """

    @classmethod
    def view_pull_feet_pitcher(cls):
        return """
            SELECT
                GD
                ,1                                                              AS TS
                ,pitcher
                , game_pk
                ,stand
                ,COUNT(*)                                                       AS bf
                ,SUM(is_ab)                                                     AS ab_against
                ,SUM(is_hit)                                                    AS hits_allowed
                ,SUM(is_hr)                                                     AS hr_allowed
                ,SUM(is_bb)                                                     AS bb_allowed
                ,SUM(is_k)                                                      AS k_pitcher
                ,SUM(total_bases)                                               AS total_bases_allowed
                ,SUM(CASE WHEN launch_speed IS NOT NULL THEN launch_speed END)  AS launch_speed
                ,SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END)      AS launch_speed_cnt
                ,SUM(CASE WHEN xba          IS NOT NULL THEN xba          END)  AS xba_allowed
                ,SUM(CASE WHEN xba          IS NOT NULL THEN 1 ELSE 0 END)      AS xba_cnt
                ,SUM(woba_value)                                                AS woba_value
                ,SUM(woba_denom)                                                AS woba_denom
                ,SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END)            AS hard_hit_allowed
                ,SUM(CASE WHEN launch_speed IS NULL THEN 0
                WHEN launch_speed >= 95 THEN 1 ELSE 0 END)                      AS barrel_allowed
            FROM etl_pa
            GROUP BY GD, pitcher, game_pk, stand
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
    def view_model_ba_baseline(cls):
        return """
            SELECT DISTINCT
                e.GD,
                e.batter,
                e.game_pk,
                b.ba                                                       AS predicted
            FROM      etl_pa      e
            JOIN      feet_batter b  ON  b.batter   = e.batter
                                      AND b.p_throws  = e.p_throws
                                      AND b.TS         = 200
            WHERE e.at_bat_number = (
                SELECT MIN(at_bat_number)
                FROM   etl_pa e2
                WHERE  e2.game_pk = e.game_pk
            )
        """

    @classmethod
    def view_batter_games(cls):
        return """
            SELECT
                GD,
                batter,
                game_pk,
                SUM(is_hit)                                                AS hits
            FROM  etl_pa
            GROUP BY GD, batter, game_pk
        """


    @classmethod
    def view_pull_forest_mixin_pitcher_season(cls):
        return """
            SELECT pitcher, stand, ba_against, p_k_pct, p_woba_against
                        FROM   feet_pitcher
                        WHERE  TS = 200
        """

    # ═══ _SchemaViews.py — pull_forest, no subqueries, same-day equi-joins ═══
    @classmethod
    def view_pull_forest(cls):
        return """
            SELECT
                m.GD,
                m.batter,
                m.game_pk,
                bg.hits          AS t_hits,
                b.ba             AS b_ba,
                p.ba_against     AS p_ba_against
            FROM      etl_matchup  m
            LEFT JOIN batter_games bg  ON bg.GD = m.GD AND bg.batter = m.batter AND bg.game_pk = m.game_pk
            LEFT JOIN feet_batter  b   ON b.batter  = m.batter  AND b.p_throws = m.p_throws AND b.TS = 200 AND b.GD = m.GD
            LEFT JOIN feet_pitcher p   ON p.pitcher = m.pitcher AND p.stand    = m.stand    AND p.TS = 200 AND p.GD = m.GD
        """

    @classmethod
    def view_update_feet_batter(cls):
        return """
            SELECT GD, TS, batter, game_pk, p_throws
                ,hits * 1.0 / NULLIF(ab, 0)          AS ba
                ,k   * 1.0 / NULLIF(pa, 0)           AS b_k_pct
                ,woba_value / NULLIF(woba_denom, 0)  AS b_woba
            FROM feet_batter
        """

    @classmethod
    def view_update_feet_pitcher(cls):
        return """
            SELECT GD, TS, pitcher,game_pk as  game_pk, stand
                                        ,hits_allowed * 1.0 / NULLIF(ab_against,  0)   AS ba_against
                                        ,k_pitcher    * 1.0 / NULLIF(bf,           0)  AS p_k_pct
                                        ,woba_value         / NULLIF(woba_denom,   0)  AS p_woba_against
                                    FROM feet_pitcher
        """
    @classmethod
    def view_pull_forest_mixin_batter_season(cls):
        return """
            SELECt batter, p_throws, ba,b_k_pct,b_woba
                                                FROM   feet_batter
                                                WHERE  TS = 200
        """

    @classmethod
    def view_pull_etl_testclone(cls):
        return """
            SELECT
                0 AS GD,
                0                                            AS batter,
                0                                            AS game_pk,
                0                                            AS at_bat_number,
                0                                            AS pitcher,
                ''                                           AS stand,
                ''                                           AS p_throws
        """

    @classmethod
    def view_pull_forest_pa_simplest(cls):
        return """
            SELECT
                            etl_pa.GD, etl_pa.batter, game_pk, at_bat_number -- i believe the key
                            ,  etl_pa.pitcher                 , is_hit AS t_hit -- the t_ identifies field AS target
                        ,1 as kiss
                        FROM etl_pa
                        LEFT JOIN pull_forest_pa_mixin_batter
        """

    @classmethod
    def view_pull_forest_pa(cls):
        return """
            SELECT
                etl_pa.GD, etl_pa.batter, game_pk, at_bat_number -- i believe the key
                ,  etl_pa.pitcher
                , is_hit AS t_hit -- the t_ identifies field AS target
                ,b_ba
                ,p_ba_against
            FROM etl_pa
            LEFT JOIN pull_forest_pa_mixin_batter
            ON  pull_forest_pa_mixin_batter.GD = etl_pa.GD
                AND  pull_forest_pa_mixin_batter.batter = etl_pa.batter
            LEFT JOIN pull_forest_pa_mixin_pitcher
            ON  pull_forest_pa_mixin_pitcher.GD = etl_pa.GD
                AND  pull_forest_pa_mixin_pitcher.pitcher = etl_pa.pitcher
        """
    @classmethod
    def view_pull_forest_pa_mixin_batter(cls):
        return """
            SELECT GD, batter
                                        ,SUM(hits) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba
                                    FROM feet_batter
                        WHERE ts=200 -- season numbers 
                                    GROUP BY gd, batter
        """

    @classmethod
    def view_pull_forest_pa_mixin_pitcher(cls):
        return """
            SELECT GD, pitcher
                ,SUM(hits_allowed) * 1.0 / NULLIF(SUM(ab_against), 0) AS p_ba_against
            FROM feet_pitcher
            WHERE ts=200 -- season numbers
            GROUP BY GD,pitcher
        """

    @classmethod
    def view_pull_etl_smally_pa(cls):
        return """
            SELECT pull_etl_smally_pa_mixin_pitches.GD
                ,pull_etl_smally_pa_mixin_pitches.batter
                ,pull_etl_smally_pa_mixin_pitches.at_bat_number  AS pa
                ,pull_etl_smally_pa_mixin_pitches.pitcher
                ,pull_etl_smally_pa_mixin_pitches.game_pk        AS game
                ,pull_etl_smally_pa_mixin_pitches.is_hit         AS h
                ,pull_etl_smally_pa_mixin_pitches.is_ab          AS ab
            FROM pull_etl_smally_pa_mixin_pitches
        """
    @classmethod
    def view_pull_etl_smally_pa_mixin_pitches(cls):
        return """
            SELECT
                GD
                ,batter
                ,game_pk
                ,at_bat_number
                ,pitcher
                ,stand
                ,p_throws
                ,home_team
                ,away_team
                ,inning_topbot
                ,events
                ,launch_speed
                ,launch_angle
                ,woba_value
                ,woba_denom
                ,estimated_ba_using_speedangle                                      AS xba
                ,CASE WHEN inning_topbot = 'Bot' THEN 1 ELSE 0 END                  AS home
                ,CASE WHEN inning_topbot = 'Top' THEN away_team ELSE home_team END  AS bat_team
                ,CASE WHEN inning_topbot = 'Top' THEN home_team ELSE away_team END  AS pit_team
                ,CASE WHEN events IN ('single','double','triple','home_run')
                THEN 1 ELSE 0 END                                              AS is_hit
                ,CASE WHEN events IN ('walk','hit_by_pitch','sac_bunt','sac_fly'
                ,'catcher_interf','intent_walk')
                OR events IS NULL
                THEN 0 ELSE 1 END                                              AS is_ab
                ,CASE WHEN events IN ('strikeout','strikeout_double_play')
                THEN 1 ELSE 0 END                                              AS is_k
                ,CASE WHEN events IN ('walk','intent_walk')
                THEN 1 ELSE 0 END                                              AS is_bb
                ,CASE WHEN events = 'home_run'
                THEN 1 ELSE 0 END                                              AS is_hr
                ,CASE events
                WHEN 'single'   THEN 1
                WHEN 'double'   THEN 2
                WHEN 'triple'   THEN 3
                WHEN 'home_run' THEN 4
                ELSE 0 END                                                     AS total_bases
            FROM raw_pitches
            WHERE events IS NOT NULL
        """

    @classmethod
    def view_pull_etl_matchup(cls):
        return """
            SELECT pitcher.GD, batters_first_bat_num.batter,  pitcher.game_pk, pitcher.pitcher
                ,pitcher.p_throws, pitcher.stand, batters_first_bat_num.first_bat as at_bat_number
            FROM etl_pa pitcher
            JOIN (
                SELECT  batter,game_pk, MIN(at_bat_number) AS first_bat
                FROM etl_pa batter
                    -- WHERE batter. batter =  514888
                GROUP BY batter, game_pk
                ) batters_first_bat_num
            ON  batters_first_bat_num.game_pk = pitcher.game_pk
                AND  batters_first_bat_num.first_bat = pitcher.at_bat_number
        """

    @classmethod
    def view_pull_forest_dart(cls):
        return """
            SELECT
                etl_starters.GD    ,etl_starters.batter    ,etl_starters.game
                --                            bg.hits        AS t_hits,                          b.ba             AS b_ba,                            --p.ba     AS p_ba
                ,pull_forest_dart_mixin_batter_season.h  AS t_h
                ,pull_forest_dart_mixin_batter_season.ba b_ba
                ,pull_forest_dart_mixin_pitcher_season.ba p_ba
            FROM      etl_starters
            
            LEFT JOIN pull_forest_dart_mixin_batter_season
            ON  pull_forest_dart_mixin_batter_season.GD = etl_starters.GD
                AND  pull_forest_dart_mixin_batter_season.batter = etl_starters.batter
            LEFT JOIN pull_forest_dart_mixin_pitcher_season
            ON  pull_forest_dart_mixin_pitcher_season.GD = etl_starters.GD
            
                -- WHERE  t_h>0
        """

    @classmethod
    def view_pull_forest_dart_mixin_batter_season(cls):
        return """
            SELECT GD, batter, ab, h, ba
            FROM   feet_dart_batter
            WHERE  TS = 200
        """
    @classmethod
    def view_pull_forest_dart_mixin_pitcher_season(cls):
        return """
            SELECT GD, pitcher, ab, h, ba
            FROM   feet_dart_pitcher
            WHERE  TS = 200
        """

    @classmethod
    def view_pull_forest_dart_pa(cls):
        return """
            SELECT
                etl_dart_pa.GD, etl_dart_pa.batter, etl_dart_pa.game, etl_dart_pa.pa ,  etl_dart_pa.pitcher -- i believe the key    ,etl_dart_pa. h  AS t_h -- the t_ identifies field AS target
                ,etl_dart_pa.h                                                                                                                        AS t_h, b_ba     ,p_ba
            FROM etl_dart_pa
            LEFT JOIN pull_forest_dart_pa_mixin_batter mx
            ON  mx.GD = etl_dart_pa.GD
                AND mx.batter = etl_dart_pa.batter
            LEFT JOIN pull_forest_dart_pa_mixin_pitcher mx_pitch
            ON  mx_pitch.GD = etl_dart_pa.GD
                AND mx_pitch.pitcher = etl_dart_pa.pitcher
                -- WHERE p_ba>0
        """
    @classmethod
    def view_pull_forest_dart_pa_mixin_batter(cls):
        return """
            SELECT GD, batter
                ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS b_ba
            FROM feet_dart_batter
            WHERE ts=200 -- season numbers
            GROUP BY gd, batter
        """
    @classmethod
    def view_pull_etl_dart_pa(cls):
        return """
            SELECT GD, batter, pitcher, game, pa, h, ab
            FROM etl_pitch
            WHERE pa_flag = 1
        """

    @classmethod
    def view_pull_feet_dart_batter(cls):
        return """
            SELECT
                                        GD
                                        ,1         AS TS
                                        ,batter
                                       -- ,game
                                        ,COUNT(*)  AS pa
                                        ,SUM(ab)   AS ab
                                        ,SUM(h)    AS h
                                    FROM etl_dart_pa
                                    GROUP BY GD, batter
        """
    @classmethod
    def view_update_feet_dart_batter(cls):
        return """
            SELECT GD, TS, batter
                            ,h * 1.0 / NULLIF(ab, 0) AS ba
                        FROM feet_dart_batter
        """

    @classmethod
    def view_pull_feet_dart_pitcher(cls):
        return """
            SELECT
                GD
                ,1         AS TS
                ,pitcher
                -- ,game
                ,COUNT(*)  AS pa
                ,SUM(ab)   AS ab
                ,SUM(h)    AS h
            FROM etl_dart_pa
            GROUP BY GD, pitcher
        """
    @classmethod
    def view_update_feet_dart_pitcher(cls):
        return """
            SELECT GD, TS, pitcher
                ,h * 1.0 / NULLIF(ab, 0) AS ba
            FROM feet_dart_pitcher
        """

    @classmethod
    def view_pull_etl_starters(cls):
        return """
            SELECT pitcher.GD, batters_first_bat_num.batter,  pitcher.game, pitcher.pitcher, pitcher.pa
                --    ,pitcher.p_throws, pitcher.stand, batters_first_bat_num.first_bat AS at_bat_number
            FROM etl_dart_pa pitcher
            JOIN (
                SELECT  GD,batter,game, MIN(pa) AS first_bat
                FROM etl_dart_pa batter
                    -- WHERE batter =543807 AND game = 822839
                GROUP BY GD,batter, game
                ) batters_first_bat_num
            ON  batters_first_bat_num.game = pitcher.game
                AND  batters_first_bat_num.first_bat = pitcher.pa
        """
    @classmethod
    def view_pull_etl_matchups(cls):
        return """
            SELECT
                p.GD
                ,p.game
                ,p.batter
                ,p.pitcher
                ,MIN(p.pa) AS pa
            FROM etl_dart_pa p
            GROUP BY
                p.GD
                ,p.game
                ,p.batter
                ,p.pitcher
        """

    @classmethod
    def view_pull_forest_dart_pa_mixin_pitcher(cls):
        return """
            SELECT GD, pitcher
                ,SUM(h) * 1.0 / NULLIF(SUM(ab), 0) AS p_ba
            FROM feet_dart_pitcher
            WHERE ts=200 -- season numbers
            GROUP BY gd, pitcher;
        """
