"""
ポジション別 KMeans 実行の共通基盤。

外部ライブラリ未導入の環境でも実行できるように、
標準ライブラリのみで CSV 読み込み、KMeans、silhouette score、
レポート生成まで完結させる。
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Iterable

MISSING_MARKERS = {"", "nan", "none", "null", "na", "n/a"}


@dataclass(frozen=True)
class PositionConfig:
    """ポジション別の実行設定。"""

    position_code: str
    position_name_jp: str
    input_csv_path: Path
    output_dir: Path
    z_columns: list[str]
    feature_labels: dict[str, str]
    theme_groups: dict[str, list[str]]
    n_clusters: int = 4
    random_state: int = 42
    n_init: int = 50
    max_iter: int = 300
    reference_k_values: tuple[int, ...] = (2, 3, 4, 5, 6)
    include_source_feature_columns: bool = False
    include_imputation_stats: bool = False
    enable_residual_z_median_imputation: bool = False

    @property
    def clustered_players_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_clustered_players.csv"

    @property
    def cluster_centers_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_cluster_centers_z.csv"

    @property
    def cluster_summary_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_cluster_summary.csv"

    @property
    def report_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_kmeans_report.md"


def log(position_code: str, message: str) -> None:
    """簡易ログ出力。"""

    print(f"[{position_code}] {message}")


def format_float(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def read_csv_rows(csv_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        headers = reader.fieldnames or []

    if not headers:
        raise ValueError(f"ヘッダーが読めませんでした: {csv_path}")

    if not rows:
        raise ValueError(f"入力 CSV にデータ行がありません: {csv_path}")

    return rows, headers


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def identifier_columns_from_headers(headers: list[str]) -> list[str]:
    prefixes = ("raw_", "win_", "z_", "imputed_")
    return [column for column in headers if not column.startswith(prefixes)]


@dataclass(frozen=True)
class FeatureColumnBundle:
    raw_column: str
    win_column: str
    z_column: str
    imputed_column: str


@dataclass(frozen=True)
class PreparedInputData:
    matrix: list[list[float]]
    z_value_rows: list[dict[str, float]]
    clustered_rows: list[dict[str, object]]
    clustered_fieldnames: list[str]
    source_feature_columns: list[str]
    source_imputed_counts: dict[str, int]
    supplemental_imputed_counts: dict[str, int]
    median_by_z_column: dict[str, float]
    imputed_player_count: int


def feature_bundle_from_z_column(z_column: str) -> FeatureColumnBundle:
    suffix = z_column[2:] if z_column.startswith("z_") else z_column
    return FeatureColumnBundle(
        raw_column=f"raw_{suffix}",
        win_column=f"win_{suffix}",
        z_column=z_column,
        imputed_column=f"imputed_{suffix}",
    )


def feature_bundles_from_z_columns(z_columns: list[str]) -> list[FeatureColumnBundle]:
    return [feature_bundle_from_z_column(column) for column in z_columns]


def parse_optional_numeric_cell(value: str, column_name: str, row_number: int) -> float | None:
    text = (value or "").strip()
    if text.lower() in MISSING_MARKERS:
        return None
    try:
        numeric = float(text)
    except ValueError as exc:
        raise ValueError(
            f"数値変換に失敗しました: row={row_number}, column={column_name}, value={text}"
        ) from exc
    if math.isnan(numeric):
        return None
    return numeric


def parse_numeric_cell(value: str, column_name: str, row_number: int) -> float:
    numeric = parse_optional_numeric_cell(value=value, column_name=column_name, row_number=row_number)
    if numeric is None:
        raise ValueError(f"欠損が残っています: row={row_number}, column={column_name}")
    return numeric


def parse_imputed_flag(value: str) -> bool:
    text = (value or "").strip().lower()
    return text in {"1", "1.0", "true", "yes"}


def build_matrix(
    rows: list[dict[str, str]],
    z_columns: list[str],
) -> tuple[list[list[float]], list[dict[str, float]]]:
    matrix: list[list[float]] = []
    z_value_rows: list[dict[str, float]] = []

    for row_index, row in enumerate(rows, start=2):
        vector: list[float] = []
        z_values: dict[str, float] = {}
        for column in z_columns:
            numeric = parse_numeric_cell(row.get(column, ""), column_name=column, row_number=row_index)
            vector.append(numeric)
            z_values[column] = numeric
        matrix.append(vector)
        z_value_rows.append(z_values)

    return matrix, z_value_rows


def validate_source_feature_columns(headers: list[str], bundles: list[FeatureColumnBundle]) -> None:
    missing_columns: list[str] = []
    for bundle in bundles:
        for column in (bundle.raw_column, bundle.win_column, bundle.imputed_column):
            if column not in headers:
                missing_columns.append(column)
    if missing_columns:
        raise ValueError(f"必要な raw / win / imputed 列が存在しません: {missing_columns}")


def build_prepared_input_data(
    config: PositionConfig,
    rows: list[dict[str, str]],
    headers: list[str],
    identifier_columns: list[str],
) -> PreparedInputData:
    bundles = feature_bundles_from_z_columns(config.z_columns)

    if config.include_source_feature_columns:
        validate_source_feature_columns(headers=headers, bundles=bundles)

    if not config.enable_residual_z_median_imputation and not config.include_source_feature_columns and not config.include_imputation_stats:
        matrix, z_value_rows = build_matrix(rows, config.z_columns)
        clustered_rows: list[dict[str, object]] = []
        for raw_row, z_row in zip(rows, z_value_rows):
            output_row: dict[str, object] = {
                column: raw_row[column]
                for column in identifier_columns
            }
            for column in config.z_columns:
                output_row[column] = format_float(z_row[column])
            clustered_rows.append(output_row)
        return PreparedInputData(
            matrix=matrix,
            z_value_rows=z_value_rows,
            clustered_rows=clustered_rows,
            clustered_fieldnames=identifier_columns + config.z_columns,
            source_feature_columns=[],
            source_imputed_counts={column: 0 for column in config.z_columns},
            supplemental_imputed_counts={column: 0 for column in config.z_columns},
            median_by_z_column={column: 0.0 for column in config.z_columns},
            imputed_player_count=0,
        )

    observed_values: dict[str, list[float]] = {column: [] for column in config.z_columns}
    for row_index, row in enumerate(rows, start=2):
        for column in config.z_columns:
            numeric = parse_optional_numeric_cell(
                row.get(column, ""),
                column_name=column,
                row_number=row_index,
            )
            if numeric is not None:
                observed_values[column].append(numeric)

    median_by_z_column: dict[str, float] = {}
    for column, values in observed_values.items():
        if not values:
            raise ValueError(f"{column} は全件欠損のため中央値補完できません。")
        median_by_z_column[column] = float(median(values))

    matrix: list[list[float]] = []
    z_value_rows: list[dict[str, float]] = []
    clustered_rows: list[dict[str, object]] = []
    source_feature_columns: list[str] = []
    if config.include_source_feature_columns:
        for bundle in bundles:
            source_feature_columns.extend(
                [bundle.raw_column, bundle.win_column, bundle.z_column, bundle.imputed_column]
            )
    else:
        source_feature_columns.extend(config.z_columns)

    source_imputed_counts = {column: 0 for column in config.z_columns}
    supplemental_imputed_counts = {column: 0 for column in config.z_columns}
    imputed_player_count = 0

    for row_index, raw_row in enumerate(rows, start=2):
        output_row: dict[str, object] = {
            column: raw_row[column]
            for column in identifier_columns
        }
        vector: list[float] = []
        z_values: dict[str, float] = {}
        imputed_count = 0

        for bundle in bundles:
            if config.include_source_feature_columns:
                output_row[bundle.raw_column] = raw_row.get(bundle.raw_column, "")
                output_row[bundle.win_column] = raw_row.get(bundle.win_column, "")

            source_imputed = parse_imputed_flag(raw_row.get(bundle.imputed_column, ""))
            if source_imputed:
                source_imputed_counts[bundle.z_column] += 1

            numeric = parse_optional_numeric_cell(
                raw_row.get(bundle.z_column, ""),
                column_name=bundle.z_column,
                row_number=row_index,
            )
            supplemental_imputed = False
            if numeric is None:
                if not config.enable_residual_z_median_imputation:
                    raise ValueError(f"欠損が残っています: row={row_index}, column={bundle.z_column}")
                numeric = median_by_z_column[bundle.z_column]
                supplemental_imputed = True
                supplemental_imputed_counts[bundle.z_column] += 1

            effective_imputed = source_imputed or supplemental_imputed
            if effective_imputed:
                imputed_count += 1

            z_values[bundle.z_column] = numeric
            vector.append(numeric)

            output_row[bundle.z_column] = format_float(numeric)
            if config.include_source_feature_columns:
                output_row[bundle.imputed_column] = 1 if effective_imputed else 0

        if config.include_imputation_stats:
            output_row["imputed_count"] = imputed_count
            output_row["imputed_ratio"] = format_float(imputed_count / len(bundles), digits=4)

        if imputed_count > 0:
            imputed_player_count += 1

        matrix.append(vector)
        z_value_rows.append(z_values)
        clustered_rows.append(output_row)

    clustered_fieldnames = identifier_columns + source_feature_columns
    if config.include_imputation_stats:
        clustered_fieldnames.extend(["imputed_count", "imputed_ratio"])

    return PreparedInputData(
        matrix=matrix,
        z_value_rows=z_value_rows,
        clustered_rows=clustered_rows,
        clustered_fieldnames=clustered_fieldnames,
        source_feature_columns=source_feature_columns,
        source_imputed_counts=source_imputed_counts,
        supplemental_imputed_counts=supplemental_imputed_counts,
        median_by_z_column=median_by_z_column,
        imputed_player_count=imputed_player_count,
    )


def squared_euclidean(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(squared_euclidean(a, b))


def vector_mean(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        raise ValueError("空ベクトル集合の平均は計算できません。")
    dimension = len(vectors[0])
    return [
        sum(vector[column_index] for vector in vectors) / len(vectors)
        for column_index in range(dimension)
    ]


def assign_points(points: list[list[float]], centers: list[list[float]]) -> tuple[list[int], list[float]]:
    labels: list[int] = []
    min_squared_distances: list[float] = []

    for point in points:
        best_label = 0
        best_distance = squared_euclidean(point, centers[0])
        for label in range(1, len(centers)):
            distance = squared_euclidean(point, centers[label])
            if distance < best_distance:
                best_label = label
                best_distance = distance
        labels.append(best_label)
        min_squared_distances.append(best_distance)

    return labels, min_squared_distances


def rebalance_empty_clusters(
    points: list[list[float]],
    labels: list[int],
    min_squared_distances: list[float],
    k: int,
) -> None:
    """空クラスタが出た場合、距離の大きい点を再配置する。"""

    while True:
        counts = [0] * k
        for label in labels:
            counts[label] += 1

        empty_clusters = [cluster_id for cluster_id, count in enumerate(counts) if count == 0]
        if not empty_clusters:
            return

        empty_cluster = empty_clusters[0]
        donor_candidates = [cluster_id for cluster_id, count in enumerate(counts) if count > 1]
        if not donor_candidates:
            raise ValueError("空クラスタを解消できませんでした。")

        donor_label = max(
            donor_candidates,
            key=lambda cluster_id: max(
                min_squared_distances[index]
                for index, label in enumerate(labels)
                if label == cluster_id
            ),
        )

        donor_index = max(
            (index for index, label in enumerate(labels) if label == donor_label),
            key=lambda index: min_squared_distances[index],
        )
        labels[donor_index] = empty_cluster
        min_squared_distances[donor_index] = 0.0


def recompute_centers(points: list[list[float]], labels: list[int], k: int) -> list[list[float]]:
    grouped_points: list[list[list[float]]] = [[] for _ in range(k)]
    for point, label in zip(points, labels):
        grouped_points[label].append(point)
    return [vector_mean(group) for group in grouped_points]


def initialize_centers_kmeans_plus_plus(
    points: list[list[float]],
    k: int,
    rng: random.Random,
) -> list[list[float]]:
    centers = [list(points[rng.randrange(len(points))])]

    while len(centers) < k:
        distances = [
            min(squared_euclidean(point, center) for center in centers)
            for point in points
        ]
        total_distance = sum(distances)
        if total_distance <= 0:
            centers.append(list(points[rng.randrange(len(points))]))
            continue

        threshold = rng.random() * total_distance
        cumulative = 0.0
        selected_index = len(points) - 1
        for index, distance in enumerate(distances):
            cumulative += distance
            if cumulative >= threshold:
                selected_index = index
                break
        centers.append(list(points[selected_index]))

    return centers


def run_single_kmeans(
    points: list[list[float]],
    k: int,
    random_seed: int,
    max_iter: int,
) -> tuple[list[list[float]], list[int], float]:
    if len(points) < k:
        raise ValueError(f"サンプル数 {len(points)} がクラスタ数 {k} より少ないため実行できません。")

    rng = random.Random(random_seed)
    centers = initialize_centers_kmeans_plus_plus(points, k, rng)
    previous_labels: list[int] | None = None

    for _ in range(max_iter):
        labels, min_squared_distances = assign_points(points, centers)
        rebalance_empty_clusters(points, labels, min_squared_distances, k)

        if previous_labels == labels:
            break

        centers = recompute_centers(points, labels, k)
        previous_labels = labels
    else:
        labels, min_squared_distances = assign_points(points, centers)
        rebalance_empty_clusters(points, labels, min_squared_distances, k)
        centers = recompute_centers(points, labels, k)

    labels, min_squared_distances = assign_points(points, centers)
    rebalance_empty_clusters(points, labels, min_squared_distances, k)
    centers = recompute_centers(points, labels, k)
    inertia = sum(min_squared_distances)
    return centers, labels, inertia


def fit_kmeans(points: list[list[float]], k: int, n_init: int, random_state: int, max_iter: int) -> dict[str, object]:
    best_result: dict[str, object] | None = None

    for init_index in range(n_init):
        seed = random_state + init_index
        centers, labels, inertia = run_single_kmeans(points, k=k, random_seed=seed, max_iter=max_iter)

        if best_result is None or inertia < best_result["inertia"]:
            best_result = {
                "centers": centers,
                "labels": labels,
                "inertia": inertia,
                "seed": seed,
            }

    if best_result is None:
        raise RuntimeError("KMeans の初期化反復が 1 回も実行されませんでした。")

    return best_result


def silhouette_score(points: list[list[float]], labels: list[int], k: int) -> float:
    grouped_indices: dict[int, list[int]] = {cluster_id: [] for cluster_id in range(k)}
    for index, label in enumerate(labels):
        grouped_indices[label].append(index)

    silhouettes: list[float] = []
    for index, point in enumerate(points):
        own_cluster = labels[index]
        own_members = grouped_indices[own_cluster]

        if len(own_members) <= 1:
            silhouettes.append(0.0)
            continue

        a = sum(
            euclidean(point, points[member_index])
            for member_index in own_members
            if member_index != index
        ) / (len(own_members) - 1)

        b_candidates: list[float] = []
        for cluster_id, member_indices in grouped_indices.items():
            if cluster_id == own_cluster or not member_indices:
                continue
            average_distance = sum(
                euclidean(point, points[member_index])
                for member_index in member_indices
            ) / len(member_indices)
            b_candidates.append(average_distance)

        b = min(b_candidates)
        if a == 0.0 and b == 0.0:
            silhouettes.append(0.0)
        else:
            silhouettes.append((b - a) / max(a, b))

    return sum(silhouettes) / len(silhouettes)


def cluster_counts(labels: list[int], k: int) -> dict[int, int]:
    counts = {cluster_id: 0 for cluster_id in range(k)}
    for label in labels:
        counts[label] += 1
    return counts


def center_as_mapping(z_columns: list[str], center: list[float]) -> dict[str, float]:
    return {column: value for column, value in zip(z_columns, center)}


def top_abs_features(center_map: dict[str, float], top_n: int = 3) -> list[tuple[str, float]]:
    return sorted(center_map.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n]


def top_positive_features(center_map: dict[str, float], top_n: int = 3) -> list[tuple[str, float]]:
    positives = [(column, value) for column, value in center_map.items() if value > 0]
    return sorted(positives, key=lambda item: item[1], reverse=True)[:top_n]


def distance_from_origin(center: list[float]) -> float:
    return math.sqrt(sum(value * value for value in center))


def describe_average_cluster(distance_value: float, second_distance: float | None) -> str:
    if distance_value <= 0.8:
        return "はい。原点にかなり近く、平均型候補とみなしやすいです。"
    if distance_value <= 1.2:
        if second_distance is not None and (second_distance - distance_value) >= 0.1:
            return "概ねはい。原点に比較的近く、他クラスタより平均型候補として扱いやすいです。"
        return "条件付きではい。原点には近いものの、他クラスタとの差は大きくありません。"
    return "慎重判断です。最も近いクラスタではありますが、原点からはやや離れています。"


def infer_cluster_expression(
    theme_groups: dict[str, list[str]],
    center_map: dict[str, float],
) -> str:
    scores: list[tuple[str, float]] = []
    for label, columns in theme_groups.items():
        score = sum(max(center_map.get(column, 0.0), 0.0) for column in columns)
        scores.append((label, score))

    scores.sort(key=lambda item: item[1], reverse=True)
    strong_groups = [label for label, score in scores if score >= 0.25]
    if strong_groups:
        return " / ".join(strong_groups[:2])

    strongest_label, strongest_score = scores[0]
    if strongest_score > 0:
        return strongest_label

    return "特定の一方向に寄り切らないバランス差"


def build_reference_metrics(config: PositionConfig, points: list[list[float]]) -> list[dict[str, object]]:
    metrics: list[dict[str, object]] = []
    for k in config.reference_k_values:
        result = fit_kmeans(
            points,
            k=k,
            n_init=config.n_init,
            random_state=config.random_state,
            max_iter=config.max_iter,
        )
        labels = result["labels"]
        inertia = result["inertia"]
        score = silhouette_score(points, labels, k)
        metrics.append(
            {
                "k": k,
                "inertia": inertia,
                "silhouette_score": score,
                "seed": result["seed"],
            }
        )
    return metrics


def build_cluster_summary_rows(
    config: PositionConfig,
    centers: list[list[float]],
    labels: list[int],
) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    counts = cluster_counts(labels, config.n_clusters)
    center_mappings = [center_as_mapping(config.z_columns, center) for center in centers]
    distances = [distance_from_origin(center) for center in centers]
    average_cluster_id = min(range(config.n_clusters), key=lambda cluster_id: distances[cluster_id])

    summary_rows: list[dict[str, object]] = []
    analysis_rows: list[dict[str, object]] = []

    sorted_distances = sorted((distance, cluster_id) for cluster_id, distance in enumerate(distances))
    second_distance = sorted_distances[1][0] if len(sorted_distances) > 1 else None

    for cluster_id in range(config.n_clusters):
        center_map = center_mappings[cluster_id]
        abs_features = top_abs_features(center_map, top_n=3)
        positive_features = top_positive_features(center_map, top_n=3)
        expression = infer_cluster_expression(config.theme_groups, center_map)
        is_average_candidate = cluster_id == average_cluster_id

        row: dict[str, object] = {
            "cluster_id": cluster_id,
            "player_count": counts[cluster_id],
            "distance_from_origin": format_float(distances[cluster_id]),
            "top_abs_feature_1": abs_features[0][0],
            "top_abs_feature_1_z": format_float(abs_features[0][1]),
            "top_abs_feature_2": abs_features[1][0],
            "top_abs_feature_2_z": format_float(abs_features[1][1]),
            "top_abs_feature_3": abs_features[2][0],
            "top_abs_feature_3_z": format_float(abs_features[2][1]),
            "candidate_expression": expression,
            "is_average_candidate": "yes" if is_average_candidate else "no",
        }
        for column in config.z_columns:
            row[column] = format_float(center_map[column])
        summary_rows.append(row)

        analysis_rows.append(
            {
                "cluster_id": cluster_id,
                "player_count": counts[cluster_id],
                "distance_from_origin": distances[cluster_id],
                "center_map": center_map,
                "top_abs_features": abs_features,
                "top_positive_features": positive_features,
                "candidate_expression": expression,
                "average_cluster_comment": describe_average_cluster(
                    distances[cluster_id],
                    second_distance=second_distance if is_average_candidate else None,
                ),
            }
        )

    return summary_rows, analysis_rows, average_cluster_id


def feature_display(config: PositionConfig, column_name: str) -> str:
    return config.feature_labels.get(column_name, column_name)


def build_cluster_report(
    config: PositionConfig,
    sample_count: int,
    reference_metrics: list[dict[str, object]],
    analysis_rows: list[dict[str, object]],
    average_cluster_id: int,
    final_inertia: float,
    final_silhouette_score: float,
    identifier_columns: list[str],
    source_imputed_counts: dict[str, int],
    supplemental_imputed_counts: dict[str, int],
    median_by_z_column: dict[str, float],
    imputed_player_count: int,
) -> str:
    counts_lookup = {
        row["cluster_id"]: row["player_count"]
        for row in analysis_rows
    }
    best_reference = max(reference_metrics, key=lambda item: item["silhouette_score"])
    selected_k_reference = next(
        (item for item in reference_metrics if item["k"] == config.n_clusters),
        None,
    )
    reference_k_text = ", ".join(str(k) for k in config.reference_k_values)

    lines: list[str] = []
    lines.append(f"# {config.position_code} KMeans Report")
    lines.append("")
    lines.append("## 入力概要")
    lines.append(f"- 入力ファイル: `{config.input_csv_path}`")
    lines.append(f"- サンプル数: {sample_count}")
    lines.append(f"- 識別列: {', '.join(f'`{column}`' for column in identifier_columns)}")
    lines.append("- 使用した z 列:")
    for column in config.z_columns:
        lines.append(f"  - `{column}` ({feature_display(config, column)})")
    lines.append("")
    if config.include_source_feature_columns:
        lines.append("## 使用対象列")
        lines.append("- 指定 z 列に対応する raw / win / z / imputed 列を使用しました。")
        for bundle in feature_bundles_from_z_columns(config.z_columns):
            lines.append(
                f"- `{bundle.raw_column}` / `{bundle.win_column}` / "
                f"`{bundle.z_column}` / `{bundle.imputed_column}`"
            )
        lines.append("")
    if config.include_imputation_stats or config.enable_residual_z_median_imputation:
        lines.append("## 欠損補完メモ")
        if config.enable_residual_z_median_imputation:
            lines.append("- 残存 z 欠損はポジション内中央値で補完しました。")
        else:
            lines.append("- 追加の中央値補完は行っていません。")
        lines.append(f"- `imputed_count > 0` の選手数: {imputed_player_count}")
        if config.include_imputation_stats:
            lines.append("- 出力列として `imputed_count` / `imputed_ratio` を付与しています。")
        lines.append("- 入力 `imputed_*` 列の件数:")
        for column in config.z_columns:
            lines.append(
                f"  - `{column}`: {source_imputed_counts.get(column, 0)} 件"
            )
        lines.append("- 追加で中央値補完した列と件数:")
        supplemented_columns = [
            column
            for column in config.z_columns
            if supplemental_imputed_counts.get(column, 0) > 0
        ]
        if supplemented_columns:
            for column in supplemented_columns:
                lines.append(
                    f"  - `{column}`: {supplemental_imputed_counts[column]} 件 "
                    f"(median={format_float(median_by_z_column[column], digits=4)})"
                )
        else:
            lines.append("  - 追加補完は発生していません。")
        lines.append("")
    lines.append("## KMeans 設定")
    lines.append(f"- n_clusters: {config.n_clusters}")
    lines.append(f"- random_state: {config.random_state}")
    lines.append(f"- n_init: {config.n_init}")
    lines.append(f"- max_iter: {config.max_iter}")
    lines.append(f"- k={config.n_clusters} の inertia: {format_float(final_inertia)}")
    lines.append(f"- k={config.n_clusters} の silhouette score: {format_float(final_silhouette_score)}")
    lines.append("")
    lines.append(f"## 参考指標 (k={reference_k_text})")
    lines.append("| k | inertia | silhouette_score | 採用 seed |")
    lines.append("| --- | ---: | ---: | ---: |")
    for metric in reference_metrics:
        lines.append(
            f"| {metric['k']} | {format_float(metric['inertia'])} | "
            f"{format_float(metric['silhouette_score'])} | {metric['seed']} |"
        )
    lines.append("")
    lines.append(
        f"- silhouette score の最大は k={best_reference['k']} "
        f"({format_float(best_reference['silhouette_score'])}) でした。"
    )
    if best_reference["k"] == config.n_clusters:
        lines.append(
            f"- 固定条件の k={config.n_clusters} は、参考レンジ内でも最も高い silhouette score でした。"
        )
    else:
        lines.append(
            f"- 今回は要件どおり k={config.n_clusters} を採用しています。"
            f" 参考上は k={best_reference['k']} の方が分離度は高めでした。"
        )
    if selected_k_reference is not None:
        lines.append(
            f"- k={config.n_clusters} の silhouette score は "
            f"{format_float(selected_k_reference['silhouette_score'])} で、"
            " クラスタ解釈と業務用途の両立を前提に見る必要があります。"
        )
    else:
        lines.append(
            f"- k={config.n_clusters} の本実行 silhouette score は "
            f"{format_float(final_silhouette_score)} でした。"
        )
    lines.append("")
    lines.append("## 各クラスタ人数")
    for cluster_id in range(config.n_clusters):
        lines.append(f"- Cluster {cluster_id}: {counts_lookup[cluster_id]} 名")
    lines.append("")
    lines.append(
        f"## 原点に最も近いクラスタ\n- Cluster {average_cluster_id} が最も原点に近く、"
        "「平均型候補」として扱います。"
    )
    average_row = next(row for row in analysis_rows if row["cluster_id"] == average_cluster_id)
    lines.append(
        f"- 距離: {format_float(average_row['distance_from_origin'])}"
        f" / 判定メモ: {average_row['average_cluster_comment']}"
    )
    lines.append("")
    lines.append("## クラスタ中心の特徴")
    for row in analysis_rows:
        cluster_id = row["cluster_id"]
        center_map = row["center_map"]
        abs_features = row["top_abs_features"]
        positive_features = row["top_positive_features"]
        top_abs_text = ", ".join(
            f"{feature_display(config, column)} ({format_float(value)})"
            for column, value in abs_features
        )
        if positive_features:
            positive_text = ", ".join(
                f"{feature_display(config, column)} ({format_float(value)})"
                for column, value in positive_features
            )
        else:
            positive_text = "正方向に大きい変数は限定的"

        lines.append(f"### Cluster {cluster_id}")
        lines.append(f"- 人数: {row['player_count']} 名")
        lines.append(f"- 原点からの距離: {format_float(row['distance_from_origin'])}")
        lines.append(f"- 絶対値上位3変数: {top_abs_text}")
        lines.append(f"- 高い z 値の主軸: {positive_text}")
        if cluster_id == average_cluster_id:
            lines.append(
                f"- 解釈: 平均型候補。{row['average_cluster_comment']}"
            )
        else:
            lines.append(
                f"- 解釈候補: {row['candidate_expression']}。"
                " 最終ラベルは RandomForest と代表選手確認で詰める前提です。"
            )
        lines.append("- クラスタ中心の z 値:")
        for column in config.z_columns:
            lines.append(
                f"  - {feature_display(config, column)}: {format_float(center_map[column])}"
            )
        lines.append("")

    lines.append("## 他クラスタの大まかな特徴")
    for row in analysis_rows:
        if row["cluster_id"] == average_cluster_id:
            continue
        lines.append(
            f"- Cluster {row['cluster_id']}: {row['candidate_expression']} を示す候補。"
            f" 原点距離は {format_float(row['distance_from_origin'])}。"
        )
    lines.append("")
    lines.append("## 今後 RandomForest で見るべき論点")
    lines.append(
        f"- Cluster {average_cluster_id} を one-vs-rest にして、"
        " 平均型候補を他クラスタから最も分ける変数が何かを確認する。"
    )
    lines.append(
        "- 各 specialized cluster 候補について、上位変数が本当に判別寄与でも上位に来るかを確認する。"
    )
    lines.append(
        "- 走力系と技術系、守備系と配球系のような相関の強い軸で重要度が偏りすぎないかを確認する。"
    )
    lines.append(
        "- 代表選手をクラスタ距離の近い順に見て、クラスタ中心の解釈が現場感覚と矛盾しないか確認する。"
    )

    return "\n".join(lines) + "\n"


def write_report(path: Path, markdown_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_text, encoding="utf-8")


def run_position_kmeans(config: PositionConfig) -> dict[str, object]:
    log(config.position_code, f"入力ファイルを読み込みます: {config.input_csv_path}")
    rows, headers = read_csv_rows(config.input_csv_path)
    identifier_columns = identifier_columns_from_headers(headers)

    missing_columns = [column for column in config.z_columns if column not in headers]
    if missing_columns:
        raise ValueError(f"必要な z 列が存在しません: {missing_columns}")

    log(
        config.position_code,
        f"サンプル数={len(rows)}, 識別列={identifier_columns}, 使用 z 列数={len(config.z_columns)}",
    )

    prepared = build_prepared_input_data(
        config=config,
        rows=rows,
        headers=headers,
        identifier_columns=identifier_columns,
    )
    matrix = prepared.matrix
    z_value_rows = prepared.z_value_rows
    if config.enable_residual_z_median_imputation:
        supplemental_total = sum(prepared.supplemental_imputed_counts.values())
        log(
            config.position_code,
            f"前処理済み入力を確認し、残存 z 欠損への中央値補完を適用しました。追加補完件数={supplemental_total}",
        )
    else:
        log(config.position_code, "z 列の欠損確認を通過しました。")

    log(
        config.position_code,
        f"参考指標用に k={','.join(str(k) for k in config.reference_k_values)} の inertia / silhouette score を計算します。",
    )
    reference_metrics = build_reference_metrics(config, matrix)

    log(
        config.position_code,
        f"k={config.n_clusters} で本実行します "
        f"(random_state={config.random_state}, n_init={config.n_init})。",
    )
    final_result = fit_kmeans(
        matrix,
        k=config.n_clusters,
        n_init=config.n_init,
        random_state=config.random_state,
        max_iter=config.max_iter,
    )
    centers = final_result["centers"]
    labels = final_result["labels"]
    final_inertia = final_result["inertia"]
    final_silhouette = silhouette_score(matrix, labels, config.n_clusters)

    cluster_distances = [
        euclidean(vector, centers[label])
        for vector, label in zip(matrix, labels)
    ]

    summary_rows, analysis_rows, average_cluster_id = build_cluster_summary_rows(
        config=config,
        centers=centers,
        labels=labels,
    )

    clustered_rows: list[dict[str, object]] = []
    for prepared_row, cluster_id, distance_value in zip(prepared.clustered_rows, labels, cluster_distances):
        output_row = dict(prepared_row)
        output_row["cluster_id"] = cluster_id
        output_row["cluster_distance_to_center"] = format_float(distance_value)
        clustered_rows.append(output_row)

    centers_rows: list[dict[str, object]] = []
    for cluster_id, center in enumerate(centers):
        row: dict[str, object] = {"cluster_id": cluster_id}
        for column, value in zip(config.z_columns, center):
            row[column] = format_float(value)
        centers_rows.append(row)

    log(config.position_code, f"出力ディレクトリを準備します: {config.output_dir}")
    config.output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        config.clustered_players_path,
        fieldnames=prepared.clustered_fieldnames + ["cluster_id", "cluster_distance_to_center"],
        rows=clustered_rows,
    )
    log(config.position_code, f"出力しました: {config.clustered_players_path}")

    write_csv(
        config.cluster_centers_path,
        fieldnames=["cluster_id"] + config.z_columns,
        rows=centers_rows,
    )
    log(config.position_code, f"出力しました: {config.cluster_centers_path}")

    write_csv(
        config.cluster_summary_path,
        fieldnames=[
            "cluster_id",
            "player_count",
            "distance_from_origin",
            "top_abs_feature_1",
            "top_abs_feature_1_z",
            "top_abs_feature_2",
            "top_abs_feature_2_z",
            "top_abs_feature_3",
            "top_abs_feature_3_z",
            "candidate_expression",
            "is_average_candidate",
        ] + config.z_columns,
        rows=summary_rows,
    )
    log(config.position_code, f"出力しました: {config.cluster_summary_path}")

    markdown_report = build_cluster_report(
        config=config,
        sample_count=len(rows),
        reference_metrics=reference_metrics,
        analysis_rows=analysis_rows,
        average_cluster_id=average_cluster_id,
        final_inertia=final_inertia,
        final_silhouette_score=final_silhouette,
        identifier_columns=identifier_columns,
        source_imputed_counts=prepared.source_imputed_counts,
        supplemental_imputed_counts=prepared.supplemental_imputed_counts,
        median_by_z_column=prepared.median_by_z_column,
        imputed_player_count=prepared.imputed_player_count,
    )
    write_report(config.report_path, markdown_report)
    log(config.position_code, f"出力しました: {config.report_path}")

    verify_rows, _ = read_csv_rows(config.clustered_players_path)
    if len(verify_rows) != len(rows):
        raise ValueError(
            f"出力行数が一致しません: input={len(rows)}, output={len(verify_rows)}"
        )

    counts = cluster_counts(labels, config.n_clusters)
    log(
        config.position_code,
        "実行完了: "
        f"input_rows={len(rows)}, output_rows={len(verify_rows)}, "
        f"cluster_counts={counts}, average_cluster={average_cluster_id}",
    )

    return {
        "sample_count": len(rows),
        "cluster_counts": counts,
        "average_cluster_id": average_cluster_id,
        "reference_metrics": reference_metrics,
        "final_inertia": final_inertia,
        "final_silhouette_score": final_silhouette,
        "output_files": [
            config.clustered_players_path,
            config.cluster_centers_path,
            config.cluster_summary_path,
            config.report_path,
        ],
    }
