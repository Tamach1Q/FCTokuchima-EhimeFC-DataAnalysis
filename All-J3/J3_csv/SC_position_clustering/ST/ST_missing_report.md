# ST Missing Report

- サンプル数: `11`
- winsorize 条件: `2.5/97.5` percentile
- z-score ルール: `z = (x - mean) / std`

|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|carry_into_box_proxy_per90|1|9.09|1|0.246914|2.13402|1|1|中央値補完あり|
|speed_carry_proxy_per_match|0|0.00|0|0.0238095|1.39474|1|1|中央値補完なし|
|attacking_third_touch_proxy_per90|1|9.09|1|7.90125|16.4112|1|1|中央値補完あり|
|open_space_receive_proxy_per90|6|54.55|6|0|0|0|0|中央値補完あり|
|coming_short_runs_proxy_per90|1|9.09|1|20.4321|39.7951|1|1|中央値補完あり|
|runs_in_behind_proxy_per_match|0|0.00|0|2.91718|8.86508|1|1|中央値補完なし|
|xthreat_received_runs_proxy_per90|6|54.55|6|0|0|0|0|中央値補完あり|
|pocket_entry_proxy_per90|6|54.55|6|0|0|0|0|中央値補完あり|
|second_assist_proxy_per90|1|9.09|1|0.996423|2.06982|1|1|中央値補完あり|
|shot_conversion_rate_pct|1|9.09|1|0|16.6667|0|0|中央値補完あり|
|assist_through_pass_proxy_per90|1|9.09|1|0.609|2.14661|1|1|中央値補完あり|
|attacking_third_tackle_win_proxy_pct|1|9.09|1|56.6606|81.7647|1|1|中央値補完あり|
|pressure_engagement_proxy_per90|1|9.09|1|0.459751|2.34434|1|1|中央値補完あり|
|dropping_off_runs_proxy_per90|1|9.09|1|20.4321|39.7951|1|1|中央値補完あり|
|first_shot_proxy_per90|1|9.09|1|0.690707|1.96128|1|1|中央値補完あり|

- zscore_constant_feature: open_space_receive_proxy_per90, xthreat_received_runs_proxy_per90, pocket_entry_proxy_per90
