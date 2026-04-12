"""
FW 向け one-vs-rest RandomForest 実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from position_definitions import (
    FW_FEATURE_LABELS,
    FW_THEME_GROUPS,
    FW_THEME_LABEL_CANDIDATES,
    FW_Z_COLUMNS,
)
from randomforest_pipeline import RandomForestPositionConfig, run_position_randomforest


def main() -> None:
    config = RandomForestPositionConfig(
        position_code="FW",
        position_name_jp="フォワード",
        clustered_players_path=CURRENT_DIR / "output" / "FW_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "FW_cluster_centers_z.csv",
        cluster_summary_path=CURRENT_DIR / "output" / "FW_cluster_summary.csv",
        kmeans_report_path=CURRENT_DIR / "output" / "FW_kmeans_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=FW_Z_COLUMNS,
        feature_labels=FW_FEATURE_LABELS,
        theme_groups=FW_THEME_GROUPS,
        theme_label_candidates=FW_THEME_LABEL_CANDIDATES,
        average_cluster_id=None,
        n_estimators=1000,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=2,
    )
    run_position_randomforest(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[FW][RF][ERROR] {exc}", file=sys.stderr)
        raise
