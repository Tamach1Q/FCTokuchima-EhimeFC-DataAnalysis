# ST Feature Definition

|概念変数|採用列名|参照列|区分|理由|採用不能理由|
|---|---|---|---|---|---|
|キャリーによるPA進入|carry_into_box_proxy_per90|PA進入, 出場時間|proxy_weak|carry 起点は識別できないため、PA進入頻度を proxy とした。||
|count_8m_carry_at_speed_all_possessions_per_match|speed_carry_proxy_per_match|Explosive Acceleration to Sprint Count|proxy_weak|高速キャリー直接列がないため、Explosive Acceleration to Sprint Count 試合平均を proxy とした。||
|ATタッチ|attacking_third_touch_proxy_per90|ATからパス, 出場時間|proxy_medium|ATタッチ直接列がないため、ATからパス頻度を proxy とした。||
|count_received_in_open_space_all_possessions_per_match|open_space_receive_proxy_per90|30m進入, 出場時間|proxy_medium|open space reception 直接列がないため、30m進入頻度を proxy とした。||
|coming_short_runs|coming_short_runs_proxy_per90|パス, 出場時間|proxy_weak|coming short run 直接列がないため、受けに降りる関与として総パス頻度を proxy とした。||
|runs_in_behind|runs_in_behind_proxy_per_match|Sprint Count|proxy_weak|裏抜け直接列がないため、Sprint Count 試合平均を proxy とした。||
|xthreat_received_off_ball_runs_per_match|xthreat_received_runs_proxy_per90|ニアゾーン進入, 出場時間|proxy_weak|xThreat 直接列がないため、危険度の高い受け位置に近いニアゾーン進入頻度を proxy とした。||
|ポケット進入|pocket_entry_proxy_per90|PA脇進入, 出場時間|proxy_strong|ポケット進入に最も近い Football Box の PA脇進入を採用。||
|セカンドアシスト|second_assist_proxy_per90|ラストパス, 出場時間|proxy_medium|セカンドアシスト列がないため、ラストパス頻度を proxy とした。||
|シュート決定率|shot_conversion_rate_pct|ゴール, シュート|exact|基本サマリーのゴールと攻撃サマリーのシュートから全体決定率を再計算。||
|アシストスルーパス|assist_through_pass_proxy_per90|スルーパス, スルーパス成功率(%), 出場時間|proxy_medium|アシスト付きスルーパス列がないため、成功スルーパス頻度を proxy とした。||
|ATでのタックル奪取率|attacking_third_tackle_win_proxy_pct|タックル, タックル奪取率(%)|proxy_weak|AT限定タックル奪取率がないため、総タックル奪取率を proxy とした。||
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|proxy_weak|pressure の直接列がないため、タックル頻度を proxy とした。||
|dropping_off_runs|dropping_off_runs_proxy_per90|パス, 出場時間|proxy_weak|dropping off run 直接列がないため、総パス頻度を proxy とした。||
|1stシュート|first_shot_proxy_per90|PA内シュート, 出場時間|proxy_weak|1stシュート列がないため、最も近い proxy として PA内シュート頻度を採用。||
