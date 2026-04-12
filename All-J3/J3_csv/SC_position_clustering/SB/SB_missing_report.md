# SB Missing Report

- サンプル数: `123`
- winsorize 条件: `1/99` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|running_distance_full_all_per_match|0|0.00|0|475.42|1687.43|2|2|中央値補完なし|
|hi_distance_full_all_per_match|0|0.00|0|222.505|982.796|2|2|中央値補完なし|
|sprint_count_full_all_per_match|0|0.00|0|2.19924|14.5087|2|2|中央値補完なし|
|crosses_per90|31|25.20|31|0.485792|8.40375|2|2|中央値補完あり|
|cross_success_rate_pct|31|25.20|31|0|33.3333|0|1|中央値補完あり|
|pa_entry_per90|31|25.20|31|0.440396|3.19017|2|2|中央値補完あり|
|tackle_win_rate_pct|31|25.20|31|29.619|79.8725|2|2|中央値補完あり|
|blocks_per90|31|25.20|31|1.10446|4.8102|2|2|中央値補完あり|
|forward_long_pass_success_rate_pct|31|25.20|31|0|45.3978|0|2|中央値補完あり|
|regain_within_5s_per90|31|25.20|31|0.280325|2.83172|2|2|中央値補完あり|

- zscore_constant_feature: なし
