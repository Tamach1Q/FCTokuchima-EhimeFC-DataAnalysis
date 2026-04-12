"""
SH 向け KMeans 実行スクリプト。
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
from position_definitions import SH_FEATURE_LABELS, SH_THEME_GROUPS, SH_Z_COLUMNS


def main() -> None:
    config = PositionConfig(
        position_code="SH",
        position_name_jp="サイドハーフ",
        input_csv_path=ALL_J3_DIR / "J3_csv" / "SC_position_clustering" / "SH" / "SH_features_preprocessed.csv",
        output_dir=CURRENT_DIR / "output",
        z_columns=SH_Z_COLUMNS,
        feature_labels=SH_FEATURE_LABELS,
        theme_groups=SH_THEME_GROUPS,
        n_clusters=4,
        random_state=42,
        n_init=50,
        max_iter=300,
        include_source_feature_columns=True,
        include_imputation_stats=True,
        enable_residual_z_median_imputation=True,
    )
    run_position_kmeans(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[SH][ERROR] {exc}", file=sys.stderr)
        raise
