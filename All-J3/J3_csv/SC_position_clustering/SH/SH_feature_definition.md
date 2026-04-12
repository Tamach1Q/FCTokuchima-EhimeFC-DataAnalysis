# SH Feature Definition

|概念変数|採用列名|参照列|区分|元区分|最終採用対象|今回の扱い|置換先|理由|採用不能理由|
|---|---|---|---|---|---|---|---|---|---|
|Sprint Distance_per_match|sprint_distance_full_all_per_match|Sprint Distance|exact|exact|yes|adopted||縦の突破力を直接示すため採用。||
|HSR Count_per_match|hsr_count_full_all_per_match|HSR Count|exact|exact|yes|adopted||高強度ランの頻度を直接示すため採用。||
|ドリブル成功率|dribble_success_rate_pct|ドリブル, ドリブル成功率(%)|exact|exact|yes|adopted||突破の質を直接示すため採用。||
|クロス数_per90|crosses_per90|クロス, 出場時間|exact|exact|yes|adopted||幅を取るプレー量として採用。||
|クロス成功率|cross_success_rate_pct|クロス, クロス成功率(%)|exact|exact|yes|adopted||配球の質として採用。||
|ラストパス_per90|last_passes_per90|ラストパス, 出場時間|exact|exact|yes|adopted||チャンスメイク量を直接示すため採用。||
|PA進入_per90|pa_entry_per90|PA進入, 出場時間|exact|exact|yes|adopted||内側への侵入量を直接示すため採用。||
|シュート決定率|shot_conversion_rate_pct|ゴール, シュート|exact|exact|yes|adopted||フィニッシュ効率を直接示すため採用。||
|ロスト後5秒未満リゲイン_per90|regain_within_5s_per90|ロスト後5秒未満リゲイン, 出場時間|exact|exact|yes|adopted||pressure をタックル単独で置くより、即時奪回の実測列の方が守備強度を説明しやすいため採用。||
|psv99_per_match|psv99_per_match|PSV-99|dropped|exact|no|dropped||SH は走行量の内訳を残した方が役割差を説明しやすいため不採用。|Sprint Distance / HSR Count を優先した。|
|アシストクロス|assist_cross_proxy_per90|クロス, クロス成功率(%), 出場時間|dropped|proxy_medium|no|dropped|crosses_per90|アシスト付きに限定できないため、クロス量と成功率を個別に採用した。|アシスト起点かを識別できない。|
|dropping_off_runs|dropping_off_runs_proxy_per90|パス, 出場時間|dropped|proxy_weak|no|dropped||総パス頻度では dropping off run を説明しにくい weak proxy のため不採用。|受けに降りる動きそのものは観測できない。|
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|dropped|proxy_weak|no|dropped|regain_within_5s_per90|タックル単独の weak proxy は採らず、即時奪回の実測列を採用した。|pressure 直接列がない。|
|count_consecutive_on_ball_engagements_per_match|consecutive_on_ball_engagement_proxy_per90|クロス, クロス成功率(%), スルーパス, スルーパス成功率(%), ドリブル, ドリブル成功率(%), 前方向パス, 前方向パス成功率(%)|dropped|proxy_medium|no|dropped||合成 proxy よりドリブル・クロス・ラストパスの個別指標の方が解釈しやすいため不採用。|構成要素を分けた方が説明しやすい。|
|count_above_hsr_on_ball_engagements_per_match|above_hsr_engagement_proxy_per_match|HSR Count|dropped|proxy_medium|no|dropped|hsr_count_full_all_per_match|proxy 名を維持せず、HSR Count 自体を実測の高強度頻度として採用した。|on-ball engagement 限定ではない。|
|キャリーによるPA進入|carry_into_box_proxy_per90|PA進入, 出場時間|dropped|proxy_weak|no|dropped|pa_entry_per90|carry 起点は識別できないため、PA進入_per90 を侵入量の実測列として採用した。|carry 起点を識別できない。|
|クロス受|cross_reception_proxy_per90|PA内シュート, 出場時間|unavailable|proxy_weak|no|unavailable||クロス受けの直接列がなく、PA内シュートで置くと概念が離れすぎるため不採用。|受け手イベントを観測できない。|
|pulling_wide_runs|pulling_wide_runs_proxy_per90|クロス, 出場時間|dropped|proxy_medium|no|dropped|crosses_per90|wide run は直接観測できないため、実測のクロス数として扱う方が説明しやすい。|走り方そのものは観測できない。|
|敵陣PA内ボールゲイン|opponent_box_ball_gain_proxy_per90|ATでの回数, 出場時間|dropped|proxy_medium|no|dropped||PA内限定ではなく、SH では優先度も低いため不採用。|ゾーン限定で解釈できない。|
|ドリブルからのシュート|dribble_shot_proxy_per90|ドリブル, ドリブル成功率(%), 出場時間|unavailable|proxy_weak|no|unavailable||ドリブル後シュートの連結イベントがなく、成功ドリブル頻度では代替しにくいため不採用。|イベント連結が観測できない。|
