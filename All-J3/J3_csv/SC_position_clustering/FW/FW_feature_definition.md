# FW Feature Definition

|概念変数|採用列名|参照列|区分|理由|採用不能理由|
|---|---|---|---|---|---|
|シュート決定率|shot_conversion_rate_pct|ゴール, シュート|exact|基本サマリーのゴールと攻撃サマリーのシュートから全体決定率を再計算。||
|PA外シュート数|out_box_shots_per90|PA外シュート, 出場時間|exact|PA外シュート数を per90 化。||
|PA内シュート数|box_shots_per90|PA内シュート, 出場時間|exact|PA内シュート数を per90 化。||
|枠内シュート率|shot_on_target_rate_pct|PA内シュート, PA内シュート枠内率(%), PA外シュート, PA外シュート枠内率(%)|exact|PA内/外の枠内数から全体枠内率を再計算。||
|空中戦勝利でボール保持|aerial_retain_proxy_pct|空中戦, 空中戦勝率(%)|proxy_medium|保持に繋がった内訳がないため、空中戦勝率を proxy とした。||
|空中戦勝利でパス|aerial_pass_proxy_per90|空中戦, 空中戦勝率(%), 出場時間|proxy_medium|パスに繋がった内訳がないため、空中戦勝利数 per90 を proxy とした。||
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|proxy_weak|pressure の直接列がないため、タックル頻度を proxy とした。||
|count_consecutive_on_ball_engagements_per_match|consecutive_on_ball_engagement_proxy_per90|クロス, クロス成功率(%), スルーパス, スルーパス成功率(%), ドリブル, ドリブル成功率(%), 前方向パス, 前方向パス成功率(%)|proxy_medium|連続 on-ball engagement の直接列がないため、成功 on-ball action 合算を proxy とした。||
|runs_in_behind|runs_in_behind_proxy_per_match|Sprint Count|proxy_weak|裏抜け直接列がないため、Sprint Count 試合平均を proxy とした。||
|count_received_passing_option_per_match|passing_option_receive_proxy_per90|ATからパス, 出場時間|proxy_medium|passing option reception 直接列がないため、ATでのパス関与頻度を proxy とした。||
|xthreat_passing_option_per_match|xthreat_passing_option_proxy_per90|ニアゾーン進入, 出場時間|proxy_weak|xThreat passing option の直接列がないため、危険度の高い受け位置に近いニアゾーン進入頻度を proxy とした。||
|前方へのパス成功|successful_forward_passes_per90|前方向パス, 前方向パス成功率(%), 出場時間|proxy_strong|前方へのパス成功割合ではなく成功数を per90 で採用。||
|ATでのタックル奪取|attacking_third_tackle_gain_proxy_per90|ATでの回数, 出場時間|proxy_medium|ATでのタックル奪取直接列がないため、ATでのボールゲイン頻度を proxy とした。||
|ゴール|goals_per90|ゴール, 出場時間|exact|基本サマリーのゴールを per90 化。||
|1stシュート|first_shot_proxy_per90|シュート, 出場時間|proxy_weak|1stシュート列がないため、総シュート頻度を proxy とした。||
