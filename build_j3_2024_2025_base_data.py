from __future__ import annotations

import os
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd
from pykakasi import kakasi

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "csv"
BASE_DIR = Path(
    os.environ.get(
        "RAW_DATA_BASE_DIR",
        "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ",
    )
)
FB_DIR = BASE_DIR / "football box"
SC_DIR = BASE_DIR / "skill corner"
MASTER_FILE = CSV_DIR / "master_name_mapping_final.csv"
OUTPUT_FILE = CSV_DIR / "clustering_base_data_j3_2024_2025.csv"
VALID_MAPPING_FILE = CSV_DIR / "j3_2024_2025_valid_name_mapping.csv"
MAPPING_ISSUES_FILE = CSV_DIR / "j3_2024_2025_mapping_issues.csv"

TARGET_YEARS = ("2024", "2025")
TARGET_LEAGUE = "J3"
MIN_MINUTES_THRESHOLD = 300

AUTO_MATCH_SCORE_THRESHOLD = 82.0
AUTO_MATCH_GAP_THRESHOLD = 12.0
AUTO_MATCH_NAME_SCORE_THRESHOLD = 70.0
AUTO_MATCH_SOURCE = "auto_j3_outfield"
MANUAL_MATCH_SOURCE = "manual_master"
FIELD_POSITIONS = {"DF", "MF", "FW"}

FB_CATEGORIES = [
    "攻撃サマリー",
    "エリア別シュート",
    "エリア進入プレー",
    "セットプレー得点",
    "守備サマリー",
    "ゲインエリア",
    "ゲイン結果",
    "方向別パス",
    "基本サマリー",
]
FB_MERGE_KEYS = ["season", "チーム名", "選手名", "試合日"]

FB_SUM_VARS = [
    "シュート",
    "PA内シュート",
    "PA内ゴール",
    "PA外ゴール",
    "PA進入",
    "PA進入3プレー以内得点",
    "セットプレー5プレー以内得点",
    "ボールゲイン",
    "相手陣での回数",
    "ATでの回数",
    "ゲイン後至シュート",
    "ゲイン後至PA進入",
    "ゲイン後10秒未満でシュート",
    "パス",
    "後方向パス",
    "ラストパス",
    "30m進入",
    "ニアゾーン進入",
    "ドリブル",
]
FB_MEAN_VARS = [
    "PA内シュート枠内率(%)",
    "PA内シュート決定率(%)",
    "タックル奪取率(%)",
    "相手陣割合(%)",
    "平均ゲインライン(m)",
    "空中戦勝率(%)",
    "パス成功率(%)",
    "後方向パス成功率(%)",
]

SC_SUM_VARS_TIP = [
    "Sprint Count TIP",
    "Sprint Distance TIP",
    "Explosive Acceleration to Sprint Count TIP",
    "Explosive Acceleration to HSR Count TIP",
    "High Acceleration Count TIP",
    "Medium Acceleration Count TIP",
    "High Deceleration Count TIP",
    "Medium Deceleration Count TIP",
    "Change of Direction Count TIP",
    "HI Count TIP",
    "HSR Distance TIP",
    "HSR Count TIP",
    "Running Distance TIP",
    "Distance TIP",
    "HI Distance TIP",
]
SC_SUM_VARS_OTIP = [
    "Distance OTIP",
    "Running Distance OTIP",
    "HSR Distance OTIP",
    "HSR Count OTIP",
    "Sprint Distance OTIP",
    "Sprint Count OTIP",
    "High Acceleration Count OTIP",
    "HI Distance OTIP",
]
SC_SUM_VARS_ALL = [
    "High Acceleration Count",
    "Explosive Acceleration to HSR Count",
    "Explosive Acceleration to Sprint Count",
    "Change of Direction Count",
]

SC_COLUMN_ALIASES = {
    "Player": ["Player", "player_name"],
    "Team": ["Team", "team_name"],
    "Competition": ["Competition", "competition_name"],
    "Position Group": ["Position Group", "position_group"],
    "Position": ["Position", "position"],
    "Minutes": ["Minutes", "minutes_full_all"],
    "Minutes TIP": ["Minutes TIP", "minutes_full_tip"],
    "Minutes OTIP": ["Minutes OTIP", "minutes_full_otip"],
    "M/min": ["M/min", "total_metersperminute_full_all"],
    "M/min OTIP": ["M/min OTIP", "total_metersperminute_full_otip"],
    "PSV-99": ["PSV-99", "psv99"],
    "Sprint Count TIP": ["Sprint Count TIP", "sprint_count_full_tip"],
    "Sprint Distance TIP": ["Sprint Distance TIP", "sprint_distance_full_tip"],
    "Explosive Acceleration to Sprint Count TIP": [
        "Explosive Acceleration to Sprint Count TIP",
        "explacceltosprint_count_full_tip",
    ],
    "Explosive Acceleration to HSR Count TIP": [
        "Explosive Acceleration to HSR Count TIP",
        "explacceltohsr_count_full_tip",
    ],
    "High Acceleration Count TIP": [
        "High Acceleration Count TIP",
        "highaccel_count_full_tip",
    ],
    "Medium Acceleration Count TIP": [
        "Medium Acceleration Count TIP",
        "medaccel_count_full_tip",
    ],
    "High Deceleration Count TIP": [
        "High Deceleration Count TIP",
        "highdecel_count_full_tip",
    ],
    "Medium Deceleration Count TIP": [
        "Medium Deceleration Count TIP",
        "meddecel_count_full_tip",
    ],
    "Change of Direction Count TIP": [
        "Change of Direction Count TIP",
        "cod_count_full_tip",
    ],
    "HI Count TIP": ["HI Count TIP", "hi_count_full_tip"],
    "HSR Distance TIP": ["HSR Distance TIP", "hsr_distance_full_tip"],
    "HSR Count TIP": ["HSR Count TIP", "hsr_count_full_tip"],
    "Running Distance TIP": ["Running Distance TIP", "running_distance_full_tip"],
    "Distance TIP": ["Distance TIP", "total_distance_full_tip"],
    "HI Distance TIP": ["HI Distance TIP", "hi_distance_full_tip"],
    "Distance OTIP": ["Distance OTIP", "total_distance_full_otip"],
    "Running Distance OTIP": [
        "Running Distance OTIP",
        "running_distance_full_otip",
    ],
    "HSR Distance OTIP": ["HSR Distance OTIP", "hsr_distance_full_otip"],
    "HSR Count OTIP": ["HSR Count OTIP", "hsr_count_full_otip"],
    "Sprint Distance OTIP": ["Sprint Distance OTIP", "sprint_distance_full_otip"],
    "Sprint Count OTIP": ["Sprint Count OTIP", "sprint_count_full_otip"],
    "High Acceleration Count OTIP": [
        "High Acceleration Count OTIP",
        "highaccel_count_full_otip",
    ],
    "HI Distance OTIP": ["HI Distance OTIP", "hi_distance_full_otip"],
    "High Acceleration Count": [
        "High Acceleration Count",
        "highaccel_count_full_all",
    ],
    "Explosive Acceleration to HSR Count": [
        "Explosive Acceleration to HSR Count",
        "explacceltohsr_count_full_all",
    ],
    "Explosive Acceleration to Sprint Count": [
        "Explosive Acceleration to Sprint Count",
        "explacceltosprint_count_full_all",
    ],
    "Change of Direction Count": [
        "Change of Direction Count",
        "cod_count_full_all",
    ],
}

SC_NUMERIC_COLUMNS = [
    "Minutes",
    "Minutes TIP",
    "Minutes OTIP",
    "M/min OTIP",
    "M/min",
    "PSV-99",
    *SC_SUM_VARS_TIP,
    *SC_SUM_VARS_OTIP,
    *SC_SUM_VARS_ALL,
]

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

SC_TO_FB_POS_MAP = {
    "Center Forward": "FW",
    "Central Defender": "DF",
    "Full Back": "DF",
    "Goalkeeper": "GK",
    "Midfield": "MF",
    "Substitute": np.nan,
    "Wide Attacker": "FW",
}

VALID_MAPPING_COLUMNS = [
    "FB_Name",
    "SC_Name",
    "FB_Pos",
    "SC_Position_Group",
    "FB_Minutes",
    "SC_Minutes",
    "Mapping_Source",
    "Top_Score",
    "Gap_to_Second",
    "Name_Score",
    "Vector_Score",
    "Minutes_Score",
    "Candidate_Count",
    "Notes",
]

ISSUE_COLUMNS = [
    "Issue_Type",
    "FB_Name",
    "FB_Pos",
    "FB_Minutes",
    "SC_Name",
    "SC_Position_Group",
    "SC_Minutes",
    "Mapping_Source",
    "Top_Score",
    "Gap_to_Second",
    "Name_Score",
    "Vector_Score",
    "Minutes_Score",
    "Candidate_Count",
    "Notes",
]

KAKASI = kakasi()


def safe_mode(series: pd.Series) -> str | float:
    values = series.dropna()
    if values.empty:
        return np.nan
    modes = values.mode()
    if modes.empty:
        return values.iloc[0]
    return modes.iloc[0]


def normalize_spaces(value: str) -> str:
    return " ".join(str(value).replace("\u3000", " ").split())


def simple_ascii(value: str) -> str:
    normalized = normalize_spaces(value).lower()
    translation = str.maketrans(
        {
            "ā": "a",
            "á": "a",
            "à": "a",
            "â": "a",
            "ä": "a",
            "ã": "a",
            "å": "a",
            "æ": "ae",
            "ç": "c",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "í": "i",
            "ì": "i",
            "î": "i",
            "ï": "i",
            "ñ": "n",
            "ó": "o",
            "ò": "o",
            "ô": "o",
            "ö": "o",
            "õ": "o",
            "ø": "o",
            "ú": "u",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ý": "y",
            "ÿ": "y",
            "ū": "u",
            "ō": "o",
            "’": "",
            "'": "",
            "-": " ",
            "_": " ",
        }
    )
    translated = normalized.translate(translation)
    return "".join(
        character for character in translated if character.isalnum() or character == " "
    )


def squeeze_long_vowels(token: str) -> str:
    result: list[str] = []
    previous = ""
    for character in token:
        if character in "aeiou" and character == previous:
            continue
        result.append(character)
        previous = character
    return "".join(result)


def japanese_name_variants(name: str) -> set[str]:
    raw_name = "".join(normalize_spaces(name).split())
    converted = KAKASI.convert(raw_name)
    tokens = [simple_ascii(item["passport"]) for item in converted]
    tokens = [token for token in tokens if token]
    if not tokens:
        return {simple_ascii(name)}

    variants = {
        " ".join(tokens),
        " ".join(squeeze_long_vowels(token) for token in tokens),
    }
    if len(tokens) >= 2:
        family_name = tokens[0]
        given_name = " ".join(tokens[1:])
        variants.update(
            {
                f"{family_name} {given_name}".strip(),
                f"{given_name} {family_name}".strip(),
                f"{squeeze_long_vowels(family_name)} {squeeze_long_vowels(given_name)}".strip(),
                f"{squeeze_long_vowels(given_name)} {squeeze_long_vowels(family_name)}".strip(),
            }
        )
    return {variant.strip() for variant in variants if variant.strip()}


def english_name_variants(name: str) -> set[str]:
    tokens = simple_ascii(name).split()
    if not tokens:
        return {simple_ascii(name)}

    variants = {
        " ".join(tokens),
        " ".join(squeeze_long_vowels(token) for token in tokens),
    }
    if len(tokens) >= 2:
        family_name = tokens[-1]
        given_name = " ".join(tokens[:-1])
        variants.update(
            {
                f"{family_name} {given_name}".strip(),
                f"{given_name} {family_name}".strip(),
                f"{squeeze_long_vowels(family_name)} {squeeze_long_vowels(given_name)}".strip(),
                f"{squeeze_long_vowels(given_name)} {squeeze_long_vowels(family_name)}".strip(),
            }
        )
    return {variant.strip() for variant in variants if variant.strip()}


def best_name_similarity(fb_name: str, sc_name: str) -> float:
    best_score = 0.0
    for jp_variant in japanese_name_variants(fb_name):
        for en_variant in english_name_variants(sc_name):
            best_score = max(
                best_score,
                SequenceMatcher(None, jp_variant, en_variant).ratio(),
            )
    return best_score


def collect_fb_files() -> dict[str, list[Path]]:
    fb_dict = {category: [] for category in FB_CATEGORIES}
    for year in TARGET_YEARS:
        league_dir = FB_DIR / year / TARGET_LEAGUE
        for file_path in sorted(league_dir.glob("*.xlsx")):
            for category in FB_CATEGORIES:
                if category in file_path.name:
                    fb_dict[category].append(file_path)
                    break
    return fb_dict


def load_fb_match_data() -> pd.DataFrame:
    fb_dict = collect_fb_files()
    df_fb_merged: pd.DataFrame | None = None

    for category, files in fb_dict.items():
        if not files:
            continue

        frames = []
        for file_path in files:
            df_category = pd.read_excel(file_path, engine="openpyxl")
            df_category["season"] = file_path.parent.parent.name
            frames.append(df_category)

        df_category = pd.concat(frames, ignore_index=True)
        if df_fb_merged is None:
            df_fb_merged = df_category
            continue

        duplicate_columns = [
            column
            for column in df_category.columns
            if column in df_fb_merged.columns and column not in FB_MERGE_KEYS
        ]
        df_category = df_category.drop(columns=duplicate_columns)
        df_fb_merged = pd.merge(
            df_fb_merged,
            df_category,
            on=FB_MERGE_KEYS,
            how="outer",
        )

    if df_fb_merged is None:
        raise RuntimeError("FBのJ3ファイルを読み込めませんでした。")

    return df_fb_merged


def aggregate_fb(df_fb_match: pd.DataFrame) -> pd.DataFrame:
    df_fb_match = df_fb_match.copy()

    for column in ["出場時間", *FB_SUM_VARS, *FB_MEAN_VARS]:
        if column in df_fb_match.columns:
            df_fb_match[column] = (
                pd.to_numeric(df_fb_match[column], errors="coerce").fillna(0)
            )

    agg_dict: dict[str, str | callable] = {
        "出場時間": "sum",
        "Pos": safe_mode,
    }
    for column in FB_SUM_VARS:
        if column in df_fb_match.columns:
            agg_dict[column] = "sum"
    for column in FB_MEAN_VARS:
        if column in df_fb_match.columns:
            agg_dict[column] = "mean"

    df_fb_agg = df_fb_match.groupby("選手名", as_index=False).agg(agg_dict)
    df_fb_agg = df_fb_agg.rename(columns={"Pos": "ポジション"})

    for column in FB_SUM_VARS:
        if column in df_fb_agg.columns:
            df_fb_agg[f"{column}_per90"] = np.where(
                df_fb_agg["出場時間"] > 0,
                (df_fb_agg[column] / df_fb_agg["出場時間"]) * 90,
                0,
            )

    return df_fb_agg


def standardize_sc_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    standardized = pd.DataFrame(index=df.index)
    for canonical_name, aliases in SC_COLUMN_ALIASES.items():
        source_name = next((alias for alias in aliases if alias in df.columns), None)
        if source_name is None:
            standardized[canonical_name] = np.nan
        else:
            standardized[canonical_name] = df[source_name]
    return standardized


def load_sc_match_data() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for year in TARGET_YEARS:
        league_dir = SC_DIR / year / TARGET_LEAGUE
        for file_path in sorted(league_dir.glob("*.csv")):
            df_raw = pd.read_csv(file_path)
            df_standardized = standardize_sc_dataframe(df_raw)
            df_standardized["season"] = year
            frames.append(df_standardized)

    if not frames:
        raise RuntimeError("SCのJ3ファイルを読み込めませんでした。")

    return pd.concat(frames, ignore_index=True)


def aggregate_sc(df_sc_match: pd.DataFrame) -> pd.DataFrame:
    df_sc_match = df_sc_match.copy()

    for column in SC_NUMERIC_COLUMNS:
        if column in df_sc_match.columns:
            df_sc_match[column] = (
                pd.to_numeric(df_sc_match[column], errors="coerce").fillna(0)
            )

    agg_dict: dict[str, str] = {
        "Minutes": "sum",
        "Minutes TIP": "sum",
        "Minutes OTIP": "sum",
        "M/min OTIP": "mean",
        "M/min": "mean",
        "PSV-99": "max",
    }
    for column in [*SC_SUM_VARS_TIP, *SC_SUM_VARS_OTIP, *SC_SUM_VARS_ALL]:
        if column in df_sc_match.columns:
            agg_dict[column] = "sum"

    df_sc_agg = df_sc_match.groupby("Player", as_index=False).agg(agg_dict)

    for column in SC_SUM_VARS_TIP:
        if column in df_sc_agg.columns:
            df_sc_agg[f"{column}_per90"] = np.where(
                df_sc_agg["Minutes TIP"] > 0,
                (df_sc_agg[column] / df_sc_agg["Minutes TIP"]) * 90,
                0,
            )
    for column in SC_SUM_VARS_OTIP:
        if column in df_sc_agg.columns:
            df_sc_agg[f"{column}_per90"] = np.where(
                df_sc_agg["Minutes OTIP"] > 0,
                (df_sc_agg[column] / df_sc_agg["Minutes OTIP"]) * 90,
                0,
            )
    for column in SC_SUM_VARS_ALL:
        if column in df_sc_agg.columns:
            df_sc_agg[f"{column}_per90"] = np.where(
                df_sc_agg["Minutes"] > 0,
                (df_sc_agg[column] / df_sc_agg["Minutes"]) * 90,
                0,
            )

    return df_sc_agg


def build_fb_mapping_metadata(
    df_fb_match: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    metadata = df_fb_match[["選手名", "season", "チーム名", "Pos", "出場時間"]].copy()
    metadata["出場時間"] = pd.to_numeric(metadata["出場時間"], errors="coerce").fillna(0)

    df_fb_meta = metadata.groupby("選手名", as_index=False).agg(
        {
            "出場時間": "sum",
            "Pos": safe_mode,
        }
    )
    df_fb_meta = df_fb_meta.rename(
        columns={
            "選手名": "FB_Name",
            "出場時間": "FB_Minutes",
            "Pos": "FB_Pos",
        }
    )

    df_fb_team_year = metadata.groupby(
        ["選手名", "season", "チーム名"], as_index=False
    )["出場時間"].sum()
    vectors = {
        player_name: {
            f"{row['season']}|{row['チーム名']}": float(row["出場時間"])
            for _, row in group.iterrows()
        }
        for player_name, group in df_fb_team_year.groupby("選手名")
    }
    return df_fb_meta, vectors


def build_sc_mapping_metadata(
    df_sc_match: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    metadata = df_sc_match[
        ["Player", "season", "Team", "Position Group", "Minutes"]
    ].copy()
    metadata["Minutes"] = pd.to_numeric(metadata["Minutes"], errors="coerce").fillna(0)
    metadata["Team_JP"] = metadata["Team"].map(TEAM_NAME_MAP)
    metadata["FB_Pos_From_SC"] = metadata["Position Group"].map(SC_TO_FB_POS_MAP)

    df_sc_meta = metadata.groupby("Player", as_index=False).agg(
        {
            "Minutes": "sum",
            "Position Group": safe_mode,
            "FB_Pos_From_SC": safe_mode,
        }
    )
    df_sc_meta = df_sc_meta.rename(
        columns={
            "Player": "SC_Name",
            "Minutes": "SC_Minutes",
            "Position Group": "SC_Position_Group",
        }
    )

    df_sc_team_year = metadata.groupby(
        ["Player", "season", "Team_JP"], as_index=False
    )["Minutes"].sum()
    vectors = {
        player_name: {
            f"{row['season']}|{row['Team_JP']}": float(row["Minutes"])
            for _, row in group.iterrows()
            if pd.notna(row["Team_JP"])
        }
        for player_name, group in df_sc_team_year.groupby("Player")
    }
    return df_sc_meta, vectors


def vector_similarity(
    vector_a: dict[str, float],
    vector_b: dict[str, float],
) -> float:
    keys = sorted(set(vector_a) | set(vector_b))
    if not keys:
        return 0.0

    array_a = np.array([vector_a.get(key, 0.0) for key in keys], dtype=float)
    array_b = np.array([vector_b.get(key, 0.0) for key in keys], dtype=float)
    if not array_a.any() or not array_b.any():
        return 0.0

    cosine_similarity = float(
        np.dot(array_a, array_b)
        / (np.linalg.norm(array_a) * np.linalg.norm(array_b))
    )
    minutes_ratio = (
        min(array_a.sum(), array_b.sum()) / max(array_a.sum(), array_b.sum())
        if max(array_a.sum(), array_b.sum())
        else 0.0
    )
    return (0.75 * cosine_similarity) + (0.25 * minutes_ratio)


def build_issue_row(
    issue_type: str,
    *,
    fb_name: str,
    fb_pos: str | float,
    fb_minutes: float,
    sc_name: str | float = np.nan,
    sc_position_group: str | float = np.nan,
    sc_minutes: float | float = np.nan,
    mapping_source: str,
    top_score: float | float = np.nan,
    gap_to_second: float | float = np.nan,
    name_score: float | float = np.nan,
    vector_score: float | float = np.nan,
    minutes_score: float | float = np.nan,
    candidate_count: int | float = np.nan,
    notes: str = "",
) -> dict[str, object]:
    return {
        "Issue_Type": issue_type,
        "FB_Name": fb_name,
        "FB_Pos": fb_pos,
        "FB_Minutes": fb_minutes,
        "SC_Name": sc_name,
        "SC_Position_Group": sc_position_group,
        "SC_Minutes": sc_minutes,
        "Mapping_Source": mapping_source,
        "Top_Score": top_score,
        "Gap_to_Second": gap_to_second,
        "Name_Score": name_score,
        "Vector_Score": vector_score,
        "Minutes_Score": minutes_score,
        "Candidate_Count": candidate_count,
        "Notes": notes,
    }


def prepare_manual_mapping(
    df_fb_meta: pd.DataFrame,
    df_sc_meta: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_master = pd.read_csv(MASTER_FILE).dropna(subset=["FB_Name", "SC_Name"]).copy()
    df_manual = df_master.merge(df_fb_meta, on="FB_Name", how="inner").merge(
        df_sc_meta, on="SC_Name", how="inner"
    )

    duplicate_fb_names = set(
        df_manual.loc[df_manual.duplicated("FB_Name", keep=False), "FB_Name"]
    )
    duplicate_sc_names = set(
        df_manual.loc[df_manual.duplicated("SC_Name", keep=False), "SC_Name"]
    )

    issue_rows = []
    for row in df_manual.itertuples(index=False):
        reasons = []
        if row.FB_Name in duplicate_fb_names:
            reasons.append("duplicate_fb_name")
        if row.SC_Name in duplicate_sc_names:
            reasons.append("duplicate_sc_name")
        if reasons:
            issue_rows.append(
                build_issue_row(
                    ",".join(reasons),
                    fb_name=row.FB_Name,
                    fb_pos=row.FB_Pos,
                    fb_minutes=float(row.FB_Minutes),
                    sc_name=row.SC_Name,
                    sc_position_group=row.SC_Position_Group,
                    sc_minutes=float(row.SC_Minutes),
                    mapping_source=MANUAL_MATCH_SOURCE,
                    notes="master_name_mapping_final.csv で重複したため除外",
                )
            )

    df_issues = pd.DataFrame(issue_rows, columns=ISSUE_COLUMNS)
    if df_issues.empty:
        df_valid = df_manual.copy()
    else:
        invalid_fb_names = set(df_issues["FB_Name"])
        invalid_sc_names = set(df_issues["SC_Name"].dropna())
        df_valid = df_manual[
            ~df_manual["FB_Name"].isin(invalid_fb_names)
            & ~df_manual["SC_Name"].isin(invalid_sc_names)
        ].copy()

    df_valid["Mapping_Source"] = MANUAL_MATCH_SOURCE
    df_valid["Top_Score"] = np.nan
    df_valid["Gap_to_Second"] = np.nan
    df_valid["Name_Score"] = np.nan
    df_valid["Vector_Score"] = np.nan
    df_valid["Minutes_Score"] = np.nan
    df_valid["Candidate_Count"] = np.nan
    df_valid["Notes"] = "master_name_mapping_final.csv 採用"
    df_valid = df_valid[VALID_MAPPING_COLUMNS].sort_values(
        ["FB_Name", "SC_Name"]
    ).reset_index(drop=True)

    return (
        df_valid,
        df_issues.sort_values(["Issue_Type", "FB_Name", "SC_Name"]).reset_index(
            drop=True
        ),
    )


def build_auto_mapping_candidates(
    df_fb_meta: pd.DataFrame,
    df_sc_meta: pd.DataFrame,
    fb_vectors: dict[str, dict[str, float]],
    sc_vectors: dict[str, dict[str, float]],
    used_fb_names: set[str],
    used_sc_names: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    sc_candidates = df_sc_meta[~df_sc_meta["SC_Name"].isin(used_sc_names)].copy()
    issue_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []

    for fb_row in df_fb_meta.sort_values("FB_Minutes", ascending=False).itertuples(
        index=False
    ):
        fb_name = fb_row.FB_Name
        fb_pos = fb_row.FB_Pos
        fb_minutes = float(fb_row.FB_Minutes)

        if fb_name in used_fb_names or fb_minutes < MIN_MINUTES_THRESHOLD:
            continue

        if fb_pos == "GK":
            issue_rows.append(
                build_issue_row(
                    "sc_goalkeeper_not_available",
                    fb_name=fb_name,
                    fb_pos=fb_pos,
                    fb_minutes=fb_minutes,
                    mapping_source=AUTO_MATCH_SOURCE,
                    notes="SkillCorner J3 raw data に GK の Position Group が存在しないため対象外",
                )
            )
            continue

        if fb_pos not in FIELD_POSITIONS:
            issue_rows.append(
                build_issue_row(
                    "unsupported_fb_position",
                    fb_name=fb_name,
                    fb_pos=fb_pos,
                    fb_minutes=fb_minutes,
                    mapping_source=AUTO_MATCH_SOURCE,
                    notes="自動照合対象のポジション外",
                )
            )
            continue

        fb_team_keys = set(fb_vectors.get(fb_name, {}))
        local_candidates = []
        for sc_row in sc_candidates.itertuples(index=False):
            if sc_row.FB_Pos_From_SC != fb_pos:
                continue

            sc_team_keys = set(sc_vectors.get(sc_row.SC_Name, {}))
            if fb_team_keys and sc_team_keys.isdisjoint(fb_team_keys):
                continue

            vector_score = vector_similarity(
                fb_vectors.get(fb_name, {}),
                sc_vectors.get(sc_row.SC_Name, {}),
            )
            name_score = best_name_similarity(fb_name, sc_row.SC_Name)
            minutes_score = (
                min(fb_minutes, float(sc_row.SC_Minutes))
                / max(fb_minutes, float(sc_row.SC_Minutes))
                if max(fb_minutes, float(sc_row.SC_Minutes))
                else 0.0
            )
            total_score = 100 * (
                (0.52 * vector_score)
                + (0.30 * name_score)
                + (0.10 * minutes_score)
                + 0.08
            )
            local_candidates.append(
                {
                    "FB_Name": fb_name,
                    "FB_Pos": fb_pos,
                    "FB_Minutes": fb_minutes,
                    "SC_Name": sc_row.SC_Name,
                    "SC_Position_Group": sc_row.SC_Position_Group,
                    "SC_Minutes": float(sc_row.SC_Minutes),
                    "Top_Score": round(total_score, 2),
                    "Name_Score": round(name_score * 100, 2),
                    "Vector_Score": round(vector_score * 100, 2),
                    "Minutes_Score": round(minutes_score * 100, 2),
                }
            )

        if not local_candidates:
            issue_rows.append(
                build_issue_row(
                    "no_candidate_after_filter",
                    fb_name=fb_name,
                    fb_pos=fb_pos,
                    fb_minutes=fb_minutes,
                    mapping_source=AUTO_MATCH_SOURCE,
                    notes="同一ポジションかつ年度+チーム重なりありの候補が見つからない",
                )
            )
            continue

        local_candidates.sort(
            key=lambda row: (
                row["Top_Score"],
                row["Name_Score"],
                row["Vector_Score"],
                row["Minutes_Score"],
            ),
            reverse=True,
        )
        top_candidate = local_candidates[0]
        second_score = (
            local_candidates[1]["Top_Score"] if len(local_candidates) > 1 else 0.0
        )
        candidate_rows.append(
            {
                **top_candidate,
                "Gap_to_Second": round(top_candidate["Top_Score"] - second_score, 2),
                "Candidate_Count": len(local_candidates),
                "Mapping_Source": AUTO_MATCH_SOURCE,
            }
        )

    return (
        pd.DataFrame(candidate_rows),
        pd.DataFrame(issue_rows, columns=ISSUE_COLUMNS),
    )


def select_auto_mappings(
    df_candidates: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df_candidates.empty:
        return (
            pd.DataFrame(columns=VALID_MAPPING_COLUMNS),
            pd.DataFrame(columns=ISSUE_COLUMNS),
        )

    acceptance_mask = (
        (df_candidates["Top_Score"] >= AUTO_MATCH_SCORE_THRESHOLD)
        & (df_candidates["Gap_to_Second"] >= AUTO_MATCH_GAP_THRESHOLD)
        & (df_candidates["Name_Score"] >= AUTO_MATCH_NAME_SCORE_THRESHOLD)
    )

    df_accepted = df_candidates[acceptance_mask].copy().sort_values(
        ["Top_Score", "Gap_to_Second", "Name_Score", "Vector_Score"],
        ascending=False,
    )
    df_rejected = df_candidates[~acceptance_mask].copy()

    selected_rows = []
    issue_rows = []
    used_fb_names: set[str] = set()
    used_sc_names: set[str] = set()

    for row in df_accepted.itertuples(index=False):
        if row.FB_Name in used_fb_names or row.SC_Name in used_sc_names:
            issue_rows.append(
                build_issue_row(
                    "conflict_on_sc_name",
                    fb_name=row.FB_Name,
                    fb_pos=row.FB_Pos,
                    fb_minutes=float(row.FB_Minutes),
                    sc_name=row.SC_Name,
                    sc_position_group=row.SC_Position_Group,
                    sc_minutes=float(row.SC_Minutes),
                    mapping_source=AUTO_MATCH_SOURCE,
                    top_score=float(row.Top_Score),
                    gap_to_second=float(row.Gap_to_Second),
                    name_score=float(row.Name_Score),
                    vector_score=float(row.Vector_Score),
                    minutes_score=float(row.Minutes_Score),
                    candidate_count=int(row.Candidate_Count),
                    notes="より高スコアの自動マッピングと衝突したため除外",
                )
            )
            continue

        used_fb_names.add(row.FB_Name)
        used_sc_names.add(row.SC_Name)
        selected_rows.append(
            {
                "FB_Name": row.FB_Name,
                "SC_Name": row.SC_Name,
                "FB_Pos": row.FB_Pos,
                "SC_Position_Group": row.SC_Position_Group,
                "FB_Minutes": float(row.FB_Minutes),
                "SC_Minutes": float(row.SC_Minutes),
                "Mapping_Source": AUTO_MATCH_SOURCE,
                "Top_Score": float(row.Top_Score),
                "Gap_to_Second": float(row.Gap_to_Second),
                "Name_Score": float(row.Name_Score),
                "Vector_Score": float(row.Vector_Score),
                "Minutes_Score": float(row.Minutes_Score),
                "Candidate_Count": int(row.Candidate_Count),
                "Notes": (
                    f"score>={AUTO_MATCH_SCORE_THRESHOLD}, "
                    f"gap>={AUTO_MATCH_GAP_THRESHOLD}, "
                    f"name>={AUTO_MATCH_NAME_SCORE_THRESHOLD}"
                ),
            }
        )

    for row in df_rejected.itertuples(index=False):
        issue_rows.append(
            build_issue_row(
                "low_confidence_top_candidate",
                fb_name=row.FB_Name,
                fb_pos=row.FB_Pos,
                fb_minutes=float(row.FB_Minutes),
                sc_name=row.SC_Name,
                sc_position_group=row.SC_Position_Group,
                sc_minutes=float(row.SC_Minutes),
                mapping_source=AUTO_MATCH_SOURCE,
                top_score=float(row.Top_Score),
                gap_to_second=float(row.Gap_to_Second),
                name_score=float(row.Name_Score),
                vector_score=float(row.Vector_Score),
                minutes_score=float(row.Minutes_Score),
                candidate_count=int(row.Candidate_Count),
                notes=(
                    f"自動採用条件未達: score>={AUTO_MATCH_SCORE_THRESHOLD}, "
                    f"gap>={AUTO_MATCH_GAP_THRESHOLD}, "
                    f"name>={AUTO_MATCH_NAME_SCORE_THRESHOLD}"
                ),
            )
        )

    return (
        pd.DataFrame(selected_rows, columns=VALID_MAPPING_COLUMNS),
        pd.DataFrame(issue_rows, columns=ISSUE_COLUMNS),
    )


def prepare_expanded_mapping(
    df_fb_meta: pd.DataFrame,
    df_sc_meta: pd.DataFrame,
    fb_vectors: dict[str, dict[str, float]],
    sc_vectors: dict[str, dict[str, float]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_manual_valid, df_manual_issues = prepare_manual_mapping(df_fb_meta, df_sc_meta)
    used_fb_names = set(df_manual_valid["FB_Name"])
    used_sc_names = set(df_manual_valid["SC_Name"])

    df_auto_candidates, df_auto_prefilter_issues = build_auto_mapping_candidates(
        df_fb_meta=df_fb_meta,
        df_sc_meta=df_sc_meta,
        fb_vectors=fb_vectors,
        sc_vectors=sc_vectors,
        used_fb_names=used_fb_names,
        used_sc_names=used_sc_names,
    )
    df_auto_valid, df_auto_issues = select_auto_mappings(df_auto_candidates)

    df_valid = pd.concat(
        [df_manual_valid, df_auto_valid],
        ignore_index=True,
    )
    df_valid = df_valid.sort_values(
        ["Mapping_Source", "FB_Pos", "FB_Minutes", "FB_Name"],
        ascending=[True, True, False, True],
    ).reset_index(drop=True)

    df_issues = pd.concat(
        [df_manual_issues, df_auto_prefilter_issues, df_auto_issues],
        ignore_index=True,
    )
    if not df_issues.empty:
        df_issues = df_issues.sort_values(
            ["Issue_Type", "FB_Pos", "FB_Minutes", "FB_Name"],
            ascending=[True, True, False, True],
        ).reset_index(drop=True)
    else:
        df_issues = pd.DataFrame(columns=ISSUE_COLUMNS)

    return df_valid, df_issues


def main() -> None:
    print("--- J3 2024-2025 全ポジション前処理を開始します ---")

    df_fb_match = load_fb_match_data()
    print(f"FB試合データ: {len(df_fb_match)} 行")
    df_fb_agg = aggregate_fb(df_fb_match)
    print(f"FB選手集計: {len(df_fb_agg)} 名")

    df_sc_match = load_sc_match_data()
    print(f"SC試合データ: {len(df_sc_match)} 行")
    df_sc_agg = aggregate_sc(df_sc_match)
    print(f"SC選手集計: {len(df_sc_agg)} 名")

    df_fb_meta, fb_vectors = build_fb_mapping_metadata(df_fb_match)
    df_sc_meta, sc_vectors = build_sc_mapping_metadata(df_sc_match)

    df_valid_mapping, df_mapping_issues = prepare_expanded_mapping(
        df_fb_meta=df_fb_meta,
        df_sc_meta=df_sc_meta,
        fb_vectors=fb_vectors,
        sc_vectors=sc_vectors,
    )

    manual_count = int(
        (df_valid_mapping["Mapping_Source"] == MANUAL_MATCH_SOURCE).sum()
    )
    auto_count = int((df_valid_mapping["Mapping_Source"] == AUTO_MATCH_SOURCE).sum())
    print(f"採用マッピング: {len(df_valid_mapping)} 件")
    print(f"  manual: {manual_count} 件")
    print(f"  auto: {auto_count} 件")
    print(f"監査対象: {len(df_mapping_issues)} 件")

    df_final = pd.merge(
        df_valid_mapping,
        df_fb_agg,
        left_on="FB_Name",
        right_on="選手名",
        how="inner",
    )
    df_final = pd.merge(
        df_final,
        df_sc_agg,
        left_on="SC_Name",
        right_on="Player",
        how="inner",
    )

    duplicate_mask = df_final.duplicated("FB_Name", keep=False) | df_final.duplicated(
        "SC_Name", keep=False
    )
    if duplicate_mask.any():
        duplicates = df_final.loc[duplicate_mask, ["FB_Name", "SC_Name"]]
        raise RuntimeError(
            "最終出力に重複した名前が残っています。\n"
            f"{duplicates.to_string(index=False)}"
        )

    initial_count = len(df_final)
    df_final = df_final[df_final["出場時間"] >= MIN_MINUTES_THRESHOLD].copy()
    filtered_count = len(df_final)

    df_final.insert(0, "対象年度", "2024-2025")
    df_final.insert(1, "対象リーグ", TARGET_LEAGUE)
    df_final = df_final.sort_values(
        ["ポジション", "出場時間", "FB_Name"], ascending=[True, False, True]
    ).reset_index(drop=True)

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    df_valid_mapping.to_csv(VALID_MAPPING_FILE, index=False, encoding="utf-8-sig")
    df_mapping_issues.to_csv(MAPPING_ISSUES_FILE, index=False, encoding="utf-8-sig")

    print(f"ベースデータ出力: {OUTPUT_FILE}")
    print(f"採用マッピング出力: {VALID_MAPPING_FILE}")
    print(f"監査マッピング出力: {MAPPING_ISSUES_FILE}")
    print(f"結合成功件数: {initial_count}")
    print(
        f"出場時間 {MIN_MINUTES_THRESHOLD} 分以上で残った件数: {filtered_count}"
    )
    print(
        "最終ポジション分布: "
        f"{df_final['ポジション'].value_counts(dropna=False).to_dict()}"
    )


if __name__ == "__main__":
    main()
