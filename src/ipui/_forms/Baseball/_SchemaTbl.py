

class _SchemaTbl:

    SCHEMA = [
        # ═══ _summary ═══
        ('_summary', 'PK tbl                                       TEXT'),
        ('_summary', '   rows                                      INTEGER'),
        ('_summary', '   cols                                      INTEGER'),
        ('_summary', '   min_gd                                    INTEGER'),
        ('_summary', '   max_gd                                    INTEGER'),


        # ═══ raw_pitches ═══ Full Statcast pitch shape. PK = (GD, game_pk, at_bat_number, pitch_number).
        # GD is auto-injected as PK col 1 by the materializer; the rest of the PK is flagged here.
        ('raw_pitches',  '   pitch_type                                  TEXT'   ),
        ('raw_pitches',  '   release_speed                               REAL'   ),
        ('raw_pitches',  '   release_pos_x                               REAL'   ),
        ('raw_pitches',  '   release_pos_z                               REAL'   ),
        ('raw_pitches',  '   player_name                                 TEXT'   ),
        ('raw_pitches',  '   batter                                      INTEGER'),
        ('raw_pitches',  '   pitcher                                     INTEGER'),
        ('raw_pitches',  '   events                                      TEXT'   ),
        ('raw_pitches',  '   description                                 TEXT'   ),
        ('raw_pitches',  '   spin_dir                                    INTEGER'),
        ('raw_pitches',  '   spin_rate_deprecated                        INTEGER'),
        ('raw_pitches',  '   break_angle_deprecated                      INTEGER'),
        ('raw_pitches',  '   break_length_deprecated                     INTEGER'),
        ('raw_pitches',  '   zone                                        INTEGER'),
        ('raw_pitches',  '   des                                         TEXT'   ),
        ('raw_pitches',  '   game_type                                   TEXT'   ),
        ('raw_pitches',  '   stand                                       TEXT'   ),
        ('raw_pitches',  '   p_throws                                    TEXT'   ),
        ('raw_pitches',  '   home_team                                   TEXT'   ),
        ('raw_pitches',  '   away_team                                   TEXT'   ),
        ('raw_pitches',  '   type                                        TEXT'   ),
        ('raw_pitches',  '   hit_location                                INTEGER'),
        ('raw_pitches',  '   bb_type                                     TEXT'   ),
        ('raw_pitches',  '   balls                                       INTEGER'),
        ('raw_pitches',  '   strikes                                     INTEGER'),
        ('raw_pitches',  '   game_year                                   INTEGER'),
        ('raw_pitches',  '   pfx_x                                       REAL'   ),
        ('raw_pitches',  '   pfx_z                                       REAL'   ),
        ('raw_pitches',  '   plate_x                                     REAL'   ),
        ('raw_pitches',  '   plate_z                                     REAL'   ),
        ('raw_pitches',  '   on_3b                                       INTEGER'),
        ('raw_pitches',  '   on_2b                                       INTEGER'),
        ('raw_pitches',  '   on_1b                                       INTEGER'),
        ('raw_pitches',  '   outs_when_up                                INTEGER'),
        ('raw_pitches',  '   inning                                      INTEGER'),
        ('raw_pitches',  '   inning_topbot                               TEXT'   ),
        ('raw_pitches',  '   hc_x                                        REAL'   ),
        ('raw_pitches',  '   hc_y                                        REAL'   ),
        ('raw_pitches',  '   tfs_deprecated                              INTEGER'),
        ('raw_pitches',  '   tfs_zulu_deprecated                         INTEGER'),
        ('raw_pitches',  '   umpire                                      INTEGER'),
        ('raw_pitches',  '   sv_id                                       INTEGER'),
        ('raw_pitches',  '   vx0                                         REAL'   ),
        ('raw_pitches',  '   vy0                                         REAL'   ),
        ('raw_pitches',  '   vz0                                         REAL'   ),
        ('raw_pitches',  '   ax                                          REAL'   ),
        ('raw_pitches',  '   ay                                          REAL'   ),
        ('raw_pitches',  '   az                                          REAL'   ),
        ('raw_pitches',  '   sz_top                                      REAL'   ),
        ('raw_pitches',  '   sz_bot                                      REAL'   ),
        ('raw_pitches',  '   hit_distance_sc                             INTEGER'),
        ('raw_pitches',  '   launch_speed                                REAL'   ),
        ('raw_pitches',  '   launch_angle                                REAL'   ),  # was INT in dump (NULL-heavy sample)
        ('raw_pitches',  '   effective_speed                             REAL'   ),
        ('raw_pitches',  '   release_spin_rate                           INTEGER'),
        ('raw_pitches',  '   release_extension                           REAL'   ),
        ('raw_pitches',  'PK game_pk                                     INTEGER'),
        ('raw_pitches',  '   fielder_2                                   INTEGER'),
        ('raw_pitches',  '   fielder_3                                   INTEGER'),
        ('raw_pitches',  '   fielder_4                                   INTEGER'),
        ('raw_pitches',  '   fielder_5                                   INTEGER'),
        ('raw_pitches',  '   fielder_6                                   INTEGER'),
        ('raw_pitches',  '   fielder_7                                   INTEGER'),
        ('raw_pitches',  '   fielder_8                                   INTEGER'),
        ('raw_pitches',  '   fielder_9                                   INTEGER'),
        ('raw_pitches',  '   release_pos_y                               REAL'   ),
        ('raw_pitches',  '   estimated_ba_using_speedangle               REAL'   ),  # xBA — was INT in dump
        ('raw_pitches',  '   estimated_woba_using_speedangle             REAL'   ),  # xwOBA — was INT in dump
        ('raw_pitches',  '   woba_value                                  REAL'   ),
        ('raw_pitches',  '   woba_denom                                  INTEGER'),
        ('raw_pitches',  '   babip_value                                 REAL'   ),  # was INT in dump
        ('raw_pitches',  '   iso_value                                   REAL'   ),  # was INT in dump
        ('raw_pitches',  '   launch_speed_angle                          INTEGER'),  # 1-6 bucket, int correct
        ('raw_pitches',  'PK at_bat_number                               INTEGER'),
        ('raw_pitches',  'PK pitch_number                                INTEGER'),
        ('raw_pitches',  '   pitch_name                                  TEXT'   ),
        ('raw_pitches',  '   home_score                                  INTEGER'),
        ('raw_pitches',  '   away_score                                  INTEGER'),
        ('raw_pitches',  '   bat_score                                   INTEGER'),
        ('raw_pitches',  '   fld_score                                   INTEGER'),
        ('raw_pitches',  '   post_away_score                             INTEGER'),
        ('raw_pitches',  '   post_home_score                             INTEGER'),
        ('raw_pitches',  '   post_bat_score                              INTEGER'),
        ('raw_pitches',  '   post_fld_score                              INTEGER'),
        ('raw_pitches',  '   if_fielding_alignment                       TEXT'   ),
        ('raw_pitches',  '   of_fielding_alignment                       TEXT'   ),
        ('raw_pitches',  '   spin_axis                                   INTEGER'),
        ('raw_pitches',  '   delta_home_win_exp                          REAL'   ),
        ('raw_pitches',  '   delta_run_exp                               REAL'   ),
        ('raw_pitches',  '   bat_speed                                   REAL'   ),  # was INT in dump
        ('raw_pitches',  '   swing_length                                REAL'   ),  # was INT in dump
        ('raw_pitches',  '   estimated_slg_using_speedangle              REAL'   ),  # xSLG — was INT in dump
        ('raw_pitches',  '   delta_pitcher_run_exp                       REAL'   ),
        ('raw_pitches',  '   hyper_speed                                 REAL'   ),
        ('raw_pitches',  '   home_score_diff                             INTEGER'),
        ('raw_pitches',  '   bat_score_diff                              INTEGER'),
        ('raw_pitches',  '   home_win_exp                                REAL'   ),
        ('raw_pitches',  '   bat_win_exp                                 REAL'   ),
        ('raw_pitches',  '   age_pit_legacy                              INTEGER'),
        ('raw_pitches',  '   age_bat_legacy                              INTEGER'),
        ('raw_pitches',  '   age_pit                                     INTEGER'),
        ('raw_pitches',  '   age_bat                                     INTEGER'),
        ('raw_pitches',  '   n_thruorder_pitcher                         INTEGER'),
        ('raw_pitches',  '   n_priorpa_thisgame_player_at_bat            INTEGER'),
        ('raw_pitches',  '   pitcher_days_since_prev_game                INTEGER'),
        ('raw_pitches',  '   batter_days_since_prev_game                 INTEGER'),
        ('raw_pitches',  '   pitcher_days_until_next_game                INTEGER'),
        ('raw_pitches',  '   batter_days_until_next_game                 INTEGER'),
        ('raw_pitches',  '   api_break_z_with_gravity                    REAL'   ),
        ('raw_pitches',  '   api_break_x_arm                             REAL'   ),
        ('raw_pitches',  '   api_break_x_batter_in                       REAL'   ),
        ('raw_pitches',  '   arm_angle                                   REAL'   ),  # was INT in dump
        ('raw_pitches',  '   attack_angle                                REAL'   ),  # was INT in dump
        ('raw_pitches',  '   attack_direction                            REAL'   ),  # was INT in dump
        ('raw_pitches',  '   swing_path_tilt                             REAL'   ),  # was INT in dump
        ('raw_pitches',  '   intercept_ball_minus_batter_pos_x_inches    REAL'   ),  # was INT in dump
        ('raw_pitches',  '   intercept_ball_minus_batter_pos_y_inches    REAL'   ),  # was INT in dump

        # ═══ raw_schedule ═══ Game-level facts.
        ('raw_schedule',  'PK game_pk                                    INTEGER'),
        ('raw_schedule',  '   game_datetime                              TEXT'   ),
        ('raw_schedule',  '   status                                     TEXT'   ),
        ('raw_schedule',  '   home_team_id                               INTEGER'),
        ('raw_schedule',  '   away_team_id                               INTEGER'),
        ('raw_schedule',  '   home_starter_id                            INTEGER'),
        ('raw_schedule',  '   away_starter_id                            INTEGER'),
        ('raw_schedule',  '   venue                                      TEXT'   ),
        ('raw_schedule',  '   game_type                                  TEXT'   ),


        ('raw_players',  'PK player_id                                  INTEGER'),
        ('raw_players',  '   full_name                                  TEXT'   ),
        ('raw_players',  '   use_name                                   TEXT'   ),
        ('raw_players',  '   boxscore_name                              TEXT'   ),
        ('raw_players',  '   position                                   TEXT'   ),
        ('raw_players',  '   bat_side                                   TEXT'   ),
        ('raw_players',  '   throw_hand                                 TEXT'   ),
        ('raw_players',  '   team_id                                    INTEGER'),
        ('raw_players',  '   jersey_number                              TEXT'   ),

        ('raw_teams',    'PK team_id                                    INTEGER'),
        ('raw_teams',    '   team_name                                  TEXT'   ),
        ('raw_teams',    '   abbreviation                               TEXT'   ),
        ('raw_teams',    '   location_name                              TEXT'   ),
        ('raw_teams',    '   league                                     TEXT'   ),
        ('raw_teams',    '   division                                   TEXT'   ),



        # ═══ etl_pa ═══ One row per plate appearance. Cleaned event grain.
        ('etl_pa',        'PK batter                                     INTEGER'),
        ('etl_pa',        'PK game_pk                                    INTEGER'),
        ('etl_pa',        'PK at_bat_number                              INTEGER'),
        ('etl_pa',        '   pitcher                                    INTEGER'),
        ('etl_pa',        '   stand                                      TEXT'   ),
        ('etl_pa',        '   p_throws                                   TEXT'   ),
        ('etl_pa',        '   home                                       INTEGER'),
        ('etl_pa',        '   bat_team                                   TEXT'   ),
        ('etl_pa',        '   pit_team                                   TEXT'   ),
        ('etl_pa',        '   park                                       TEXT'   ),
        ('etl_pa',        '   events                                     TEXT'   ),
        ('etl_pa',        '   is_hit                                     INTEGER'),
        ('etl_pa',        '   is_ab                                      INTEGER'),
        ('etl_pa',        '   is_k                                       INTEGER'),
        ('etl_pa',        '   is_bb                                      INTEGER'),
        ('etl_pa',        '   is_hr                                      INTEGER'),
        ('etl_pa',        '   total_bases                                INTEGER'),
        ('etl_pa',        '   launch_speed                               REAL'   ),
        ('etl_pa',        '   launch_angle                               REAL'   ),
        ('etl_pa',        '   xba                                        REAL'   ),
        ('etl_pa',        '   woba_value                                 REAL'   ),
        ('etl_pa',        '   woba_denom                                 INTEGER'),


        # ═══ feet_batter ═══
        ('feet_batter', 'PK batter                                  INTEGER'),
        ('feet_batter', 'PK game_pk                                    INTEGER'),
        ('feet_batter', 'PK p_throws                                TEXT'),
        ('feet_batter', '   pa                                      INTEGER'),
        ('feet_batter', '   ab                                      INTEGER'),
        ('feet_batter', '   k                                       TEXT'),
        ('feet_batter', '   hits                                    INTEGER'),
        ('feet_batter', '   ba                                      REAL'),
        ('feet_batter', '   hr                                      INTEGER'),
        ('feet_batter', '   bb                                      INTEGER'),
        ('feet_batter', '   total_bases                             INTEGER'),
        ('feet_batter', '   launch_speed                            REAL'),
        ('feet_batter', '   launch_speed_cnt                        INTEGER'),
        ('feet_batter', '   xba                                     REAL'),
        ('feet_batter', '   xba_cnt                                 INTEGER'),
        ('feet_batter', '   woba_value                              REAL'),
        ('feet_batter', '   woba_denom                              INTEGER'),
        ('feet_batter', '   hard_hit                                INTEGER'),
        ('feet_batter', '   barrel                                  INTEGER'),
        ('feet_batter', '   b_k_pct                                 REAL'),
        ('feet_batter', '   b_woba                                  REAL'),



        # ═══ feet_pitcher ═══ Mirror of feet_batter, pitcher perspective. SUMABLE ONLY.
        ('feet_pitcher', 'PK pitcher                                    INTEGER'),
        ('feet_pitcher', 'PK game_pk                                    INTEGER'),
        ('feet_pitcher', 'PK stand                                      TEXT'),
        ('feet_pitcher', '   bf                                         INTEGER'),
        ('feet_pitcher', '   ab_against                                 INTEGER'),
        ('feet_pitcher', '   hits_allowed                               INTEGER'),
        ('feet_pitcher', '   ba_against                                 REAL'),
        ('feet_pitcher', '   hr_allowed                                 INTEGER'),
        ('feet_pitcher', '   bb_allowed                                 INTEGER'),
        ('feet_pitcher', '   k_pitcher                                  INTEGER'),
        ('feet_pitcher', '   total_bases_allowed                        INTEGER'),
        ('feet_pitcher', '   launch_speed                               REAL'),
        ('feet_pitcher', '   launch_speed_cnt                           INTEGER'),
        ('feet_pitcher', '   xba_allowed                                REAL'),
        ('feet_pitcher', '   xba_cnt                                    INTEGER'),
        ('feet_pitcher', '   woba_value                                 REAL'),
        ('feet_pitcher', '   woba_denom                                 INTEGER'),
        ('feet_pitcher', '   hard_hit_allowed                           INTEGER'),
        ('feet_pitcher', '   barrel_allowed                             INTEGER'),
        ('feet_pitcher', '   p_k_pct                                   REAL'),  # NEW
        ('feet_pitcher', '   p_woba_against                            REAL'),

        # ═══ forest ═══
        #('forest', 'PK batter                                  INTEGER'),
        #('forest', 'PK game_pk                                 INTEGER'),
        #('forest', '   hits                                    INTEGER'),
        #('forest', '   b_ba                                    REAL'),
        #('forest', '   p_ba_against                            REAL'),
        #('forest', '   p_throws                                TEXT'),
        #('forest', '   b_stand                                 TEXT'),
        #('forest', '   b_k_pct                                 REAL'),
        #('forest', '   b_woba                                  REAL'),
        #('forest', '   p_k_pct                                 REAL'),
        #('forest', '   p_woba_against                          REAL'),

        ('forest', 'PK batter        INTEGER'),
        ('forest', 'PK game_pk       INTEGER'),
        ('forest', '   t_hits          INTEGER'),  # target
        ('forest', '   b_ba          REAL'),  # feature: batter season BA, as of day before
        ('forest', '   p_ba_against  REAL'),  # feature: pitcher season BA-against, as of day before

        # _Schema_tbl.py  forest block  REPLACE: full feature matrix schema

        # ═══ etl_matchup ═══
        ('etl_matchup', 'PK batter                                  INTEGER'),
        ('etl_matchup', 'PK game_pk                                 INTEGER'),
        ('etl_matchup', 'at_bat_number                              INTEGER'),
        ('etl_matchup', '   pitcher                                 INTEGER'),
        ('etl_matchup', '   stand                                   TEXT'),
        ('etl_matchup', '   p_throws                                TEXT'),


        # ═══ forest_pa_simplest ═══
        #('forest_pa_simplest', 'PK batter                                  INTEGER'),
        #('forest_pa_simplest', 'PK game_pk                                 INTEGER'),
        #('forest_pa_simplest', 'PK at_bat_number                           INTEGER'),
        #('forest_pa_simplest', '   pitcher                                 INTEGER'),
        #('forest_pa_simplest', '   t_hit                                   INTEGER'),
        #('forest_pa_simplest', '   kiss                                    INTEGER'),
        #('forest_pa_simplest', '   b_ba                                    REAL'),
        #('forest_pa_simplest', '   p_ba_against                            REAL'),
        # ═══ _registry ═══ grammar vocabulary: Entity / Metric / Context tokens + definitions
        ('_registry', 'PK kind        TEXT'),  # Entity | Metric | Context  (key-types later, "we'll see")
        ('_registry', 'PK token       TEXT'),
        ('_registry', '   definition  TEXT'),
        ('_registry', '   dtype       TEXT'),

        # ═══ forest_pa_simplest ═══
        ('forest_pa', 'PK batter                                  INTEGER'),
        ('forest_pa', 'PK game_pk                                 INTEGER'),
        ('forest_pa', 'PK at_bat_number                           INTEGER'),
        ('forest_pa', '   pitcher                                 INTEGER'),
        ('forest_pa', '   t_hit                                   INTEGER'),
        ('forest_pa', '   b_ba                                    REAL'),
        ('forest_pa', '   p_ba_against                            REAL'),

        # ═══ model_run ═══ Current model registry. One row per current model result.
        ('model_run', 'PK run_id                                    TEXT'),
        ('model_run', '   model_name                                TEXT'),
        ('model_run', '   forest_table                              TEXT'),
        ('model_run', '   predict_table                             TEXT'),
        ('model_run', '   target_field                              TEXT'),
        ('model_run', '   grain                                     TEXT'),
        ('model_run', '   train_start_gd                            INTEGER'),
        ('model_run', '   train_end_gd                              INTEGER'),
        ('model_run', '   predict_start_gd                          INTEGER'),
        ('model_run', '   predict_end_gd                            INTEGER'),
        ('model_run', '   total_predictions                         INTEGER'),
        ('model_run', '   total_mae                                 REAL'),
        ('model_run', '   feature_count                             INTEGER'),
        ('model_run', '   features_csv                              TEXT'),
        ('model_run', '   created_ds                                TEXT'),

        # ═══ model_day ═══ Predict tab day-level drill summary.
        ('model_day', 'PK run_id                                    TEXT'),
        ('model_day', '   model_name                                TEXT'),
        ('model_day', '   predictions                               INTEGER'),
        ('model_day', '   mae                                       REAL'),
        ('model_day', '   min_err                                   REAL'),
        ('model_day', '   max_err                                   REAL'),
        ('model_day', '   actual_total                              REAL'),
        ('model_day', '   predicted_total                           REAL'),

        # ═══ model_prediction ═══ Predict tab standardized batter-game detail.
        ('model_prediction', 'PK run_id                              TEXT'),
        ('model_prediction', 'PK batter                              INTEGER'),
        ('model_prediction', 'PK game_pk                             INTEGER'),
        ('model_prediction', '   model_name                          TEXT'),
        ('model_prediction', '   predicted                           REAL'),
        ('model_prediction', '   actual                              REAL'),
        ('model_prediction', '   error                               REAL'),
















        # ═══ forest_strikes ═══
        ('forest_strikes', 'PK batter                                  INTEGER'),
        ('forest_strikes', 'PK game_pk                                 INTEGER'),
        ('forest_strikes', '   t_hits                                  INTEGER'),
        ('forest_strikes', '   b_ba                                    REAL'),
        ('forest_strikes', '   p_ba_against                            REAL'),
        ('forest_strikes', '   b_k_vsL                                 INTEGER'),
        ('forest_strikes', '   b_k_vsR                                 INTEGER'),
        ('forest_strikes', '   p_k_vsL                                 INTEGER'),
        ('forest_strikes', '   p_k_vsR                                 INTEGER'),


    ]