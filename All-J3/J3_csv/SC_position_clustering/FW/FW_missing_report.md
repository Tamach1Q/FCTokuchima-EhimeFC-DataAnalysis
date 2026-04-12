# FW Missing Report

- サンプル数: `117`
- winsorize 条件: `1/99` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|shot_conversion_rate_pct|35|29.91|35|0|46.8|0|2|中央値補完あり|
|out_box_shots_per90|35|29.91|35|0|1.37103|0|2|中央値補完あり|
|box_shots_per90|35|29.91|35|0.235628|4.23719|2|2|中央値補完あり|
|shot_on_target_rate_pct|35|29.91|35|5.97778|82|2|2|中央値補完あり|
|goals_per90|35|29.91|35|0|0.866894|0|2|中央値補完あり|
|aerial_wins_per90|35|29.91|35|0.149325|9.66986|2|2|中央値補完あり|
|successful_forward_passes_per90|35|29.91|35|0.660823|7.44674|2|2|中央値補完あり|
|last_passes_per90|35|29.91|35|0.159548|2.27205|2|2|中央値補完あり|
|attacking_third_gains_per90|35|29.91|35|0|1.53886|0|2|中央値補完あり|
|sprint_count_full_all_per_match|0|0.00|0|1.4791|13.4108|2|2|中央値補完なし|

- zscore_constant_feature: なし
