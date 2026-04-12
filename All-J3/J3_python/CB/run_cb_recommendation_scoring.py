"""
CB 向け推薦スコアリング実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from recommendation_pipeline import RecommendationPositionConfig, ScoreSpec, run_position_recommendation_scoring

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

CB_CLUSTER_LABELS = {
    0: "ビルドアップ型",
    1: "守備安定型",
    2: "対人迎撃型",
    3: "平均型",
}

CB_SCORE_SPECS = (
    ScoreSpec(
        cluster_id=0,
        cluster_label=CB_CLUSTER_LABELS[0],
        method="sum",
        formula_text=(
            "score_cluster_0 = "
            "z_successful_forward_passes_per90 + "
            "z_pass_success_rate_pct + "
            "z_successful_long_passes_per90"
        ),
        components=(
            "z_successful_forward_passes_per90",
            "z_pass_success_rate_pct",
            "z_successful_long_passes_per90",
        ),
        weights=(1.0, 1.0, 1.0),
        rationale=(
            "ビルドアップ型は KMeans 中心で前進パス・パス成功率・ロングパスがいずれも高く、"
            "RandomForest でも同じ3変数が上位でした。配球役としての像を最も素直に表すため、この3変数に限定しました。"
        ),
    ),
    ScoreSpec(
        cluster_id=1,
        cluster_label=CB_CLUSTER_LABELS[1],
        method="sum",
        formula_text=(
            "score_cluster_1 = "
            "z_clearances_per90 + "
            "z_aerial_duel_win_rate_pct - "
            "z_medaccel_count_full_all_per_match"
        ),
        components=(
            "z_clearances_per90",
            "z_aerial_duel_win_rate_pct",
            "z_medaccel_count_full_all_per_match",
        ),
        weights=(1.0, 1.0, -1.0),
        rationale=(
            "守備安定型は KMeans 側でクリアと空中戦がプラス、RandomForest 側で中加速回数の低さが強く効いていました。"
            "危険除去と空中対応を加点しつつ、相対的に機動力が低めという像を減点項で反映しました。"
        ),
    ),
    ScoreSpec(
        cluster_id=2,
        cluster_label=CB_CLUSTER_LABELS[2],
        method="sum",
        formula_text="score_cluster_2 = z_tackle_win_rate_pct + z_interceptions_per90",
        components=(
            "z_tackle_win_rate_pct",
            "z_interceptions_per90",
        ),
        weights=(1.0, 1.0),
        rationale=(
            "対人迎撃型は少数クラスタなので、無理に変数を増やさず対人勝率と迎撃回数に絞りました。"
            "タックル奪取率とインターセプトは KMeans 中心でも強く、クラスタ像をシンプルに捉えやすい2軸です。"
        ),
    ),
    ScoreSpec(
        cluster_id=3,
        cluster_label=CB_CLUSTER_LABELS[3],
        method="distance",
        formula_text="score_cluster_3 = - euclidean_distance(player_z_vector, cb_cluster_3_center_z_vector)",
        rationale=(
            "平均型は単一の突出変数で定義されるクラスタではなく、10変数全体で中心に近いかどうかで見るのが自然です。"
            "そのため単純加算ではなく、KMeans に使った全 z 列で cluster 3 中心までの距離を用います。"
        ),
    ),
)


def main() -> None:
    config = RecommendationPositionConfig(
        position_code="CB",
        position_name_jp="センターバック",
        clustered_players_path=CURRENT_DIR / "output" / "CB_clustered_players.csv",
        cluster_centers_path=CURRENT_DIR / "output" / "CB_cluster_centers_z.csv",
        rf_report_path=CURRENT_DIR / "output" / "CB_rf_report.md",
        output_dir=CURRENT_DIR / "output",
        z_columns=CB_Z_COLUMNS,
        feature_labels=CB_FEATURE_LABELS,
        cluster_labels=CB_CLUSTER_LABELS,
        score_specs=CB_SCORE_SPECS,
    )
    run_position_recommendation_scoring(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[CB][REC][ERROR] {exc}", file=sys.stderr)
        raise
