"""
SB 向け one-vs-rest RandomForest 実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from randomforest_pipeline import RandomForestPositionConfig, run_position_randomforest

SB_Z_COLUMNS = [
    "z_running_distance_full_all_per_match",
    "z_hi_distance_full_all_per_match",
    "z_sprint_count_full_all_per_match",
    "z_crosses_per90",
    "z_cross_success_rate_pct",
    "z_pa_entry_per90",
    "z_tackle_win_rate_pct",
    "z_blocks_per90",
    "z_forward_long_pass_success_rate_pct",
    "z_regain_within_5s_per90",
]

SB_FEATURE_LABELS = {
    "z_running_distance_full_all_per_match": "走行距離_per_match",
    "z_hi_distance_full_all_per_match": "HI距離_per_match",
    "z_sprint_count_full_all_per_match": "スプリント回数_per_match",
    "z_crosses_per90": "クロス数_per90",
    "z_cross_success_rate_pct": "クロス成功率",
    "z_pa_entry_per90": "PA進入_per90",
    "z_tackle_win_rate_pct": "タックル奪取率",
    "z_blocks_per90": "ブロック_per90",
    "z_forward_long_pass_success_rate_pct": "前方向ロングパス成功率",
    "z_regain_within_5s_per90": "ロスト後5秒未満リゲイン_per90",
}

SB_THEME_GROUPS = {
    "上下動・侵入寄り": [
        "z_running_distance_full_all_per_match",
        "z_hi_distance_full_all_per_match",
        "z_sprint_count_full_all_per_match",
        "z_pa_entry_per90",
    ],
    "クロス供給寄り": [
        "z_crosses_per90",
        "z_cross_success_rate_pct",
    ],
    "守備回収寄り": [
        "z_tackle_win_rate_pct",
        "z_blocks_per90",
        "z_regain_within_5s_per90",
    ],
    "配球寄り": [
        "z_forward_long_pass_success_rate_pct",
    ],
}

SB_THEME_LABEL_CANDIDATES = {
    "上下動・侵入寄り": "上下動型候補",
    "クロス供給寄り": "攻撃参加型候補",
    "守備回収寄り": "守備回収型候補",
    "配球寄り": "配球型候補",
}


def main() -> None:
    config = RandomForestPositionConfig(
        position_code="SB",
        position_name_jp="サイドバック",
        clustered_players_path=CURRENT_DIR / "output" / "SB_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "SB_cluster_centers_z.csv",
        cluster_summary_path=CURRENT_DIR / "output" / "SB_cluster_summary.csv",
        kmeans_report_path=CURRENT_DIR / "output" / "SB_kmeans_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=SB_Z_COLUMNS,
        feature_labels=SB_FEATURE_LABELS,
        theme_groups=SB_THEME_GROUPS,
        theme_label_candidates=SB_THEME_LABEL_CANDIDATES,
        average_cluster_id=2,
    )
    run_position_randomforest(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[SB][RF][ERROR] {exc}", file=sys.stderr)
        raise
