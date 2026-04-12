"""
CB 向け one-vs-rest RandomForest 実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from randomforest_pipeline import RandomForestPositionConfig, run_position_randomforest

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

CB_THEME_LABEL_CANDIDATES = {
    "対人・空中戦寄り": "対人迎撃型候補",
    "危険除去寄り": "危険除去型候補",
    "配球寄り": "配球型候補",
    "機動力寄り": "上下動型候補",
}


def main() -> None:
    config = RandomForestPositionConfig(
        position_code="CB",
        position_name_jp="センターバック",
        clustered_players_path=CURRENT_DIR / "output" / "CB_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "CB_cluster_centers_z.csv",
        cluster_summary_path=CURRENT_DIR / "output" / "CB_cluster_summary.csv",
        kmeans_report_path=CURRENT_DIR / "output" / "CB_kmeans_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=CB_Z_COLUMNS,
        feature_labels=CB_FEATURE_LABELS,
        theme_groups=CB_THEME_GROUPS,
        theme_label_candidates=CB_THEME_LABEL_CANDIDATES,
        average_cluster_id=3,
    )
    run_position_randomforest(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[CB][RF][ERROR] {exc}", file=sys.stderr)
        raise
