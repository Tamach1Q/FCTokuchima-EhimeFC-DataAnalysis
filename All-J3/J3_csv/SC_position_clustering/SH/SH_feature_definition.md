# SH Feature Definition

|概念変数|採用列名|参照列|区分|理由|採用不能理由|
|---|---|---|---|---|---|
|psv99_per_match|psv99_per_match|PSV-99|exact|SkillCorner physical の PSV-99 試合平均。||
|アシストクロス|assist_cross_proxy_per90|クロス, クロス成功率(%), 出場時間|proxy_medium|アシストクロス列がないため、成功クロス頻度を proxy とした。||
|sprint_distance_full_all_per_match|sprint_distance_full_all_per_match|Sprint Distance|exact|SkillCorner physical の Sprint Distance 試合平均。||
|dropping_off_runs|dropping_off_runs_proxy_per90|パス, 出場時間|proxy_weak|dropping off run 直接列がないため、受けに降りる関与として総パス頻度を proxy とした。||
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|proxy_weak|pressure の直接列がないため、タックル頻度を proxy とした。||
|count_consecutive_on_ball_engagements_per_match|consecutive_on_ball_engagement_proxy_per90|クロス, クロス成功率(%), スルーパス, スルーパス成功率(%), ドリブル, ドリブル成功率(%), 前方向パス, 前方向パス成功率(%)|proxy_medium|連続 on-ball engagement の直接列がないため、成功した on-ball action の合算を proxy とした。||
|count_above_hsr_on_ball_engagements_per_match|above_hsr_engagement_proxy_per_match|HSR Count|proxy_medium|HSR を上回る on-ball engagement 直接列がないため、HSR Count 試合平均を proxy とした。||
|ドリブル成功率|dribble_success_rate_pct|ドリブル, ドリブル成功率(%)|exact|Football Box 攻撃サマリーのドリブル成功率。||
|キャリーによるPA進入|carry_into_box_proxy_per90|PA進入, 出場時間|proxy_weak|carry 起点の判別はできないため、PA進入頻度を proxy とした。||
|クロス受|cross_reception_proxy_per90|PA内シュート, 出場時間|proxy_weak|クロス受けの直接列がないため、PA内シュート頻度を proxy とした。||
|シュート決定率|shot_conversion_rate_pct|ゴール, シュート|exact|基本サマリーのゴールと攻撃サマリーのシュートから全体決定率を再計算。||
|pulling_wide_runs|pulling_wide_runs_proxy_per90|クロス, 出場時間|proxy_medium|wide run の直接列がないため、幅を取った結果として表れやすいクロス頻度を proxy とした。||
|クロス成功率|cross_success_rate_pct|クロス, クロス成功率(%)|exact|Football Box 攻撃サマリーのクロス成功率。||
|敵陣PA内ボールゲイン|opponent_box_ball_gain_proxy_per90|ATでの回数, 出場時間|proxy_medium|敵陣PA内限定列がないため、ATでのボールゲインを proxy とした。||
|ドリブルからのシュート|dribble_shot_proxy_per90|ドリブル, ドリブル成功率(%), 出場時間|proxy_weak|ドリブル後シュートの連結列がないため、成功ドリブル頻度を proxy とした。||
