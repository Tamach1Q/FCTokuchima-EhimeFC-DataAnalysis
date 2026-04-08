from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "csv"
ALT_CSV_DIR = PROJECT_ROOT / "J3_csv"
BASE_DIR = Path(
    os.environ.get(
        "RAW_DATA_BASE_DIR",
        "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ",
    )
)
FB_DIR = BASE_DIR / "football box"
SC_DIR = BASE_DIR / "skill corner"

TARGET_YEARS = ("2024", "2025")
TARGET_LEAGUE = "J3"
MAX_GAMEWEEK = 38
TARGET_ISSUE_TYPE = "low_confidence_top_candidate"

DEFAULT_ISSUE_FILE = CSV_DIR / "j3_2024_2025_mapping_issues.csv"
FALLBACK_ISSUE_FILE = ALT_CSV_DIR / "j3_2024_2025_mapping_issues.csv"
ISSUE_FILE = Path(
    os.environ.get(
        "MATCH_VECTOR_ISSUE_FILE",
        str(DEFAULT_ISSUE_FILE if DEFAULT_ISSUE_FILE.exists() else FALLBACK_ISSUE_FILE),
    )
)
OUTPUT_FILE = Path(
    os.environ.get(
        "MATCH_VECTOR_OUTPUT_FILE",
        str(CSV_DIR / "j3_2024_2025_match_vector_check.csv"),
    )
)

TEAM_NAME_MAP = {
    "AC Nagano Parceiro": "長野",
    "AC Parceiro Nagano": "長野",
    "Azul Claro Numazu": "沼津",
    "FC Azul Claro Numazu": "沼津",
    "FC Gifu": "岐阜",
    "FC Imabari": "今治",
    "FC Osaka": "FC大阪",
    "FC Ryūkyū": "琉球",
    "FC Ryūkyū": "琉球",
    "Fukushima United FC": "福島",
    "Gainare Tottori": "鳥取",
    "Giravanz Kitakyushu": "北九州",
    "Grulla Morioka": "岩手",
    "Ishikawa FC Zweigen Kanazawa": "金沢",
    "Kagoshima United FC": "鹿児島",
    "Kamatamare Sanuki": "讃岐",
    "Kataller Toyama": "富山",
    "Kochi United SC": "高知",
    "MIO Biwako Shiga": "滋賀",
    "Matsumoto Yamaga FC": "松本",
    "Nara Club": "奈良",
    "Omiya Ardija": "大宮",
    "RB Omiya Ardija": "大宮",
    "SC Sagamihara": "相模原",
    "Tegevajaro Miyazaki": "宮崎",
    "Tegevajaro Miyazaki FC": "宮崎",
    "Thespa Gunma": "群馬",
    "ThespaKusatsu Gunma": "群馬",
    "Tochigi City": "栃木Ｃ",
    "Tochigi SC": "栃木SC",
    "Vanraure Hachinohe": "八戸",
    "Yokohama Sports and Culture Club": "YS横浜",
    "Zweigen Kanazawa": "金沢",
}

SC_COLUMN_ALIASES = {
    "Player": ["player_name", "Player"],
    "Team": ["team_name", "Team"],
    "Match Date": ["match_date", "Match Date"],
    "Minutes": ["minutes_full_all", "Minutes"],
}


def resolve_fb_source(year: str) -> Path:
    league_dir = FB_DIR / year / TARGET_LEAGUE
    candidates = sorted(
        [
            path
            for path in league_dir.iterdir()
            if "エリア別シュート" in path.name and "試合別" in path.name
        ],
        key=lambda path: (path.suffix.lower() != ".csv", path.name),
    )
    if not candidates:
        raise FileNotFoundError(
            f"FB のエリア別シュート試合別ファイルが見つかりません: {league_dir}"
        )
    return candidates[0]


def read_fb_game_file(file_path: Path) -> pd.DataFrame:
    use_columns = ["選手名", "チーム名", "試合日", "節"]
    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path, usecols=use_columns)
    return pd.read_excel(file_path, engine="openpyxl", usecols=use_columns)


def normalize_round(value: object) -> float:
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"(\d+)", str(value))
    if match:
        return float(match.group(1))
    return np.nan


def load_fb_game_logs() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for year in TARGET_YEARS:
        file_path = resolve_fb_source(year)
        df = read_fb_game_file(file_path)
        df["season"] = year
        frames.append(df)

    df_fb = pd.concat(frames, ignore_index=True)
    df_fb["節"] = df_fb["節"].map(normalize_round)
    df_fb = df_fb.dropna(subset=["選手名", "チーム名", "節"]).copy()
    df_fb["節"] = df_fb["節"].astype(int)
    df_fb = df_fb[df_fb["節"].between(1, MAX_GAMEWEEK)].copy()

    # FB 側は行の存在自体を 1 とみなす
    df_fb = df_fb[["season", "選手名", "チーム名", "節"]].drop_duplicates()
    return df_fb


def standardize_sc_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    standardized = pd.DataFrame(index=df.index)
    for canonical_name, aliases in SC_COLUMN_ALIASES.items():
        source_name = next((alias for alias in aliases if alias in df.columns), None)
        standardized[canonical_name] = df[source_name] if source_name else np.nan
    return standardized


def load_sc_game_logs() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for year in TARGET_YEARS:
        league_dir = SC_DIR / year / TARGET_LEAGUE
        for file_path in sorted(league_dir.glob("*.csv")):
            df_raw = pd.read_csv(file_path)
            df = standardize_sc_dataframe(df_raw)
            df["season"] = year
            frames.append(df)

    if not frames:
        raise FileNotFoundError("SC の physical_data.csv 群を読み込めませんでした。")

    df_sc = pd.concat(frames, ignore_index=True)
    df_sc["Team_JP"] = df_sc["Team"].map(TEAM_NAME_MAP)
    df_sc["Match Date"] = pd.to_datetime(df_sc["Match Date"], errors="coerce")
    df_sc["Minutes"] = pd.to_numeric(df_sc["Minutes"], errors="coerce").fillna(0)
    df_sc = df_sc.dropna(subset=["Player", "Team_JP", "Match Date"]).copy()

    df_schedule = (
        df_sc[["season", "Team_JP", "Match Date"]]
        .drop_duplicates()
        .sort_values(["season", "Team_JP", "Match Date"])
    )
    df_schedule["Pseudo_Gameweek"] = (
        df_schedule.groupby(["season", "Team_JP"]).cumcount() + 1
    )
    df_schedule = df_schedule[df_schedule["Pseudo_Gameweek"] <= MAX_GAMEWEEK].copy()

    df_sc = df_sc.merge(
        df_schedule,
        on=["season", "Team_JP", "Match Date"],
        how="inner",
    )
    return df_sc


def build_fb_vectors(df_fb: pd.DataFrame) -> dict[str, set[str]]:
    return {
        player_name: {
            f"{row.season}|{row.チーム名}|{int(row.節):02d}"
            for row in group.itertuples(index=False)
        }
        for player_name, group in df_fb.groupby("選手名")
    }


def build_sc_vectors(df_sc: pd.DataFrame) -> dict[str, set[str]]:
    df_played = df_sc[df_sc["Minutes"] > 0].copy()
    return {
        player_name: {
            f"{row.season}|{row.Team_JP}|{int(row.Pseudo_Gameweek):02d}"
            for row in group.itertuples(index=False)
        }
        for player_name, group in df_played.groupby("Player")
    }


def cosine_score_from_keys(
    fb_keys: set[str],
    sc_keys: set[str],
) -> float:
    if not fb_keys or not sc_keys:
        return 0.0

    all_keys = sorted(fb_keys | sc_keys)
    fb_vector = np.array([1 if key in fb_keys else 0 for key in all_keys]).reshape(1, -1)
    sc_vector = np.array([1 if key in sc_keys else 0 for key in all_keys]).reshape(1, -1)

    score = float(cosine_similarity(fb_vector, sc_vector)[0, 0]) * 100
    return round(score, 2)


def load_target_pairs() -> pd.DataFrame:
    if not ISSUE_FILE.exists():
        raise FileNotFoundError(f"issue ファイルが見つかりません: {ISSUE_FILE}")

    df_issues = pd.read_csv(ISSUE_FILE)
    if "Issue_Type" not in df_issues.columns:
        raise ValueError(f"Issue_Type 列がありません: {ISSUE_FILE}")

    return df_issues[df_issues["Issue_Type"] == TARGET_ISSUE_TYPE].copy()


def main() -> None:
    print("--- 試合別出場ベクトル検証を開始します ---")
    print(f"issues: {ISSUE_FILE}")

    df_pairs = load_target_pairs()
    print(f"検証対象ペア: {len(df_pairs)} 件")

    df_fb = load_fb_game_logs()
    df_sc = load_sc_game_logs()
    print(f"FB 試合別行数: {len(df_fb)}")
    print(f"SC 試合別行数: {len(df_sc)}")

    fb_vectors = build_fb_vectors(df_fb)
    sc_vectors = build_sc_vectors(df_sc)

    match_scores = []
    for row in df_pairs.itertuples(index=False):
        fb_keys = fb_vectors.get(row.FB_Name, set())
        sc_keys = sc_vectors.get(row.SC_Name, set())
        match_scores.append(cosine_score_from_keys(fb_keys, sc_keys))

    df_pairs["Match_Vector_Score"] = match_scores
    df_pairs = df_pairs.sort_values(
        ["Match_Vector_Score", "Vector_Score", "Top_Score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_pairs.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"出力: {OUTPUT_FILE}")
    print(
        "Match_Vector_Score 上位5件: "
        f"{df_pairs[['FB_Name', 'SC_Name', 'Match_Vector_Score']].head(5).to_dict(orient='records')}"
    )


if __name__ == "__main__":
    main()
