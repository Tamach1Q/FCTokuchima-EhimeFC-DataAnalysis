"""
SC raw データから position 関連列を抽出して中間CSVを生成する。

2024年と2025年でヘッダー名が異なるため、両方のフォーマットに対応:
  2024: player_name, position, position_group, minutes_full_all  (略称: LCB, DM, CF ...)
  2025: Player, Position, Position Group, Minutes               (フル名: Left Center Back, Attacking Midfield ...)
"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "J3_csv"
OUTPUT_FILE = CSV_DIR / "sc_raw_position_data.csv"

_LOCAL_RAW = PROJECT_ROOT.parent / "生データ"
_GDRIVE_RAW = Path(
    os.environ.get(
        "RAW_DATA_BASE_DIR",
        "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp"
        "/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ",
    )
)

TARGET_YEARS = ("2024", "2025")
TARGET_LEAGUE = "J3"

# 列名マッピング: 各フォーマット → 標準名
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

NEEDED_COLS = ["player_name", "team_name", "match_id", "match_date",
               "competition_name", "season_name", "position", "position_group",
               "minutes_full_all"]


def find_sc_dir() -> Path:
    for candidate in [_LOCAL_RAW / "skill corner", _GDRIVE_RAW / "skill corner"]:
        try:
            if candidate.exists() and any(candidate.iterdir()):
                return candidate
        except (PermissionError, OSError):
            continue
    raise RuntimeError("SC raw データにアクセスできません")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            rename[col] = COLUMN_MAP[col]
    df = df.rename(columns=rename)
    for needed in NEEDED_COLS:
        if needed not in df.columns:
            df[needed] = None
    return df[NEEDED_COLS]


def main():
    sc_dir = find_sc_dir()
    print(f"SC raw データディレクトリ: {sc_dir}")

    frames = []
    for year in TARGET_YEARS:
        league_dir = sc_dir / year / TARGET_LEAGUE
        csv_files = sorted(f for f in league_dir.glob("*.csv"))
        print(f"  {year}/{TARGET_LEAGUE}: {len(csv_files)} ファイル")

        for fpath in csv_files:
            try:
                df = pd.read_csv(fpath)
                df = standardize_columns(df)
                df["source_year"] = year
                frames.append(df)
            except Exception as e:
                print(f"    WARNING: {fpath.name}: {e}")

    if not frames:
        raise RuntimeError("ファイルが読み込めませんでした")

    df_all = pd.concat(frames, ignore_index=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n完了: {len(df_all)} レコード → {OUTPUT_FILE}")

    # サマリ
    print(f"\nposition ユニーク値:")
    for pos in sorted(df_all["position"].dropna().unique()):
        print(f"  {pos}: {(df_all['position'] == pos).sum()}")


if __name__ == "__main__":
    main()
