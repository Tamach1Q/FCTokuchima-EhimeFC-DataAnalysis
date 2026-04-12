# SB Missing Report

- サンプル数: `123`
- winsorize 条件: `1/99` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|psv99_per_match|0|0.00|0|26.1299|30.5922|2|2|中央値補完なし|
|total_metersperminute_full_all_per_match|0|0.00|0|100.838|125.751|2|2|中央値補完なし|
|hi_distance_full_all_per_match|0|0.00|0|222.505|982.796|2|2|中央値補完なし|
|sprint_count_full_all_per_match|0|0.00|0|2.19924|14.5087|2|2|中央値補完なし|
|dropping_off_runs_proxy_per90|31|25.20|31|8.25755|43.4364|2|2|中央値補完あり|
|overlap_runs_proxy_per90|31|25.20|31|0.485792|8.40375|2|2|中央値補完あり|
|underlap_runs_proxy_per90|36|29.27|36|0|0|0|0|中央値補完あり|
|cross_success_rate_pct|31|25.20|31|0|33.3333|0|1|中央値補完あり|
|early_cross_proxy_success_rate_pct|31|25.20|31|0|45.3978|0|2|中央値補完あり|
|pa_entry_per90|31|25.20|31|0.440396|3.19017|2|2|中央値補完あり|
|tackle_win_rate_pct|31|25.20|31|29.619|79.8725|2|2|中央値補完あり|
|cross_block_proxy_per90|31|25.20|31|1.10446|4.8102|2|2|中央値補完あり|
|pulling_half_space_runs_proxy_per90|36|29.27|36|0|0|0|0|中央値補完あり|
|successful_on_ball_actions_per90|31|25.20|31|4.93934|21.3463|2|2|中央値補完あり|
|attacking_third_entry_proxy_per90|36|29.27|36|0|0|0|0|中央値補完あり|

- zscore_constant_feature: underlap_runs_proxy_per90, pulling_half_space_runs_proxy_per90, attacking_third_entry_proxy_per90
