CREATE VIEW update_feet_pitcher AS 
            SELECT GD, TS, pitcher, stand,
                               hits_allowed * 1.0 / NULLIF(ab_against,  0)    AS ba_against,
                               k_pitcher    * 1.0 / NULLIF(bf,           0)    AS p_k_pct,
                               woba_value         / NULLIF(woba_denom,   0)    AS p_woba_against
                        FROM feet_pitcher;