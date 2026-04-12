"""
ST 向け 3 類型の直接スコアリング実行スクリプト。
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    missing_name = exc.name or "必要な依存関係"
    raise SystemExit(
        f"{missing_name} が見つかりません。`../env/bin/python` で実行するか、"
        "pandas / numpy を導入してください。"
    ) from exc

CURRENT_DIR = Path(__file__).resolve().parent
J3_PYTHON_DIR = CURRENT_DIR.parent
ALL_J3_DIR = J3_PYTHON_DIR.parent

if str(J3_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(J3_PYTHON_DIR))

from position_definitions import ST_ARCHETYPE_LABELS, ST_FEATURE_LABELS, ST_Z_COLUMNS

INPUT_CSV_PATH = ALL_J3_DIR / "J3_csv" / "SC_position_clustering" / "ST" / "ST_features_preprocessed.csv"
OUTPUT_DIR = CURRENT_DIR / "output"
SCORES_PATH = OUTPUT_DIR / "ST_archetype_scores.csv"
TOP10_PATH = OUTPUT_DIR / "ST_top10_by_archetype.csv"
REPORT_PATH = OUTPUT_DIR / "ST_archetype_report.md"

STRICT_THRESHOLD = 0.25
RELAXED_THRESHOLD = 0.40
TOP_N = 10

SCORE_SPECS = {
    "ラインレシーバー": {
        "score_column": "score_line_receiver",
        "formula": "score_line_receiver = z_last_passes_per90 + z_successful_through_passes_per90",
        "components": ["z_last_passes_per90", "z_successful_through_passes_per90"],
    },
    "シャドーストライカー": {
        "score_column": "score_shadow_striker",
        "formula": (
            "score_shadow_striker = "
            "z_box_shots_per90 + z_goals_per90 + z_shot_conversion_rate_pct"
        ),
        "components": [
            "z_box_shots_per90",
            "z_goals_per90",
            "z_shot_conversion_rate_pct",
        ],
    },
    "ハイプレス・イニシエーター": {
        "score_column": "score_high_press_initiator",
        "formula": (
            "score_high_press_initiator = "
            "z_attacking_third_gains_per90 + z_sprint_count_full_all_per_match"
        ),
        "components": [
            "z_attacking_third_gains_per90",
            "z_sprint_count_full_all_per_match",
        ],
    },
}


def related_columns(z_column: str) -> tuple[str, str, str]:
    suffix = z_column[2:] if z_column.startswith("z_") else z_column
    return f"raw_{suffix}", f"win_{suffix}", f"imputed_{suffix}"


def format_number(value: float) -> str:
    return f"{float(value):.3f}"


def build_rank(series: pd.Series, players_df: pd.DataFrame) -> pd.Series:
    working = players_df[["FB_Name", "SC_Name"]].copy()
    working["score"] = series
    working["_index"] = players_df.index
    sorted_index = (
        working.sort_values(
            by=["score", "FB_Name", "SC_Name", "_index"],
            ascending=[False, True, True, True],
            kind="mergesort",
        )["_index"]
        .tolist()
    )
    rank_series = pd.Series(index=players_df.index, dtype="int64")
    rank_series.loc[sorted_index] = np.arange(1, len(sorted_index) + 1)
    return rank_series


def main() -> None:
    if not INPUT_CSV_PATH.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {INPUT_CSV_PATH}")

    df = pd.read_csv(INPUT_CSV_PATH, encoding="utf-8-sig")
    if df.empty:
        raise ValueError(f"入力ファイルにデータがありません: {INPUT_CSV_PATH}")

    required_base_columns = ["FB_Name", "SC_Name", "analysis_position_code", "analysis_position_jp"]
    missing_columns = [column for column in required_base_columns + ST_Z_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"必要列がありません: {missing_columns}")

    bundles = {z_column: related_columns(z_column) for z_column in ST_Z_COLUMNS}
    for z_column, (raw_column, win_column, imputed_column) in bundles.items():
        for column in (raw_column, win_column, imputed_column):
            if column not in df.columns:
                raise ValueError(f"{z_column} に対応する列がありません: {column}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    working_df = df.copy()

    source_imputed_counts: dict[str, int] = {}
    supplemental_imputed_counts: dict[str, int] = {}
    for z_column, (_, _, imputed_column) in bundles.items():
        numeric_z = pd.to_numeric(working_df[z_column], errors="coerce")
        median_value = float(numeric_z.dropna().median())
        if np.isnan(median_value):
            raise ValueError(f"{z_column} は全件欠損のため中央値補完できません。")
        source_imputed = working_df[imputed_column].astype(str).str.lower().isin(["1", "1.0", "true", "yes"])
        supplemental_imputed = numeric_z.isna()
        source_imputed_counts[z_column] = int(source_imputed.sum())
        supplemental_imputed_counts[z_column] = int(supplemental_imputed.sum())
        working_df[z_column] = numeric_z.fillna(median_value)
        working_df[imputed_column] = (source_imputed | supplemental_imputed).astype(int)

    imputed_columns = [bundles[z_column][2] for z_column in ST_Z_COLUMNS]
    working_df["imputed_count"] = working_df[imputed_columns].sum(axis=1).astype(int)
    working_df["imputed_ratio"] = working_df["imputed_count"] / len(ST_Z_COLUMNS)

    working_df["score_line_receiver"] = (
        working_df["z_last_passes_per90"] + working_df["z_successful_through_passes_per90"]
    )
    working_df["score_shadow_striker"] = (
        working_df["z_box_shots_per90"] + working_df["z_goals_per90"] + working_df["z_shot_conversion_rate_pct"]
    )
    working_df["score_high_press_initiator"] = (
        working_df["z_attacking_third_gains_per90"] + working_df["z_sprint_count_full_all_per_match"]
    )

    for archetype_name in ST_ARCHETYPE_LABELS:
        score_column = SCORE_SPECS[archetype_name]["score_column"]
        rank_column = f"rank_{score_column}"
        working_df[rank_column] = build_rank(working_df[score_column], working_df).astype(int)

    base_output_columns = required_base_columns.copy()
    for z_column in ST_Z_COLUMNS:
        raw_column, win_column, imputed_column = bundles[z_column]
        base_output_columns.extend([raw_column, win_column, z_column, imputed_column])
    base_output_columns.extend(
        [
            "imputed_count",
            "imputed_ratio",
            "score_line_receiver",
            "rank_score_line_receiver",
            "score_shadow_striker",
            "rank_score_shadow_striker",
            "score_high_press_initiator",
            "rank_score_high_press_initiator",
        ]
    )
    working_df[base_output_columns].to_csv(SCORES_PATH, index=False, encoding="utf-8-sig")

    top10_frames: list[pd.DataFrame] = []
    report_lines = [
        "# ST Archetype Report",
        "",
        "## 入力ファイル",
        f"- `{INPUT_CSV_PATH}`",
        "",
        "## 使用した z 列",
    ]
    for z_column in ST_Z_COLUMNS:
        report_lines.append(f"- `{z_column}` ({ST_FEATURE_LABELS.get(z_column, z_column)})")

    report_lines.extend(
        [
            "",
            "## 3類型のスコア式",
        ]
    )
    for archetype_name in ST_ARCHETYPE_LABELS:
        report_lines.append(f"- {archetype_name}: `{SCORE_SPECS[archetype_name]['formula']}`")

    report_lines.extend(
        [
            "",
            "## KMeans をやらなかった理由",
            "- ST はサンプル数が 11 名と少なく、KMeans / RandomForest のクラスタ安定性が低いため、今回は 3 類型の直接スコアリングだけにしました。",
            "",
            "## imputed_ratio フィルタ方針",
            f"- 公式 Top{TOP_N} は原則 `imputed_ratio <= {STRICT_THRESHOLD:.2f}` を適用しました。",
            f"- {TOP_N} 人未満しか残らない類型のみ `imputed_ratio <= {RELAXED_THRESHOLD:.2f}` に緩和しました。",
            "- 全選手版 CSV はフィルタせず全員分を保持しています。",
            "",
            "## 補完メモ",
            "- 入力 `imputed_*` と残存 z 欠損の中央値補完を合算して `imputed_count` / `imputed_ratio` を計算しています。",
            "- 追加で中央値補完した列と件数:",
        ]
    )
    supplemented = [z for z in ST_Z_COLUMNS if supplemental_imputed_counts[z] > 0]
    if supplemented:
        for z_column in supplemented:
            report_lines.append(f"  - `{z_column}`: {supplemental_imputed_counts[z_column]} 件")
    else:
        report_lines.append("  - 追加補完は発生していません。")

    report_lines.extend(["", "## 類型別公式 Top10"])

    for archetype_name in ST_ARCHETYPE_LABELS:
        score_column = SCORE_SPECS[archetype_name]["score_column"]
        rank_column = f"rank_{score_column}"
        sorted_df = (
            working_df.sort_values(
                by=[score_column, "FB_Name", "SC_Name"],
                ascending=[False, True, True],
                kind="mergesort",
            )
            .copy()
        )
        sorted_df["overall_rank_without_filter"] = np.arange(1, len(sorted_df) + 1)
        strict_df = sorted_df[sorted_df["imputed_ratio"] <= STRICT_THRESHOLD].copy()
        if len(strict_df) >= TOP_N:
            eligible_df = strict_df
            filter_mode = "strict"
            threshold_used = STRICT_THRESHOLD
        else:
            eligible_df = sorted_df[sorted_df["imputed_ratio"] <= RELAXED_THRESHOLD].copy()
            filter_mode = "relaxed"
            threshold_used = RELAXED_THRESHOLD

        top_df = eligible_df.head(TOP_N).copy()
        top_df["archetype"] = archetype_name
        top_df["rank"] = np.arange(1, len(top_df) + 1)
        top_df["score"] = top_df[score_column]
        top_df["score_formula"] = SCORE_SPECS[archetype_name]["formula"]
        top_df["top10_filter_mode"] = filter_mode
        top_df["top10_imputed_ratio_threshold_used"] = threshold_used
        top10_frames.append(
            top_df[
                [
                    "archetype",
                    "rank",
                    "overall_rank_without_filter",
                    "FB_Name",
                    "SC_Name",
                    "analysis_position_code",
                    "analysis_position_jp",
                    "score",
                    "score_formula",
                    "imputed_count",
                    "imputed_ratio",
                    "top10_filter_mode",
                    "top10_imputed_ratio_threshold_used",
                ]
                + ST_Z_COLUMNS
            ]
        )

        report_lines.append(f"### {archetype_name}")
        if filter_mode == "strict":
            report_lines.append(f"- imputed_ratio フィルタ: `<= {threshold_used:.2f}` を適用")
        else:
            report_lines.append(
                f"- imputed_ratio フィルタ: strict では {len(strict_df)} 人のため `<= {threshold_used:.2f}` に緩和"
            )
        if top_df.empty:
            report_lines.append("- 公式 Top10 の該当者はいません。")
        else:
            report_lines.append(f"- 公式 Top{TOP_N}:")
            for row in top_df.itertuples():
                report_lines.append(
                    f"  - {int(row.rank)}. `{row.FB_Name}` (`{row.SC_Name}`)"
                    f" / score={format_number(row.score)}"
                    f" / imputed_ratio={format_number(row.imputed_ratio)}"
                )

        excluded_candidates = sorted_df.head(TOP_N)
        excluded_candidates = excluded_candidates[excluded_candidates["imputed_ratio"] > threshold_used]
        if excluded_candidates.empty:
            report_lines.append("- フィルタで除外された有力候補: 目立つ候補はありません。")
        else:
            report_lines.append("- フィルタで除外された有力候補:")
            for row in excluded_candidates.head(3).itertuples():
                report_lines.append(
                    f"  - `{row.FB_Name}` (`{row.SC_Name}`): 無条件順位 {int(row.overall_rank_without_filter)} 位"
                    f" / score={format_number(getattr(row, score_column))}"
                    f" / imputed_ratio={format_number(row.imputed_ratio)}"
                )
        report_lines.append("")

    top10_df = pd.concat(top10_frames, ignore_index=True)
    top10_df.to_csv(TOP10_PATH, index=False, encoding="utf-8-sig")
    REPORT_PATH.write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ST][ERROR] {exc}", file=sys.stderr)
        raise
