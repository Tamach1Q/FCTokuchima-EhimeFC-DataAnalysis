"""
新規ポジション分析で使う共通定義。
"""

from __future__ import annotations

FW_Z_COLUMNS = [
    "z_shot_conversion_rate_pct",
    "z_out_box_shots_per90",
    "z_box_shots_per90",
    "z_shot_on_target_rate_pct",
    "z_goals_per90",
    "z_aerial_wins_per90",
    "z_successful_forward_passes_per90",
    "z_last_passes_per90",
    "z_attacking_third_gains_per90",
    "z_sprint_count_full_all_per_match",
]

FW_FEATURE_LABELS = {
    "z_shot_conversion_rate_pct": "決定率",
    "z_out_box_shots_per90": "ボックス外シュート_per90",
    "z_box_shots_per90": "ボックス内シュート_per90",
    "z_shot_on_target_rate_pct": "枠内率",
    "z_goals_per90": "得点_per90",
    "z_aerial_wins_per90": "空中戦勝利数_per90",
    "z_successful_forward_passes_per90": "前進パス成功数_per90",
    "z_last_passes_per90": "ラストパス_per90",
    "z_attacking_third_gains_per90": "攻撃3rd奪回_per90",
    "z_sprint_count_full_all_per_match": "スプリント回数_per_match",
}

FW_THEME_GROUPS = {
    "フィニッシュ寄り": [
        "z_shot_conversion_rate_pct",
        "z_box_shots_per90",
        "z_shot_on_target_rate_pct",
        "z_goals_per90",
    ],
    "空中戦・前進関与寄り": [
        "z_aerial_wins_per90",
        "z_successful_forward_passes_per90",
        "z_last_passes_per90",
    ],
    "前線守備・回収寄り": [
        "z_attacking_third_gains_per90",
        "z_sprint_count_full_all_per_match",
    ],
    "ミドルレンジ関与寄り": [
        "z_out_box_shots_per90",
        "z_last_passes_per90",
    ],
}

FW_THEME_LABEL_CANDIDATES = {
    "フィニッシュ寄り": "フィニッシュ型候補",
    "空中戦・前進関与寄り": "空中戦・前進関与型候補",
    "前線守備・回収寄り": "前線守備・回収型候補",
    "ミドルレンジ関与寄り": "ミドルレンジ関与型候補",
}

SH_Z_COLUMNS = [
    "z_sprint_distance_full_all_per_match",
    "z_hsr_count_full_all_per_match",
    "z_dribble_success_rate_pct",
    "z_crosses_per90",
    "z_cross_success_rate_pct",
    "z_last_passes_per90",
    "z_pa_entry_per90",
    "z_shot_conversion_rate_pct",
    "z_regain_within_5s_per90",
]

SH_FEATURE_LABELS = {
    "z_sprint_distance_full_all_per_match": "スプリント距離_per_match",
    "z_hsr_count_full_all_per_match": "HSR回数_per_match",
    "z_dribble_success_rate_pct": "ドリブル成功率",
    "z_crosses_per90": "クロス数_per90",
    "z_cross_success_rate_pct": "クロス成功率",
    "z_last_passes_per90": "ラストパス_per90",
    "z_pa_entry_per90": "PA進入_per90",
    "z_shot_conversion_rate_pct": "決定率",
    "z_regain_within_5s_per90": "ロスト後5秒未満リゲイン_per90",
}

SH_THEME_GROUPS = {
    "縦突破寄り": [
        "z_sprint_distance_full_all_per_match",
        "z_hsr_count_full_all_per_match",
        "z_dribble_success_rate_pct",
        "z_pa_entry_per90",
    ],
    "クロス供給寄り": [
        "z_crosses_per90",
        "z_cross_success_rate_pct",
    ],
    "フィニッシュ関与寄り": [
        "z_last_passes_per90",
        "z_shot_conversion_rate_pct",
        "z_pa_entry_per90",
    ],
    "守備回収寄り": [
        "z_regain_within_5s_per90",
        "z_hsr_count_full_all_per_match",
    ],
}

SH_THEME_LABEL_CANDIDATES = {
    "縦突破寄り": "縦突破型候補",
    "クロス供給寄り": "クロス供給型候補",
    "フィニッシュ関与寄り": "フィニッシュ関与型候補",
    "守備回収寄り": "守備回収型候補",
}

CMF_Z_COLUMNS = [
    "z_running_distance_full_all_per_match",
    "z_ball_gains_per90",
    "z_interceptions_per90",
    "z_pass_success_rate_pct",
    "z_forward_pass_success_rate_pct",
    "z_short_pass_share_pct",
    "z_long_pass_share_pct",
    "z_opponent_half_gain_share_pct",
]

CMF_FEATURE_LABELS = {
    "z_running_distance_full_all_per_match": "走行距離_per_match",
    "z_ball_gains_per90": "ボール奪取_per90",
    "z_interceptions_per90": "インターセプト_per90",
    "z_pass_success_rate_pct": "パス成功率",
    "z_forward_pass_success_rate_pct": "前進パス成功率",
    "z_short_pass_share_pct": "ショートパス比率",
    "z_long_pass_share_pct": "ロングパス比率",
    "z_opponent_half_gain_share_pct": "敵陣奪回比率",
}

CMF_THEME_GROUPS = {
    "ボールハント寄り": [
        "z_ball_gains_per90",
        "z_interceptions_per90",
        "z_opponent_half_gain_share_pct",
    ],
    "ゲームメイク寄り": [
        "z_pass_success_rate_pct",
        "z_forward_pass_success_rate_pct",
        "z_short_pass_share_pct",
    ],
    "ボックストゥボックス寄り": [
        "z_running_distance_full_all_per_match",
        "z_long_pass_share_pct",
        "z_opponent_half_gain_share_pct",
    ],
}

CMF_THEME_LABEL_CANDIDATES = {
    "ボールハント寄り": "ボールハンター型候補",
    "ゲームメイク寄り": "ゲームオーガナイザー型候補",
    "ボックストゥボックス寄り": "ボックストゥボックス型候補",
}

ST_Z_COLUMNS = [
    "z_shot_conversion_rate_pct",
    "z_box_shots_per90",
    "z_goals_per90",
    "z_sprint_count_full_all_per_match",
    "z_last_passes_per90",
    "z_successful_through_passes_per90",
    "z_attacking_third_gains_per90",
]

ST_FEATURE_LABELS = {
    "z_shot_conversion_rate_pct": "決定率",
    "z_box_shots_per90": "ボックス内シュート_per90",
    "z_goals_per90": "得点_per90",
    "z_sprint_count_full_all_per_match": "スプリント回数_per_match",
    "z_last_passes_per90": "ラストパス_per90",
    "z_successful_through_passes_per90": "スルーパス成功数_per90",
    "z_attacking_third_gains_per90": "攻撃3rd奪回_per90",
}

ST_ARCHETYPE_LABELS = (
    "ラインレシーバー",
    "シャドーストライカー",
    "ハイプレス・イニシエーター",
)
