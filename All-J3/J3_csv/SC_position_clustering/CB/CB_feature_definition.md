# CB Feature Definition

|概念変数|採用列名|参照列|区分|元区分|最終採用対象|今回の扱い|置換先|理由|採用不能理由|
|---|---|---|---|---|---|---|---|---|---|
|空中戦勝率|aerial_duel_win_rate_pct|空中戦, 空中戦勝率(%)|exact|exact|yes|adopted||CB の空中対応を直接説明できるため採用。||
|タックル奪取率|tackle_win_rate_pct|タックル, タックル奪取率(%)|exact|exact|yes|adopted||対人守備の成功率として解釈しやすいため採用。||
|インターセプト_per90|interceptions_per90|インターセプト, 出場時間|exact|exact|yes|adopted||読みでの守備関与を直接表すため採用。||
|ブロック_per90|blocks_per90|ブロック, 出場時間|exact|exact|yes|adopted||総ブロック回数は守備強度を直接表せるため採用。||
|クリア_per90|clearances_per90|クリア, 出場時間|exact|exact|yes|adopted||危険除去の頻度として解釈しやすいため採用。||
|パス成功率|pass_success_rate_pct|パス, パス成功率(%)|exact|exact|yes|adopted||保持時の安定性を示す直接指標として採用。||
|前進パス成功数_per90|successful_forward_passes_per90|前方向パス, 前方向パス成功率(%), 出場時間|exact|exact|yes|adopted||line break proxy よりも前進配球そのものを実測する方が説明しやすいため採用。||
|ロングパス成功数_per90|successful_long_passes_per90|ロングパス, ロングパス成功率(%), 出場時間|exact|exact|yes|adopted||長い配球の実測値として採用。||
|中加速回数_per_match|medaccel_count_full_all_per_match|Medium Acceleration Count|exact|exact|yes|adopted||守備対応時の機動力を具体的に見られるため採用。||
|高加速回数_per_match|highaccel_count_full_all_per_match|High Acceleration Count|exact|exact|yes|adopted||高強度対応の頻度として解釈しやすいため採用。||
|psv99_per_match|psv99_per_match|PSV-99|dropped|exact|no|dropped||総合スコアより個別走行指標の方がクラスタ解釈に向くため不採用。|身体能力は加速系の実測列で代替した。|
|count_track_run_on_ball_engagements_per_match|track_run_proxy_per_match|Change of Direction Count|dropped|proxy_weak|no|dropped||方向転換回数だけでは track run を説明しにくく、weak proxy を残す優先度が低いため不採用。|概念との対応が弱い。|
|自陣PA内でのクリア|def_penalty_area_clearance_proxy_per90|クリア, 出場時間|dropped|proxy_medium|no|dropped|clearances_per90|自陣PA内限定ではないため、総クリア_per90 を実測列として採用した。|ゾーン限定で解釈できないため proxy 名のままは不採用。|
|count_affected_line_break_on_ball_engagements_per_match|affected_line_break_proxy_per90|前方向パス, 前方向パス成功率(%), 出場時間|dropped|proxy_medium|no|dropped|successful_forward_passes_per90|line break の直接列はなく、前進配球は successful_forward_passes_per90 で素直に扱う方がよい。|proxy 名と実測値のずれが大きいため不採用。|
|count_line_breaks_per_match|line_break_proxy_per90|前方向パス, 出場時間|dropped|proxy_medium|no|dropped|successful_forward_passes_per90|前方向パス頻度を line break と呼ぶと解釈がずれるため不採用。|実際に使うなら前方向パス成功数の方が説明しやすい。|
|前方へのパス成功割合|forward_pass_success_rate_pct|前方向パス, 前方向パス成功率(%)|dropped|exact|no|dropped||前進の質は保持しつつ、量を表す successful_forward_passes_per90 を優先した。|変数数を絞るため volume 指標を優先。|
|キャリーによる30m進入|carry_into_30m_proxy_per90|30m進入, 出場時間|unavailable|proxy_medium|no|unavailable||2024 J3 に 30m進入の元ファイルがなく、CB では定数化していたため不採用。|2025 側のみで欠損が多く、かつ carry 起点を識別できない。|
