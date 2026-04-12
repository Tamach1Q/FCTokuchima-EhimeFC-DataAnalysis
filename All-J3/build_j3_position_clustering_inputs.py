"""
J3 ポジション別クラスタリング前処理入力作成
===========================================

出力:
  All-J3/J3_csv/SC_position_clustering/
    README.md
    CB|SB|CMF|SH|ST|FW/
      *_players_raw.csv
      *_features_raw.csv
      *_features_preprocessed.csv
      *_feature_definition.md
      *_missing_report.md
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from rebuild_sc_detailed_positions import (
    TEAM_NAME_MAP,
    build_team_season_lookup,
    canonicalize_sc_player_name,
    canonicalize_team_name,
    normalize_name,
)

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "J3_csv"
OUTPUT_ROOT = CSV_DIR / "SC_position_clustering"

BASE_MERGED_FILE = CSV_DIR / "j3_2024_2025_valid_name_mapping_with_positions.csv"
POSITION_MAPPING_FILE = CSV_DIR / "sc_position_analysis_mapping.csv"
JOIN_REPORT_FILE = CSV_DIR / "sc_position_join_quality_report.csv"

RAW_BASE_DIR = Path(
    os.environ.get(
        "RAW_DATA_BASE_DIR",
        "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp"
        "/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ",
    )
)
FB_DIR = RAW_BASE_DIR / "football box"
SC_DIR = RAW_BASE_DIR / "skill corner"

TARGET_YEARS = ("2024", "2025")
TARGET_LEAGUE = "J3"
POSITION_CODES = ("CB", "SB", "CMF", "SH", "ST", "FW")

FB_MERGE_KEYS = ["season", "チーム名", "選手名", "試合日"]
PLAYER_RAW_COLUMNS = [
    "対象年度",
    "対象リーグ",
    "FB_Name",
    "SC_Name",
    "FB_Pos",
    "SC_Position_Group",
    "FB_Minutes",
    "SC_Minutes",
    "analysis_position_code",
    "analysis_position_jp",
    "analysis_position_source",
    "SC_Primary_Position",
    "SC_Primary_Position_Group",
    "player_name_normalized",
    "dominant_team_name",
    "team_season_signature",
    "fb_dominant_team_name",
    "fb_team_season_signature",
    "join_method",
    "join_method_detail",
    "join_status",
    "Notes",
]

SC_COLUMN_ALIASES = {
    "Player": ["Player", "player_name"],
    "Team": ["Team", "team_name"],
    "Position": ["Position", "position"],
    "Position Group": ["Position Group", "position_group"],
    "Minutes": ["Minutes", "minutes_full_all"],
    "PSV-99": ["PSV-99", "psv99"],
    "Distance": ["Distance", "total_distance_full_all"],
    "M/min": ["M/min", "total_metersperminute_full_all"],
    "HI Distance": ["HI Distance", "hi_distance_full_all"],
    "HSR Count": ["HSR Count", "hsr_count_full_all"],
    "Sprint Distance": ["Sprint Distance", "sprint_distance_full_all"],
    "Sprint Count": ["Sprint Count", "sprint_count_full_all"],
    "Medium Acceleration Count": ["Medium Acceleration Count", "medaccel_count_full_all"],
    "High Acceleration Count": ["High Acceleration Count", "highaccel_count_full_all"],
    "Explosive Acceleration to Sprint Count": [
        "Explosive Acceleration to Sprint Count",
        "explacceltosprint_count_full_all",
    ],
    "Change of Direction Count": ["Change of Direction Count", "cod_count_full_all"],
}

FB_NUMERIC_COLUMNS = [
    "出場時間",
    "ゴール",
    "シュート",
    "PA内シュート",
    "PA内ゴール",
    "PA外ゴール",
    "PA外シュート",
    "PA内シュート決定率(%)",
    "PA内シュート枠内率(%)",
    "PA外シュート決定率(%)",
    "PA外シュート枠内率(%)",
    "PA進入",
    "ボールゲイン",
    "パス",
    "ラストパス",
    "ドリブル",
    "ドリブル成功率(%)",
    "クロス",
    "クロス成功率(%)",
    "スルーパス",
    "スルーパス成功率(%)",
    "タックル",
    "タックル奪取率(%)",
    "クリア",
    "ブロック",
    "インターセプト",
    "空中戦",
    "空中戦勝率(%)",
    "前方向パス",
    "前方向パス成功率(%)",
    "ショートパス",
    "ミドルパス",
    "ロングパス",
    "ロングパス成功率(%)",
    "前方向ロングパス",
    "前方向ロングパス成功率(%)",
    "DTからパス",
    "MTからパス",
    "ATからパス",
    "ATでの回数",
    "MTでの回数",
    "相手陣での回数",
    "ニアゾーン進入",
    "PA脇進入",
    "30m進入",
]


def feature(
    concept: str,
    feature_key: str,
    source_column: str,
    match_type: str,
    reason: str,
    source_raw_columns: list[str],
) -> dict[str, object]:
    return {
        "concept_name": concept,
        "feature_key": feature_key,
        "source_column": source_column,
        "match_type": match_type,
        "reason": reason,
        "source_raw_columns": source_raw_columns,
    }


POSITION_FEATURES: dict[str, list[dict[str, object]]] = {
    "CB": [
        feature("空中戦勝率", "aerial_duel_win_rate_pct", "aerial_duel_win_rate_pct", "exact", "Football Box 守備サマリーの空中戦勝率をそのまま採用。", ["空中戦", "空中戦勝率(%)"]),
        feature("タックル奪取率", "tackle_win_rate_pct", "tackle_win_rate_pct", "exact", "Football Box 守備サマリーのタックル奪取率をそのまま採用。", ["タックル", "タックル奪取率(%)"]),
        feature("インターセプト", "interceptions_per90", "interceptions_per90", "exact", "Football Box 守備サマリーのインターセプトを per90 化。", ["インターセプト", "出場時間"]),
        feature("ブロック(シュート)", "shot_block_proxy_per90", "blocks_per90", "proxy_medium", "ブロック種別内訳がないため、総ブロックをシュートブロックの proxy とした。", ["ブロック", "出場時間"]),
        feature("psv99_per_match", "psv99_per_match", "psv99_per_match", "exact", "SkillCorner physical の PSV-99 試合平均。", ["PSV-99"]),
        feature("medaccel_count_full_all_per_match", "medaccel_count_full_all_per_match", "medaccel_count_full_all_per_match", "exact", "SkillCorner physical の中加速回数試合平均。", ["Medium Acceleration Count"]),
        feature("highaccel_count_full_all_per_match", "highaccel_count_full_all_per_match", "highaccel_count_full_all_per_match", "exact", "SkillCorner physical の高加速回数試合平均。", ["High Acceleration Count"]),
        feature("count_track_run_on_ball_engagements_per_match", "track_run_proxy_per_match", "cod_count_full_all_per_match", "proxy_weak", "on-ball track run 直接列がないため、方向転換回数の試合平均で代替。", ["Change of Direction Count"]),
        feature("自陣PA内でのクリア", "def_penalty_area_clearance_proxy_per90", "clearances_per90", "proxy_medium", "自陣PA内限定のクリア列がないため、総クリアを proxy とした。", ["クリア", "出場時間"]),
        feature("count_affected_line_break_on_ball_engagements_per_match", "affected_line_break_proxy_per90", "successful_forward_passes_per90", "proxy_medium", "line break 直接列がないため、成功した前方向パスを最も近い proxy とした。", ["前方向パス", "前方向パス成功率(%)", "出場時間"]),
        feature("count_line_breaks_per_match", "line_break_proxy_per90", "forward_passes_per90", "proxy_medium", "line break 直接列がないため、前方向パス頻度を proxy とした。", ["前方向パス", "出場時間"]),
        feature("パス成功率", "pass_success_rate_pct", "pass_success_rate_pct", "exact", "Football Box 攻撃サマリーのパス成功率を再計算して採用。", ["パス", "パス成功率(%)"]),
        feature("前方へのパス成功割合", "forward_pass_success_rate_pct", "forward_pass_success_rate_pct", "exact", "方向別パスの前方向パス成功率を採用。", ["前方向パス", "前方向パス成功率(%)"]),
        feature("ロングパス成功(30m-)", "successful_long_passes_per90", "successful_long_passes_per90", "proxy_strong", "距離別パスのロングパス成功数 per90 を 30m- 成功の proxy とした。", ["ロングパス", "ロングパス成功率(%)", "出場時間"]),
        feature("キャリーによる30m進入", "carry_into_30m_proxy_per90", "zone30_entries_per90", "proxy_medium", "carry 起点は識別できないため、30m進入回数を proxy とした。", ["30m進入", "出場時間"]),
    ],
    "SB": [
        feature("psv99_per_match", "psv99_per_match", "psv99_per_match", "exact", "SkillCorner physical の PSV-99 試合平均。", ["PSV-99"]),
        feature("total_metersperminute_full_all_per_match", "total_metersperminute_full_all_per_match", "total_metersperminute_full_all_per_match", "exact", "SkillCorner physical の M/min 試合平均。", ["M/min"]),
        feature("hi_distance_full_all_per_match", "hi_distance_full_all_per_match", "hi_distance_full_all_per_match", "exact", "SkillCorner physical の HI Distance 試合平均。", ["HI Distance"]),
        feature("sprint_count_full_all_per_match", "sprint_count_full_all_per_match", "sprint_count_full_all_per_match", "exact", "SkillCorner physical の Sprint Count 試合平均。", ["Sprint Count"]),
        feature("dropping_off_runs", "dropping_off_runs_proxy_per90", "mid_third_passes_per90", "proxy_weak", "dropping off run 直接列がないため、中盤で受ける役割に近い MTからパス頻度を proxy とした。", ["MTからパス", "出場時間"]),
        feature("overlap_runs", "overlap_runs_proxy_per90", "crosses_per90", "proxy_medium", "overlap の直接列がないため、外側の走りから生じやすいクロス頻度を proxy とした。", ["クロス", "出場時間"]),
        feature("underlap_runs", "underlap_runs_proxy_per90", "half_space_entries_per90", "proxy_strong", "underlap は PA脇進入とエリア特性が近いため最優先 proxy とした。", ["PA脇進入", "出場時間"]),
        feature("クロス成功率", "cross_success_rate_pct", "cross_success_rate_pct", "exact", "Football Box 攻撃サマリーのクロス成功率を再計算して採用。", ["クロス", "クロス成功率(%)"]),
        feature("アーリークロス成功率", "early_cross_proxy_success_rate_pct", "forward_long_pass_success_rate_pct", "proxy_medium", "アーリークロス専用列がないため、前方向ロングパス成功率を proxy とした。", ["前方向ロングパス", "前方向ロングパス成功率(%)"]),
        feature("PA進入", "pa_entry_per90", "pa_entry_per90", "exact", "PA進入を per90 化して採用。", ["PA進入", "出場時間"]),
        feature("タックル奪取率", "tackle_win_rate_pct", "tackle_win_rate_pct", "exact", "Football Box 守備サマリーのタックル奪取率。", ["タックル", "タックル奪取率(%)"]),
        feature("ブロック(クロス)", "cross_block_proxy_per90", "blocks_per90", "proxy_medium", "クロスブロックの内訳がないため、総ブロックを proxy とした。", ["ブロック", "出場時間"]),
        feature("pulling_half_space_runs", "pulling_half_space_runs_proxy_per90", "half_space_entries_per90", "proxy_strong", "half-space run と PA脇進入は侵入エリアが近いため。", ["PA脇進入", "出場時間"]),
        feature("count_successful_on_ball_engagements_per_match", "successful_on_ball_actions_per90", "successful_on_ball_actions_per90", "proxy_medium", "on-ball engagement 成功数の直接列がないため、成功クロス・スルーパス・ドリブル・前方向パスの合算を proxy とした。", ["クロス", "クロス成功率(%)", "スルーパス", "スルーパス成功率(%)", "ドリブル", "ドリブル成功率(%)", "前方向パス", "前方向パス成功率(%)"]),
        feature("AT進入", "attacking_third_entry_proxy_per90", "zone30_entries_per90", "proxy_medium", "AT進入専用列がないため、30m進入頻度を proxy とした。", ["30m進入", "出場時間"]),
    ],
    "CMF": [
        feature("total_distance_full_all_per_match", "total_distance_full_all_per_match", "total_distance_full_all_per_match", "exact", "SkillCorner physical の Distance 試合平均。", ["Distance"]),
        feature("こぼれ球奪取", "loose_ball_gain_proxy_per90", "ball_gains_per90", "proxy_medium", "こぼれ球限定列がないため、総ボールゲインを proxy とした。", ["ボールゲイン", "出場時間"]),
        feature("MTでの空中戦勝率", "mid_third_aerial_win_rate_proxy_pct", "aerial_duel_win_rate_pct", "proxy_medium", "MT限定列がないため、総空中戦勝率で代替。", ["空中戦", "空中戦勝率(%)"]),
        feature("MTでのタックル奪取率", "mid_third_tackle_win_rate_proxy_pct", "tackle_win_rate_pct", "proxy_weak", "MT限定列がないため、総タックル奪取率を proxy とした。", ["タックル", "タックル奪取率(%)"]),
        feature("PA外のシュートの決定率", "out_box_shot_conversion_rate_pct", "out_box_shot_conversion_rate_pct", "exact", "エリア別シュートの PA外シュート決定率を再計算して採用。", ["PA外シュート", "PA外ゴール"]),
        feature("枠内シュート率", "shot_on_target_rate_pct", "shot_on_target_rate_pct", "exact", "PA内/外の枠内率と本数から全体の枠内シュート率を再計算。", ["PA内シュート", "PA内シュート枠内率(%)", "PA外シュート", "PA外シュート枠内率(%)"]),
        feature("count_interception_on_ball_engagements_per_match", "interception_engagement_proxy_per90", "interceptions_per90", "proxy_medium", "interception on-ball engagement の直接列がないため、インターセプト頻度を proxy とした。", ["インターセプト", "出場時間"]),
        feature("count_pressure_on_ball_engagements_per_match", "pressure_engagement_proxy_per90", "tackles_per90", "proxy_weak", "pressure 直接列がないため、守備圧力に近いタックル頻度を proxy とした。", ["タックル", "出場時間"]),
        feature("パス成功率", "pass_success_rate_pct", "pass_success_rate_pct", "exact", "Football Box 攻撃サマリーのパス成功率。", ["パス", "パス成功率(%)"]),
        feature("前方へのパス成功割合", "forward_pass_success_rate_pct", "forward_pass_success_rate_pct", "exact", "方向別パスの前方向パス成功率。", ["前方向パス", "前方向パス成功率(%)"]),
        feature("ショートパス(0-15m)割合", "short_pass_share_pct", "short_pass_share_pct", "proxy_strong", "距離別パスのショートパス割合を 0-15m proxy とした。", ["ショートパス", "ミドルパス", "ロングパス"]),
        feature("ロングパス(30m-)割合", "long_pass_share_pct", "long_pass_share_pct", "proxy_strong", "距離別パスのロングパス割合を 30m- proxy とした。", ["ショートパス", "ミドルパス", "ロングパス"]),
        feature("count_forward_momentum_all_possessions_per_match", "forward_momentum_proxy_per90", "zone30_entries_per90", "proxy_medium", "forward momentum の直接列がないため、30m進入頻度を proxy とした。", ["30m進入", "出場時間"]),
        feature("バイタルエリア進入", "vital_area_entry_proxy_per90", "near_zone_entries_per90", "proxy_strong", "バイタルエリア進入に最も近い Football Box のニアゾーン進入を採用。", ["ニアゾーン進入", "出場時間"]),
        feature("敵陣こぼれ球奪取率", "opponent_half_loose_ball_gain_share_proxy_pct", "opponent_half_gain_share_pct", "proxy_strong", "敵陣こぼれ球奪取率の直接列がないため、相手陣割合を最も近い proxy とした。", ["ボールゲイン", "相手陣での回数"]),
    ],
    "SH": [
        feature("psv99_per_match", "psv99_per_match", "psv99_per_match", "exact", "SkillCorner physical の PSV-99 試合平均。", ["PSV-99"]),
        feature("アシストクロス", "assist_cross_proxy_per90", "successful_crosses_per90", "proxy_medium", "アシストクロス列がないため、成功クロス頻度を proxy とした。", ["クロス", "クロス成功率(%)", "出場時間"]),
        feature("sprint_distance_full_all_per_match", "sprint_distance_full_all_per_match", "sprint_distance_full_all_per_match", "exact", "SkillCorner physical の Sprint Distance 試合平均。", ["Sprint Distance"]),
        feature("dropping_off_runs", "dropping_off_runs_proxy_per90", "passes_per90", "proxy_weak", "dropping off run 直接列がないため、受けに降りる関与として総パス頻度を proxy とした。", ["パス", "出場時間"]),
        feature("count_pressure_on_ball_engagements_per_match", "pressure_engagement_proxy_per90", "tackles_per90", "proxy_weak", "pressure の直接列がないため、タックル頻度を proxy とした。", ["タックル", "出場時間"]),
        feature("count_consecutive_on_ball_engagements_per_match", "consecutive_on_ball_engagement_proxy_per90", "successful_on_ball_actions_per90", "proxy_medium", "連続 on-ball engagement の直接列がないため、成功した on-ball action の合算を proxy とした。", ["クロス", "クロス成功率(%)", "スルーパス", "スルーパス成功率(%)", "ドリブル", "ドリブル成功率(%)", "前方向パス", "前方向パス成功率(%)"]),
        feature("count_above_hsr_on_ball_engagements_per_match", "above_hsr_engagement_proxy_per_match", "hsr_count_full_all_per_match", "proxy_medium", "HSR を上回る on-ball engagement 直接列がないため、HSR Count 試合平均を proxy とした。", ["HSR Count"]),
        feature("ドリブル成功率", "dribble_success_rate_pct", "dribble_success_rate_pct", "exact", "Football Box 攻撃サマリーのドリブル成功率。", ["ドリブル", "ドリブル成功率(%)"]),
        feature("キャリーによるPA進入", "carry_into_box_proxy_per90", "pa_entry_per90", "proxy_weak", "carry 起点の判別はできないため、PA進入頻度を proxy とした。", ["PA進入", "出場時間"]),
        feature("クロス受", "cross_reception_proxy_per90", "box_shots_per90", "proxy_weak", "クロス受けの直接列がないため、PA内シュート頻度を proxy とした。", ["PA内シュート", "出場時間"]),
        feature("シュート決定率", "shot_conversion_rate_pct", "shot_conversion_rate_pct", "exact", "基本サマリーのゴールと攻撃サマリーのシュートから全体決定率を再計算。", ["ゴール", "シュート"]),
        feature("pulling_wide_runs", "pulling_wide_runs_proxy_per90", "crosses_per90", "proxy_medium", "wide run の直接列がないため、幅を取った結果として表れやすいクロス頻度を proxy とした。", ["クロス", "出場時間"]),
        feature("クロス成功率", "cross_success_rate_pct", "cross_success_rate_pct", "exact", "Football Box 攻撃サマリーのクロス成功率。", ["クロス", "クロス成功率(%)"]),
        feature("敵陣PA内ボールゲイン", "opponent_box_ball_gain_proxy_per90", "attacking_third_gains_per90", "proxy_medium", "敵陣PA内限定列がないため、ATでのボールゲインを proxy とした。", ["ATでの回数", "出場時間"]),
        feature("ドリブルからのシュート", "dribble_shot_proxy_per90", "successful_dribbles_per90", "proxy_weak", "ドリブル後シュートの連結列がないため、成功ドリブル頻度を proxy とした。", ["ドリブル", "ドリブル成功率(%)", "出場時間"]),
    ],
    "ST": [
        feature("キャリーによるPA進入", "carry_into_box_proxy_per90", "pa_entry_per90", "proxy_weak", "carry 起点は識別できないため、PA進入頻度を proxy とした。", ["PA進入", "出場時間"]),
        feature("count_8m_carry_at_speed_all_possessions_per_match", "speed_carry_proxy_per_match", "explacceltosprint_count_full_all_per_match", "proxy_weak", "高速キャリー直接列がないため、Explosive Acceleration to Sprint Count 試合平均を proxy とした。", ["Explosive Acceleration to Sprint Count"]),
        feature("ATタッチ", "attacking_third_touch_proxy_per90", "attacking_third_passes_per90", "proxy_medium", "ATタッチ直接列がないため、ATからパス頻度を proxy とした。", ["ATからパス", "出場時間"]),
        feature("count_received_in_open_space_all_possessions_per_match", "open_space_receive_proxy_per90", "zone30_entries_per90", "proxy_medium", "open space reception 直接列がないため、30m進入頻度を proxy とした。", ["30m進入", "出場時間"]),
        feature("coming_short_runs", "coming_short_runs_proxy_per90", "passes_per90", "proxy_weak", "coming short run 直接列がないため、受けに降りる関与として総パス頻度を proxy とした。", ["パス", "出場時間"]),
        feature("runs_in_behind", "runs_in_behind_proxy_per_match", "sprint_count_full_all_per_match", "proxy_weak", "裏抜け直接列がないため、Sprint Count 試合平均を proxy とした。", ["Sprint Count"]),
        feature("xthreat_received_off_ball_runs_per_match", "xthreat_received_runs_proxy_per90", "near_zone_entries_per90", "proxy_weak", "xThreat 直接列がないため、危険度の高い受け位置に近いニアゾーン進入頻度を proxy とした。", ["ニアゾーン進入", "出場時間"]),
        feature("ポケット進入", "pocket_entry_proxy_per90", "half_space_entries_per90", "proxy_strong", "ポケット進入に最も近い Football Box の PA脇進入を採用。", ["PA脇進入", "出場時間"]),
        feature("セカンドアシスト", "second_assist_proxy_per90", "last_passes_per90", "proxy_medium", "セカンドアシスト列がないため、ラストパス頻度を proxy とした。", ["ラストパス", "出場時間"]),
        feature("シュート決定率", "shot_conversion_rate_pct", "shot_conversion_rate_pct", "exact", "基本サマリーのゴールと攻撃サマリーのシュートから全体決定率を再計算。", ["ゴール", "シュート"]),
        feature("アシストスルーパス", "assist_through_pass_proxy_per90", "successful_through_passes_per90", "proxy_medium", "アシスト付きスルーパス列がないため、成功スルーパス頻度を proxy とした。", ["スルーパス", "スルーパス成功率(%)", "出場時間"]),
        feature("ATでのタックル奪取率", "attacking_third_tackle_win_proxy_pct", "tackle_win_rate_pct", "proxy_weak", "AT限定タックル奪取率がないため、総タックル奪取率を proxy とした。", ["タックル", "タックル奪取率(%)"]),
        feature("count_pressure_on_ball_engagements_per_match", "pressure_engagement_proxy_per90", "tackles_per90", "proxy_weak", "pressure の直接列がないため、タックル頻度を proxy とした。", ["タックル", "出場時間"]),
        feature("dropping_off_runs", "dropping_off_runs_proxy_per90", "passes_per90", "proxy_weak", "dropping off run 直接列がないため、総パス頻度を proxy とした。", ["パス", "出場時間"]),
        feature("1stシュート", "first_shot_proxy_per90", "box_shots_per90", "proxy_weak", "1stシュート列がないため、最も近い proxy として PA内シュート頻度を採用。", ["PA内シュート", "出場時間"]),
    ],
    "FW": [
        feature("シュート決定率", "shot_conversion_rate_pct", "shot_conversion_rate_pct", "exact", "基本サマリーのゴールと攻撃サマリーのシュートから全体決定率を再計算。", ["ゴール", "シュート"]),
        feature("PA外シュート数", "out_box_shots_per90", "out_box_shots_per90", "exact", "PA外シュート数を per90 化。", ["PA外シュート", "出場時間"]),
        feature("PA内シュート数", "box_shots_per90", "box_shots_per90", "exact", "PA内シュート数を per90 化。", ["PA内シュート", "出場時間"]),
        feature("枠内シュート率", "shot_on_target_rate_pct", "shot_on_target_rate_pct", "exact", "PA内/外の枠内数から全体枠内率を再計算。", ["PA内シュート", "PA内シュート枠内率(%)", "PA外シュート", "PA外シュート枠内率(%)"]),
        feature("空中戦勝利でボール保持", "aerial_retain_proxy_pct", "aerial_duel_win_rate_pct", "proxy_medium", "保持に繋がった内訳がないため、空中戦勝率を proxy とした。", ["空中戦", "空中戦勝率(%)"]),
        feature("空中戦勝利でパス", "aerial_pass_proxy_per90", "aerial_wins_per90", "proxy_medium", "パスに繋がった内訳がないため、空中戦勝利数 per90 を proxy とした。", ["空中戦", "空中戦勝率(%)", "出場時間"]),
        feature("count_pressure_on_ball_engagements_per_match", "pressure_engagement_proxy_per90", "tackles_per90", "proxy_weak", "pressure の直接列がないため、タックル頻度を proxy とした。", ["タックル", "出場時間"]),
        feature("count_consecutive_on_ball_engagements_per_match", "consecutive_on_ball_engagement_proxy_per90", "successful_on_ball_actions_per90", "proxy_medium", "連続 on-ball engagement の直接列がないため、成功 on-ball action 合算を proxy とした。", ["クロス", "クロス成功率(%)", "スルーパス", "スルーパス成功率(%)", "ドリブル", "ドリブル成功率(%)", "前方向パス", "前方向パス成功率(%)"]),
        feature("runs_in_behind", "runs_in_behind_proxy_per_match", "sprint_count_full_all_per_match", "proxy_weak", "裏抜け直接列がないため、Sprint Count 試合平均を proxy とした。", ["Sprint Count"]),
        feature("count_received_passing_option_per_match", "passing_option_receive_proxy_per90", "attacking_third_passes_per90", "proxy_medium", "passing option reception 直接列がないため、ATでのパス関与頻度を proxy とした。", ["ATからパス", "出場時間"]),
        feature("xthreat_passing_option_per_match", "xthreat_passing_option_proxy_per90", "near_zone_entries_per90", "proxy_weak", "xThreat passing option の直接列がないため、危険度の高い受け位置に近いニアゾーン進入頻度を proxy とした。", ["ニアゾーン進入", "出場時間"]),
        feature("前方へのパス成功", "successful_forward_passes_per90", "successful_forward_passes_per90", "proxy_strong", "前方へのパス成功割合ではなく成功数を per90 で採用。", ["前方向パス", "前方向パス成功率(%)", "出場時間"]),
        feature("ATでのタックル奪取", "attacking_third_tackle_gain_proxy_per90", "attacking_third_gains_per90", "proxy_medium", "ATでのタックル奪取直接列がないため、ATでのボールゲイン頻度を proxy とした。", ["ATでの回数", "出場時間"]),
        feature("ゴール", "goals_per90", "goals_per90", "exact", "基本サマリーのゴールを per90 化。", ["ゴール", "出場時間"]),
        feature("1stシュート", "first_shot_proxy_per90", "shots_per90", "proxy_weak", "1stシュート列がないため、総シュート頻度を proxy とした。", ["シュート", "出場時間"]),
    ],
}


def ensure_numeric(df: pd.DataFrame, columns: list[str]) -> None:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


def ratio_or_nan(numerator: float, denominator: float) -> float:
    if pd.isna(denominator):
        return np.nan
    if denominator == 0:
        return 0.0
    if pd.isna(numerator):
        numerator = 0.0
    return float(numerator) / float(denominator) * 100


def per90_or_nan(values: pd.Series, minutes: pd.Series) -> float:
    valid = values.notna()
    if not valid.any():
        return np.nan
    minutes_sum = minutes.loc[valid].sum()
    if pd.isna(minutes_sum) or minutes_sum == 0:
        return 0.0
    value_sum = values.loc[valid].sum()
    return float(value_sum) / float(minutes_sum) * 90


def sum_or_nan(series: pd.Series) -> float:
    if series.notna().sum() == 0:
        return np.nan
    return float(series.sum())


def compute_success_count(df: pd.DataFrame, count_col: str, rate_col: str, output_col: str) -> None:
    if count_col not in df.columns or rate_col not in df.columns:
        df[output_col] = np.nan
        return
    df[output_col] = (
        pd.to_numeric(df[count_col], errors="coerce")
        * pd.to_numeric(df[rate_col], errors="coerce")
        / 100.0
    )


def collect_fb_files() -> list[Path]:
    files: list[Path] = []
    for year in TARGET_YEARS:
        league_dir = FB_DIR / year / TARGET_LEAGUE
        files.extend(sorted(league_dir.glob("*.xlsx")))
    if not files:
        raise RuntimeError("Football Box J3 xlsx が見つかりません。")
    return files


def load_fb_match_data() -> pd.DataFrame:
    merged_df: pd.DataFrame | None = None
    for file_path in collect_fb_files():
        df = pd.read_excel(file_path, engine="openpyxl")
        df["season"] = file_path.parent.parent.name
        if merged_df is None:
            merged_df = df
            continue
        duplicate_columns = [
            col for col in df.columns if col in merged_df.columns and col not in FB_MERGE_KEYS
        ]
        df = df.drop(columns=duplicate_columns)
        merged_df = pd.merge(merged_df, df, on=FB_MERGE_KEYS, how="outer")
    if merged_df is None:
        raise RuntimeError("Football Box J3 データを読み込めませんでした。")
    ensure_numeric(merged_df, FB_NUMERIC_COLUMNS)
    return merged_df


def aggregate_fb_player_data(df_match: pd.DataFrame) -> pd.DataFrame:
    df = df_match.copy()
    compute_success_count(df, "パス", "パス成功率(%)", "successful_passes")
    compute_success_count(df, "クロス", "クロス成功率(%)", "successful_crosses")
    compute_success_count(df, "スルーパス", "スルーパス成功率(%)", "successful_through_passes")
    compute_success_count(df, "ドリブル", "ドリブル成功率(%)", "successful_dribbles")
    compute_success_count(df, "タックル", "タックル奪取率(%)", "successful_tackles")
    compute_success_count(df, "空中戦", "空中戦勝率(%)", "aerial_wins")
    compute_success_count(df, "前方向パス", "前方向パス成功率(%)", "successful_forward_passes")
    compute_success_count(df, "ロングパス", "ロングパス成功率(%)", "successful_long_passes")
    compute_success_count(
        df, "前方向ロングパス", "前方向ロングパス成功率(%)", "successful_forward_long_passes"
    )
    compute_success_count(df, "PA内シュート", "PA内シュート枠内率(%)", "box_shots_on_target")
    compute_success_count(df, "PA外シュート", "PA外シュート枠内率(%)", "out_box_shots_on_target")

    team_lookup = build_team_season_lookup(
        df,
        player_col="選手名",
        season_col="season",
        team_col="チーム名",
        minutes_col="出場時間",
        dominant_team_col="fb_dominant_team_name",
    ).rename(
        columns={
            "team_season_key": "fb_team_season_key",
            "team_season_signature": "fb_team_season_signature",
        }
    )

    records: list[dict[str, object]] = []
    for player_name, grp in df.groupby("選手名"):
        rec: dict[str, object] = {"FB_Name": player_name}
        rec["fb_total_minutes"] = sum_or_nan(grp["出場時間"])
        rec["goals_per90"] = per90_or_nan(grp["ゴール"], grp["出場時間"])
        rec["shots_per90"] = per90_or_nan(grp["シュート"], grp["出場時間"])
        rec["box_shots_per90"] = per90_or_nan(grp["PA内シュート"], grp["出場時間"])
        rec["out_box_shots_per90"] = per90_or_nan(grp["PA外シュート"], grp["出場時間"])
        rec["pa_entry_per90"] = per90_or_nan(grp["PA進入"], grp["出場時間"])
        rec["ball_gains_per90"] = per90_or_nan(grp["ボールゲイン"], grp["出場時間"])
        rec["passes_per90"] = per90_or_nan(grp["パス"], grp["出場時間"])
        rec["last_passes_per90"] = per90_or_nan(grp["ラストパス"], grp["出場時間"])
        rec["dribbles_per90"] = per90_or_nan(grp["ドリブル"], grp["出場時間"])
        rec["crosses_per90"] = per90_or_nan(grp["クロス"], grp["出場時間"])
        rec["through_passes_per90"] = per90_or_nan(grp["スルーパス"], grp["出場時間"])
        rec["tackles_per90"] = per90_or_nan(grp["タックル"], grp["出場時間"])
        rec["interceptions_per90"] = per90_or_nan(grp["インターセプト"], grp["出場時間"])
        rec["blocks_per90"] = per90_or_nan(grp["ブロック"], grp["出場時間"])
        rec["clearances_per90"] = per90_or_nan(grp["クリア"], grp["出場時間"])
        rec["forward_passes_per90"] = per90_or_nan(grp["前方向パス"], grp["出場時間"])
        rec["successful_forward_passes_per90"] = per90_or_nan(
            grp["successful_forward_passes"], grp["出場時間"]
        )
        rec["successful_long_passes_per90"] = per90_or_nan(
            grp["successful_long_passes"], grp["出場時間"]
        )
        rec["successful_crosses_per90"] = per90_or_nan(
            grp["successful_crosses"], grp["出場時間"]
        )
        rec["successful_through_passes_per90"] = per90_or_nan(
            grp["successful_through_passes"], grp["出場時間"]
        )
        rec["successful_dribbles_per90"] = per90_or_nan(
            grp["successful_dribbles"], grp["出場時間"]
        )
        rec["aerial_wins_per90"] = per90_or_nan(grp["aerial_wins"], grp["出場時間"])
        rec["mid_third_passes_per90"] = per90_or_nan(grp["MTからパス"], grp["出場時間"])
        rec["attacking_third_passes_per90"] = per90_or_nan(
            grp["ATからパス"], grp["出場時間"]
        )
        rec["attacking_third_gains_per90"] = per90_or_nan(
            grp["ATでの回数"], grp["出場時間"]
        )
        rec["opponent_half_gains_per90"] = per90_or_nan(
            grp["相手陣での回数"], grp["出場時間"]
        )
        rec["near_zone_entries_per90"] = per90_or_nan(
            grp["ニアゾーン進入"], grp["出場時間"]
        )
        rec["half_space_entries_per90"] = per90_or_nan(
            grp["PA脇進入"], grp["出場時間"]
        )
        rec["zone30_entries_per90"] = per90_or_nan(grp["30m進入"], grp["出場時間"])

        rec["pass_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_passes"]), sum_or_nan(grp["パス"])
        )
        rec["cross_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_crosses"]), sum_or_nan(grp["クロス"])
        )
        rec["dribble_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_dribbles"]), sum_or_nan(grp["ドリブル"])
        )
        rec["through_pass_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_through_passes"]), sum_or_nan(grp["スルーパス"])
        )
        rec["tackle_win_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_tackles"]), sum_or_nan(grp["タックル"])
        )
        rec["aerial_duel_win_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["aerial_wins"]), sum_or_nan(grp["空中戦"])
        )
        rec["forward_pass_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_forward_passes"]), sum_or_nan(grp["前方向パス"])
        )
        rec["long_pass_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_long_passes"]), sum_or_nan(grp["ロングパス"])
        )
        rec["forward_long_pass_success_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["successful_forward_long_passes"]), sum_or_nan(grp["前方向ロングパス"])
        )

        shot_total = sum_or_nan(grp["シュート"])
        goal_total = sum_or_nan(grp["ゴール"])
        rec["shot_conversion_rate_pct"] = ratio_or_nan(goal_total, shot_total)

        on_target_total = sum_or_nan(grp["box_shots_on_target"]) + sum_or_nan(
            grp["out_box_shots_on_target"]
        )
        all_area_shots_total = sum_or_nan(grp["PA内シュート"]) + sum_or_nan(grp["PA外シュート"])
        if pd.isna(on_target_total):
            on_target_total = np.nan
        rec["shot_on_target_rate_pct"] = ratio_or_nan(on_target_total, all_area_shots_total)

        rec["out_box_shot_conversion_rate_pct"] = ratio_or_nan(
            sum_or_nan(grp["PA外ゴール"]), sum_or_nan(grp["PA外シュート"])
        )
        distance_total = (
            sum_or_nan(grp["ショートパス"])
            + sum_or_nan(grp["ミドルパス"])
            + sum_or_nan(grp["ロングパス"])
        )
        rec["short_pass_share_pct"] = ratio_or_nan(sum_or_nan(grp["ショートパス"]), distance_total)
        rec["long_pass_share_pct"] = ratio_or_nan(sum_or_nan(grp["ロングパス"]), distance_total)
        rec["opponent_half_gain_share_pct"] = ratio_or_nan(
            sum_or_nan(grp["相手陣での回数"]), sum_or_nan(grp["ボールゲイン"])
        )

        action_components = grp[
            [
                "successful_crosses",
                "successful_through_passes",
                "successful_dribbles",
                "successful_forward_passes",
            ]
        ]
        valid_action_rows = action_components.notna().any(axis=1)
        if valid_action_rows.any():
            action_total = float(action_components.loc[valid_action_rows].fillna(0).sum().sum())
            action_minutes = float(grp.loc[valid_action_rows, "出場時間"].sum())
            rec["successful_on_ball_actions_per90"] = (
                action_total / action_minutes * 90 if action_minutes > 0 else 0.0
            )
        else:
            rec["successful_on_ball_actions_per90"] = np.nan

        records.append(rec)

    fb_player_df = pd.DataFrame(records).merge(team_lookup, left_on="FB_Name", right_on="選手名", how="left")
    fb_player_df = fb_player_df.drop(columns=["選手名"])
    return fb_player_df


def load_sc_physical_match_data() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for year in TARGET_YEARS:
        league_dir = SC_DIR / year / TARGET_LEAGUE
        for file_path in sorted(league_dir.glob("*.csv")):
            raw_df = pd.read_csv(file_path)
            standardized = pd.DataFrame(index=raw_df.index)
            for canonical, aliases in SC_COLUMN_ALIASES.items():
                source = next((alias for alias in aliases if alias in raw_df.columns), None)
                standardized[canonical] = raw_df[source] if source else np.nan
            standardized["source_year"] = year
            frames.append(standardized)
    if not frames:
        raise RuntimeError("SkillCorner physical J3 csv が見つかりません。")
    df = pd.concat(frames, ignore_index=True)
    ensure_numeric(
        df,
        [
            "Minutes",
            "PSV-99",
            "Distance",
            "M/min",
            "HI Distance",
            "HSR Count",
            "Sprint Distance",
            "Sprint Count",
            "Medium Acceleration Count",
            "High Acceleration Count",
            "Explosive Acceleration to Sprint Count",
            "Change of Direction Count",
        ],
    )
    return df


def aggregate_sc_player_data(df_match: pd.DataFrame) -> pd.DataFrame:
    df = df_match.copy()
    df["player_name_raw_skillcorner"] = df["Player"].fillna("").astype(str)
    df["player_name_normalized"] = df["player_name_raw_skillcorner"].apply(canonicalize_sc_player_name)
    df["team_name_canonical"] = df["Team"].apply(canonicalize_team_name)
    df["source_year"] = df["source_year"].astype(str)

    raw_name_lookup = (
        df.groupby(["player_name_normalized", "player_name_raw_skillcorner"], as_index=False)["Minutes"]
        .sum()
        .sort_values(
            ["player_name_normalized", "Minutes", "player_name_raw_skillcorner"],
            ascending=[True, False, True],
        )
        .drop_duplicates(subset=["player_name_normalized"], keep="first")
        .rename(columns={"player_name_raw_skillcorner": "sc_raw_name"})
    )

    team_lookup = build_team_season_lookup(
        df,
        player_col="player_name_normalized",
        season_col="source_year",
        team_col="team_name_canonical",
        minutes_col="Minutes",
    )

    agg = (
        df.groupby("player_name_normalized", as_index=False)
        .agg(
            sc_total_minutes=("Minutes", "sum"),
            psv99_per_match=("PSV-99", "mean"),
            total_distance_full_all_per_match=("Distance", "mean"),
            total_metersperminute_full_all_per_match=("M/min", "mean"),
            hi_distance_full_all_per_match=("HI Distance", "mean"),
            hsr_count_full_all_per_match=("HSR Count", "mean"),
            sprint_distance_full_all_per_match=("Sprint Distance", "mean"),
            sprint_count_full_all_per_match=("Sprint Count", "mean"),
            medaccel_count_full_all_per_match=("Medium Acceleration Count", "mean"),
            highaccel_count_full_all_per_match=("High Acceleration Count", "mean"),
            explacceltosprint_count_full_all_per_match=("Explosive Acceleration to Sprint Count", "mean"),
            cod_count_full_all_per_match=("Change of Direction Count", "mean"),
        )
    )
    agg = agg.merge(raw_name_lookup[["player_name_normalized", "sc_raw_name"]], on="player_name_normalized", how="left")
    agg = agg.merge(team_lookup, on="player_name_normalized", how="left")
    return agg


def resolve_analysis_position(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mapping_df = pd.read_csv(POSITION_MAPPING_FILE)
    mapping = {
        (str(row["sc_position"]), str(row["sc_position_group"])): row["analysis_position_code"]
        for _, row in mapping_df.iterrows()
        if pd.notna(row["sc_position"])
    }

    def _resolve(row: pd.Series) -> str:
        if pd.notna(row.get("analysis_position_code")) and str(row["analysis_position_code"]).strip():
            return str(row["analysis_position_code"]).strip()
        key = (str(row.get("SC_Primary_Position", "")), str(row.get("SC_Primary_Position_Group", "")))
        return mapping.get(key, "")

    df["analysis_position_code_resolved"] = df.apply(_resolve, axis=1)
    return df


def composite_merge_enrichment(
    df_base: pd.DataFrame,
    fb_features: pd.DataFrame,
    sc_features: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    merge_stats = {"fb_name_only_fallback_count": 0, "sc_name_only_fallback_count": 0}

    fb_meta_cols = ["FB_Name", "fb_team_season_key", "fb_team_season_signature", "fb_dominant_team_name"]
    df_base = df_base.merge(fb_features[fb_meta_cols], on="FB_Name", how="left")

    fb_feature_cols = [col for col in fb_features.columns if col not in fb_meta_cols]
    df_enriched = df_base.merge(
        fb_features,
        on=["FB_Name", "fb_team_season_key", "fb_team_season_signature", "fb_dominant_team_name"],
        how="left",
        suffixes=("", "_fb"),
    )

    fb_missing_mask = df_enriched[fb_feature_cols].isna().all(axis=1)
    if fb_missing_mask.any():
        fallback = df_base.loc[fb_missing_mask].merge(
            fb_features,
            on="FB_Name",
            how="left",
            suffixes=("", "_fbfallback"),
        )
        for col in fb_feature_cols:
            df_enriched.loc[fb_missing_mask, col] = fallback[col].values
        merge_stats["fb_name_only_fallback_count"] = int(fb_missing_mask.sum())

    sc_key_cols = ["player_name_normalized", "team_season_key", "team_season_signature", "dominant_team_name"]
    sc_feature_cols = [col for col in sc_features.columns if col not in sc_key_cols and col != "sc_raw_name"]
    df_enriched = df_enriched.merge(
        sc_features,
        on=sc_key_cols,
        how="left",
        suffixes=("", "_scagg"),
    )

    sc_missing_mask = df_enriched[sc_feature_cols].isna().all(axis=1)
    if sc_missing_mask.any():
        fallback = df_base.loc[sc_missing_mask].merge(
            sc_features.drop(columns=["team_season_key", "team_season_signature", "dominant_team_name"]).drop_duplicates("player_name_normalized"),
            on="player_name_normalized",
            how="left",
            suffixes=("", "_scfallback"),
        )
        for col in sc_feature_cols:
            df_enriched.loc[sc_missing_mask, col] = fallback[col].values
        merge_stats["sc_name_only_fallback_count"] = int(sc_missing_mask.sum())

    return df_enriched, merge_stats


def quantile_rule(n: int) -> tuple[float, float]:
    if n >= 40:
        return 0.01, 0.99
    return 0.025, 0.975


def build_feature_frame(
    position_df: pd.DataFrame,
    config: list[dict[str, object]],
) -> pd.DataFrame:
    data = position_df.copy()
    feature_cols: dict[str, pd.Series] = {}
    for item in config:
        feature_cols[item["feature_key"]] = data[item["source_column"]]
    return pd.DataFrame(feature_cols, index=data.index)


def write_feature_definition(
    output_path: Path,
    position_code: str,
    config: list[dict[str, object]],
) -> dict[str, int]:
    counts = {"exact": 0, "proxy_strong": 0, "proxy_medium": 0, "proxy_weak": 0, "unavailable": 0}
    lines = [f"# {position_code} Feature Definition", "", "|概念変数|採用列名|参照列|区分|理由|採用不能理由|", "|---|---|---|---|---|---|"]
    for item in config:
        counts[item["match_type"]] += 1
        lines.append(
            "|{concept}|{feature}|{sources}|{match_type}|{reason}|{unavailable}|".format(
                concept=item["concept_name"],
                feature=item["feature_key"],
                sources=", ".join(item["source_raw_columns"]),
                match_type=item["match_type"],
                reason=item["reason"],
                unavailable="" if item["match_type"] != "unavailable" else item["reason"],
            )
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return counts


def write_missing_report(
    output_path: Path,
    position_code: str,
    n_players: int,
    lower_q: float,
    upper_q: float,
    report_rows: list[dict[str, object]],
    constant_features: list[str],
) -> None:
    lines = [
        f"# {position_code} Missing Report",
        "",
        f"- サンプル数: `{n_players}`",
        f"- winsorize 条件: `{lower_q * 100:g}/{upper_q * 100:g}` percentile",
        f"- z-score ルール: `z = (x - mean) / std`",
        "",
        "|feature|欠損数|欠損率(%)|補完件数|lower_bound|upper_bound|clip_low|clip_high|備考|",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report_rows:
        lines.append(
            "|{feature_key}|{missing_count}|{missing_rate_pct:.2f}|{imputed_count}|{lower_bound:.6g}|{upper_bound:.6g}|{clip_low}|{clip_high}|{note}|".format(
                **row
            )
        )
    lines.append("")
    if constant_features:
        lines.append(f"- zscore_constant_feature: {', '.join(constant_features)}")
    else:
        lines.append("- zscore_constant_feature: なし")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_position_outputs(
    position_code: str,
    position_df: pd.DataFrame,
    config: list[dict[str, object]],
) -> dict[str, object]:
    position_dir = OUTPUT_ROOT / position_code
    position_dir.mkdir(parents=True, exist_ok=True)

    position_df = position_df.sort_values(["FB_Minutes", "FB_Name"], ascending=[False, True]).reset_index(drop=True)
    players_raw = position_df[[col for col in PLAYER_RAW_COLUMNS if col in position_df.columns]].copy()
    players_raw_path = position_dir / f"{position_code}_players_raw.csv"
    players_raw.to_csv(players_raw_path, index=False, encoding="utf-8-sig")

    features_only = build_feature_frame(position_df, config)
    id_cols = position_df[["FB_Name", "SC_Name", "analysis_position_code", "analysis_position_jp"]].copy()
    features_raw = pd.concat([id_cols, features_only], axis=1)
    features_raw_path = position_dir / f"{position_code}_features_raw.csv"
    features_raw.to_csv(features_raw_path, index=False, encoding="utf-8-sig")

    n_players = len(features_only)
    lower_q, upper_q = quantile_rule(n_players)

    report_rows: list[dict[str, object]] = []
    constant_features: list[str] = []
    raw_prefixed: dict[str, pd.Series] = {}
    win_prefixed: dict[str, pd.Series] = {}
    z_prefixed: dict[str, pd.Series] = {}
    imputed_prefixed: dict[str, pd.Series] = {}

    for item in config:
        feature_key = item["feature_key"]
        raw_series = features_only[feature_key].astype(float)
        missing_mask = raw_series.isna()
        imputed_series = raw_series.copy()
        if missing_mask.any():
            median_value = raw_series.median(skipna=True)
            if pd.isna(median_value):
                median_value = 0.0
            imputed_series.loc[missing_mask] = median_value
        lower_bound = float(imputed_series.quantile(lower_q))
        upper_bound = float(imputed_series.quantile(upper_q))
        clipped_low = int((imputed_series < lower_bound).sum())
        clipped_high = int((imputed_series > upper_bound).sum())
        winsorized = imputed_series.clip(lower=lower_bound, upper=upper_bound)
        std = float(winsorized.std(ddof=0))
        if std == 0:
            z_series = pd.Series(0.0, index=winsorized.index)
            constant_features.append(feature_key)
            note = "std=0 のため z=0 固定"
        else:
            z_series = (winsorized - float(winsorized.mean())) / std
            note = ""

        raw_prefixed[f"raw_{feature_key}"] = raw_series
        win_prefixed[f"win_{feature_key}"] = winsorized
        z_prefixed[f"z_{feature_key}"] = z_series
        imputed_prefixed[f"imputed_{feature_key}"] = missing_mask.astype(int)
        report_rows.append(
            {
                "feature_key": feature_key,
                "missing_count": int(missing_mask.sum()),
                "missing_rate_pct": float(missing_mask.mean() * 100),
                "imputed_count": int(missing_mask.sum()),
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "clip_low": clipped_low,
                "clip_high": clipped_high,
                "note": note or "中央値補完なし" if missing_mask.sum() == 0 else "中央値補完あり",
            }
        )

    preprocessed_df = pd.concat(
        [
            id_cols,
            pd.DataFrame(raw_prefixed),
            pd.DataFrame(win_prefixed),
            pd.DataFrame(z_prefixed),
            pd.DataFrame(imputed_prefixed),
        ],
        axis=1,
    )
    preprocessed_path = position_dir / f"{position_code}_features_preprocessed.csv"
    preprocessed_df.to_csv(preprocessed_path, index=False, encoding="utf-8-sig")

    definition_path = position_dir / f"{position_code}_feature_definition.md"
    adoption_counts = write_feature_definition(definition_path, position_code, config)

    missing_report_path = position_dir / f"{position_code}_missing_report.md"
    write_missing_report(
        missing_report_path,
        position_code,
        n_players,
        lower_q,
        upper_q,
        report_rows,
        constant_features,
    )

    missing_features = [row["feature_key"] for row in report_rows if row["missing_count"] > 0]
    total_imputations = int(sum(row["imputed_count"] for row in report_rows))

    return {
        "position_code": position_code,
        "player_count": n_players,
        "winsor_rule": f"{lower_q * 100:g}/{upper_q * 100:g}",
        "adoption_counts": adoption_counts,
        "missing_features": missing_features,
        "total_imputations": total_imputations,
        "constant_features": constant_features,
        "files": [
            players_raw_path,
            features_raw_path,
            preprocessed_path,
            definition_path,
            missing_report_path,
        ],
    }


def write_root_readme(
    summaries: list[dict[str, object]],
    merge_stats: dict[str, int],
    minutes_check_count: int,
    join_report_df: pd.DataFrame,
) -> Path:
    lines = [
        "# SC_position_clustering",
        "",
        "## フォルダ構成",
        "",
        "```text",
        "SC_position_clustering/",
    ]
    for summary in summaries:
        code = summary["position_code"]
        lines.append(f"  {code}/")
        lines.append(f"    {code}_players_raw.csv")
        lines.append(f"    {code}_features_raw.csv")
        lines.append(f"    {code}_features_preprocessed.csv")
        lines.append(f"    {code}_feature_definition.md")
        lines.append(f"    {code}_missing_report.md")
    lines.extend(["  README.md", "```", "", "## 選手数", ""])
    for summary in summaries:
        lines.append(f"- `{summary['position_code']}`: {summary['player_count']} 名")

    lines.extend(["", "## 15変数の対応状況", ""])
    for summary in summaries:
        counts = summary["adoption_counts"]
        lines.append(
            "- `{code}`: exact={exact}, proxy_strong={proxy_strong}, proxy_medium={proxy_medium}, proxy_weak={proxy_weak}, unavailable={unavailable}".format(
                code=summary["position_code"], **counts
            )
        )

    lines.extend(["", "## 欠損・補完", ""])
    for summary in summaries:
        missing_text = ", ".join(summary["missing_features"]) if summary["missing_features"] else "なし"
        lines.append(
            f"- `{summary['position_code']}`: 欠損列={missing_text} / 補完件数={summary['total_imputations']}"
        )

    lines.extend(["", "## winsorize / Zスコア", ""])
    for summary in summaries:
        const_text = ", ".join(summary["constant_features"]) if summary["constant_features"] else "なし"
        lines.append(
            f"- `{summary['position_code']}`: n={summary['player_count']}, winsorize={summary['winsor_rule']}, zscore_constant_feature={const_text}"
        )

    lines.extend(
        [
            "",
            "## name-only 利用箇所",
            "",
            f"- `fix_position_join.py` の `normalized_only` 件数: {int(join_report_df.loc[join_report_df['metric'] == 'method_normalized_only', 'value'].iloc[0]) if (join_report_df['metric'] == 'method_normalized_only').any() else 0}",
            f"- FB 再集計 merge の name-only fallback 件数: {merge_stats['fb_name_only_fallback_count']}",
            f"- SC 再集計 merge の name-only fallback 件数: {merge_stats['sc_name_only_fallback_count']}",
            "",
            "## その他",
            "",
            f"- `FB_Minutes < 300` 確認件数: {minutes_check_count}",
            "- 300分未満の追加除外はしていない",
            "- `raw_*` は元値、`win_*` は winsorize 後、`z_*` はポジション内 z-score、`imputed_*` は中央値補完フラグ",
            "- 次工程では各 `*_features_preprocessed.csv` の `z_*` 列を KMeans 入力として利用できる",
            "- RandomForest 用には同ファイルの `raw_*` / `win_*` / `z_*` を説明変数候補として利用できる",
        ]
    )

    readme_path = OUTPUT_ROOT / "README.md"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return readme_path


def main() -> None:
    print("=== J3 ポジション別クラスタリング前処理入力作成 開始 ===")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    df_base = pd.read_csv(BASE_MERGED_FILE, encoding="utf-8-sig")
    df_base = resolve_analysis_position(df_base)
    assert len(df_base) == 647, f"ベース行数が647ではありません: {len(df_base)}"
    minutes_check_count = int((pd.to_numeric(df_base["FB_Minutes"], errors="coerce") < 300).sum())

    if "player_name_normalized" not in df_base.columns:
        raise RuntimeError("fix_position_join.py 再生成後の merged CSV が必要です。player_name_normalized がありません。")

    print("  Football Box raw 再集計中...")
    fb_match_df = load_fb_match_data()
    fb_features = aggregate_fb_player_data(fb_match_df)

    print("  SkillCorner physical raw 再集計中...")
    sc_match_df = load_sc_physical_match_data()
    sc_features = aggregate_sc_player_data(sc_match_df)

    print("  composite key 優先で再結合中...")
    df_enriched, merge_stats = composite_merge_enrichment(df_base, fb_features, sc_features)
    assert len(df_enriched) == 647, f"再結合後の行数が647ではありません: {len(df_enriched)}"

    summaries: list[dict[str, object]] = []
    output_files: list[Path] = []
    for position_code in POSITION_CODES:
        position_df = df_enriched[
            df_enriched["analysis_position_code_resolved"] == position_code
        ].copy()
        summary = prepare_position_outputs(position_code, position_df, POSITION_FEATURES[position_code])
        summaries.append(summary)
        output_files.extend(summary["files"])
        print(f"  {position_code}: {summary['player_count']} rows")

    join_report_df = pd.read_csv(JOIN_REPORT_FILE, encoding="utf-8-sig")
    readme_path = write_root_readme(summaries, merge_stats, minutes_check_count, join_report_df)
    output_files.append(readme_path)

    print(f"  出力ファイル数: {len(output_files)}")
    print(f"  ルートREADME: {readme_path}")
    print("=== 完了 ===")


if __name__ == "__main__":
    main()
