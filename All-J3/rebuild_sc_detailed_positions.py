"""
SkillCorner 細分類ポジション復元スクリプト
=========================================

目的:
  raw SkillCorner 試合別CSV から position (細分類) を再抽出し、
  選手単位で Primary/Secondary ポジションを集計する。

主な追加仕様:
  - canonical name を生成し、"Haru Kano Haru Kano" のような
    ASCII 完全反復名を "Haru Kano" に正規化する
  - raw 原文名は player_name_raw_skillcorner として保持する
  - team_season_signature / team_season_key / dominant_team_name を生成する
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# パス設定
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "J3_csv"

_LOCAL_RAW = PROJECT_ROOT.parent / "生データ"
_GDRIVE_RAW = Path(
    os.environ.get(
        "RAW_DATA_BASE_DIR",
        "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp"
        "/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ",
    )
)

SC_DIR: Path | None = None
for candidate in [_LOCAL_RAW / "skill corner", _GDRIVE_RAW / "skill corner"]:
    try:
        if candidate.exists():
            SC_DIR = candidate
            break
    except (PermissionError, OSError):
        continue

VALID_MAPPING_FILE = CSV_DIR / "j3_2024_2025_valid_name_mapping.csv"
INTERMEDIATE_FILE = CSV_DIR / "sc_raw_position_data.csv"

TARGET_YEARS = ("2024", "2025")
TARGET_LEAGUE = "J3"

COLUMN_MAP = {
    "player_name": "player_name",
    "Player": "player_name",
    "team_name": "team_name",
    "Team": "team_name",
    "match_id": "match_id",
    "Match ID": "match_id",
    "match_date": "match_date",
    "Date": "match_date",
    "competition_name": "competition_name",
    "Competition": "competition_name",
    "season_name": "season_name",
    "Season": "season_name",
    "position": "position",
    "Position": "position",
    "position_group": "position_group",
    "Position Group": "position_group",
    "minutes_full_all": "minutes_full_all",
    "Minutes": "minutes_full_all",
}

NEEDED_COLS = [
    "player_name",
    "team_name",
    "match_id",
    "match_date",
    "competition_name",
    "season_name",
    "position",
    "position_group",
    "minutes_full_all",
]

TEAM_NAME_MAP: dict[str, str] = {
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

# ---------------------------------------------------------------------------
# 分析カテゴリ変換マップ
# ---------------------------------------------------------------------------
POSITION_TO_ANALYSIS: dict[str, str] = {
    "CB": "CB",
    "LCB": "CB",
    "RCB": "CB",
    "LB": "SB",
    "RB": "SB",
    "LWB": "SB",
    "RWB": "SB",
    "DM": "CMF",
    "CM": "CMF",
    "LDM": "CMF",
    "RDM": "CMF",
    "LM": "SH",
    "RM": "SH",
    "LW": "SH",
    "RW": "SH",
    "AM": "ST",
    "CF": "FW",
    "LF": "SH",
    "RF": "SH",
    "Center Back": "CB",
    "Left Center Back": "CB",
    "Right Center Back": "CB",
    "Left Back": "SB",
    "Right Back": "SB",
    "Left Wing Back": "SB",
    "Right Wing Back": "SB",
    "Defensive Midfield": "CMF",
    "Center Midfield": "CMF",
    "Left Defensive Midfield": "CMF",
    "Right Defensive Midfield": "CMF",
    "Left Midfield": "SH",
    "Right Midfield": "SH",
    "Left Winger": "SH",
    "Right Winger": "SH",
    "Attacking Midfield": "ST",
    "Center Forward": "FW",
    "Left Forward": "SH",
    "Right Forward": "SH",
}

ANALYSIS_CODE_TO_JP: dict[str, str] = {
    "CB": "センターバック",
    "SB": "サイドバック",
    "CMF": "セントラルMF",
    "SH": "サイドハーフ",
    "ST": "セカンドトップ",
    "FW": "フォワード",
}


def normalize_whitespace(value: str) -> str:
    """空白を正規化する。"""
    s = unicodedata.normalize("NFKC", str(value))
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def normalize_name(name: str) -> str:
    """比較用キーを作る。"""
    if pd.isna(name) or not isinstance(name, str):
        return ""
    s = normalize_whitespace(name)
    s = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uff0d]", "-", s)
    return s.casefold()


def canonicalize_sc_player_name(name: str) -> str:
    """
    SkillCorner 選手名を canonical 化する。

    ルール:
      - NFKC + 空白正規化
      - ASCII token が完全反復 (A B A B) の場合は前半へ縮約
    """
    if pd.isna(name) or not isinstance(name, str):
        return ""

    normalized = normalize_whitespace(name)
    tokens = normalized.split(" ")
    if len(tokens) >= 2 and len(tokens) % 2 == 0:
        half = len(tokens) // 2
        left = [token.casefold() for token in tokens[:half]]
        right = [token.casefold() for token in tokens[half:]]
        if left == right:
            return " ".join(tokens[:half])
    return normalized


def canonicalize_team_name(name: str) -> str:
    """SC チーム名を FB 側と比較しやすい形へ寄せる。"""
    if pd.isna(name):
        return ""
    normalized = normalize_whitespace(name)
    return TEAM_NAME_MAP.get(normalized, normalized)


def build_team_season_lookup(
    df: pd.DataFrame,
    *,
    player_col: str,
    season_col: str,
    team_col: str,
    minutes_col: str,
    dominant_team_col: str = "dominant_team_name",
) -> pd.DataFrame:
    """
    選手ごとの team/season 構成を minutes 降順で要約する。
    """
    grouped = (
        df.groupby([player_col, season_col, team_col], as_index=False)[minutes_col]
        .sum()
        .rename(columns={minutes_col: "team_season_minutes"})
    )
    grouped[season_col] = grouped[season_col].astype(str)
    grouped[team_col] = grouped[team_col].fillna("").astype(str)
    grouped = grouped.sort_values(
        [player_col, "team_season_minutes", season_col, team_col],
        ascending=[True, False, True, True],
    ).reset_index(drop=True)

    records: list[dict[str, object]] = []
    for player, grp in grouped.groupby(player_col):
        rows = grp.reset_index(drop=True)
        signature = "; ".join(
            f"{row[season_col]}|{row[team_col]}|{float(row['team_season_minutes']):.2f}"
            for _, row in rows.iterrows()
        )
        key = "; ".join(
            f"{row[season_col]}|{row[team_col]}"
            for _, row in rows.iterrows()
        )
        dominant_team_name = rows.iloc[0][team_col] if not rows.empty else ""
        records.append(
            {
                player_col: player,
                dominant_team_col: dominant_team_name,
                "team_season_key": key,
                "team_season_signature": signature,
            }
        )

    return pd.DataFrame(records)


def standardize_sc_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {col: COLUMN_MAP[col] for col in df.columns if col in COLUMN_MAP}
    standardized = df.rename(columns=rename)
    for needed in NEEDED_COLS:
        if needed not in standardized.columns:
            standardized[needed] = None
    return standardized[NEEDED_COLS]


# ---------------------------------------------------------------------------
# Step 1: Raw SC データ読み込み
# ---------------------------------------------------------------------------
def load_raw_sc_position_data() -> pd.DataFrame:
    """
    2024-2025 J3 の全 raw SC CSV から position 関連列を抽出する。
    """
    if INTERMEDIATE_FILE.exists():
        print(f"中間CSV を使用: {INTERMEDIATE_FILE}")
        df = pd.read_csv(INTERMEDIATE_FILE)
        df = standardize_sc_columns(df)
        if "source_year" not in df.columns and "season_name" in df.columns:
            df["source_year"] = df["season_name"].astype(str).str.extract(r"(\d{4})", expand=False)
        print(f"  レコード数: {len(df)}")
        return df

    if SC_DIR is None:
        raise RuntimeError(
            "SkillCorner raw データにアクセスできません。\n"
            "以下のいずれかの方法で中間CSVを作成してください:\n\n"
            "【方法1】macOS で Terminal にフルディスクアクセスを付与してから:\n"
            "  bash All-J3/extract_sc_position_data.sh\n\n"
            "【方法2】環境変数を設定:\n"
            "  export RAW_DATA_BASE_DIR=/path/to/生データ\n\n"
            f"中間CSV の想定パス: {INTERMEDIATE_FILE}"
        )

    print(f"SC raw データディレクトリ: {SC_DIR}")
    frames: list[pd.DataFrame] = []

    for year in TARGET_YEARS:
        league_dir = SC_DIR / year / TARGET_LEAGUE
        csv_files = sorted(league_dir.glob("*.csv"))
        print(f"  {year}/{TARGET_LEAGUE}: {len(csv_files)} ファイル")

        for fpath in csv_files:
            try:
                df = pd.read_csv(fpath)
                df = standardize_sc_columns(df)
                df["source_year"] = year
                frames.append(df)
            except Exception as exc:
                print(f"    WARNING: {fpath.name} 読込失敗: {exc}")

    if not frames:
        raise RuntimeError("raw SC ファイルが1件も読み込めませんでした。")

    df_all = pd.concat(frames, ignore_index=True)
    print(f"  合計レコード数: {len(df_all)}")

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(INTERMEDIATE_FILE, index=False, encoding="utf-8-sig")
    print(f"  中間CSV保存: {INTERMEDIATE_FILE}")

    return df_all


# ---------------------------------------------------------------------------
# Step 2: 選手 × ポジション別 minutes 集計
# ---------------------------------------------------------------------------
def aggregate_positions_by_player(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    選手ごとにポジション別の minutes を集計し、
    Primary / Secondary ポジションを決定する。
    """
    df = df_raw.copy()
    df["minutes_full_all"] = pd.to_numeric(df["minutes_full_all"], errors="coerce").fillna(0)
    df["source_year"] = df["source_year"].astype(str)
    df["player_name_raw_skillcorner"] = df["player_name"].fillna("").astype(str).apply(normalize_whitespace)
    df["player_name_normalized"] = df["player_name_raw_skillcorner"].apply(canonicalize_sc_player_name)
    df["team_name_canonical"] = df["team_name"].apply(canonicalize_team_name)

    raw_name_lookup = (
        df.groupby(["player_name_normalized", "player_name_raw_skillcorner"], as_index=False)[
            "minutes_full_all"
        ]
        .sum()
        .sort_values(
            ["player_name_normalized", "minutes_full_all", "player_name_raw_skillcorner"],
            ascending=[True, False, True],
        )
        .drop_duplicates(subset=["player_name_normalized"], keep="first")
        .set_index("player_name_normalized")["player_name_raw_skillcorner"]
        .to_dict()
    )

    df_pos = (
        df.groupby(["player_name_normalized", "position", "position_group"], as_index=False)[
            "minutes_full_all"
        ]
        .sum()
        .rename(columns={"minutes_full_all": "pos_minutes"})
    )
    df_total = (
        df.groupby("player_name_normalized", as_index=False)["minutes_full_all"]
        .sum()
        .rename(columns={"minutes_full_all": "sc_total_minutes"})
    )
    df_team_lookup = build_team_season_lookup(
        df,
        player_col="player_name_normalized",
        season_col="source_year",
        team_col="team_name_canonical",
        minutes_col="minutes_full_all",
    )

    df_pos = df_pos.sort_values(
        ["player_name_normalized", "pos_minutes", "position"],
        ascending=[True, False, True],
    )

    results: list[dict[str, object]] = []
    for player, grp in df_pos.groupby("player_name_normalized"):
        total_min = float(
            df_total.loc[df_total["player_name_normalized"] == player, "sc_total_minutes"].iloc[0]
        )
        rows = grp.reset_index(drop=True)
        team_summary = df_team_lookup.loc[
            df_team_lookup["player_name_normalized"] == player
        ].iloc[0]

        primary = rows.iloc[0]
        rec: dict[str, object] = {
            "player_name_raw_skillcorner": raw_name_lookup.get(player, player),
            "player_name_normalized": player,
            "dominant_team_name": team_summary["dominant_team_name"],
            "team_season_key": team_summary["team_season_key"],
            "team_season_signature": team_summary["team_season_signature"],
            "season_scope": "2024-2025",
            "sc_total_minutes": round(total_min, 2),
            "SC_Primary_Position": primary["position"],
            "SC_Primary_Position_Minutes": round(primary["pos_minutes"], 2),
            "SC_Primary_Position_Share": (
                round(primary["pos_minutes"] / total_min * 100, 2)
                if total_min > 0
                else 0.0
            ),
            "SC_Primary_Position_Group": primary["position_group"],
        }

        if len(rows) >= 2:
            secondary = rows.iloc[1]
            rec["SC_Secondary_Position"] = secondary["position"]
            rec["SC_Secondary_Position_Minutes"] = round(secondary["pos_minutes"], 2)
            rec["SC_Secondary_Position_Share"] = (
                round(secondary["pos_minutes"] / total_min * 100, 2)
                if total_min > 0
                else 0.0
            )
            rec["SC_Secondary_Position_Group"] = secondary["position_group"]
        else:
            rec["SC_Secondary_Position"] = np.nan
            rec["SC_Secondary_Position_Minutes"] = np.nan
            rec["SC_Secondary_Position_Share"] = np.nan
            rec["SC_Secondary_Position_Group"] = np.nan

        pos_detail_parts = []
        for _, row in rows.iterrows():
            share = round(row["pos_minutes"] / total_min * 100, 1) if total_min > 0 else 0.0
            pos_detail_parts.append(f"{row['position']}({row['pos_minutes']:.0f}min/{share}%)")
        rec["SC_All_Positions_Detail"] = ", ".join(pos_detail_parts)
        results.append(rec)

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Step 3: 分析カテゴリ変換
# ---------------------------------------------------------------------------
def assign_analysis_category(df_positions: pd.DataFrame) -> pd.DataFrame:
    """
    SC_Primary_Position から分析カテゴリ (CB/SB/CMF/SH/ST/FW) を付与する。
    """
    df = df_positions.copy()

    def _map_position(row: pd.Series) -> tuple[str, str, str]:
        pos = row["SC_Primary_Position"]
        pgroup = row["SC_Primary_Position_Group"]
        forward_positions = {"LF", "RF", "Left Forward", "Right Forward"}
        if pos in forward_positions and pgroup == "Center Forward":
            code = "FW"
        else:
            code = POSITION_TO_ANALYSIS.get(pos, "UNKNOWN")
        jp = ANALYSIS_CODE_TO_JP.get(code, "不明")
        source_desc = f"{pos} (Position Group: {pgroup})"
        return code, jp, source_desc

    mapped = df.apply(_map_position, axis=1, result_type="expand")
    df["analysis_position_code"] = mapped[0]
    df["analysis_position_jp"] = mapped[1]
    df["analysis_position_source"] = mapped[2]
    return df


# ---------------------------------------------------------------------------
# Step 4: 変換マップ CSV の作成
# ---------------------------------------------------------------------------
def build_analysis_mapping_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    """実データに基づく position → analysis_position_code の全組み合わせマップを生成する。"""
    df = df_raw[["position", "position_group"]].drop_duplicates().sort_values(
        ["position_group", "position"]
    )

    rows: list[dict[str, object]] = []
    for _, row in df.iterrows():
        pos = row["position"]
        pgroup = row["position_group"]
        forward_positions = {"LF", "RF", "Left Forward", "Right Forward"}
        if pos in forward_positions and pgroup == "Center Forward":
            code = "FW"
        else:
            code = POSITION_TO_ANALYSIS.get(pos, "UNKNOWN")
        rows.append(
            {
                "sc_position": pos,
                "sc_position_group": pgroup,
                "analysis_position_code": code,
                "analysis_position_jp": ANALYSIS_CODE_TO_JP.get(code, "不明"),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Step 5: 既存マッピング CSV とのマージ
# ---------------------------------------------------------------------------
def merge_with_existing_mapping(
    df_positions: pd.DataFrame,
    valid_mapping_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    既存 valid_name_mapping.csv と復元した細分類ポジションを名前正規化でマージする。
    """
    df_existing = pd.read_csv(valid_mapping_path)
    existing_count = len(df_existing)

    print(f"\n既存マッピング: {existing_count} 件")
    print(f"細分類ポジション集計: {len(df_positions)} 件")

    df_existing["join_name_normalized"] = df_existing["SC_Name"].apply(normalize_name)
    df_positions = df_positions.copy()
    df_positions["join_name_normalized"] = df_positions["player_name_normalized"].apply(
        normalize_name
    )

    pos_dup_count = int(
        df_positions.duplicated(subset=["join_name_normalized"], keep=False).sum()
    )
    if pos_dup_count > 0:
        print(f"  [WARNING] 細分類側に正規化後重複: {pos_dup_count} 行")

    df_merged = pd.merge(
        df_existing,
        df_positions,
        on="join_name_normalized",
        how="left",
        suffixes=("", "_sc"),
    )

    joined_count = df_merged["player_name_normalized"].notna().sum()
    unjoined_count = df_merged["player_name_normalized"].isna().sum()
    join_rate = joined_count / existing_count * 100 if existing_count > 0 else 0
    dup_count = int(df_merged.duplicated(subset=["SC_Name", "対象年度"], keep=False).sum())

    unjoined_players = df_merged.loc[
        df_merged["player_name_normalized"].isna(),
        ["SC_Name", "FB_Name", "SC_Position_Group"],
    ].copy()

    print("\nJoin 結果:")
    print(f"  結合成功: {joined_count} / {existing_count} ({join_rate:.1f}%)")
    print(f"  未結合: {unjoined_count} 件")
    print(f"  重複行: {dup_count} 件")

    quality_records = [
        {
            "metric": "existing_mapping_count",
            "value": existing_count,
            "detail": "既存マッピング件数",
        },
        {
            "metric": "position_data_count",
            "value": len(df_positions),
            "detail": "SC細分類ポジション集計件数",
        },
        {
            "metric": "join_key",
            "value": "normalize(SC_Name) = normalize(player_name_normalized)",
            "detail": "使用した結合キー",
        },
        {
            "metric": "joined_count",
            "value": joined_count,
            "detail": "結合成功件数",
        },
        {
            "metric": "unjoined_count",
            "value": unjoined_count,
            "detail": "未結合件数",
        },
        {
            "metric": "join_rate_pct",
            "value": round(join_rate, 2),
            "detail": "結合成功率 (%)",
        },
        {
            "metric": "duplicate_rows",
            "value": dup_count,
            "detail": "重複行数 (0が正常)",
        },
    ]

    for _, row in unjoined_players.iterrows():
        quality_records.append(
            {
                "metric": "unjoined_player",
                "value": row["SC_Name"],
                "detail": f"FB_Name={row.get('FB_Name', 'N/A')}, SC_PosGroup={row.get('SC_Position_Group', 'N/A')}",
            }
        )

    return df_merged, pd.DataFrame(quality_records)


# ---------------------------------------------------------------------------
# Step 6: レポート出力
# ---------------------------------------------------------------------------
def print_final_report(
    df_raw: pd.DataFrame,
    df_positions: pd.DataFrame,
    df_merged: pd.DataFrame,
) -> None:
    print("\n" + "=" * 70)
    print("SkillCorner 細分類ポジション復元レポート")
    print("=" * 70)

    unique_positions = sorted(df_raw["position"].dropna().unique())
    unique_pgroups = sorted(df_raw["position_group"].dropna().unique())
    print(f"\n■ SC細分類ポジション (position) ユニーク値 ({len(unique_positions)}種):")
    for pos in unique_positions:
        print(f"    {pos}: {(df_raw['position'] == pos).sum()} レコード")

    print(f"\n■ SC Position Group ユニーク値 ({len(unique_pgroups)}種):")
    for group in unique_pgroups:
        print(f"    {group}: {(df_raw['position_group'] == group).sum()} レコード")

    canonicalized = df_positions[
        df_positions["player_name_raw_skillcorner"] != df_positions["player_name_normalized"]
    ]
    print(f"\n■ canonical name 適用件数: {len(canonicalized)}")
    for _, row in canonicalized.head(10).iterrows():
        print(
            f"    - {row['player_name_raw_skillcorner']} → {row['player_name_normalized']}"
        )

    print("\n■ 分析カテゴリ分布 (Primary Position ベース):")
    cat_counts = df_positions["analysis_position_code"].value_counts().sort_index()
    for code, count in cat_counts.items():
        print(f"    {code} ({ANALYSIS_CODE_TO_JP.get(code, '?')}): {count} 選手")

    print("\n■ 今回の復元で追加された情報:")
    print("    - raw 名と canonical 名の両方")
    print("    - dominant_team_name / team_season_key / team_season_signature")
    print("    - SC_Primary_Position / SC_Secondary_Position")
    print("    - analysis_position_code / analysis_position_source")
    print(f"\n■ merged 側結合成功: {int(df_merged['player_name_normalized'].notna().sum())} 件")
    print("=" * 70)


def main() -> None:
    print("=== SkillCorner 細分類ポジション復元処理 開始 ===\n")

    print("--- Step 1: Raw SC データ読み込み ---")
    df_raw = load_raw_sc_position_data()

    print("\n--- Step 2: 選手別ポジション集計 ---")
    df_positions = aggregate_positions_by_player(df_raw)
    print(f"  集計選手数: {len(df_positions)}")

    print("\n--- Step 3: 分析カテゴリ付与 ---")
    df_positions = assign_analysis_category(df_positions)

    print("\n--- Step 4: 変換マップ生成 ---")
    df_analysis_map = build_analysis_mapping_table(df_raw)
    print(f"  変換マップエントリ数: {len(df_analysis_map)}")

    print("\n--- Step 5: 既存マッピングとのマージ ---")
    df_merged, df_quality = merge_with_existing_mapping(df_positions, VALID_MAPPING_FILE)

    print("\n--- Step 6: ファイル保存 ---")
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    out_positions = CSV_DIR / "sc_detailed_positions_2024_2025.csv"
    out_map = CSV_DIR / "sc_position_analysis_mapping.csv"
    out_merged = CSV_DIR / "j3_2024_2025_valid_name_mapping_with_positions.csv"
    out_quality = CSV_DIR / "sc_position_join_quality_report.csv"

    df_positions.to_csv(out_positions, index=False, encoding="utf-8-sig")
    df_analysis_map.to_csv(out_map, index=False, encoding="utf-8-sig")
    df_merged.to_csv(out_merged, index=False, encoding="utf-8-sig")
    df_quality.to_csv(out_quality, index=False, encoding="utf-8-sig")

    print(f"  ✅ {out_positions.name} ({len(df_positions)} 行)")
    print(f"  ✅ {out_map.name} ({len(df_analysis_map)} 行)")
    print(f"  ✅ {out_merged.name} ({len(df_merged)} 行)")
    print(f"  ✅ {out_quality.name} ({len(df_quality)} 行)")

    print_final_report(df_raw, df_positions, df_merged)
    print("\n=== 処理完了 ===")


if __name__ == "__main__":
    main()
