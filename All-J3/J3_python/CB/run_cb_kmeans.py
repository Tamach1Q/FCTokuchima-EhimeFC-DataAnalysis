"""
CB 向け KMeans 実行スクリプト。
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

CB_Z_COLUMNS = [
    "z_aerial_duel_win_rate_pct",
    "z_tackle_win_rate_pct",
    "z_interceptions_per90",
    "z_blocks_per90",
    "z_clearances_per90",
    "z_pass_success_rate_pct",
    "z_successful_forward_passes_per90",
    "z_successful_long_passes_per90",
    "z_medaccel_count_full_all_per_match",
    "z_highaccel_count_full_all_per_match",
]

CB_FEATURE_LABELS = {
    "z_aerial_duel_win_rate_pct": "空中戦勝率",
    "z_tackle_win_rate_pct": "タックル奪取率",
    "z_interceptions_per90": "インターセプト_per90",
    "z_blocks_per90": "ブロック_per90",
    "z_clearances_per90": "クリア_per90",
    "z_pass_success_rate_pct": "パス成功率",
    "z_successful_forward_passes_per90": "前進パス成功数_per90",
    "z_successful_long_passes_per90": "ロングパス成功数_per90",
    "z_medaccel_count_full_all_per_match": "中加速回数_per_match",
    "z_highaccel_count_full_all_per_match": "高加速回数_per_match",
}

CB_THEME_GROUPS = {
    "対人・空中戦寄り": [
        "z_aerial_duel_win_rate_pct",
        "z_tackle_win_rate_pct",
    ],
    "危険除去寄り": [
        "z_interceptions_per90",
        "z_blocks_per90",
        "z_clearances_per90",
    ],
    "配球寄り": [
        "z_pass_success_rate_pct",
        "z_successful_forward_passes_per90",
        "z_successful_long_passes_per90",
    ],
    "機動力寄り": [
        "z_medaccel_count_full_all_per_match",
        "z_highaccel_count_full_all_per_match",
    ],
}


def main() -> None:
    config = PositionConfig(
        position_code="CB",
        position_name_jp="センターバック",
        input_csv_path=ALL_J3_DIR / "J3_csv" / "SC_position_clustering" / "CB" / "CB_features_preprocessed.csv",
        output_dir=CURRENT_DIR / "output",
        z_columns=CB_Z_COLUMNS,
        feature_labels=CB_FEATURE_LABELS,
        theme_groups=CB_THEME_GROUPS,
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
        print(f"[CB][ERROR] {exc}", file=sys.stderr)
        raise
