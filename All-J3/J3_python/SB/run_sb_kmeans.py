"""
SB 向け KMeans 実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent
ALL_J3_DIR = J3_PYTHON_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from kmeans_pipeline import PositionConfig, run_position_kmeans

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


def main() -> None:
    config = PositionConfig(
        position_code="SB",
        position_name_jp="サイドバック",
        input_csv_path=ALL_J3_DIR / "J3_csv" / "SC_position_clustering" / "SB" / "SB_features_preprocessed.csv",
        output_dir=CURRENT_DIR / "output",
        z_columns=SB_Z_COLUMNS,
        feature_labels=SB_FEATURE_LABELS,
        theme_groups=SB_THEME_GROUPS,
        n_clusters=4,
        random_state=42,
        n_init=50,
        max_iter=300,
    )
    run_position_kmeans(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[SB][ERROR] {exc}", file=sys.stderr)
        raise
