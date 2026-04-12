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
|aerial_retain_proxy_pct|35|29.91|35|8.84615|61.0123|2|2|中央値補完あり|
|aerial_pass_proxy_per90|35|29.91|35|0.149325|9.66986|2|2|中央値補完あり|
|pressure_engagement_proxy_per90|35|29.91|35|0.172558|2.27546|2|2|中央値補完あり|
|consecutive_on_ball_engagement_proxy_per90|35|29.91|35|1.02235|9.02786|2|2|中央値補完あり|
|runs_in_behind_proxy_per_match|0|0.00|0|1.4791|13.4108|2|2|中央値補完なし|
|passing_option_receive_proxy_per90|35|29.91|35|4.10972|17.7652|2|2|中央値補完あり|
|xthreat_passing_option_proxy_per90|31|26.50|31|0|0|0|0|中央値補完あり|
|successful_forward_passes_per90|35|29.91|35|0.660823|7.44674|2|2|中央値補完あり|
|attacking_third_tackle_gain_proxy_per90|35|29.91|35|0|1.53886|0|2|中央値補完あり|
|goals_per90|35|29.91|35|0|0.866894|0|2|中央値補完あり|
|first_shot_proxy_per90|35|29.91|35|0.281781|5.67043|2|2|中央値補完あり|

- zscore_constant_feature: xthreat_passing_option_proxy_per90
