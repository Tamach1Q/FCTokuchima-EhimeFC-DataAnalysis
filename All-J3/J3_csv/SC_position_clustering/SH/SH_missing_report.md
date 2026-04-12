# SH Missing Report

- サンプル数: `215`
- winsorize 条件: `1/99` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|psv99_per_match|0|0.00|0|24.6975|30.8365|3|3|中央値補完なし|
|assist_cross_proxy_per90|69|32.09|69|0|1.73162|0|3|中央値補完あり|
|sprint_distance_full_all_per_match|0|0.00|0|16.5994|254.902|3|3|中央値補完なし|
|dropping_off_runs_proxy_per90|69|32.09|69|20.3984|74.131|3|3|中央値補完あり|
|pressure_engagement_proxy_per90|69|32.09|69|0.649071|4.31017|3|3|中央値補完あり|
|consecutive_on_ball_engagement_proxy_per90|69|32.09|69|3.40858|16.6602|3|3|中央値補完あり|
|above_hsr_engagement_proxy_per_match|0|0.00|0|9.14278|60.2723|3|3|中央値補完なし|
|dribble_success_rate_pct|69|32.09|69|0|89.0678|0|3|中央値補完あり|
|carry_into_box_proxy_per90|69|32.09|69|0.270746|5.9317|3|3|中央値補完あり|
|cross_reception_proxy_per90|69|32.09|69|0|2.43129|0|3|中央値補完あり|
|shot_conversion_rate_pct|69|32.09|69|0|28.5714|0|2|中央値補完あり|
|pulling_wide_runs_proxy_per90|69|32.09|69|0.200586|8.00136|3|3|中央値補完あり|
|cross_success_rate_pct|69|32.09|69|0|56.1551|0|3|中央値補完あり|
|opponent_box_ball_gain_proxy_per90|69|32.09|69|0|1.69354|0|3|中央値補完あり|
|dribble_shot_proxy_per90|69|32.09|69|0|4.67329|0|3|中央値補完あり|

- zscore_constant_feature: なし
