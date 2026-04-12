# CMF Missing Report

- サンプル数: `32`
- winsorize 条件: `2.5/97.5` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|running_distance_full_all_per_match|0|0.00|0|693.744|2012.55|1|1|中央値補完なし|
|ball_gains_per90|8|25.00|8|4.37225|10.4974|1|1|中央値補完あり|
|interceptions_per90|8|25.00|8|0|0.433786|0|1|中央値補完あり|
|pass_success_rate_pct|8|25.00|8|68.8475|86.0871|1|1|中央値補完あり|
|forward_pass_success_rate_pct|8|25.00|8|43.2822|68.2417|1|1|中央値補完あり|
|short_pass_share_pct|8|25.00|8|50.5487|71.1618|1|1|中央値補完あり|
|long_pass_share_pct|8|25.00|8|4.235|14.197|1|1|中央値補完あり|
|opponent_half_gain_share_pct|8|25.00|8|25.3523|45.1003|1|1|中央値補完あり|

- zscore_constant_feature: なし
