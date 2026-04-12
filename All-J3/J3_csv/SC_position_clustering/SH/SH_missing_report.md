# SH Missing Report

- サンプル数: `215`
- winsorize 条件: `1/99` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|sprint_distance_full_all_per_match|0|0.00|0|16.5994|254.902|3|3|中央値補完なし|
|hsr_count_full_all_per_match|0|0.00|0|9.14278|60.2723|3|3|中央値補完なし|
|dribble_success_rate_pct|69|32.09|69|0|89.0678|0|3|中央値補完あり|
|crosses_per90|69|32.09|69|0.200586|8.00136|3|3|中央値補完あり|
|cross_success_rate_pct|69|32.09|69|0|56.1551|0|3|中央値補完あり|
|last_passes_per90|69|32.09|69|0.0380665|2.68649|3|3|中央値補完あり|
|pa_entry_per90|69|32.09|69|0.270746|5.9317|3|3|中央値補完あり|
|shot_conversion_rate_pct|69|32.09|69|0|28.5714|0|2|中央値補完あり|
|regain_within_5s_per90|69|32.09|69|0.0271259|2.59269|3|3|中央値補完あり|

- zscore_constant_feature: なし
