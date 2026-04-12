# CMF Feature Definition

|概念変数|採用列名|参照列|区分|理由|採用不能理由|
|---|---|---|---|---|---|
|total_distance_full_all_per_match|total_distance_full_all_per_match|Distance|exact|SkillCorner physical の Distance 試合平均。||
|こぼれ球奪取|loose_ball_gain_proxy_per90|ボールゲイン, 出場時間|proxy_medium|こぼれ球限定列がないため、総ボールゲインを proxy とした。||
|MTでの空中戦勝率|mid_third_aerial_win_rate_proxy_pct|空中戦, 空中戦勝率(%)|proxy_medium|MT限定列がないため、総空中戦勝率で代替。||
|MTでのタックル奪取率|mid_third_tackle_win_rate_proxy_pct|タックル, タックル奪取率(%)|proxy_weak|MT限定列がないため、総タックル奪取率を proxy とした。||
|PA外のシュートの決定率|out_box_shot_conversion_rate_pct|PA外シュート, PA外ゴール|exact|エリア別シュートの PA外シュート決定率を再計算して採用。||
|枠内シュート率|shot_on_target_rate_pct|PA内シュート, PA内シュート枠内率(%), PA外シュート, PA外シュート枠内率(%)|exact|PA内/外の枠内率と本数から全体の枠内シュート率を再計算。||
|count_interception_on_ball_engagements_per_match|interception_engagement_proxy_per90|インターセプト, 出場時間|proxy_medium|interception on-ball engagement の直接列がないため、インターセプト頻度を proxy とした。||
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|proxy_weak|pressure 直接列がないため、守備圧力に近いタックル頻度を proxy とした。||
|パス成功率|pass_success_rate_pct|パス, パス成功率(%)|exact|Football Box 攻撃サマリーのパス成功率。||
|前方へのパス成功割合|forward_pass_success_rate_pct|前方向パス, 前方向パス成功率(%)|exact|方向別パスの前方向パス成功率。||
|ショートパス(0-15m)割合|short_pass_share_pct|ショートパス, ミドルパス, ロングパス|proxy_strong|距離別パスのショートパス割合を 0-15m proxy とした。||
|ロングパス(30m-)割合|long_pass_share_pct|ショートパス, ミドルパス, ロングパス|proxy_strong|距離別パスのロングパス割合を 30m- proxy とした。||
|count_forward_momentum_all_possessions_per_match|forward_momentum_proxy_per90|30m進入, 出場時間|proxy_medium|forward momentum の直接列がないため、30m進入頻度を proxy とした。||
|バイタルエリア進入|vital_area_entry_proxy_per90|ニアゾーン進入, 出場時間|proxy_strong|バイタルエリア進入に最も近い Football Box のニアゾーン進入を採用。||
|敵陣こぼれ球奪取率|opponent_half_loose_ball_gain_share_proxy_pct|ボールゲイン, 相手陣での回数|proxy_strong|敵陣こぼれ球奪取率の直接列がないため、相手陣割合を最も近い proxy とした。||
