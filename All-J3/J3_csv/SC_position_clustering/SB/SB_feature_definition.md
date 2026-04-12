# SB Feature Definition

|概念変数|採用列名|参照列|区分|理由|採用不能理由|
|---|---|---|---|---|---|
|psv99_per_match|psv99_per_match|PSV-99|exact|SkillCorner physical の PSV-99 試合平均。||
|total_metersperminute_full_all_per_match|total_metersperminute_full_all_per_match|M/min|exact|SkillCorner physical の M/min 試合平均。||
|hi_distance_full_all_per_match|hi_distance_full_all_per_match|HI Distance|exact|SkillCorner physical の HI Distance 試合平均。||
|sprint_count_full_all_per_match|sprint_count_full_all_per_match|Sprint Count|exact|SkillCorner physical の Sprint Count 試合平均。||
|dropping_off_runs|dropping_off_runs_proxy_per90|MTからパス, 出場時間|proxy_weak|dropping off run 直接列がないため、中盤で受ける役割に近い MTからパス頻度を proxy とした。||
|overlap_runs|overlap_runs_proxy_per90|クロス, 出場時間|proxy_medium|overlap の直接列がないため、外側の走りから生じやすいクロス頻度を proxy とした。||
|underlap_runs|underlap_runs_proxy_per90|PA脇進入, 出場時間|proxy_strong|underlap は PA脇進入とエリア特性が近いため最優先 proxy とした。||
|クロス成功率|cross_success_rate_pct|クロス, クロス成功率(%)|exact|Football Box 攻撃サマリーのクロス成功率を再計算して採用。||
|アーリークロス成功率|early_cross_proxy_success_rate_pct|前方向ロングパス, 前方向ロングパス成功率(%)|proxy_medium|アーリークロス専用列がないため、前方向ロングパス成功率を proxy とした。||
|PA進入|pa_entry_per90|PA進入, 出場時間|exact|PA進入を per90 化して採用。||
|タックル奪取率|tackle_win_rate_pct|タックル, タックル奪取率(%)|exact|Football Box 守備サマリーのタックル奪取率。||
|ブロック(クロス)|cross_block_proxy_per90|ブロック, 出場時間|proxy_medium|クロスブロックの内訳がないため、総ブロックを proxy とした。||
|pulling_half_space_runs|pulling_half_space_runs_proxy_per90|PA脇進入, 出場時間|proxy_strong|half-space run と PA脇進入は侵入エリアが近いため。||
|count_successful_on_ball_engagements_per_match|successful_on_ball_actions_per90|クロス, クロス成功率(%), スルーパス, スルーパス成功率(%), ドリブル, ドリブル成功率(%), 前方向パス, 前方向パス成功率(%)|proxy_medium|on-ball engagement 成功数の直接列がないため、成功クロス・スルーパス・ドリブル・前方向パスの合算を proxy とした。||
|AT進入|attacking_third_entry_proxy_per90|30m進入, 出場時間|proxy_medium|AT進入専用列がないため、30m進入頻度を proxy とした。||
