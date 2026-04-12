# CB Feature Definition

|概念変数|採用列名|参照列|区分|理由|採用不能理由|
|---|---|---|---|---|---|
|空中戦勝率|aerial_duel_win_rate_pct|空中戦, 空中戦勝率(%)|exact|Football Box 守備サマリーの空中戦勝率をそのまま採用。||
|タックル奪取率|tackle_win_rate_pct|タックル, タックル奪取率(%)|exact|Football Box 守備サマリーのタックル奪取率をそのまま採用。||
|インターセプト|interceptions_per90|インターセプト, 出場時間|exact|Football Box 守備サマリーのインターセプトを per90 化。||
|ブロック(シュート)|shot_block_proxy_per90|ブロック, 出場時間|proxy_medium|ブロック種別内訳がないため、総ブロックをシュートブロックの proxy とした。||
|psv99_per_match|psv99_per_match|PSV-99|exact|SkillCorner physical の PSV-99 試合平均。||
|medaccel_count_full_all_per_match|medaccel_count_full_all_per_match|Medium Acceleration Count|exact|SkillCorner physical の中加速回数試合平均。||
|highaccel_count_full_all_per_match|highaccel_count_full_all_per_match|High Acceleration Count|exact|SkillCorner physical の高加速回数試合平均。||
|count_track_run_on_ball_engagements_per_match|track_run_proxy_per_match|Change of Direction Count|proxy_weak|on-ball track run 直接列がないため、方向転換回数の試合平均で代替。||
|自陣PA内でのクリア|def_penalty_area_clearance_proxy_per90|クリア, 出場時間|proxy_medium|自陣PA内限定のクリア列がないため、総クリアを proxy とした。||
|count_affected_line_break_on_ball_engagements_per_match|affected_line_break_proxy_per90|前方向パス, 前方向パス成功率(%), 出場時間|proxy_medium|line break 直接列がないため、成功した前方向パスを最も近い proxy とした。||
|count_line_breaks_per_match|line_break_proxy_per90|前方向パス, 出場時間|proxy_medium|line break 直接列がないため、前方向パス頻度を proxy とした。||
|パス成功率|pass_success_rate_pct|パス, パス成功率(%)|exact|Football Box 攻撃サマリーのパス成功率を再計算して採用。||
|前方へのパス成功割合|forward_pass_success_rate_pct|前方向パス, 前方向パス成功率(%)|exact|方向別パスの前方向パス成功率を採用。||
|ロングパス成功(30m-)|successful_long_passes_per90|ロングパス, ロングパス成功率(%), 出場時間|proxy_strong|距離別パスのロングパス成功数 per90 を 30m- 成功の proxy とした。||
|キャリーによる30m進入|carry_into_30m_proxy_per90|30m進入, 出場時間|proxy_medium|carry 起点は識別できないため、30m進入回数を proxy とした。||
