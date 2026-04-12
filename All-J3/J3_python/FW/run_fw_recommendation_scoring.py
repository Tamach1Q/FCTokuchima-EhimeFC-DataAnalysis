"""
FW 向け推薦スコアリング実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from position_definitions import FW_FEATURE_LABELS, FW_Z_COLUMNS
from recommendation_pipeline import RecommendationPositionConfig, ScoreSpec, run_position_recommendation_scoring

FW_CLUSTER_LABELS = {
    0: "平均型",
    1: "フィニッシュ型",
    2: "空中戦・前進関与型",
    3: "前線守備・回収型",
}

FW_SCORE_SPECS = (
    ScoreSpec(
        cluster_id=0,
        cluster_label=FW_CLUSTER_LABELS[0],
        method="distance",
        formula_text="score_cluster_0 = - euclidean_distance(player_z_vector, fw_cluster_0_center_z_vector)",
        rationale=(
            "Cluster 0 は原点に最も近い平均型でした。突出変数よりも、10変数全体で中心にどれだけ近いかを見た方が"
            " KMeans の定義と整合するため、距離ベースで評価します。"
        ),
    ),
    ScoreSpec(
        cluster_id=1,
        cluster_label=FW_CLUSTER_LABELS[1],
        method="sum",
        formula_text=(
            "score_cluster_1 = "
            "z_shot_conversion_rate_pct + "
            "z_goals_per90 + "
            "z_shot_on_target_rate_pct"
        ),
        components=(
            "z_shot_conversion_rate_pct",
            "z_goals_per90",
            "z_shot_on_target_rate_pct",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "Cluster 1 は少数ながら決定率・得点_per90・枠内率が極端に高いクラスタでした。"
            " KMeans 中心でもこの3変数が最も突出し、RF 側でも分離軸は同じ3変数に集中していたため、"
            " フィニッシュ性能に絞って評価します。"
        ),
    ),
    ScoreSpec(
        cluster_id=2,
        cluster_label=FW_CLUSTER_LABELS[2],
        method="sum",
        formula_text=(
            "score_cluster_2 = "
            "z_last_passes_per90 + "
            "z_aerial_wins_per90 + "
            "z_box_shots_per90"
        ),
        components=(
            "z_last_passes_per90",
            "z_aerial_wins_per90",
            "z_box_shots_per90",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "Cluster 2 はラストパス・空中戦勝利・ボックス内シュートが同時に高く、"
            " 前進関与とターゲット性能の両方が見えるクラスタでした。"
            " KMeans 中心と RF 上位の重なりから、この3変数に絞って像を表現します。"
        ),
    ),
    ScoreSpec(
        cluster_id=3,
        cluster_label=FW_CLUSTER_LABELS[3],
        method="sum",
        formula_text=(
            "score_cluster_3 = "
            "z_successful_forward_passes_per90 + "
            "z_attacking_third_gains_per90"
        ),
        components=(
            "z_successful_forward_passes_per90",
            "z_attacking_third_gains_per90",
        ),
        weights=(1.0, 1.0),
        rationale=(
            "Cluster 3 は得点・ボックス内シュートが低い一方、前進パス成功数と攻撃3rd奪回が高く、"
            " 前線での回収から前進局面に関わる色が強く出ました。"
            " RF でもこの2変数が上位だったため、前線守備・回収型の核として採用します。"
        ),
    ),
)


def main() -> None:
    config = RecommendationPositionConfig(
        position_code="FW",
        position_name_jp="フォワード",
        clustered_players_path=CURRENT_DIR / "output" / "FW_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "FW_cluster_centers_z.csv",
        rf_report_path=CURRENT_DIR / "output" / "FW_rf_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=FW_Z_COLUMNS,
        feature_labels=FW_FEATURE_LABELS,
        cluster_labels=FW_CLUSTER_LABELS,
        score_specs=FW_SCORE_SPECS,
    )
    run_position_recommendation_scoring(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[FW][REC][ERROR] {exc}", file=sys.stderr)
        raise
