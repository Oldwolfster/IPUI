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
                            GD,
                            1                                                              AS TS,
                            batter,
                            p_throws,
                            COUNT(*)                                                       AS pa,
                            SUM(is_ab)                                                     AS ab,
                            SUM(is_hit)                                                    AS hits,
                            SUM(is_hr)                                                     AS hr,
                            SUM(is_bb)                                                     AS bb,
                            SUM(is_k)                                                      AS k,
                            SUM(total_bases)                                               AS total_bases,
                            SUM(CASE WHEN launch_speed IS NOT NULL THEN launch_speed END)                                                           AS launch_speed,
                            SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END)      AS launch_speed_cnt,
                            SUM(CASE WHEN xba          IS NOT NULL THEN xba          END)  AS xba,
                            SUM(CASE WHEN xba          IS NOT NULL THEN 1 ELSE 0 END)      AS xba_cnt,
                            SUM(woba_value)                                                AS woba_value,
                            SUM(woba_denom)                                                AS woba_denom,
                            SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END)           AS hard_hit,
                            SUM(CASE WHEN launch_speed IS NULL THEN 0
                                     WHEN launch_speed >= 95 THEN 1 ELSE 0 END)           AS barrel
                        FROM etl_pa
                        GROUP BY GD, batter, p_throws
        """

    @classmethod
    def view_pull_feet_pitcher(cls):
        return """
            SELECT
                GD,
                1                                                              AS TS,
                pitcher,
                stand,
                COUNT(*)                                                       AS bf,
                SUM(is_ab)                                                     AS ab_against,
                SUM(is_hit)                                                    AS hits_allowed,
                SUM(is_hr)                                                     AS hr_allowed,
                SUM(is_bb)                                                     AS bb_allowed,
                SUM(is_k)                                                      AS k_pitcher,
                SUM(total_bases)                                               AS total_bases_allowed,
                SUM(CASE WHEN launch_speed IS NOT NULL THEN launch_speed END)  AS launch_speed,
                SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END)      AS launch_speed_cnt,
                SUM(CASE WHEN xba          IS NOT NULL THEN xba          END)  AS xba_allowed,
                SUM(CASE WHEN xba          IS NOT NULL THEN 1 ELSE 0 END)      AS xba_cnt,
                SUM(woba_value)                                                AS woba_value,
                SUM(woba_denom)                                                AS woba_denom,
                SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END)           AS hard_hit_allowed,
                SUM(CASE WHEN launch_speed IS NULL THEN 0
                         WHEN launch_speed >= 95 THEN 1 ELSE 0 END)           AS barrel_allowed
            FROM etl_pa
            GROUP BY GD, pitcher, stand;
        """

    @classmethod
    def view_model_log5(cls):  # UPDATE: scale to hits-per-game
        """Log5 hit probability — output scaled to expected hits per game."""
        return """
            WITH
            league AS (
                SELECT
                    SUM(is_hit) * 1.0 / NULLIF(SUM(is_ab), 0)             AS lg_ba
                FROM etl_pa
            ),
            scores AS (
                SELECT
                    matchup.GD,
                    matchup.batter,
                    matchup.pitcher,
                    matchup.game_pk,
                    league.lg_ba,
                    batter_season.ba                                        AS batter_ba,
                    pitcher_season.ba_against                               AS pitcher_ba,
                    (batter_season.ba * pitcher_season.ba_against / league.lg_ba)
                                                                           AS hit_score,
                    ((1-batter_season.ba) * (1-pitcher_season.ba_against) / NULLIF(1-league.lg_ba, 0))
                                                                           AS out_score
                FROM      etl_matchup        matchup
                INNER JOIN pull_forest_mixin_batter_season  batter_season
                           ON  batter_season.batter   = matchup.batter
                          AND  batter_season.p_throws = matchup.p_throws
                INNER JOIN pull_forest_mixin_pitcher_season pitcher_season
                           ON  pitcher_season.pitcher = matchup.pitcher
                          AND  pitcher_season.stand   = matchup.stand
                CROSS JOIN league
            )
            SELECT
                GD,
                batter,
                pitcher,
                game_pk,
                lg_ba,
                batter_ba,
                pitcher_ba,
                hit_score,
                out_score,
                hit_score / NULLIF(hit_score + out_score, 0) * 3.8         AS predicted
            FROM scores
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
    def view_model_xgb_v1(cls):
        """XGBoost v1 — reads from predict_xgb_v1 table written by trainer."""
        return """
            SELECT
                GD,
                batter,
                game_pk,
                predicted
            FROM predict_xgb_v1
        """

        # _SchemaViews.py  class: deleteme

        # ═══ MIXIN VIEWS — building blocks, never materialized ═══

        # _SchemaViews.py  class: deleteme

    @classmethod
    def view_pull_forest_mixin_pitcher_season(cls):
        return """
            SELECT pitcher, stand, ba_against, p_k_pct, p_woba_against
                        FROM   feet_pitcher
                        WHERE  TS = 200
        """

    @classmethod
    def view_pull_forest(cls):
        return """
            SELECT
                            m.GD,
                            m.batter,
                            m.game_pk,
                            bg.hits                                                    AS hits,
                            b.ba                                                       AS b_ba,
                            p.ba_against                                               AS p_ba_against,
                            m.p_throws,
                            m.stand                                                    AS b_stand,
                            b.b_k_pct, b.b_woba, p.p_k_pct, p.p_woba_against
                        FROM      etl_matchup        m
                        LEFT JOIN batter_games                     bg ON  bg.GD      = m.GD
                                                                  AND bg.batter  = m.batter
                                                                  AND bg.game_pk = m.game_pk
                        LEFT JOIN pull_forest_mixin_batter_season  b  ON  b.batter   = m.batter
                                                                  AND b.p_throws = m.p_throws
                        LEFT JOIN pull_forest_mixin_pitcher_season p  ON  p.pitcher  = m.pitcher
                                                                  AND p.stand    = m.stand
        """

    @classmethod
    def view_update_feet_batter(cls):
        return """
            SELECT GD, TS, batter, p_throws
                ,hits * 1.0  / NULLIF(ab,         0)   AS ba
                ,k    * 1.0  / NULLIF(pa,         0)   AS b_k_pct
                ,woba_value  / NULLIF(woba_denom,  0)  AS b_woba
            FROM feet_batter
        """
    @classmethod
    def view_update_feet_pitcher(cls):
        return """
            SELECT GD, TS, pitcher, stand,
                               hits_allowed * 1.0 / NULLIF(ab_against,  0)    AS ba_against,
                               k_pitcher    * 1.0 / NULLIF(bf,           0)    AS p_k_pct,
                               woba_value         / NULLIF(woba_denom,   0)    AS p_woba_against
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
