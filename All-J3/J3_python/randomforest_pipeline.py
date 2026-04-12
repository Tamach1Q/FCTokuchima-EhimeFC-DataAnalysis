"""
ポジション別 one-vs-rest RandomForest 実行の共通基盤。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold, cross_val_score
except ModuleNotFoundError as exc:
    missing_name = exc.name or "必要な依存関係"
    raise SystemExit(
        f"{missing_name} が見つかりません。`../env/bin/python` で実行するか、"
        "pandas / numpy / scikit-learn を導入してください。"
    ) from exc


@dataclass(frozen=True)
class RandomForestPositionConfig:
    """ポジション別 RandomForest 実行設定。"""

    position_code: str
    position_name_jp: str
    clustered_players_path: Path
    cluster_centers_path: Path
    cluster_summary_path: Path
    kmeans_report_path: Path
    output_dir: Path
    z_columns: list[str]
    feature_labels: dict[str, str]
    theme_groups: dict[str, list[str]]
    theme_label_candidates: dict[str, str]
    average_cluster_id: int | None = None
    n_estimators: int = 1000
    random_state: int = 42
    class_weight: str = "balanced"
    min_samples_leaf: int = 2
    permutation_repeats: int = 30
    permutation_scoring: str = "roc_auc"
    cv_folds: int = 5

    @property
    def overall_summary_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_rf_overall_summary.csv"

    def cluster_importance_path(self, cluster_id: int) -> Path:
        return self.output_dir / f"{self.position_code}_rf_cluster_{cluster_id}_importance.csv"

    @property
    def rf_report_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_rf_report.md"


def log(position_code: str, message: str) -> None:
    print(f"[{position_code}][RF] {message}")


def format_float(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float) and np.isnan(value):
        return "N/A"
    return f"{float(value):.{digits}f}"


def read_csv_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"入力ファイルにデータがありません: {path}")
    return df


def validate_columns(df: pd.DataFrame, required_columns: list[str], path: Path) -> None:
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"{path.name} に必要列がありません: {missing_columns}")


def resolve_average_cluster_id(
    config: RandomForestPositionConfig,
    summary_df: pd.DataFrame,
) -> int:
    if config.average_cluster_id is not None:
        return int(config.average_cluster_id)

    average_rows = summary_df[summary_df["is_average_candidate"].astype(str).str.lower() == "yes"]
    if average_rows.empty:
        raise ValueError(
            "average_cluster_id が未指定で、cluster_summary.csv に is_average_candidate=yes がありません。"
        )
    if len(average_rows) > 1:
        raise ValueError(
            "average_cluster_id が未指定ですが、cluster_summary.csv に is_average_candidate=yes が複数あります。"
        )
    return int(average_rows.iloc[0]["cluster_id"])


def normalize_cluster_id_series(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="raise")
    if numeric.isna().any():
        raise ValueError("cluster_id に欠損があります。")
    return numeric.astype(int)


def build_feature_matrix(df: pd.DataFrame, z_columns: list[str]) -> pd.DataFrame:
    matrix = df[z_columns].apply(pd.to_numeric, errors="raise")
    if matrix.isna().any().any():
        nan_columns = matrix.columns[matrix.isna().any()].tolist()
        raise ValueError(f"説明変数に欠損があります: {nan_columns}")
    return matrix


def compute_cv_auc(
    X: pd.DataFrame,
    y: pd.Series,
    model_params: dict[str, object],
    cv_folds: int,
    random_state: int,
) -> tuple[float, float, str]:
    positive_count = int(y.sum())
    negative_count = int(len(y) - positive_count)
    n_splits = min(cv_folds, positive_count, negative_count)

    if n_splits < 2:
        return np.nan, np.nan, "CV skipped: positive/negative 件数が不足"

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    model = RandomForestClassifier(**model_params)

    try:
        scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=1)
    except ValueError as exc:
        return np.nan, np.nan, f"CV skipped: {exc}"

    return float(scores.mean()), float(scores.std(ddof=0)), f"StratifiedKFold({n_splits})"


def theme_scores_from_importance(
    importance_df: pd.DataFrame,
    theme_groups: dict[str, list[str]],
) -> dict[str, float]:
    score_map: dict[str, float] = {}
    importance_by_feature = importance_df.set_index("feature_name")["permutation_importance_mean"].to_dict()

    for theme_name, features in theme_groups.items():
        score_map[theme_name] = float(sum(max(importance_by_feature.get(feature, 0.0), 0.0) for feature in features))

    return score_map


def rank_themes(theme_scores: dict[str, float]) -> list[tuple[str, float]]:
    return sorted(theme_scores.items(), key=lambda item: (-item[1], item[0]))


def build_average_cluster_label_candidate(
    cluster_id: int,
    average_cluster_id: int,
    candidate_expression: str,
) -> str:
    if cluster_id == average_cluster_id:
        return "平均型候補"
    return f"specialized cluster ({candidate_expression})"


def build_label_candidate(
    cluster_id: int,
    average_cluster_id: int,
    ranked_themes: list[tuple[str, float]],
    theme_label_candidates: dict[str, str],
) -> str:
    if cluster_id == average_cluster_id:
        return "平均型候補"

    selected_labels: list[str] = []
    for theme_name, score in ranked_themes:
        if score <= 0:
            continue
        label = theme_label_candidates.get(theme_name, theme_name)
        if label not in selected_labels:
            selected_labels.append(label)
        if len(selected_labels) == 2:
            break

    if not selected_labels:
        return "specialized cluster 候補"
    return " / ".join(selected_labels)


def summarize_directional_features(
    importance_df: pd.DataFrame,
    feature_labels: dict[str, str],
    top_n: int = 3,
) -> str:
    phrases: list[str] = []
    for row in importance_df.head(top_n).itertuples():
        feature_label = feature_labels.get(row.feature_name, row.feature_name)
        if row.cluster_center_z >= 0.15:
            phrases.append(f"{feature_label}が高い")
        elif row.cluster_center_z <= -0.15:
            phrases.append(f"{feature_label}が低い")
        else:
            phrases.append(f"{feature_label}が中庸")
    return "、".join(phrases)


def build_consistency_comment(
    config: RandomForestPositionConfig,
    cluster_id: int,
    average_cluster_id: int,
    candidate_expression: str,
    importance_df: pd.DataFrame,
    ranked_themes: list[tuple[str, float]],
) -> str:
    directional_summary = summarize_directional_features(
        importance_df=importance_df,
        feature_labels=config.feature_labels,
        top_n=3,
    )

    if cluster_id == average_cluster_id:
        return (
            f"KMeans の平均型候補と整合します。RF では {directional_summary} が上位ですが、"
            "いずれも specialized cluster 側の極端さを弾く軸として効いており、"
            "単一ラベルより『平均型候補』として扱う方が自然です。"
        )

    top_theme_names = [theme_name for theme_name, score in ranked_themes[:2] if score > 0]
    is_aligned = any(theme_name in candidate_expression for theme_name in top_theme_names)
    top_theme_text = " / ".join(top_theme_names) if top_theme_names else "主要テーマ未検出"

    if is_aligned:
        return (
            f"KMeans の「{candidate_expression}」候補と概ね整合します。"
            f"RF でも {directional_summary} が主な分離軸で、{top_theme_text} の解釈が妥当です。"
        )

    return (
        f"KMeans の「{candidate_expression}」候補とは部分的に整合します。"
        f"RF では {directional_summary} の寄与が大きく、{top_theme_text} の軸で見た方が説明しやすいです。"
    )


def choose_score_features(
    config: RandomForestPositionConfig,
    cluster_id: int,
    average_cluster_id: int,
    importance_df: pd.DataFrame,
    center_row: pd.Series,
) -> tuple[str, list[str]]:
    if cluster_id == average_cluster_id:
        return (
            "平均型候補は 2〜3 変数の単純加算より、"
            f"`{config.position_code}_cluster_centers_z.csv` の cluster {cluster_id} 中心への距離ベースが適切です。",
            [],
        )

    positive_center_df = importance_df[importance_df["cluster_center_z"] > 0].copy()
    selected_features = positive_center_df["feature_name"].tolist()[:3]

    if len(selected_features) >= 3:
        third_row = positive_center_df.iloc[2]
        if third_row["cluster_center_z"] < 0.15 or third_row["permutation_importance_mean"] < 0.01:
            selected_features = selected_features[:2]

    if len(selected_features) < 2:
        for feature_name in center_row.sort_values(ascending=False).index.tolist():
            if center_row[feature_name] <= 0:
                continue
            if feature_name not in selected_features:
                selected_features.append(feature_name)
            if len(selected_features) == 2:
                break

    selected_features = selected_features[:3]
    score_formula = " + ".join(selected_features)

    negative_top_features = [
        row.feature_name
        for row in importance_df.head(5).itertuples()
        if row.cluster_center_z < -0.15
    ]
    if negative_top_features:
        note = (
            f"`{score_formula}` を主軸にしつつ、"
            f"低値が効く {negative_top_features[0]} は補助条件として併用するのが自然です。"
        )
    else:
        note = f"`{score_formula}` の z 合算が自然です。"

    return note, selected_features


def format_feature_ranking_lines(
    importance_df: pd.DataFrame,
    feature_labels: dict[str, str],
    column_name: str,
    top_n: int = 5,
    include_std: bool = False,
) -> list[str]:
    sorted_df = importance_df.sort_values(by=column_name, ascending=False).head(top_n)
    lines: list[str] = []
    for rank, row in enumerate(sorted_df.itertuples(), start=1):
        feature_label = feature_labels.get(row.feature_name, row.feature_name)
        base = (
            f"{rank}. {feature_label} (`{row.feature_name}`)"
            f" / center_z={row.cluster_center_z:+.3f}"
            f" / {column_name}={getattr(row, column_name):.4f}"
        )
        if include_std:
            base += f" / std={row.permutation_importance_std:.4f}"
        lines.append(base)
    return lines


def render_report(
    config: RandomForestPositionConfig,
    average_cluster_id: int,
    player_count: int,
    cluster_counts: dict[int, int],
    model_params: dict[str, object],
    results: list[dict[str, object]],
) -> str:
    lines: list[str] = [
        f"# {config.position_code} RandomForest Report",
        "",
        "## 入力ファイル",
        f"- `{config.clustered_players_path}`",
        f"- `{config.cluster_centers_path}`",
        f"- `{config.cluster_summary_path}`",
        f"- `{config.kmeans_report_path}`",
        "",
        "## 使用した z 列",
    ]

    for feature_name in config.z_columns:
        feature_label = config.feature_labels.get(feature_name, feature_name)
        lines.append(f"- `{feature_name}` ({feature_label})")

    lines.extend(
        [
            "",
            "## データ概要",
            f"- サンプル数: {player_count}",
            f"- cluster_id 一覧: {', '.join(str(cluster_id) for cluster_id in sorted(cluster_counts))}",
            "- cluster ごとの positive / negative 件数:",
        ]
    )

    for result in results:
        lines.append(
            f"  - Cluster {result['cluster_id']}: "
            f"{result['positive_count']} / {result['negative_count']}"
        )

    lines.extend(
        [
            "",
            "## RandomForest 設定",
            f"- `RandomForestClassifier(n_estimators={model_params['n_estimators']}, "
            f"random_state={model_params['random_state']}, "
            f"class_weight=\"{model_params['class_weight']}\", "
            f"min_samples_leaf={model_params['min_samples_leaf']}, "
            f"max_depth=None, n_jobs={model_params['n_jobs']})`",
            "- one-vs-rest で各 cluster を個別に二値分類",
            f"- permutation importance: scoring=`{config.permutation_scoring}`, "
            f"`n_repeats={config.permutation_repeats}`, `random_state={config.random_state}`",
            "- 評価指標: train ROC AUC, StratifiedKFold ROC AUC",
            "- 注記: 今回の主目的は予測精度の最適化ではなく、各クラスタを説明する変数の解釈です。",
            "",
            "## Cluster 別結果",
        ]
    )

    for result in results:
        importance_df: pd.DataFrame = result["importance_df"]
        lines.extend(
            [
                f"### Cluster {result['cluster_id']}",
                f"- positive / negative: {result['positive_count']} / {result['negative_count']}",
                f"- train AUC: {format_float(result['train_auc'])}",
                (
                    f"- CV AUC: {format_float(result['cv_auc_mean'])} ± "
                    f"{format_float(result['cv_auc_std'])} ({result['cv_note']})"
                ),
                f"- KMeans candidate_expression: {result['candidate_expression']}",
                f"- ラベル候補: {result['label_candidate']}",
                f"- KMeans 解釈との整合性コメント: {result['consistency_comment']}",
                "- permutation importance 上位5:",
            ]
        )
        lines.extend(
            [f"  - {line}" for line in format_feature_ranking_lines(
                importance_df=importance_df,
                feature_labels=config.feature_labels,
                column_name="permutation_importance_mean",
                top_n=5,
                include_std=True,
            )]
        )
        lines.append("- impurity importance 上位5:")
        lines.extend(
            [f"  - {line}" for line in format_feature_ranking_lines(
                importance_df=importance_df,
                feature_labels=config.feature_labels,
                column_name="impurity_importance",
                top_n=5,
                include_std=False,
            )]
        )
        lines.append(f"- 推薦スコア候補: {result['score_note']}")
        lines.append("")

    average_result = next(result for result in results if result["cluster_id"] == average_cluster_id)
    average_top_features = ", ".join(average_result["top_features"][:3])
    lines.extend(
        [
            "## 全体所見",
            (
                f"- 平均型候補は Cluster {average_cluster_id} です。"
                f"他クラスタとの分岐で目立った変数は {average_top_features} でした。"
            ),
        ]
    )

    for result in results:
        if result["cluster_id"] == average_cluster_id:
            continue
        top_features = ", ".join(result["top_features"][:3])
        lines.append(
            f"- Cluster {result['cluster_id']} の specialized な分離軸は {top_features} でした。"
        )

    lines.extend(
        [
            "- ラベル解釈は断定ではなく候補です。KMeans 中心の高低と RF の判別寄与が同時に揃う変数を優先して読んでいます。",
            "",
            "## 推薦スコア設計メモ",
        ]
    )

    for result in results:
        if result["cluster_id"] == average_cluster_id:
            lines.append(
                f"- Cluster {result['cluster_id']}: "
                "平均型候補のため、単純加算ではなくクラスタ中心への距離ベース推奨。"
            )
            continue

        if result["score_features"]:
            lines.append(
                f"- Cluster {result['cluster_id']}: "
                f"`{' + '.join(result['score_features'])}` を主候補。"
            )
        else:
            lines.append(f"- Cluster {result['cluster_id']}: 距離ベース推奨。")

    unstable_clusters = [
        result["cluster_id"]
        for result in results
        if np.isnan(result["cv_auc_mean"]) or result["cv_auc_std"] >= 0.05
    ]
    if unstable_clusters:
        lines.extend(
            [
                "",
                "## CV 安定性メモ",
                f"- 変動がやや大きかった cluster: {', '.join(str(cluster_id) for cluster_id in unstable_clusters)}",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## CV 安定性メモ",
                "- 今回は全 cluster で 5-fold CV が実行でき、極端に不安定な cluster はありませんでした。",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def run_position_randomforest(config: RandomForestPositionConfig) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    clustered_df = read_csv_required(config.clustered_players_path)
    centers_df = read_csv_required(config.cluster_centers_path)
    summary_df = read_csv_required(config.cluster_summary_path)

    validate_columns(clustered_df, ["cluster_id", *config.z_columns], config.clustered_players_path)
    validate_columns(centers_df, ["cluster_id", *config.z_columns], config.cluster_centers_path)
    validate_columns(
        summary_df,
        ["cluster_id", "candidate_expression", "is_average_candidate", *config.z_columns],
        config.cluster_summary_path,
    )

    clustered_df["cluster_id"] = normalize_cluster_id_series(clustered_df["cluster_id"])
    centers_df["cluster_id"] = normalize_cluster_id_series(centers_df["cluster_id"])
    summary_df["cluster_id"] = normalize_cluster_id_series(summary_df["cluster_id"])
    average_cluster_id = resolve_average_cluster_id(config=config, summary_df=summary_df)

    X = build_feature_matrix(clustered_df, config.z_columns)
    cluster_ids = sorted(clustered_df["cluster_id"].unique().tolist())
    center_cluster_ids = sorted(centers_df["cluster_id"].unique().tolist())
    summary_cluster_ids = sorted(summary_df["cluster_id"].unique().tolist())

    if cluster_ids != center_cluster_ids or cluster_ids != summary_cluster_ids:
        raise ValueError(
            "cluster_id の集合が入力ファイル間で一致しません。"
            f" clustered={cluster_ids}, centers={center_cluster_ids}, summary={summary_cluster_ids}"
        )

    centers_df = centers_df.set_index("cluster_id")
    summary_df = summary_df.set_index("cluster_id")
    cluster_id_series = clustered_df["cluster_id"]

    model_params = {
        "n_estimators": config.n_estimators,
        "random_state": config.random_state,
        "class_weight": config.class_weight,
        "min_samples_leaf": config.min_samples_leaf,
        "max_depth": None,
        "n_jobs": -1,
    }

    results: list[dict[str, object]] = []

    for cluster_id in cluster_ids:
        y = (cluster_id_series == cluster_id).astype(int)
        positive_count = int(y.sum())
        negative_count = int(len(y) - positive_count)
        center_row = centers_df.loc[cluster_id, config.z_columns]
        summary_row = summary_df.loc[cluster_id]
        candidate_expression = str(summary_row["candidate_expression"])

        log(config.position_code, f"Cluster {cluster_id} 学習開始 (positive={positive_count}, negative={negative_count})")

        model = RandomForestClassifier(**model_params)
        model.fit(X, y)
        train_prob = model.predict_proba(X)[:, 1]
        train_auc = float(roc_auc_score(y, train_prob))

        cv_auc_mean, cv_auc_std, cv_note = compute_cv_auc(
            X=X,
            y=y,
            model_params=model_params,
            cv_folds=config.cv_folds,
            random_state=config.random_state,
        )

        permutation = permutation_importance(
            estimator=model,
            X=X,
            y=y,
            n_repeats=config.permutation_repeats,
            random_state=config.random_state,
            scoring=config.permutation_scoring,
            n_jobs=1,
        )

        importance_df = pd.DataFrame(
            {
                "feature_name": config.z_columns,
                "feature_label": [config.feature_labels.get(feature_name, feature_name) for feature_name in config.z_columns],
                "cluster_center_z": [float(center_row[feature_name]) for feature_name in config.z_columns],
                "impurity_importance": model.feature_importances_,
                "permutation_importance_mean": permutation.importances_mean,
                "permutation_importance_std": permutation.importances_std,
                "cluster_id": cluster_id,
                "positive_count": positive_count,
                "negative_count": negative_count,
            }
        )
        importance_df = importance_df.sort_values(
            by=["permutation_importance_mean", "impurity_importance", "feature_name"],
            ascending=[False, False, True],
        ).reset_index(drop=True)
        importance_df["rank_by_permutation"] = np.arange(1, len(importance_df) + 1)

        output_columns = [
            "feature_name",
            "impurity_importance",
            "permutation_importance_mean",
            "permutation_importance_std",
            "cluster_id",
            "positive_count",
            "negative_count",
            "rank_by_permutation",
            "feature_label",
            "cluster_center_z",
        ]
        importance_df.to_csv(
            config.cluster_importance_path(cluster_id),
            index=False,
            encoding="utf-8-sig",
            float_format="%.6f",
            columns=output_columns,
        )

        theme_scores = theme_scores_from_importance(importance_df=importance_df, theme_groups=config.theme_groups)
        ranked_themes = rank_themes(theme_scores)
        label_candidate = build_label_candidate(
            cluster_id=cluster_id,
            average_cluster_id=average_cluster_id,
            ranked_themes=ranked_themes,
            theme_label_candidates=config.theme_label_candidates,
        )
        consistency_comment = build_consistency_comment(
            config=config,
            cluster_id=cluster_id,
            average_cluster_id=average_cluster_id,
            candidate_expression=candidate_expression,
            importance_df=importance_df,
            ranked_themes=ranked_themes,
        )
        score_note, score_features = choose_score_features(
            config=config,
            cluster_id=cluster_id,
            average_cluster_id=average_cluster_id,
            importance_df=importance_df,
            center_row=center_row,
        )

        top_features = importance_df["feature_name"].tolist()[:5]

        results.append(
            {
                "cluster_id": cluster_id,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "train_auc": train_auc,
                "cv_auc_mean": cv_auc_mean,
                "cv_auc_std": cv_auc_std,
                "cv_note": cv_note,
                "top_features": top_features,
                "average_cluster_label_candidate": build_average_cluster_label_candidate(
                    cluster_id=cluster_id,
                    average_cluster_id=average_cluster_id,
                    candidate_expression=candidate_expression,
                ),
                "candidate_expression": candidate_expression,
                "label_candidate": label_candidate,
                "consistency_comment": consistency_comment,
                "score_note": score_note,
                "score_features": score_features,
                "importance_df": importance_df,
            }
        )

        log(
            config.position_code,
            f"Cluster {cluster_id} 完了: train_auc={train_auc:.4f}, cv_auc={format_float(cv_auc_mean)}",
        )

    summary_rows = []
    for result in results:
        summary_rows.append(
            {
                "cluster_id": result["cluster_id"],
                "positive_count": result["positive_count"],
                "negative_count": result["negative_count"],
                "train_auc": result["train_auc"],
                "cv_auc_mean": result["cv_auc_mean"],
                "cv_auc_std": result["cv_auc_std"],
                "top1_feature": result["top_features"][0],
                "top2_feature": result["top_features"][1],
                "top3_feature": result["top_features"][2],
                "average_cluster_label_candidate": result["average_cluster_label_candidate"],
            }
        )

    summary_df_out = pd.DataFrame(summary_rows).sort_values("cluster_id").reset_index(drop=True)
    summary_df_out.to_csv(
        config.overall_summary_path,
        index=False,
        encoding="utf-8-sig",
        float_format="%.6f",
    )

    report_text = render_report(
        config=config,
        average_cluster_id=average_cluster_id,
        player_count=len(clustered_df),
        cluster_counts=cluster_id_series.value_counts().sort_index().to_dict(),
        model_params=model_params,
        results=sorted(results, key=lambda item: int(item["cluster_id"])),
    )
    config.rf_report_path.write_text(report_text, encoding="utf-8")

    log(config.position_code, f"overall summary: {config.overall_summary_path}")
    log(config.position_code, f"report: {config.rf_report_path}")
    log(config.position_code, f"average_cluster_id={average_cluster_id}")
