"""
ポジション別推薦スコアリングの共通基盤。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    missing_name = exc.name or "必要な依存関係"
    raise SystemExit(
        f"{missing_name} が見つかりません。`../env/bin/python` で実行するか、"
        "pandas / numpy を導入してください。"
    ) from exc


REQUIRED_PLAYER_COLUMNS = [
    "FB_Name",
    "SC_Name",
    "analysis_position_code",
    "cluster_id",
]


@dataclass(frozen=True)
class ScoreSpec:
    """クラスタ別の推薦スコア定義。"""

    cluster_id: int
    cluster_label: str
    method: Literal["sum", "distance"]
    formula_text: str
    rationale: str
    components: tuple[str, ...] = ()
    weights: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if self.method == "sum":
            if not self.components:
                raise ValueError(f"cluster {self.cluster_id}: sum スコアには components が必要です。")
            if len(self.components) != len(self.weights):
                raise ValueError(f"cluster {self.cluster_id}: components と weights の長さが一致しません。")
        if self.method == "distance" and (self.components or self.weights):
            raise ValueError(f"cluster {self.cluster_id}: distance スコアに components / weights は不要です。")

    @property
    def score_column(self) -> str:
        return f"score_cluster_{self.cluster_id}"

    @property
    def rank_column(self) -> str:
        return f"rank_cluster_{self.cluster_id}"

    @property
    def distance_column(self) -> str:
        return f"distance_to_cluster_center_{self.cluster_id}"


@dataclass(frozen=True)
class RecommendationPositionConfig:
    """ポジション別推薦スコアリング設定。"""

    position_code: str
    position_name_jp: str
    clustered_players_path: Path
    cluster_centers_path: Path
    rf_report_path: Path
    output_dir: Path
    z_columns: list[str]
    feature_labels: dict[str, str]
    cluster_labels: dict[int, str]
    score_specs: tuple[ScoreSpec, ...]

    @property
    def recommendation_scores_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_recommendation_scores.csv"

    @property
    def recommendation_top10_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_recommendation_top10_by_cluster.csv"

    @property
    def recommendation_report_path(self) -> Path:
        return self.output_dir / f"{self.position_code}_recommendation_report.md"


def log(position_code: str, message: str) -> None:
    print(f"[{position_code}][REC] {message}")


def read_csv_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    if df.empty:
        raise ValueError(f"入力ファイルにデータがありません: {path}")
    return df


def read_text_required(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"入力 Markdown が空です: {path}")
    return text


def validate_columns(df: pd.DataFrame, required_columns: list[str], path: Path) -> None:
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"{path.name} に必要列がありません: {missing_columns}")


def normalize_cluster_id_series(series: pd.Series, source_name: str) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.isna().any():
        raise ValueError(f"{source_name} の cluster_id に数値変換できない値があります。")
    return numeric.astype(int)


def numeric_frame_required(df: pd.DataFrame, columns: list[str], source_name: str) -> pd.DataFrame:
    numeric_df = df[columns].apply(pd.to_numeric, errors="coerce")
    if numeric_df.isna().any().any():
        nan_columns = numeric_df.columns[numeric_df.isna().any()].tolist()
        raise ValueError(f"{source_name} の数値列に欠損または非数値があります: {nan_columns}")
    return numeric_df


def validate_config(config: RecommendationPositionConfig) -> list[ScoreSpec]:
    spec_ids = [spec.cluster_id for spec in config.score_specs]
    if len(spec_ids) != len(set(spec_ids)):
        raise ValueError("score_specs の cluster_id が重複しています。")

    cluster_label_ids = sorted(config.cluster_labels.keys())
    if sorted(spec_ids) != cluster_label_ids:
        raise ValueError(
            "cluster_labels と score_specs の cluster_id が一致しません: "
            f"labels={cluster_label_ids}, specs={sorted(spec_ids)}"
        )

    return sorted(config.score_specs, key=lambda spec: spec.cluster_id)


def build_ordinal_rank(df: pd.DataFrame, score_column: str) -> pd.Series:
    working = df[[score_column, "FB_Name", "SC_Name"]].copy()
    working["_index"] = df.index
    sorted_index = (
        working.sort_values(
            by=[score_column, "FB_Name", "SC_Name", "_index"],
            ascending=[False, True, True, True],
            kind="mergesort",
        )["_index"]
        .tolist()
    )

    rank_series = pd.Series(index=df.index, dtype="int64")
    rank_series.loc[sorted_index] = np.arange(1, len(sorted_index) + 1)
    return rank_series


def format_number(value: float) -> str:
    return f"{float(value):.3f}"


def component_summary(spec: ScoreSpec, feature_labels: dict[str, str]) -> str:
    if spec.method == "distance":
        return "KMeans に使った全 z 列"

    parts: list[str] = []
    for column, weight in zip(spec.components, spec.weights):
        feature_label = feature_labels.get(column, column)
        operator = "+" if weight >= 0 else "-"
        parts.append(f"{operator} {feature_label} (`{column}`)")
    return " ".join(parts).lstrip("+ ").strip()


def cluster_overview_sentence(spec: ScoreSpec, feature_labels: dict[str, str]) -> str:
    if spec.method == "distance":
        return "全 z 列ベクトルでクラスタ中心との距離が小さい選手が上位です。"

    positive_features = [
        feature_labels.get(column, column)
        for column, weight in zip(spec.components, spec.weights)
        if weight > 0
    ]
    negative_features = [
        feature_labels.get(column, column)
        for column, weight in zip(spec.components, spec.weights)
        if weight < 0
    ]

    if positive_features and negative_features:
        return (
            f"{'・'.join(positive_features)}が高く、"
            f"{'・'.join(negative_features)}は低めの選手が上位です。"
        )
    if positive_features:
        return f"{'・'.join(positive_features)}が高い選手が上位です。"
    if negative_features:
        return f"{'・'.join(negative_features)}が低めの選手が上位です。"
    return "指定変数のクラスタ像に近い選手が上位です。"


def describe_example_components(
    row: pd.Series,
    spec: ScoreSpec,
    feature_labels: dict[str, str],
) -> str:
    if spec.method == "distance":
        return f"distance={format_number(row[spec.distance_column])}"

    values: list[str] = []
    for column in spec.components:
        feature_label = feature_labels.get(column, column)
        values.append(f"{feature_label}={format_number(row[column])}")
    return ", ".join(values)


def compute_sum_score(
    numeric_players_df: pd.DataFrame,
    spec: ScoreSpec,
) -> pd.Series:
    score_array = np.zeros(len(numeric_players_df), dtype=float)
    for column, weight in zip(spec.components, spec.weights):
        score_array += numeric_players_df[column].to_numpy() * weight
    return pd.Series(score_array, index=numeric_players_df.index, dtype="float64")


def compute_distance_score(
    numeric_players_df: pd.DataFrame,
    center_vector: np.ndarray,
) -> tuple[pd.Series, pd.Series]:
    player_matrix = numeric_players_df.to_numpy(dtype=float)
    distances = np.linalg.norm(player_matrix - center_vector, axis=1)
    distance_series = pd.Series(distances, index=numeric_players_df.index, dtype="float64")
    score_series = -distance_series
    return distance_series, score_series


def build_top10_rows(
    scored_df: pd.DataFrame,
    spec: ScoreSpec,
    config: RecommendationPositionConfig,
) -> pd.DataFrame:
    sorted_df = (
        scored_df.sort_values(
            by=[spec.score_column, "FB_Name", "SC_Name"],
            ascending=[False, True, True],
            kind="mergesort",
        )
        .head(10)
        .copy()
    )
    sorted_df["cluster_id"] = spec.cluster_id
    sorted_df["cluster_label"] = spec.cluster_label
    sorted_df["rank"] = np.arange(1, len(sorted_df) + 1)
    sorted_df["original_cluster_id"] = scored_df.loc[sorted_df.index, "cluster_id"].astype(int).to_numpy()
    sorted_df["original_cluster_label"] = sorted_df["original_cluster_id"].map(config.cluster_labels)
    sorted_df["score"] = sorted_df[spec.score_column]
    sorted_df["score_formula"] = spec.formula_text
    sorted_df["distance_to_cluster_center"] = (
        sorted_df[spec.distance_column] if spec.method == "distance" else np.nan
    )

    base_columns = [
        "cluster_id",
        "cluster_label",
        "rank",
        "FB_Name",
        "SC_Name",
        "analysis_position_code",
        "original_cluster_id",
        "original_cluster_label",
        "score",
        "distance_to_cluster_center",
        "score_formula",
    ]
    optional_columns = [column for column in ["analysis_position_jp"] if column in sorted_df.columns]
    ordered_columns = base_columns + optional_columns + config.z_columns
    return sorted_df[ordered_columns]


def collect_notable_examples(
    scored_df: pd.DataFrame,
    specs: list[ScoreSpec],
    config: RecommendationPositionConfig,
) -> list[str]:
    candidates: list[tuple[int, float, str]] = []

    for spec in specs:
        mismatch_df = (
            scored_df[scored_df["cluster_id"] != spec.cluster_id]
            .sort_values(
                by=[spec.rank_column, spec.score_column, "FB_Name", "SC_Name"],
                ascending=[True, False, True, True],
                kind="mergesort",
            )
        )
        if mismatch_df.empty:
            continue

        row = mismatch_df.iloc[0]
        original_cluster_id = int(row["cluster_id"])
        component_text = describe_example_components(row=row, spec=spec, feature_labels=config.feature_labels)
        description = (
            f"- `{row['FB_Name']}` (`{row['SC_Name']}`) は元 `Cluster {original_cluster_id}: "
            f"{config.cluster_labels[original_cluster_id]}` ですが、"
            f" `Cluster {spec.cluster_id}: {spec.cluster_label}` スコアで "
            f"{int(row[spec.rank_column])} 位です "
            f"(`score={format_number(row[spec.score_column])}`, {component_text})。"
        )
        candidates.append((int(row[spec.rank_column]), -float(row[spec.score_column]), description))

    candidates.sort(key=lambda item: (item[0], item[1]))

    selected: list[str] = []
    seen_players: set[tuple[str, str]] = set()
    for _, _, description in candidates:
        split_tokens = description.split("`")
        if len(split_tokens) < 4:
            continue
        player_key = (split_tokens[1], split_tokens[3])
        if player_key in seen_players:
            continue
        selected.append(description)
        seen_players.add(player_key)
        if len(selected) == 2:
            break

    return selected


def render_report(
    config: RecommendationPositionConfig,
    specs: list[ScoreSpec],
    scored_df: pd.DataFrame,
    top10_df: pd.DataFrame,
) -> str:
    lines: list[str] = [
        f"# {config.position_code} Recommendation Report",
        "",
        "## 入力ファイル",
        f"- `{config.clustered_players_path}`",
        f"- `{config.cluster_centers_path}`",
        f"- `{config.rf_report_path}`",
        "",
        "## 採用したクラスタラベル",
        "- 今回のラベルは分析用の作業ラベルです。",
    ]

    for cluster_id, label in sorted(config.cluster_labels.items()):
        lines.append(f"- Cluster {cluster_id}: {label}")

    lines.extend(
        [
            "",
            "## スコア設計方針",
            "- 10変数全部の単純合算は使わず、専門型クラスタは KMeans 中心と RandomForest 解釈の両方で効いていた 2〜3 変数だけを使いました。",
            "- 平均型クラスタだけは単純加算にせず、KMeans で使った全 z 列ベクトルのクラスタ中心とのユークリッド距離で評価しました。",
            "- スコアはクラスタ像への近さを見るもので、選手の総合力順位ではありません。",
            "",
            "## 各クラスタのスコア式と変数選定理由",
        ]
    )

    for spec in specs:
        lines.append(f"### Cluster {spec.cluster_id}: {spec.cluster_label}")
        lines.append(f"- スコア式: `{spec.formula_text}`")
        lines.append(f"- 使用変数: {component_summary(spec=spec, feature_labels=config.feature_labels)}")
        lines.append(f"- 変数選定理由: {spec.rationale}")
        if spec.method == "distance":
            lines.append(f"- 距離列: `{spec.distance_column}`")
        lines.append("")

    lines.extend(
        [
            "## 平均型だけ距離ベースにした理由",
            "- 平均型は特定の少数変数が突出するクラスタではなく、全体ベクトルでクラスタ中心に近いかどうかを見た方が KMeans の定義に忠実です。",
            "- 2〜3 変数の単純加算にすると specialized cluster 側の特徴量だけを拾ってしまい、平均型を平均型として評価しにくくなります。",
            "",
            "## 各クラスタ Top10 の概要",
        ]
    )

    for spec in specs:
        cluster_top10 = top10_df[top10_df["cluster_id"] == spec.cluster_id].copy()
        same_cluster_count = int((cluster_top10["original_cluster_id"] == spec.cluster_id).sum())
        top_count = len(cluster_top10)
        ratio = 0.0 if top_count == 0 else same_cluster_count / top_count * 100
        top3_names = " / ".join(cluster_top10["FB_Name"].head(3).tolist()) if top_count else "該当なし"

        lines.append(f"### Cluster {spec.cluster_id}: {spec.cluster_label}")
        lines.append(f"- Top3: {top3_names}")
        lines.append(f"- Top10 内の元同クラスタ所属: {same_cluster_count}/{top_count} ({ratio:.1f}%)")
        lines.append(f"- 概要: {cluster_overview_sentence(spec=spec, feature_labels=config.feature_labels)}")
        if spec.method == "distance" and top_count > 0:
            lines.append(
                f"- 距離の目安: 1位の `{spec.distance_column}` = "
                f"{format_number(cluster_top10['distance_to_cluster_center'].iloc[0])}"
            )
        lines.append("")

    mismatch_examples = collect_notable_examples(scored_df=scored_df, specs=specs, config=config)
    lines.append("## 「クラスタ所属」と「クラスタ像へのスコア順位」がズレた代表例")
    if mismatch_examples:
        lines.extend(mismatch_examples)
    else:
        lines.append("- 目立つズレ事例は抽出されませんでした。")

    lines.extend(
        [
            "",
            "## スコア式の注意点",
            "- これは総合力ランキングではありません。",
            "- あくまで特定のクラスタ像への近さを見るためのスコアです。",
            "- specialized cluster の式は、そのクラスタ像を表す少数変数だけを強く見ています。",
            "- 平均型は距離ベースなので、`score = -distance` です。0 に近いほど中心に近く、より平均型らしいと解釈します。",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def run_position_recommendation_scoring(config: RecommendationPositionConfig) -> None:
    specs = validate_config(config)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    log(config.position_code, "入力ファイルを読み込みます。")
    players_df = read_csv_required(config.clustered_players_path)
    centers_df = read_csv_required(config.cluster_centers_path)
    _ = read_text_required(config.rf_report_path)

    validate_columns(
        df=players_df,
        required_columns=REQUIRED_PLAYER_COLUMNS + config.z_columns,
        path=config.clustered_players_path,
    )
    validate_columns(
        df=centers_df,
        required_columns=["cluster_id"] + config.z_columns,
        path=config.cluster_centers_path,
    )

    players_df = players_df.copy()
    players_df["cluster_id"] = normalize_cluster_id_series(players_df["cluster_id"], config.clustered_players_path.name)
    centers_df = centers_df.copy()
    centers_df["cluster_id"] = normalize_cluster_id_series(centers_df["cluster_id"], config.cluster_centers_path.name)

    numeric_players_df = numeric_frame_required(players_df, config.z_columns, config.clustered_players_path.name)
    numeric_centers_df = numeric_frame_required(centers_df, config.z_columns, config.cluster_centers_path.name)
    centers_by_cluster = numeric_centers_df.copy()
    centers_by_cluster.index = centers_df["cluster_id"]

    missing_cluster_ids = [spec.cluster_id for spec in specs if spec.cluster_id not in centers_by_cluster.index]
    if missing_cluster_ids:
        raise ValueError(f"{config.cluster_centers_path.name} に cluster 中心がありません: {missing_cluster_ids}")

    log(config.position_code, "クラスタ別スコアと順位を計算します。")
    for spec in specs:
        if spec.method == "sum":
            missing_components = [column for column in spec.components if column not in numeric_players_df.columns]
            if missing_components:
                raise ValueError(f"cluster {spec.cluster_id} の score components が見つかりません: {missing_components}")
            players_df[spec.score_column] = compute_sum_score(numeric_players_df=numeric_players_df, spec=spec)
        else:
            center_vector = centers_by_cluster.loc[spec.cluster_id, config.z_columns].to_numpy(dtype=float)
            distance_series, score_series = compute_distance_score(
                numeric_players_df=numeric_players_df[config.z_columns],
                center_vector=center_vector,
            )
            players_df[spec.distance_column] = distance_series
            players_df[spec.score_column] = score_series

        players_df[spec.rank_column] = build_ordinal_rank(players_df, spec.score_column).astype(int)
        log(config.position_code, f"Cluster {spec.cluster_id}: `{spec.score_column}` / `{spec.rank_column}` を作成しました。")

    distance_columns = [spec.distance_column for spec in specs if spec.method == "distance"]
    score_columns = [spec.score_column for spec in specs]
    rank_columns = [spec.rank_column for spec in specs]

    optional_input_columns = [
        column
        for column in ["analysis_position_jp", "cluster_distance_to_center"]
        if column in players_df.columns
    ]
    score_output_columns = REQUIRED_PLAYER_COLUMNS + optional_input_columns + config.z_columns + distance_columns + score_columns + rank_columns
    recommendation_scores_df = players_df[score_output_columns].copy()

    log(config.position_code, f"推薦スコア CSV を出力します: {config.recommendation_scores_path}")
    recommendation_scores_df.to_csv(config.recommendation_scores_path, index=False, encoding="utf-8-sig")

    top10_frames = [build_top10_rows(scored_df=players_df, spec=spec, config=config) for spec in specs]
    top10_df = pd.concat(top10_frames, ignore_index=True)
    log(config.position_code, f"クラスタ別 Top10 CSV を出力します: {config.recommendation_top10_path}")
    top10_df.to_csv(config.recommendation_top10_path, index=False, encoding="utf-8-sig")

    report_text = render_report(
        config=config,
        specs=specs,
        scored_df=players_df,
        top10_df=top10_df,
    )
    log(config.position_code, f"Markdown レポートを出力します: {config.recommendation_report_path}")
    config.recommendation_report_path.write_text(report_text, encoding="utf-8")

    if len(recommendation_scores_df) != len(players_df):
        raise ValueError("出力行数が入力行数と一致しません。")

    log(config.position_code, f"完了: {len(players_df)} 件の選手に対して {len(specs)} クラスタ分のスコアを計算しました。")
