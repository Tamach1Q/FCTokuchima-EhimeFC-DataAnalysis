"""
SB 向け推薦スコアリング実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from recommendation_pipeline import RecommendationPositionConfig, ScoreSpec, run_position_recommendation_scoring

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

SB_CLUSTER_LABELS = {
    0: "上下動型",
    1: "守備回収・配球型",
    2: "平均型",
    3: "攻撃参加型",
}

SB_SCORE_SPECS = (
    ScoreSpec(
        cluster_id=0,
        cluster_label=SB_CLUSTER_LABELS[0],
        method="sum",
        formula_text=(
            "score_cluster_0 = "
            "z_hi_distance_full_all_per_match + "
            "z_running_distance_full_all_per_match + "
            "z_sprint_count_full_all_per_match"
        ),
        components=(
            "z_hi_distance_full_all_per_match",
            "z_running_distance_full_all_per_match",
            "z_sprint_count_full_all_per_match",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "上下動型は KMeans 中心でも RandomForest でも HI距離、走行距離、スプリント回数が主要軸でした。"
            "運動量と往復強度をそのまま表す3変数に絞ることで、上下動型の像を明確に出します。"
        ),
    ),
    ScoreSpec(
        cluster_id=1,
        cluster_label=SB_CLUSTER_LABELS[1],
        method="sum",
        formula_text=(
            "score_cluster_1 = "
            "z_blocks_per90 + "
            "z_regain_within_5s_per90 + "
            "z_forward_long_pass_success_rate_pct"
        ),
        components=(
            "z_blocks_per90",
            "z_regain_within_5s_per90",
            "z_forward_long_pass_success_rate_pct",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "守備回収・配球型は守備回収と前方向への配球を両立するクラスタとして扱います。"
            "ブロックと即時奪回で守備回収を、前方向ロングパス成功率で配球面を表現する3変数を採用しました。"
        ),
    ),
    ScoreSpec(
        cluster_id=2,
        cluster_label=SB_CLUSTER_LABELS[2],
        method="distance",
        formula_text="score_cluster_2 = - euclidean_distance(player_z_vector, sb_cluster_2_center_z_vector)",
        rationale=(
            "平均型は specialized cluster のような突出変数ではなく、10変数の全体バランスで定義されるため、"
            "KMeans に使った全 z 列の cluster 2 中心への距離をそのまま使います。"
        ),
    ),
    ScoreSpec(
        cluster_id=3,
        cluster_label=SB_CLUSTER_LABELS[3],
        method="sum",
        formula_text=(
            "score_cluster_3 = "
            "z_pa_entry_per90 + "
            "z_crosses_per90 + "
            "z_tackle_win_rate_pct"
        ),
        components=(
            "z_pa_entry_per90",
            "z_crosses_per90",
            "z_tackle_win_rate_pct",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "攻撃参加型は PA 侵入とクロス供給が主軸で、RandomForest でも PA進入・クロス数・タックル奪取率が上位でした。"
            "前進参加だけでなく、前で潰せる守備強度も含めてこの3変数で表します。"
        ),
    ),
)


def main() -> None:
    config = RecommendationPositionConfig(
        position_code="SB",
        position_name_jp="サイドバック",
        clustered_players_path=CURRENT_DIR / "output" / "SB_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "SB_cluster_centers_z.csv",
        rf_report_path=CURRENT_DIR / "output" / "SB_rf_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=SB_Z_COLUMNS,
        feature_labels=SB_FEATURE_LABELS,
        cluster_labels=SB_CLUSTER_LABELS,
        score_specs=SB_SCORE_SPECS,
    )
    run_position_recommendation_scoring(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[SB][REC][ERROR] {exc}", file=sys.stderr)
        raise
