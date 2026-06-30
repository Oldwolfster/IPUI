

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

        # ═══ etl_pitch ═══
        ('etl_pitch', 'PK batter                                  INTEGER'),
        ('etl_pitch', 'PK pitcher                                 INTEGER'),
        ('etl_pitch', 'PK pa                                      INTEGER'),
        ('etl_pitch', 'PK pitch_number                            INTEGER'),
        ('etl_pitch', 'PK b_hand                                  TEXT'),
        ('etl_pitch', 'PK p_hand                                  TEXT'),
        ('etl_pitch', '   pa_flag                                 INTEGER'),
        ('etl_pitch', '   home                                    INTEGER'),
        ('etl_pitch', '   h                                       INTEGER'),
        ('etl_pitch', '   ab                                      INTEGER'),
        ('etl_pitch', '   k                                       INTEGER'),
        ('etl_pitch', '   bb                                      INTEGER'),
        ('etl_pitch', '   hr                                      INTEGER'),
        ('etl_pitch', '   tb                                      INTEGER'),
        ('etl_pitch', '   engineered_fields_above                 INTEGER'),
        ('etl_pitch', '   pitch_type                              TEXT'),
        ('etl_pitch', '   release_speed                           REAL'),
        ('etl_pitch', '   release_pos_x                           REAL'),
        ('etl_pitch', '   release_pos_z                           REAL'),
        ('etl_pitch', '   player_name                             TEXT'),
        ('etl_pitch', '   events                                  TEXT'),
        ('etl_pitch', '   description                             TEXT'),
        ('etl_pitch', '   spin_dir                                INTEGER'),
        ('etl_pitch', '   spin_rate_deprecated                    INTEGER'),
        ('etl_pitch', '   break_angle_deprecated                  INTEGER'),
        ('etl_pitch', '   break_length_deprecated                 INTEGER'),
        ('etl_pitch', '   zone                                    INTEGER'),
        ('etl_pitch', '   des                                     TEXT'),
        ('etl_pitch', '   game_type                               TEXT'),
        ('etl_pitch', '   stand                                   TEXT'),
        ('etl_pitch', '   p_throws                                TEXT'),
        ('etl_pitch', '   home_team                               TEXT'),
        ('etl_pitch', '   away_team                               TEXT'),
        ('etl_pitch', '   type                                    TEXT'),
        ('etl_pitch', '   hit_location                            INTEGER'),
        ('etl_pitch', '   bb_type                                 TEXT'),
        ('etl_pitch', '   balls                                   INTEGER'),
        ('etl_pitch', '   strikes                                 INTEGER'),
        ('etl_pitch', '   game_year                               INTEGER'),
        ('etl_pitch', '   pfx_x                                   REAL'),
        ('etl_pitch', '   pfx_z                                   REAL'),
        ('etl_pitch', '   plate_x                                 REAL'),
        ('etl_pitch', '   plate_z                                 REAL'),
        ('etl_pitch', '   on_3b                                   INTEGER'),
        ('etl_pitch', '   on_2b                                   INTEGER'),
        ('etl_pitch', '   on_1b                                   INTEGER'),
        ('etl_pitch', '   outs_when_up                            INTEGER'),
        ('etl_pitch', '   inning                                  INTEGER'),
        ('etl_pitch', '   inning_topbot                           TEXT'),
        ('etl_pitch', '   hc_x                                    REAL'),
        ('etl_pitch', '   hc_y                                    REAL'),
        ('etl_pitch', '   tfs_deprecated                          INTEGER'),
        ('etl_pitch', '   tfs_zulu_deprecated                     INTEGER'),
        ('etl_pitch', '   umpire                                  INTEGER'),
        ('etl_pitch', '   sv_id                                   INTEGER'),
        ('etl_pitch', '   vx0                                     REAL'),
        ('etl_pitch', '   vy0                                     REAL'),
        ('etl_pitch', '   vz0                                     REAL'),
        ('etl_pitch', '   ax                                      REAL'),
        ('etl_pitch', '   ay                                      REAL'),
        ('etl_pitch', '   az                                      REAL'),
        ('etl_pitch', '   sz_top                                  REAL'),
        ('etl_pitch', '   sz_bot                                  REAL'),
        ('etl_pitch', '   hit_distance_sc                         INTEGER'),
        ('etl_pitch', '   launch_speed                            REAL'),
        ('etl_pitch', '   launch_angle                            REAL'),
        ('etl_pitch', '   effective_speed                         REAL'),
        ('etl_pitch', '   release_spin_rate                       INTEGER'),
        ('etl_pitch', '   release_extension                       REAL'),
        ('etl_pitch', '   fielder_2                               INTEGER'),
        ('etl_pitch', '   fielder_3                               INTEGER'),
        ('etl_pitch', '   fielder_4                               INTEGER'),
        ('etl_pitch', '   fielder_5                               INTEGER'),
        ('etl_pitch', '   fielder_6                               INTEGER'),
        ('etl_pitch', '   fielder_7                               INTEGER'),
        ('etl_pitch', '   fielder_8                               INTEGER'),
        ('etl_pitch', '   fielder_9                               INTEGER'),
        ('etl_pitch', '   release_pos_y                           REAL'),
        ('etl_pitch', '   woba_value                              REAL'),
        ('etl_pitch', '   woba_denom                              INTEGER'),
        ('etl_pitch', '   babip_value                             REAL'),
        ('etl_pitch', '   iso_value                               REAL'),
        ('etl_pitch', '   launch_speed_angle                      INTEGER'),
        ('etl_pitch', '   pitch_name                              TEXT'),
        ('etl_pitch', '   home_score                              INTEGER'),
        ('etl_pitch', '   away_score                              INTEGER'),
        ('etl_pitch', '   bat_score                               INTEGER'),
        ('etl_pitch', '   fld_score                               INTEGER'),
        ('etl_pitch', '   post_away_score                         INTEGER'),
        ('etl_pitch', '   post_home_score                         INTEGER'),
        ('etl_pitch', '   post_bat_score                          INTEGER'),
        ('etl_pitch', '   post_fld_score                          INTEGER'),
        ('etl_pitch', '   if_fielding_alignment                   TEXT'),
        ('etl_pitch', '   of_fielding_alignment                   TEXT'),
        ('etl_pitch', '   spin_axis                               INTEGER'),
        ('etl_pitch', '   delta_home_win_exp                      REAL'),
        ('etl_pitch', '   delta_run_exp                           REAL'),
        ('etl_pitch', '   bat_speed                               REAL'),
        ('etl_pitch', '   swing_length                            REAL'),
        ('etl_pitch', '   delta_pitcher_run_exp                   REAL'),
        ('etl_pitch', '   hyper_speed                             REAL'),
        ('etl_pitch', '   home_score_diff                         INTEGER'),
        ('etl_pitch', '   bat_score_diff                          INTEGER'),
        ('etl_pitch', '   home_win_exp                            REAL'),
        ('etl_pitch', '   bat_win_exp                             REAL'),
        ('etl_pitch', '   age_pit_legacy                          INTEGER'),
        ('etl_pitch', '   age_bat_legacy                          INTEGER'),
        ('etl_pitch', '   age_pit                                 INTEGER'),
        ('etl_pitch', '   age_bat                                 INTEGER'),
        ('etl_pitch', '   n_thruorder_pitcher                     INTEGER'),
        ('etl_pitch', '   n_priorpa_thisgame_player_at_bat        INTEGER'),
        ('etl_pitch', '   pitcher_days_since_prev_game            INTEGER'),
        ('etl_pitch', '   batter_days_since_prev_game             INTEGER'),
        ('etl_pitch', '   pitcher_days_until_next_game            INTEGER'),
        ('etl_pitch', '   batter_days_until_next_game             INTEGER'),
        ('etl_pitch', '   api_break_z_with_gravity                REAL'),
        ('etl_pitch', '   api_break_x_arm                         REAL'),
        ('etl_pitch', '   api_break_x_batter_in                   REAL'),
        ('etl_pitch', '   arm_angle                               REAL'),
        ('etl_pitch', '   attack_angle                            REAL'),
        ('etl_pitch', '   attack_direction                        REAL'),
        ('etl_pitch', '   swing_path_tilt                         REAL'),
        ('etl_pitch', '   intercept_ball_minus_batter_pos_x_inches REAL'),
        ('etl_pitch', '   intercept_ball_minus_batter_pos_y_inches REAL'),







        # -- engineered --

        # -- raw passthrough --

        # ═══ etl_pa ═══
        ('etl_pa', 'PK batter                                  INTEGER'),
        ('etl_pa', 'PK pitcher                                 INTEGER'),
        ('etl_pa', 'PK pa                                      INTEGER'),
        ('etl_pa', 'PK b_hand                                  TEXT'),
        ('etl_pa', 'PK p_hand                                  TEXT'),
        ('etl_pa', '   h                                       INTEGER'),
        ('etl_pa', '   ab                                      INTEGER'),
        ('etl_pa', 'PK home                                    INTEGER'),
        ('etl_pa', '   k                                       INTEGER'),






        # ═══ etl_starters ═══
        #('etl_starters', 'PK game                                    INTEGER'),
        ('etl_starters', 'PK batter                                  INTEGER'),
        ('etl_starters', 'PK pitcher                                 INTEGER'),
        ('etl_starters', 'PK pa                                      INTEGER'),













        # _Schema_tbl.py  forest block  REPLACE: full feature matrix schema



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
        ('_registry', '   seq         INTEGER'),

        # ═══ _track_tables ═══ many-to-many: which tables belong to which named tracks
        ('_track_tables', 'PK track       TEXT'),                        # NEW
        ('_track_tables', 'PK tbl         TEXT'),


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
        #('model_prediction', 'PK game                                INTEGER'),
        ('model_prediction', '   model_name                          TEXT'),
        ('model_prediction', '   predicted                           REAL'),
        ('model_prediction', '   actual                              REAL'),
        ('model_prediction', '   error                               REAL'),









        # ═══ feet_batter ═══
        ('feet_batter', 'PK batter                                  INTEGER'),
        ('feet_batter', '   ab                                      INTEGER'),
        ('feet_batter', '   h                                       INTEGER'),
        ('feet_batter', '   ba                                      REAL'),


        # ═══ feet_pitcher ═══
        ('feet_pitcher', 'PK pitcher                                 INTEGER'),
        ('feet_pitcher', '   ab                                      INTEGER'),
        ('feet_pitcher', '   h                                       INTEGER'),
        ('feet_pitcher', '   ba                                      REAL'),


        # ═══ forest_pa ═══
        #('forest_pa', 'PK game                                    INTEGER'),
        ('forest_pa', 'PK batter                                  INTEGER'),
        ('forest_pa', 'PK pa                                      INTEGER'),
        ('forest_pa', '   pitcher                                 INTEGER'),
        ('forest_pa', '   t_h                                     INTEGER'),
        ('forest_pa', '   b_ba                                    REAL'),
        ('forest_pa', '   p_ba                                    REAL'),




        # ═══ forest_batter ═══
        #('forest_batter', 'PK game                                    INTEGER'),
        ('forest_batter', 'PK batter                                  INTEGER'),
        ('forest_batter', '   pitcher                                 INTEGER'),
        ('forest_batter', '   t_h                                     INTEGER'),
        ('forest_batter', '   b_ba                                    REAL'),
        ('forest_batter', '   p_ba                                    REAL'),




        # ═══ feet_batter_hand ═══
        ('feet_batter_hand', 'PK batter                                  INTEGER'),
        ('feet_batter_hand', 'PK hand                                    TEXT'),
        ('feet_batter_hand', '   ab                                      INTEGER'),
        ('feet_batter_hand', '   h                                       INTEGER'),
        ('feet_batter_hand', '   ba                                      REAL'),




        # ═══ feet_pitcher_hand ═══
        ('feet_pitcher_hand', 'PK pitcher                                 INTEGER'),
        ('feet_pitcher_hand', 'PK hand                                    TEXT'),
        ('feet_pitcher_hand', '   ab                                      INTEGER'),
        ('feet_pitcher_hand', '   h                                       INTEGER'),
        ('feet_pitcher_hand', '   ba                                      REAL'),


        # ═══ forest_pa_both ═══
        ('forest_pa_both', 'PK batter                                  INTEGER'),
        ('forest_pa_both', '   pitcher                                 INTEGER'),
        ('forest_pa_both', 'PK pa                                      INTEGER'),
        ('forest_pa_both', '   t_h                                     INTEGER'),
        ('forest_pa_both', '   b_ba                                    REAL'),
        ('forest_pa_both', '   p_ba                                    REAL'),
        ('forest_pa_both', '   b_ba_hand                               REAL'),
        ('forest_pa_both', '   p_ba_hand                               REAL'),












        # ═══ forest_pa_hand ═══
        ('forest_pa_hand', 'PK batter                                  INTEGER'),
        ('forest_pa_hand', '   pitcher                                 INTEGER'),
        ('forest_pa_hand', 'PK pa                                      INTEGER'),
        ('forest_pa_hand', '   t_h                                     INTEGER'),
        ('forest_pa_hand', '   b_ba_hand                               REAL'),
        ('forest_pa_hand', '   p_ba_hand                               REAL'),




        # ═══ feet_batter_home ═══
        ('feet_batter_home', 'PK batter                                  INTEGER'),
        ('feet_batter_home', 'PK home                                    INTEGER'),
        ('feet_batter_home', '   ab                                      INTEGER'),
        ('feet_batter_home', '   h                                       INTEGER'),
        ('feet_batter_home', '   ba                                      REAL'),




        # ═══ feet_pitcher_home ═══
        ('feet_pitcher_home', 'PK pitcher                                 INTEGER'),
        ('feet_pitcher_home', 'PK home                                    INTEGER'),
        ('feet_pitcher_home', '   ab                                      INTEGER'),
        ('feet_pitcher_home', '   h                                       INTEGER'),
        ('feet_pitcher_home', '   ba                                      REAL'),


        # ═══ forest_pa_home ═══
        ('forest_pa_home', 'PK batter                                  INTEGER'),
        ('forest_pa_home', '   pitcher                                 INTEGER'),
        ('forest_pa_home', 'PK pa                                      INTEGER'),
        ('forest_pa_home', '   t_h                                     INTEGER'),
        ('forest_pa_home', '   b_ba_home                               REAL'),
        ('forest_pa_home', '   p_ba_home                               REAL'),

        ('forest_pa_all', 'PK batter                                  INTEGER'),
        ('forest_pa_all', 'PK pa                                      INTEGER'),
        ('forest_pa_all', '   pitcher                                 INTEGER'),
        ('forest_pa_all', '   t_h                                     INTEGER'),
        ('forest_pa_all', '   b_ba                                    REAL'),
        ('forest_pa_all', '   p_ba                                    REAL'),
        ('forest_pa_all', '   b_ba_hand                               REAL'),
        ('forest_pa_all', '   p_ba_hand                                REAL'),
        ('forest_pa_all', '   b_ba_home                               REAL'),
        ('forest_pa_all', '   p_ba_home                               REAL'),

        # ═══ feet_batter_hand_home ═══
        ('feet_batter_hand_home', 'PK batter                                  INTEGER'),
        ('feet_batter_hand_home', 'PK hand                                    TEXT'),
        ('feet_batter_hand_home', 'PK home                                    INTEGER'),
        ('feet_batter_hand_home', '   ab                                      INTEGER'),
        ('feet_batter_hand_home', '   h                                       INTEGER'),
        ('feet_batter_hand_home', '   ba                                      REAL'),

        # ═══ feet_pitcher_hand_home ═══
        ('feet_pitcher_hand_home', 'PK pitcher                                 INTEGER'),
        ('feet_pitcher_hand_home', 'PK hand                                    TEXT'),
        ('feet_pitcher_hand_home', 'PK home                                    INTEGER'),
        ('feet_pitcher_hand_home', '   ab                                      INTEGER'),
        ('feet_pitcher_hand_home', '   h                                       INTEGER'),
        ('feet_pitcher_hand_home', '   ba                                      REAL'),

        # ═══ forest_pa_hand_home ═══
        ('forest_pa_hand_home', 'PK batter                                  INTEGER'),
        ('forest_pa_hand_home', 'PK pa                                      INTEGER'),
        ('forest_pa_hand_home', '   pitcher                                 INTEGER'),
        ('forest_pa_hand_home', '   t_h                                     INTEGER'),
        ('forest_pa_hand_home', '   b_ba_hand_home                          REAL'),
        ('forest_pa_hand_home', '   p_ba_hand_home                          REAL'),

        # ═══ forest_pa_all2 ═══
        ('forest_pa_all2', 'PK batter                                  INTEGER'),
        ('forest_pa_all2', 'PK pa                                      INTEGER'),
        ('forest_pa_all2', '   pitcher                                 INTEGER'),
        ('forest_pa_all2', '   t_h                                     INTEGER'),
        ('forest_pa_all2', '   b_ba                                    REAL'),
        ('forest_pa_all2', '   p_ba                                    REAL'),
        ('forest_pa_all2', '   b_ba_hand                               REAL'),
        ('forest_pa_all2', '   p_ba_hand                                REAL'),
        ('forest_pa_all2', '   b_ba_home                               REAL'),
        ('forest_pa_all2', '   p_ba_home                               REAL'),
        ('forest_pa_all2', '   b_ba_hand_home                          REAL'),
        ('forest_pa_all2', '   p_ba_hand_home                          REAL'),

        # ══════════════════════════════════════════════════════════════
        # _SchemaTbl.py  — ADD all blocks below (true_dmg track)
        # ══════════════════════════════════════════════════════════════

        # ═══ etl_agg ═══
        ('etl_agg', 'PK player                                  INTEGER'),
        ('etl_agg', '   ab                                      INTEGER'),
        ('etl_agg', '   h                                       INTEGER'),
        ('etl_agg', 'PK hand                                    TEXT'),
        ('etl_agg', 'PK home                                    INTEGER'),
        ('etl_agg', '   k                                       INTEGER'),



        # ═══ feet_atom ═══
        ('feet_atom', 'PK player                                  INTEGER'),
        ('feet_atom', 'PK hand                                    TEXT'),
        ('feet_atom', 'PK home                                    INTEGER'),
        ('feet_atom', '   ab                                      INTEGER'),
        ('feet_atom', '   h                                       INTEGER'),
        ('feet_atom', '   ba                                      REAL'),
        ('feet_atom', '   k                                       INTEGER'),
        ('feet_atom', '   k_rate                                  REAL'),



        # ═══ feet_fast ═══
        ('feet_fast', 'PK player                                 INTEGER'),
        ('feet_fast', '   ab                                     INTEGER'),
        ('feet_fast', '   h                                      INTEGER'),
        ('feet_fast', '   ba                                     REAL'),
        ('feet_fast', '   k                                       INTEGER'),
        ('feet_fast', '   k_rate                                  REAL'),

        # ═══ forest_pa_dmg ═══
        ('forest_pa_dmg', 'PK batter                                  INTEGER'),
        ('forest_pa_dmg', 'PK pa                                      INTEGER'),
        ('forest_pa_dmg', '   pitcher                                 INTEGER'),
        ('forest_pa_dmg', '   t_h                                     INTEGER'),
        ('forest_pa_dmg', '   b_ba                                    REAL'),
        ('forest_pa_dmg', '   p_ba                                    REAL'),
        ('forest_pa_dmg', '   b_ba_hand                               REAL'),
        ('forest_pa_dmg', '   p_ba_hand                               REAL'),
        ('forest_pa_dmg', '   b_ba_home                               REAL'),
        ('forest_pa_dmg', '   p_ba_home                               REAL'),
        ('forest_pa_dmg', '   b_ba_hand_home                          REAL'),
        ('forest_pa_dmg', '   p_ba_hand_home                          REAL'),
        ('forest_pa_dmg', '   b_k_rate                                REAL'),
        ('forest_pa_dmg', '   p_k_rate                                REAL'),
        ('forest_pa_dmg', '   b_k_rate_hand                           REAL'),
        ('forest_pa_dmg', '   p_k_rate_hand                           REAL'),
        ('forest_pa_dmg', '   b_k_rate_home                           REAL'),
        ('forest_pa_dmg', '   p_k_rate_home                           REAL'),
        ('forest_pa_dmg', '   b_k_rate_hand_home                      REAL'),
        ('forest_pa_dmg', '   p_k_rate_hand_home                      REAL'),

    ]


