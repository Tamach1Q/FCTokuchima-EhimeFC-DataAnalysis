# SB Feature Definition

|概念変数|採用列名|参照列|区分|元区分|最終採用対象|今回の扱い|置換先|理由|採用不能理由|
|---|---|---|---|---|---|---|---|---|---|
|Running Distance_per_match|running_distance_full_all_per_match|Running Distance|exact|exact|yes|adopted||上下動の総量を直接示すため採用。||
|HI Distance_per_match|hi_distance_full_all_per_match|HI Distance|exact|exact|yes|adopted||高強度移動量として解釈しやすいため採用。||
|Sprint Count_per_match|sprint_count_full_all_per_match|Sprint Count|exact|exact|yes|adopted||反復スプリント頻度を直接示すため採用。||
|クロス数_per90|crosses_per90|クロス, 出場時間|exact|exact|yes|adopted||幅を取って配球する SB の役割を直接表すため採用。||
|クロス成功率|cross_success_rate_pct|クロス, クロス成功率(%)|exact|exact|yes|adopted||クロスの質を直接示すため採用。||
|PA進入_per90|pa_entry_per90|PA進入, 出場時間|exact|exact|yes|adopted||攻撃参加による侵入量を直接表すため採用。||
|タックル奪取率|tackle_win_rate_pct|タックル, タックル奪取率(%)|exact|exact|yes|adopted||対人守備の質を直接示すため採用。||
|ブロック_per90|blocks_per90|ブロック, 出場時間|exact|exact|yes|adopted||守備時のブロック頻度を直接扱うため採用。||
|前方向ロングパス成功率|forward_long_pass_success_rate_pct|前方向ロングパス, 前方向ロングパス成功率(%)|exact|exact|yes|adopted||アーリー配球の質を実測列で見るため採用。||
|ロスト後5秒未満リゲイン_per90|regain_within_5s_per90|ロスト後5秒未満リゲイン, 出場時間|exact|exact|yes|adopted||pressure をタックル単独で置くより、即時奪回の実測列の方が説明しやすいため採用。||
|psv99_per_match|psv99_per_match|PSV-99|dropped|exact|no|dropped||総合スコアよりも走行量とスプリント系の個別列を優先した。|物理出力は個別の実測列で表現する。|
|total_metersperminute_full_all_per_match|total_metersperminute_full_all_per_match|M/min|dropped|exact|no|dropped||running distance / HI distance / sprint count を残すため、近い情報を持つ M/min は削減対象とした。|物理指標の重複を避けるため。|
|dropping_off_runs|dropping_off_runs_proxy_per90|MTからパス, 出場時間|dropped|proxy_weak|no|dropped|running_distance_full_all_per_match|MTからパスは dropping off run の説明として弱く、走行量の実測列を優先した。|受けに降りる動きそのものは観測できない。|
|overlap_runs|overlap_runs_proxy_per90|クロス, 出場時間|dropped|proxy_medium|no|dropped|crosses_per90|overlap 概念をクロス頻度と呼び替えると誤解が少ないため、実測の crosses_per90 を採用した。|run タイプそのものは観測できない。|
|underlap_runs|underlap_runs_proxy_per90|PA脇進入, 出場時間|unavailable|proxy_strong|no|unavailable||2024 J3 に PA脇進入元データがなく、SB では定数化していたため不採用。|時系列カバレッジ不足で安定しない。|
|アーリークロス成功率|early_cross_proxy_success_rate_pct|前方向ロングパス, 前方向ロングパス成功率(%)|dropped|proxy_medium|no|dropped|forward_long_pass_success_rate_pct|proxy 名を外して前方向ロングパス成功率として直接採用する方が説明しやすい。|アーリークロス専用列ではないため proxy 名のままは使わない。|
|ブロック(クロス)|cross_block_proxy_per90|ブロック, 出場時間|dropped|proxy_medium|no|dropped|blocks_per90|クロス限定ではないため、総ブロック_per90 をそのまま採用した。|イベント種別を限定できない。|
|pulling_half_space_runs|pulling_half_space_runs_proxy_per90|PA脇進入, 出場時間|unavailable|proxy_strong|no|unavailable||2024 J3 に PA脇進入元データがなく、SB では定数化していたため不採用。|時系列カバレッジ不足で安定しない。|
|count_successful_on_ball_engagements_per_match|successful_on_ball_actions_per90|クロス, クロス成功率(%), スルーパス, スルーパス成功率(%), ドリブル, ドリブル成功率(%), 前方向パス, 前方向パス成功率(%)|dropped|proxy_medium|no|dropped||合成指標よりもクロス量・成功率・PA進入の個別指標の方が役割を説明しやすい。|構成要素を分けた方がクラスタ解釈が明快。|
|AT進入|attacking_third_entry_proxy_per90|30m進入, 出場時間|unavailable|proxy_medium|no|unavailable||2024 J3 に 30m進入元データがなく、SB では定数化していたため不採用。|時系列カバレッジ不足で安定しない。|
