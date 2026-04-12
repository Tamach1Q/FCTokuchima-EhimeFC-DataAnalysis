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

## 最終採用概要

- 全体: proxy_weak 削除=22, 置換=10
- `CB`: 採用=10 / dropped=6 / unavailable=1 / exact=10, proxy_strong=0, proxy_medium=0, proxy_weak=0 / proxy_weak削除=1, 置換=0
- `SB`: 採用=10 / dropped=7 / unavailable=3 / exact=10, proxy_strong=0, proxy_medium=0, proxy_weak=0 / proxy_weak削除=1, 置換=1
- `CMF`: 採用=8 / dropped=9 / unavailable=2 / exact=8, proxy_strong=0, proxy_medium=0, proxy_weak=0 / proxy_weak削除=2, 置換=0
- `SH`: 採用=9 / dropped=9 / unavailable=2 / exact=9, proxy_strong=0, proxy_medium=0, proxy_weak=0 / proxy_weak削除=5, 置換=2
- `ST`: 採用=7 / dropped=11 / unavailable=3 / exact=7, proxy_strong=0, proxy_medium=0, proxy_weak=0 / proxy_weak削除=9, 置換=4
- `FW`: 採用=10 / dropped=9 / unavailable=1 / exact=10, proxy_strong=0, proxy_medium=0, proxy_weak=0 / proxy_weak削除=4, 置換=3

## 最終採用列

- `CB`: aerial_duel_win_rate_pct, tackle_win_rate_pct, interceptions_per90, blocks_per90, clearances_per90, pass_success_rate_pct, successful_forward_passes_per90, successful_long_passes_per90, medaccel_count_full_all_per_match, highaccel_count_full_all_per_match
- `SB`: running_distance_full_all_per_match, hi_distance_full_all_per_match, sprint_count_full_all_per_match, crosses_per90, cross_success_rate_pct, pa_entry_per90, tackle_win_rate_pct, blocks_per90, forward_long_pass_success_rate_pct, regain_within_5s_per90
- `CMF`: running_distance_full_all_per_match, ball_gains_per90, interceptions_per90, pass_success_rate_pct, forward_pass_success_rate_pct, short_pass_share_pct, long_pass_share_pct, opponent_half_gain_share_pct
- `SH`: sprint_distance_full_all_per_match, hsr_count_full_all_per_match, dribble_success_rate_pct, crosses_per90, cross_success_rate_pct, last_passes_per90, pa_entry_per90, shot_conversion_rate_pct, regain_within_5s_per90
- `ST`: shot_conversion_rate_pct, box_shots_per90, goals_per90, sprint_count_full_all_per_match, last_passes_per90, successful_through_passes_per90, attacking_third_gains_per90
- `FW`: shot_conversion_rate_pct, out_box_shots_per90, box_shots_per90, shot_on_target_rate_pct, goals_per90, aerial_wins_per90, successful_forward_passes_per90, last_passes_per90, attacking_third_gains_per90, sprint_count_full_all_per_match

## 欠損・補完

- `CB`: 欠損列=aerial_duel_win_rate_pct, tackle_win_rate_pct, interceptions_per90, blocks_per90, clearances_per90, pass_success_rate_pct, successful_forward_passes_per90, successful_long_passes_per90 / 補完件数=320 / 補完率=21.5%
- `SB`: 欠損列=crosses_per90, cross_success_rate_pct, pa_entry_per90, tackle_win_rate_pct, blocks_per90, forward_long_pass_success_rate_pct, regain_within_5s_per90 / 補完件数=217 / 補完率=17.6%
- `CMF`: 欠損列=ball_gains_per90, interceptions_per90, pass_success_rate_pct, forward_pass_success_rate_pct, short_pass_share_pct, long_pass_share_pct, opponent_half_gain_share_pct / 補完件数=56 / 補完率=21.9%
- `SH`: 欠損列=dribble_success_rate_pct, crosses_per90, cross_success_rate_pct, last_passes_per90, pa_entry_per90, shot_conversion_rate_pct, regain_within_5s_per90 / 補完件数=483 / 補完率=25.0%
- `ST`: 欠損列=shot_conversion_rate_pct, box_shots_per90, goals_per90, last_passes_per90, successful_through_passes_per90, attacking_third_gains_per90 / 補完件数=6 / 補完率=7.8%
- `FW`: 欠損列=shot_conversion_rate_pct, out_box_shots_per90, box_shots_per90, shot_on_target_rate_pct, goals_per90, aerial_wins_per90, successful_forward_passes_per90, last_passes_per90, attacking_third_gains_per90 / 補完件数=315 / 補完率=26.9%

## winsorize / Zスコア

- `CB`: n=149, winsorize=1/99, zscore_constant_feature=なし
- `SB`: n=123, winsorize=1/99, zscore_constant_feature=なし
- `CMF`: n=32, winsorize=2.5/97.5, zscore_constant_feature=なし
- `SH`: n=215, winsorize=1/99, zscore_constant_feature=なし
- `ST`: n=11, winsorize=2.5/97.5, zscore_constant_feature=なし
- `FW`: n=117, winsorize=1/99, zscore_constant_feature=なし

## KMeans 前評価

- `CB`: ready / n=149 / vars=10 / exact=10, proxy_strong=0, proxy_medium=0, proxy_weak=0 / 定数列=なし / exact 中心で定数列もなく、前処理後にそのまま投入可能
- `SB`: ready / n=123 / vars=10 / exact=10, proxy_strong=0, proxy_medium=0, proxy_weak=0 / 定数列=なし / exact 中心で定数列もなく、前処理後にそのまま投入可能
- `CMF`: caution / n=32 / vars=8 / exact=8, proxy_strong=0, proxy_medium=0, proxy_weak=0 / 定数列=なし / サンプル数が少ない
- `SH`: caution / n=215 / vars=9 / exact=9, proxy_strong=0, proxy_medium=0, proxy_weak=0 / 定数列=なし / 欠損補完率が高い
- `ST`: unstable / n=11 / vars=7 / exact=7, proxy_strong=0, proxy_medium=0, proxy_weak=0 / 定数列=なし / サンプル数が少なすぎる
- `FW`: caution / n=117 / vars=10 / exact=10, proxy_strong=0, proxy_medium=0, proxy_weak=0 / 定数列=なし / 欠損補完率が高い

## ポジション別メモ

- `SH`: 旧定義の weak proxy を大幅に削り、走力・突破・クロス・侵入・即時奪回に絞った。
- `ST`: n=11 と小さく、proxy 依存を避けるためボックス内フィニッシュ・配球・前線守備の 7 変数まで圧縮した。

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
