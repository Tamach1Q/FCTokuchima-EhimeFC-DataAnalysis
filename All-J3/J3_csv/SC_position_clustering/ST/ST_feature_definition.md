# ST Feature Definition

|概念変数|採用列名|参照列|区分|元区分|最終採用対象|今回の扱い|置換先|理由|採用不能理由|
|---|---|---|---|---|---|---|---|---|---|
|シュート決定率|shot_conversion_rate_pct|ゴール, シュート|exact|exact|yes|adopted||フィニッシュ効率を直接示すため採用。||
|PA内シュート_per90|box_shots_per90|PA内シュート, 出場時間|exact|exact|yes|adopted||1stシュート proxy よりもボックス内での実際のシュート量を採用する方が妥当。||
|ゴール_per90|goals_per90|ゴール, 出場時間|exact|exact|yes|adopted||得点量を直接示すため採用。||
|Sprint Count_per_match|sprint_count_full_all_per_match|Sprint Count|exact|exact|yes|adopted||走力・裏抜け傾向の土台となる実測値として採用。||
|ラストパス_per90|last_passes_per90|ラストパス, 出場時間|exact|exact|yes|adopted||下りて受けた後の配球関与を実測で見られるため採用。||
|成功スルーパス_per90|successful_through_passes_per90|スルーパス, スルーパス成功率(%), 出場時間|exact|exact|yes|adopted||アシスト付きに限定せず、味方を前進させる配球量として採用。||
|ATボールゲイン_per90|attacking_third_gains_per90|ATでの回数, 出場時間|exact|exact|yes|adopted||ST の前線守備は総タックル率より AT でのボールゲイン回数の方が妥当なため採用。||
|キャリーによるPA進入|carry_into_box_proxy_per90|PA進入, 出場時間|dropped|proxy_weak|no|dropped||carry 起点は識別できず、ST ではボックス内シュート量を優先した。|carry 起点を識別できない。|
|count_8m_carry_at_speed_all_possessions_per_match|speed_carry_proxy_per_match|Explosive Acceleration to Sprint Count|dropped|proxy_weak|no|dropped||高速キャリーの proxy としては粗く、ST の採用軸としては優先度が低いため不採用。|概念との対応が弱い。|
|ATタッチ|attacking_third_touch_proxy_per90|ATからパス, 出場時間|dropped|proxy_medium|no|dropped|last_passes_per90|タッチではなくパス起点回数なので、ラストパス_per90 を残す方が説明しやすい。|touch そのものではない。|
|count_received_in_open_space_all_possessions_per_match|open_space_receive_proxy_per90|30m進入, 出場時間|unavailable|proxy_medium|no|unavailable||30m進入では open space receive を説明しにくく、2024 J3 の元データも不足するため不採用。|受け位置イベントを観測できない。|
|coming_short_runs|coming_short_runs_proxy_per90|パス, 出場時間|dropped|proxy_weak|no|dropped|last_passes_per90|総パス頻度では下りる動きを説明しにくく、ラストパス_per90 を残す方が役割差を見やすい。|受けに下りる動きそのものは観測できない。|
|runs_in_behind|runs_in_behind_proxy_per_match|Sprint Count|dropped|proxy_weak|no|dropped|sprint_count_full_all_per_match|Sprint Count は exact の走力指標として採用し、runs in behind の proxy 名では使わない。|裏抜けイベント自体は観測できない。|
|xthreat_received_off_ball_runs_per_match|xthreat_received_runs_proxy_per90|ニアゾーン進入, 出場時間|unavailable|proxy_weak|no|unavailable||xThreat 直接列がなく、ニアゾーン進入は 2024 J3 欠落もあって不安定なため不採用。|xThreat の直接観測がない。|
|ポケット進入|pocket_entry_proxy_per90|PA脇進入, 出場時間|unavailable|proxy_strong|no|unavailable||2024 J3 に PA脇進入元データがなく、ST では定数化していたため不採用。|時系列カバレッジ不足で安定しない。|
|セカンドアシスト|second_assist_proxy_per90|ラストパス, 出場時間|dropped|proxy_medium|no|dropped|last_passes_per90|セカンドアシストに限定できないため、ラストパス_per90 の実測列として採用した。|セカンドアシスト専用列がない。|
|アシストスルーパス|assist_through_pass_proxy_per90|スルーパス, スルーパス成功率(%), 出場時間|dropped|proxy_medium|no|dropped|successful_through_passes_per90|アシスト付きに限定できないため、成功スルーパス_per90 の実測列として採用した。|アシスト有無を識別できない。|
|ATでのタックル奪取率|attacking_third_tackle_win_proxy_pct|タックル, タックル奪取率(%)|dropped|proxy_weak|no|dropped|attacking_third_gains_per90|ST の前線守備は AT ボールゲイン回数の方が説明しやすいため、総タックル率 proxy は不採用。|AT限定の奪取率は観測できない。|
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|dropped|proxy_weak|no|dropped||pressure をタックル単独で置くのは weak proxy のため不採用。|pressure 直接列がない。|
|dropping_off_runs|dropping_off_runs_proxy_per90|パス, 出場時間|dropped|proxy_weak|no|dropped||総パス頻度では dropping off run を説明しにくいため不採用。|受けに降りる動きそのものは観測できない。|
|1stシュート|first_shot_proxy_per90|PA内シュート, 出場時間|dropped|proxy_weak|no|dropped|box_shots_per90|sequence order は観測できないため、ボックス内シュート量を実測列として採用した。|1st シュートの順序情報がない。|
