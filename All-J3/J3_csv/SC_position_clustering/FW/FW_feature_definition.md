# FW Feature Definition

|概念変数|採用列名|参照列|区分|元区分|最終採用対象|今回の扱い|置換先|理由|採用不能理由|
|---|---|---|---|---|---|---|---|---|---|
|シュート決定率|shot_conversion_rate_pct|ゴール, シュート|exact|exact|yes|adopted||フィニッシュ効率を直接示すため採用。||
|PA外シュート数_per90|out_box_shots_per90|PA外シュート, 出場時間|exact|exact|yes|adopted||外から打つ傾向を直接示すため採用。||
|PA内シュート数_per90|box_shots_per90|PA内シュート, 出場時間|exact|exact|yes|adopted||ボックス内でのフィニッシュ量を直接示すため採用。||
|枠内シュート率|shot_on_target_rate_pct|PA内シュート, PA内シュート枠内率(%), PA外シュート, PA外シュート枠内率(%)|exact|exact|yes|adopted||シュート精度を直接示すため採用。||
|ゴール_per90|goals_per90|ゴール, 出場時間|exact|exact|yes|adopted||得点量を直接示すため採用。||
|空中戦勝利数_per90|aerial_wins_per90|空中戦, 空中戦勝率(%), 出場時間|exact|exact|yes|adopted||空中戦の関与量を実測で見られるため採用。||
|前進パス成功数_per90|successful_forward_passes_per90|前方向パス, 前方向パス成功率(%), 出場時間|exact|exact|yes|adopted||サポート役としての前進配球を実測で見られるため採用。||
|ラストパス_per90|last_passes_per90|ラストパス, 出場時間|exact|exact|yes|adopted||サポート FW の創出量を直接示すため採用。||
|ATボールゲイン_per90|attacking_third_gains_per90|ATでの回数, 出場時間|exact|exact|yes|adopted||前線守備の量を直接示すため採用。||
|Sprint Count_per_match|sprint_count_full_all_per_match|Sprint Count|exact|exact|yes|adopted||走力と抜け出し傾向の基礎指標として採用。||
|空中戦勝利でボール保持|aerial_retain_proxy_pct|空中戦, 空中戦勝率(%)|dropped|proxy_medium|no|dropped|aerial_wins_per90|保持に繋がった内訳は観測できないため、空中戦勝利数_per90 を実測列として採用した。|保持に繋がったかは識別できない。|
|空中戦勝利でパス|aerial_pass_proxy_per90|空中戦, 空中戦勝率(%), 出場時間|dropped|proxy_medium|no|dropped|aerial_wins_per90|パスに繋がった内訳は観測できないため、空中戦勝利数_per90 を実測列として採用した。|勝利後の処理は識別できない。|
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|dropped|proxy_weak|no|dropped|attacking_third_gains_per90|pressure をタックル単独で表すのは weak proxy のため不採用。前線守備は AT ボールゲインで見る。|pressure 直接列がない。|
|count_consecutive_on_ball_engagements_per_match|consecutive_on_ball_engagement_proxy_per90|クロス, クロス成功率(%), スルーパス, スルーパス成功率(%), ドリブル, ドリブル成功率(%), 前方向パス, 前方向パス成功率(%)|dropped|proxy_medium|no|dropped||合成 proxy より、前進パス成功数とラストパスの方が役割差を説明しやすいため不採用。|構成要素を分けた方が説明しやすい。|
|runs_in_behind|runs_in_behind_proxy_per_match|Sprint Count|dropped|proxy_weak|no|dropped|sprint_count_full_all_per_match|Sprint Count は exact の走力指標として採用し、runs in behind の proxy 名では使わない。|裏抜けイベント自体は観測できない。|
|count_received_passing_option_per_match|passing_option_receive_proxy_per90|ATからパス, 出場時間|dropped|proxy_medium|no|dropped|last_passes_per90|受け手イベントではないため、創出量はラストパス_per90 で扱う。|receive そのものではない。|
|xthreat_passing_option_per_match|xthreat_passing_option_proxy_per90|ニアゾーン進入, 出場時間|unavailable|proxy_weak|no|unavailable||xThreat の直接列がなく、ニアゾーン進入は 2024 J3 欠落もあって不安定なため不採用。|xThreat の直接観測がない。|
|前方へのパス成功|successful_forward_passes_per90|前方向パス, 前方向パス成功率(%), 出場時間|dropped|proxy_strong|no|dropped|successful_forward_passes_per90|proxy ではなく、前進パス成功数_per90 という実測列として採用した。|proxy 名のままより実測概念として使う方がよい。|
|ATでのタックル奪取|attacking_third_tackle_gain_proxy_per90|ATでの回数, 出場時間|dropped|proxy_medium|no|dropped|attacking_third_gains_per90|タックル奪取限定ではないため、AT ボールゲイン_per90 の実測列として採用した。|タックル由来かは識別できない。|
|1stシュート|first_shot_proxy_per90|シュート, 出場時間|dropped|proxy_weak|no|dropped|box_shots_per90|sequence order は観測できないため、PA内シュート数_per90 を実測列として採用した。|1st シュートの順序情報がない。|
