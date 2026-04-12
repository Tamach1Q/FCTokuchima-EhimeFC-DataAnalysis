"""
CMF 向け推薦スコアリング実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from position_definitions import CMF_FEATURE_LABELS, CMF_Z_COLUMNS
from recommendation_pipeline import RecommendationPositionConfig, ScoreSpec, run_position_recommendation_scoring

CMF_CLUSTER_LABELS = {
    0: "ボールハンター型",
    1: "ボックストゥボックス型",
    2: "ゲームオーガナイザー型",
}

CMF_SCORE_SPECS = (
    ScoreSpec(
        cluster_id=0,
        cluster_label=CMF_CLUSTER_LABELS[0],
        method="sum",
        formula_text=(
            "score_cluster_0 = "
            "z_ball_gains_per90 + "
            "z_long_pass_share_pct - "
            "z_pass_success_rate_pct"
        ),
        components=(
            "z_ball_gains_per90",
            "z_long_pass_share_pct",
            "z_pass_success_rate_pct",
        ),
        weights=(1.0, 1.0, -1.0),
        rationale=(
            "Cluster 0 はボール奪取とロングパス比率が高く、パス成功率は低めのダイレクト志向でした。"
            " KMeans 中心と RF 上位の重なりから、奪って前へ運ぶボールハンター型としてこの3変数で評価します。"
        ),
    ),
    ScoreSpec(
        cluster_id=1,
        cluster_label=CMF_CLUSTER_LABELS[1],
        method="distance",
        formula_text="score_cluster_1 = - euclidean_distance(player_z_vector, cmf_cluster_1_center_z_vector)",
        rationale=(
            "Cluster 1 は原点に最も近い一方で、走行距離と敵陣奪回比率がプラスの二方向型でした。"
            " 平均寄りのボックストゥボックス像として、少数変数の合算ではなく全体ベクトルの距離で見ます。"
        ),
    ),
    ScoreSpec(
        cluster_id=2,
        cluster_label=CMF_CLUSTER_LABELS[2],
        method="sum",
        formula_text=(
            "score_cluster_2 = "
            "z_short_pass_share_pct + "
            "z_forward_pass_success_rate_pct + "
            "z_pass_success_rate_pct"
        ),
        components=(
            "z_short_pass_share_pct",
            "z_forward_pass_success_rate_pct",
            "z_pass_success_rate_pct",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "Cluster 2 はショートパス比率、前進パス成功率、パス成功率がいずれも高いゲームメイク特化型でした。"
            " KMeans 中心と RF の両方でこの3変数が揃っていたため、そのまま採用します。"
        ),
    ),
)


def main() -> None:
    config = RecommendationPositionConfig(
        position_code="CMF",
        position_name_jp="セントラルMF",
        clustered_players_path=CURRENT_DIR / "output" / "CMF_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "CMF_cluster_centers_z.csv",
        rf_report_path=CURRENT_DIR / "output" / "CMF_rf_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=CMF_Z_COLUMNS,
        feature_labels=CMF_FEATURE_LABELS,
        cluster_labels=CMF_CLUSTER_LABELS,
        score_specs=CMF_SCORE_SPECS,
    )
    run_position_recommendation_scoring(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[CMF][REC][ERROR] {exc}", file=sys.stderr)
        raise
