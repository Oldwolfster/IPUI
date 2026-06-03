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
                SUM(CASE WHEN launch_speed IS NOT NULL THEN launch_speed END)  AS launch_speed,
                SUM(CASE WHEN launch_speed IS NOT NULL THEN 1 ELSE 0 END)      AS launch_speed_cnt,
                SUM(CASE WHEN xba          IS NOT NULL THEN xba          END)  AS xba,
                SUM(CASE WHEN xba          IS NOT NULL THEN 1 ELSE 0 END)      AS xba_cnt,
                SUM(woba_value)                                                AS woba_value,
                SUM(woba_denom)                                                AS woba_denom,
                SUM(CASE WHEN launch_speed >= 95 THEN 1 ELSE 0 END)           AS hard_hit,
                SUM(CASE WHEN launch_speed IS NULL THEN 0
                         WHEN launch_speed >= 95 THEN 1 ELSE 0 END)           AS barrel
            FROM etl_pa
            GROUP BY GD, batter, p_throws;
        """


    @classmethod
    def view_pull_feet_bat2(cls):
        return """
            SELECT
                GD,
                TS,
                batter,
                p_throws,
                pa,
                ab,
                hits,
                hits * 1.0 / NULLIF(ab, 0)                             AS ba,
                hr,
                bb,
                k,
                total_bases,
                launch_speed,
                launch_speed_cnt,
                xba,
                xba_cnt,
                woba_value,
                woba_denom,
                hard_hit,
                barrel
            FROM feet_batter
        """


        # _Schema_views.py  method: view_pull_feet_pitcher  NEW: pitcher primitives from etl_pa
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

    # _Schema_views.py  method: view_pull_feet_pitch2  NEW: feet_pitcher + ba_against ratio
    @classmethod
    def view_pull_feet_pitch2(cls):
        return """
            SELECT
                GD,
                TS,
                pitcher,
                stand,
                bf,
                ab_against,
                hits_allowed,
                hits_allowed * 1.0 / NULLIF(ab_against, 0)                    AS ba_against,
                hr_allowed,
                bb_allowed,
                k_pitcher,
                total_bases_allowed,
                launch_speed,
                launch_speed_cnt,
                xba_allowed,
                xba_cnt,
                woba_value,
                woba_denom,
                hard_hit_allowed,
                barrel_allowed
            FROM feet_pitcher
        """



    # _Schema_views.py  method: view_model_log5  UPDATE: expose formula components in SELECT
    @classmethod
    def view_model_log5(cls):
        """
        Log5 hit probability model — Bill James, 1981.

        Estimates the probability of a hit given a specific batter/pitcher matchup,
        adjusting both players' batting averages relative to league average.

        Formula:
            hit_score  =  b * p / lg
            out_score  =  (1-b) * (1-p) / (1-lg)
            predicted  =  hit_score / (hit_score + out_score)

        Where:
            b   = batter BA (season to date, split by pitcher handedness)
            p   = pitcher BA-against (season to date, split by batter stance)
            lg  = league BA (season to date, all PA)

        Intuition:
            p/lg is the pitcher's multiplier — how much better or worse than average.
            b * (p/lg) is the batter's BA adjusted for that pitcher's quality.
            Dividing by (hit_score + out_score) normalizes back to a valid probability,
            since the raw scores are relative weights, not probabilities.

        Notes:
            - Pitcher is the game starter, identified as MIN(at_bat_number) per game_pk.
            - Unknown pitchers (not in feet_pitch2) fall back to lg_ba via LEFT JOIN + COALESCE.
            - Season-to-date BAs include the target day (bleeding deferred to v2).
        """
        return """
            WITH
            league AS (
                SELECT
                    SUM(is_hit) * 1.0 / NULLIF(SUM(is_ab), 0)             AS lg_ba
                FROM etl_pa
            ),
            matchups AS (
                SELECT DISTINCT
                    GD,
                    batter,
                    game_pk,
                    p_throws,
                    pitcher,
                    stand
                FROM etl_pa
                WHERE at_bat_number = (
                    SELECT MIN(at_bat_number)
                    FROM   etl_pa e2
                    WHERE  e2.game_pk = etl_pa.game_pk
                )
            ),
            batter_ba AS (
                SELECT batter, p_throws,
                    SUM(hits) * 1.0 / NULLIF(SUM(ab), 0)    AS ba
                FROM feet_bat2
                GROUP BY batter, p_throws
            ),
            pitcher_ba AS (
                SELECT pitcher, stand,
                    SUM(hits_allowed) * 1.0 / NULLIF(SUM(ab_against), 0)    AS ba_against
                FROM feet_pitch2
                GROUP BY pitcher, stand
            ),
            scores AS (
                SELECT
                    m.GD,
                    m.batter,
                    m.pitcher,
                    m.game_pk,
                    l.lg_ba,
                    b.ba                                                    AS batter_ba,
                    p.ba_against                                            AS pitcher_ba,
                    (b.ba * p.ba_against / l.lg_ba)                        AS hit_score,
                    ((1-b.ba) * (1-p.ba_against) / NULLIF(1-l.lg_ba, 0))  AS out_score
                FROM        matchups   m
                INNER JOIN  batter_ba  b  ON  b.batter   = m.batter   AND b.p_throws = m.p_throws
                INNER JOIN  pitcher_ba p  ON  p.pitcher  = m.pitcher  AND p.stand    = m.stand
                CROSS JOIN  league     l
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
                hit_score / NULLIF(hit_score + out_score, 0)               AS predicted
            FROM scores
        """



    # _Schema_views.py  method: view_model_ba_baseline  UPDATE: starter filter to match log5 grain
    @classmethod
    def view_model_ba_baseline(cls):
        return """
            SELECT DISTINCT
                e.GD,
                e.batter,
                e.game_pk,
                b.ba                                                       AS predicted
            FROM      etl_pa    e
            JOIN      feet_bat2 b  ON  b.batter   = e.batter
                                   AND b.p_throws  = e.p_throws
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
                m.stand                                                    AS b_stand
            FROM (
                SELECT DISTINCT GD, batter, game_pk, pitcher, p_throws, stand
                FROM   etl_pa
                WHERE  at_bat_number = (
                    SELECT MIN(at_bat_number)
                    FROM   etl_pa e2
                    WHERE  e2.game_pk = etl_pa.game_pk
                )
            ) m
            LEFT JOIN batter_games  bg  ON  bg.GD      = m.GD
                                        AND bg.batter  = m.batter
                                        AND bg.game_pk = m.game_pk
            LEFT JOIN (
                SELECT batter, p_throws,
                    SUM(hits) * 1.0 / NULLIF(SUM(ab), 0)                  AS ba
                FROM  feet_bat2
                GROUP BY batter, p_throws
            ) b  ON  b.batter   = m.batter
                 AND b.p_throws = m.p_throws
            LEFT JOIN (
                SELECT pitcher, stand,
                    SUM(hits_allowed) * 1.0 / NULLIF(SUM(ab_against), 0)  AS ba_against
                FROM  feet_pitch2
                GROUP BY pitcher, stand
            ) p  ON  p.pitcher = m.pitcher
                 AND p.stand   = m.stand
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