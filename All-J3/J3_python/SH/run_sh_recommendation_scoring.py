"""
SH 向け推薦スコアリング実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from position_definitions import SH_FEATURE_LABELS, SH_Z_COLUMNS
from recommendation_pipeline import RecommendationPositionConfig, ScoreSpec, run_position_recommendation_scoring

SH_CLUSTER_LABELS = {
    0: "縦突破型",
    1: "守備回収型",
    2: "クロス供給型",
    3: "平均型",
}

SH_SCORE_SPECS = (
    ScoreSpec(
        cluster_id=0,
        cluster_label=SH_CLUSTER_LABELS[0],
        method="sum",
        formula_text=(
            "score_cluster_0 = "
            "z_sprint_distance_full_all_per_match + "
            "z_hsr_count_full_all_per_match + "
            "z_pa_entry_per90"
        ),
        components=(
            "z_sprint_distance_full_all_per_match",
            "z_hsr_count_full_all_per_match",
            "z_pa_entry_per90",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "Cluster 0 はスプリント距離と HSR 回数が大きく、PA 進入もプラスでした。"
            " RF でも縦方向のスピードと侵入量が主な分離軸だったため、縦突破型はこの3変数で表現します。"
        ),
    ),
    ScoreSpec(
        cluster_id=1,
        cluster_label=SH_CLUSTER_LABELS[1],
        method="sum",
        formula_text=(
            "score_cluster_1 = "
            "z_regain_within_5s_per90 - "
            "z_dribble_success_rate_pct"
        ),
        components=(
            "z_regain_within_5s_per90",
            "z_dribble_success_rate_pct",
        ),
        weights=(1.0, -1.0),
        rationale=(
            "Cluster 1 は即時奪回が非常に高く、逆にドリブル成功率が低い守備寄りクラスタでした。"
            " KMeans 中心と RF の双方でこの対比が最も明確だったため、守備回収型は 2 変数で素直に切ります。"
        ),
    ),
    ScoreSpec(
        cluster_id=2,
        cluster_label=SH_CLUSTER_LABELS[2],
        method="sum",
        formula_text=(
            "score_cluster_2 = "
            "z_crosses_per90 + "
            "z_pa_entry_per90 + "
            "z_last_passes_per90"
        ),
        components=(
            "z_crosses_per90",
            "z_pa_entry_per90",
            "z_last_passes_per90",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "Cluster 2 はクロス数と PA 進入が突出し、ラストパスも高い供給特化クラスタでした。"
            " RF と KMeans 中心の共通項として、この3変数でクロス供給型を表します。"
        ),
    ),
    ScoreSpec(
        cluster_id=3,
        cluster_label=SH_CLUSTER_LABELS[3],
        method="distance",
        formula_text="score_cluster_3 = - euclidean_distance(player_z_vector, sh_cluster_3_center_z_vector)",
        rationale=(
            "Cluster 3 は原点に最も近い平均型でした。速度・供給・回収のいずれか一つだけで説明しにくいため、"
            " 9変数全体の中心距離で評価します。"
        ),
    ),
)


def main() -> None:
    config = RecommendationPositionConfig(
        position_code="SH",
        position_name_jp="サイドハーフ",
        clustered_players_path=CURRENT_DIR / "output" / "SH_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "SH_cluster_centers_z.csv",
        rf_report_path=CURRENT_DIR / "output" / "SH_rf_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=SH_Z_COLUMNS,
        feature_labels=SH_FEATURE_LABELS,
        cluster_labels=SH_CLUSTER_LABELS,
        score_specs=SH_SCORE_SPECS,
    )
    run_position_recommendation_scoring(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[SH][REC][ERROR] {exc}", file=sys.stderr)
        raise
