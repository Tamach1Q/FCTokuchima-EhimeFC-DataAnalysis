# ST Missing Report

- サンプル数: `11`
- winsorize 条件: `2.5/97.5` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|shot_conversion_rate_pct|1|9.09|1|0|16.6667|0|0|中央値補完あり|
|box_shots_per90|1|9.09|1|0.690707|1.96128|1|1|中央値補完あり|
|goals_per90|1|9.09|1|0|0.262158|0|1|中央値補完あり|
|sprint_count_full_all_per_match|0|0.00|0|2.91718|8.86508|1|1|中央値補完なし|
|last_passes_per90|1|9.09|1|0.996423|2.06982|1|1|中央値補完あり|
|successful_through_passes_per90|1|9.09|1|0.609|2.14661|1|1|中央値補完あり|
|attacking_third_gains_per90|1|9.09|1|0|0.96042|0|1|中央値補完あり|

- zscore_constant_feature: なし
