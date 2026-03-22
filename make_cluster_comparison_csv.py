import argparse
from pathlib import Path

import pandas as pd


# RandomForestと同じ9変数を既定の比較対象にする
FEATURES = [
    "PA内シュート_per90",
    "PA内シュート決定率(%)",
    "Explosive Acceleration to Sprint Count TIP_per90",
    "ボールゲイン_per90",
    "Sprint Count OTIP_per90",
    "M/min OTIP",
    "空中戦勝率(%)",
    "パス_per90",
    "PSV-99",
]


# CSVを見たときに意味がすぐ分かるよう、短い説明を付ける
FEATURE_DESCRIPTIONS = {
    "PA内シュート_per90": "90分あたりのPA内シュート数",
    "PA内シュート決定率(%)": "PA内シュートの決定率",
    "Explosive Acceleration to Sprint Count TIP_per90": "インプレー時90分あたりの爆発的加速からスプリントへの回数",
    "ボールゲイン_per90": "90分あたりのボール奪取数",
    "Sprint Count OTIP_per90": "アウトオブプレー時90分あたりのスプリント回数",
    "M/min OTIP": "アウトオブプレー時の毎分移動距離",
    "空中戦勝率(%)": "空中戦の勝率",
    "パス_per90": "90分あたりのパス数",
    "PSV-99": "最高到達スピード",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="各クラスターの平均値を比較しやすいCSVにまとめるスクリプト"
    )
    parser.add_argument(
        "--input",
        default="kmeans_results_refined.csv",
        help="K-Meansの結果CSVファイル",
    )
    parser.add_argument(
        "--output",
        default="cluster_comparison_refined.csv",
        help="出力する比較用CSVファイル",
    )
    parser.add_argument(
        "--cluster-col",
        default="Cluster_Refined",
        help="クラスター番号が入っている列名",
    )
    return parser.parse_args()


def validate_columns(df, cluster_col, features):
    missing_columns = [col for col in [cluster_col, *features] if col not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"必要な列が見つかりません: {missing_text}")


def build_comparison_table(df, cluster_col, features):
    working_df = df.copy()
    working_df[features] = working_df[features].fillna(0)

    cluster_means = working_df.groupby(cluster_col)[features].mean().sort_index()
    overall_means = working_df[features].mean()
    cluster_ranks = cluster_means.rank(axis=0, method="min", ascending=False).astype(int)
    cluster_counts = working_df[cluster_col].value_counts().sort_index()

    rows = []
    for feature in features:
        feature_means = cluster_means[feature]
        max_cluster = feature_means.idxmax()
        min_cluster = feature_means.idxmin()

        row = {
            "変数名": feature,
            "説明": FEATURE_DESCRIPTIONS.get(feature, ""),
            "全体平均": round(overall_means[feature], 3),
            "最大平均Cluster": f"Cluster {int(max_cluster)}",
            "最大平均値": round(feature_means.loc[max_cluster], 3),
            "最小平均Cluster": f"Cluster {int(min_cluster)}",
            "最小平均値": round(feature_means.loc[min_cluster], 3),
        }

        for cluster_id in cluster_means.index:
            cluster_label = f"Cluster{int(cluster_id)}"
            cluster_mean = feature_means.loc[cluster_id]
            row[f"{cluster_label}_平均"] = round(cluster_mean, 3)
            row[f"{cluster_label}_平均との差"] = round(
                cluster_mean - overall_means[feature], 3
            )
            row[f"{cluster_label}_順位"] = int(cluster_ranks.loc[cluster_id, feature])
            row[f"{cluster_label}_人数"] = int(cluster_counts.loc[cluster_id])

        rows.append(row)

    return pd.DataFrame(rows)


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = pd.read_csv(input_path)
    validate_columns(df, args.cluster_col, FEATURES)

    comparison_df = build_comparison_table(df, args.cluster_col, FEATURES)
    comparison_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"比較用CSVを保存しました: {output_path}")


if __name__ == "__main__":
    main()
