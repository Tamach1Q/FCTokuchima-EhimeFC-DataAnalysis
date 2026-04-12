# SC_position_clustering

## フォルダ構成

```text
SC_position_clustering/
  CB/
    CB_players_raw.csv
    CB_features_raw.csv
    CB_features_preprocessed.csv
    CB_feature_definition.md
    CB_missing_report.md
  SB/
    SB_players_raw.csv
    SB_features_raw.csv
    SB_features_preprocessed.csv
    SB_feature_definition.md
    SB_missing_report.md
  CMF/
    CMF_players_raw.csv
    CMF_features_raw.csv
    CMF_features_preprocessed.csv
    CMF_feature_definition.md
    CMF_missing_report.md
  SH/
    SH_players_raw.csv
    SH_features_raw.csv
    SH_features_preprocessed.csv
    SH_feature_definition.md
    SH_missing_report.md
  ST/
    ST_players_raw.csv
    ST_features_raw.csv
    ST_features_preprocessed.csv
    ST_feature_definition.md
    ST_missing_report.md
  FW/
    FW_players_raw.csv
    FW_features_raw.csv
    FW_features_preprocessed.csv
    FW_feature_definition.md
    FW_missing_report.md
  README.md
```

## 選手数

- `CB`: 149 名
- `SB`: 123 名
- `CMF`: 32 名
- `SH`: 215 名
- `ST`: 11 名
- `FW`: 117 名

## 15変数の対応状況

- `CB`: exact=8, proxy_strong=1, proxy_medium=5, proxy_weak=1, unavailable=0
- `SB`: exact=7, proxy_strong=2, proxy_medium=5, proxy_weak=1, unavailable=0
- `CMF`: exact=5, proxy_strong=4, proxy_medium=4, proxy_weak=2, unavailable=0
- `SH`: exact=5, proxy_strong=0, proxy_medium=5, proxy_weak=5, unavailable=0
- `ST`: exact=1, proxy_strong=1, proxy_medium=4, proxy_weak=9, unavailable=0
- `FW`: exact=5, proxy_strong=1, proxy_medium=5, proxy_weak=4, unavailable=0

## 欠損・補完

- `CB`: 欠損列=aerial_duel_win_rate_pct, tackle_win_rate_pct, interceptions_per90, shot_block_proxy_per90, def_penalty_area_clearance_proxy_per90, affected_line_break_proxy_per90, line_break_proxy_per90, pass_success_rate_pct, forward_pass_success_rate_pct, successful_long_passes_per90, carry_into_30m_proxy_per90 / 補完件数=445
- `SB`: 欠損列=dropping_off_runs_proxy_per90, overlap_runs_proxy_per90, underlap_runs_proxy_per90, cross_success_rate_pct, early_cross_proxy_success_rate_pct, pa_entry_per90, tackle_win_rate_pct, cross_block_proxy_per90, pulling_half_space_runs_proxy_per90, successful_on_ball_actions_per90, attacking_third_entry_proxy_per90 / 補完件数=356
- `CMF`: 欠損列=loose_ball_gain_proxy_per90, mid_third_aerial_win_rate_proxy_pct, mid_third_tackle_win_rate_proxy_pct, out_box_shot_conversion_rate_pct, shot_on_target_rate_pct, interception_engagement_proxy_per90, pressure_engagement_proxy_per90, pass_success_rate_pct, forward_pass_success_rate_pct, short_pass_share_pct, long_pass_share_pct, forward_momentum_proxy_per90, vital_area_entry_proxy_per90, opponent_half_loose_ball_gain_share_proxy_pct / 補完件数=114
- `SH`: 欠損列=assist_cross_proxy_per90, dropping_off_runs_proxy_per90, pressure_engagement_proxy_per90, consecutive_on_ball_engagement_proxy_per90, dribble_success_rate_pct, carry_into_box_proxy_per90, cross_reception_proxy_per90, shot_conversion_rate_pct, pulling_wide_runs_proxy_per90, cross_success_rate_pct, opponent_box_ball_gain_proxy_per90, dribble_shot_proxy_per90 / 補完件数=828
- `ST`: 欠損列=carry_into_box_proxy_per90, attacking_third_touch_proxy_per90, open_space_receive_proxy_per90, coming_short_runs_proxy_per90, xthreat_received_runs_proxy_per90, pocket_entry_proxy_per90, second_assist_proxy_per90, shot_conversion_rate_pct, assist_through_pass_proxy_per90, attacking_third_tackle_win_proxy_pct, pressure_engagement_proxy_per90, dropping_off_runs_proxy_per90, first_shot_proxy_per90 / 補完件数=28
- `FW`: 欠損列=shot_conversion_rate_pct, out_box_shots_per90, box_shots_per90, shot_on_target_rate_pct, aerial_retain_proxy_pct, aerial_pass_proxy_per90, pressure_engagement_proxy_per90, consecutive_on_ball_engagement_proxy_per90, passing_option_receive_proxy_per90, xthreat_passing_option_proxy_per90, successful_forward_passes_per90, attacking_third_tackle_gain_proxy_per90, goals_per90, first_shot_proxy_per90 / 補完件数=486

## winsorize / Zスコア

- `CB`: n=149, winsorize=1/99, zscore_constant_feature=carry_into_30m_proxy_per90
- `SB`: n=123, winsorize=1/99, zscore_constant_feature=underlap_runs_proxy_per90, pulling_half_space_runs_proxy_per90, attacking_third_entry_proxy_per90
- `CMF`: n=32, winsorize=2.5/97.5, zscore_constant_feature=forward_momentum_proxy_per90, vital_area_entry_proxy_per90
- `SH`: n=215, winsorize=1/99, zscore_constant_feature=なし
- `ST`: n=11, winsorize=2.5/97.5, zscore_constant_feature=open_space_receive_proxy_per90, xthreat_received_runs_proxy_per90, pocket_entry_proxy_per90
- `FW`: n=117, winsorize=1/99, zscore_constant_feature=xthreat_passing_option_proxy_per90

## name-only 利用箇所

- `fix_position_join.py` の `normalized_only` 件数: 1
- FB 再集計 merge の name-only fallback 件数: 0
- SC 再集計 merge の name-only fallback 件数: 0

## その他

- `FB_Minutes < 300` 確認件数: 0
- 300分未満の追加除外はしていない
- `raw_*` は元値、`win_*` は winsorize 後、`z_*` はポジション内 z-score、`imputed_*` は中央値補完フラグ
- 次工程では各 `*_features_preprocessed.csv` の `z_*` 列を KMeans 入力として利用できる
- RandomForest 用には同ファイルの `raw_*` / `win_*` / `z_*` を説明変数候補として利用できる
