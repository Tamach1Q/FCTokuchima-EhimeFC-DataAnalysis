# CMF Feature Definition

|概念変数|採用列名|参照列|区分|元区分|最終採用対象|今回の扱い|置換先|理由|採用不能理由|
|---|---|---|---|---|---|---|---|---|---|
|Running Distance_per_match|running_distance_full_all_per_match|Running Distance|exact|exact|yes|adopted||中盤の運動量を具体的に示すため採用。||
|ボールゲイン_per90|ball_gains_per90|ボールゲイン, 出場時間|exact|exact|yes|adopted||守備関与量を直接示すため採用。||
|インターセプト_per90|interceptions_per90|インターセプト, 出場時間|exact|exact|yes|adopted||読みでの回収能力を直接示すため採用。||
|パス成功率|pass_success_rate_pct|パス, パス成功率(%)|exact|exact|yes|adopted||配球の安定性として採用。||
|前方向パス成功率|forward_pass_success_rate_pct|前方向パス, 前方向パス成功率(%)|exact|exact|yes|adopted||前進配球の質を直接示すため採用。||
|ショートパス割合|short_pass_share_pct|ショートパス, ミドルパス, ロングパス|exact|exact|yes|adopted||保持型かどうかを直接説明できるため採用。||
|ロングパス割合|long_pass_share_pct|ショートパス, ミドルパス, ロングパス|exact|exact|yes|adopted||展開型かどうかを直接説明できるため採用。||
|相手陣ボールゲイン割合|opponent_half_gain_share_pct|ボールゲイン, 相手陣での回数|exact|exact|yes|adopted||守備位置の高さを直接示すため採用。||
|total_distance_full_all_per_match|total_distance_full_all_per_match|Distance|dropped|exact|no|dropped||運動量は running distance の方が実戦解釈に向くため不採用。|総移動量よりも走行量を優先。|
|こぼれ球奪取|loose_ball_gain_proxy_per90|ボールゲイン, 出場時間|dropped|proxy_medium|no|dropped|ball_gains_per90|こぼれ球限定ではないため、総ボールゲイン_per90 を実測列として採用した。|限定概念としては扱えない。|
|MTでの空中戦勝率|mid_third_aerial_win_rate_proxy_pct|空中戦, 空中戦勝率(%)|dropped|proxy_medium|no|dropped||中盤限定ではなく、CMF で優先すべき説明軸でもないため不採用。|ゾーン限定で解釈できない。|
|MTでのタックル奪取率|mid_third_tackle_win_rate_proxy_pct|タックル, タックル奪取率(%)|dropped|proxy_weak|no|dropped||総タックル奪取率を MT 守備に置き換えるのは weak proxy で説明力が低いため不採用。|ゾーン限定で解釈できない。|
|PA外のシュートの決定率|out_box_shot_conversion_rate_pct|PA外シュート, PA外ゴール|dropped|exact|no|dropped||CMF はサンプル数が少なく、シュート系は疎で不安定なため不採用。|n=32 で外れ値影響が大きい。|
|枠内シュート率|shot_on_target_rate_pct|PA内シュート, PA内シュート枠内率(%), PA外シュート, PA外シュート枠内率(%)|dropped|exact|no|dropped||CMF ではシュート母数が小さく、クラスタ解釈が不安定になりやすいため不採用。|シュート母数が小さい。|
|count_interception_on_ball_engagements_per_match|interception_engagement_proxy_per90|インターセプト, 出場時間|dropped|proxy_medium|no|dropped|interceptions_per90|proxy 名を維持せず、インターセプト_per90 を実測列として採用した。|概念名より実測列の方が説明しやすい。|
|count_pressure_on_ball_engagements_per_match|pressure_engagement_proxy_per90|タックル, 出場時間|dropped|proxy_weak|no|dropped||pressure をタックル単独で表すのは weak proxy で説明力が低いため不採用。|pressure 直接列がない。|
|count_forward_momentum_all_possessions_per_match|forward_momentum_proxy_per90|30m進入, 出場時間|unavailable|proxy_medium|no|unavailable||2024 J3 に 30m進入元データがなく、CMF では定数化していたため不採用。|時系列カバレッジ不足で安定しない。|
|バイタルエリア進入|vital_area_entry_proxy_per90|ニアゾーン進入, 出場時間|unavailable|proxy_strong|no|unavailable||2024 J3 にニアゾーン進入元データがなく、CMF では定数化していたため不採用。|時系列カバレッジ不足で安定しない。|
|敵陣こぼれ球奪取率|opponent_half_loose_ball_gain_share_proxy_pct|ボールゲイン, 相手陣での回数|dropped|proxy_strong|no|dropped|opponent_half_gain_share_pct|こぼれ球限定ではないため、相手陣ボールゲイン割合として実測列を採用した。|限定概念としては扱えない。|
