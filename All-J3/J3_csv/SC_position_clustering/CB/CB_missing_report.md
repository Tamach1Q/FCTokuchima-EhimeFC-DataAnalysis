# CB Missing Report

- サンプル数: `149`
- winsorize 条件: `1/99` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|aerial_duel_win_rate_pct|40|26.85|40|20.7797|80.4732|2|2|中央値補完あり|
|tackle_win_rate_pct|40|26.85|40|12|100|2|0|中央値補完あり|
|interceptions_per90|40|26.85|40|0|0.472808|0|2|中央値補完あり|
|blocks_per90|40|26.85|40|0|4.20038|0|2|中央値補完あり|
|clearances_per90|40|26.85|40|1.41531|9.4287|2|2|中央値補完あり|
|pass_success_rate_pct|40|26.85|40|59.2358|88.8376|2|2|中央値補完あり|
|successful_forward_passes_per90|40|26.85|40|4.66854|23.4525|2|2|中央値補完あり|
|successful_long_passes_per90|40|26.85|40|0|7.45954|0|2|中央値補完あり|
|medaccel_count_full_all_per_match|0|0.00|0|42.0173|118.444|2|2|中央値補完なし|
|highaccel_count_full_all_per_match|0|0.00|0|2.12|7.03538|2|2|中央値補完なし|

- zscore_constant_feature: なし
