"""
SkillCorner 細分類ポジション復元スクリプト
=========================================

目的:
  raw SkillCorner 試合別CSV から position (細分類) を再抽出し、
  選手単位で Primary/Secondary ポジションを集計。
  既存の j3_2024_2025_valid_name_mapping.csv に新規列として再マージする。

入力:
  - 生データ/skill corner/{2024,2025}/J3/*.csv  (raw SC試合データ)
  - All-J3/J3_csv/j3_2024_2025_valid_name_mapping.csv (既存マッピング)

出力:
  - All-J3/J3_csv/sc_detailed_positions_2024_2025.csv  (細分類集計結果)
  - All-J3/J3_csv/sc_position_analysis_mapping.csv      (変換マップ)
  - All-J3/J3_csv/j3_2024_2025_valid_name_mapping_with_positions.csv (merged)
  - All-J3/J3_csv/sc_position_join_quality_report.csv   (join品質レポート)

同率処理ルール:
  - 同一選手で複数ポジションの minutes が同率の場合、
    position のアルファベット順で先のものを Primary とする
  - Secondary がない場合 (1ポジションのみ) は空欄

LF/RF の扱い:
  - position_group='Wide Attacker' の場合 → SH (サイドハーフ) 扱い
  - position_group='Center Forward' の場合 → FW 扱い (もし存在すれば)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# パス設定
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "J3_csv"

# raw データへのアクセスパス (複数候補)
# 優先1: ローカルシンボリックリンク  優先2: Google Drive
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

# ---------------------------------------------------------------------------
# 分析カテゴリ変換マップ
# ---------------------------------------------------------------------------
# position (SC raw) → analysis_position_code
# 注: LF/RF は position_group で判定するため、ここでは暫定 SH とし
#     後で position_group='Center Forward' の場合に FW へ修正する
POSITION_TO_ANALYSIS: dict[str, str] = {
    # --- 2024 format (abbreviated) ---
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
    # --- 2025 format (full name) ---
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


# ---------------------------------------------------------------------------
# Step 1: Raw SC データ読み込み
# ---------------------------------------------------------------------------
def load_raw_sc_position_data() -> pd.DataFrame:
    """
    2024-2025 J3 の全 raw SC CSV から position 関連列を抽出する。
    
    読み込み優先度:
      1. 中間CSV (sc_raw_position_data.csv) が存在する場合はそれを使用
      2. SC_DIR が利用可能な場合は raw ファイルを直接読み込み
      3. どちらもない場合はエラー
    """
    # --- 優先1: 中間CSV ---
    if INTERMEDIATE_FILE.exists():
        print(f"中間CSV を使用: {INTERMEDIATE_FILE}")
        df = pd.read_csv(INTERMEDIATE_FILE)
        # 列名を標準化 (中間CSVのヘッダーに合わせる)
        col_map = {}
        for col in df.columns:
            col_lower = col.strip().lower()
            if col_lower == "player_name":
                col_map[col] = "player_name"
            elif col_lower == "position":
                col_map[col] = "position"
            elif col_lower == "position_group":
                col_map[col] = "position_group"
            elif col_lower == "minutes_full_all":
                col_map[col] = "minutes_full_all"
            elif col_lower == "source_year":
                col_map[col] = "source_year"
            elif col_lower == "team_name":
                col_map[col] = "team_name"
        if col_map:
            df = df.rename(columns=col_map)
        print(f"  レコード数: {len(df)}")
        return df

    # --- 優先2: Raw SC ディレクトリ ---
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
                df = pd.read_csv(fpath, usecols=[
                    "player_name", "team_name", "match_id", "match_date",
                    "competition_name", "season_name",
                    "position", "position_group", "minutes_full_all",
                ])
                df["source_year"] = year
                frames.append(df)
            except Exception as e:
                print(f"    WARNING: {fpath.name} 読込失敗: {e}")

    if not frames:
        raise RuntimeError("raw SC ファイルが1件も読み込めませんでした。")

    df_all = pd.concat(frames, ignore_index=True)
    print(f"  合計レコード数: {len(df_all)}")

    # 中間CSVとして保存 (次回以降の高速化)
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

    同率処理ルール:
      - minutes が同率の場合、position のアルファベット順で先のものを Primary とする
    """
    df = df_raw.copy()
    df["minutes_full_all"] = pd.to_numeric(df["minutes_full_all"], errors="coerce").fillna(0)

    # 選手 × position × position_group ごとに minutes を合計
    df_pos = (
        df.groupby(["player_name", "position", "position_group"], as_index=False)
        ["minutes_full_all"]
        .sum()
        .rename(columns={"minutes_full_all": "pos_minutes"})
    )

    # 選手ごとの合計 minutes
    df_total = (
        df.groupby("player_name", as_index=False)["minutes_full_all"]
        .sum()
        .rename(columns={"minutes_full_all": "sc_total_minutes"})
    )

    # 選手ごとにポジション minutes の降順 + アルファベット順でソート
    df_pos = df_pos.sort_values(
        ["player_name", "pos_minutes", "position"],
        ascending=[True, False, True],
    )

    results: list[dict] = []
    for player, grp in df_pos.groupby("player_name"):
        total_min = float(df_total.loc[df_total["player_name"] == player, "sc_total_minutes"].iloc[0])
        rows = grp.reset_index(drop=True)

        # Primary
        primary = rows.iloc[0]
        rec: dict = {
            "player_name_raw_skillcorner": player,
            "sc_total_minutes": round(total_min, 2),
            "SC_Primary_Position": primary["position"],
            "SC_Primary_Position_Minutes": round(primary["pos_minutes"], 2),
            "SC_Primary_Position_Share": (
                round(primary["pos_minutes"] / total_min * 100, 2)
                if total_min > 0 else 0.0
            ),
            "SC_Primary_Position_Group": primary["position_group"],
        }

        # Secondary
        if len(rows) >= 2:
            secondary = rows.iloc[1]
            rec["SC_Secondary_Position"] = secondary["position"]
            rec["SC_Secondary_Position_Minutes"] = round(secondary["pos_minutes"], 2)
            rec["SC_Secondary_Position_Share"] = (
                round(secondary["pos_minutes"] / total_min * 100, 2)
                if total_min > 0 else 0.0
            )
            rec["SC_Secondary_Position_Group"] = secondary["position_group"]
        else:
            rec["SC_Secondary_Position"] = np.nan
            rec["SC_Secondary_Position_Minutes"] = np.nan
            rec["SC_Secondary_Position_Share"] = np.nan
            rec["SC_Secondary_Position_Group"] = np.nan

        # 全ポジション詳細 (カンマ区切り)
        pos_detail_parts = []
        for _, r in rows.iterrows():
            share = round(r["pos_minutes"] / total_min * 100, 1) if total_min > 0 else 0
            pos_detail_parts.append(f"{r['position']}({r['pos_minutes']:.0f}min/{share}%)")
        rec["SC_All_Positions_Detail"] = ", ".join(pos_detail_parts)

        results.append(rec)

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Step 3: 分析カテゴリ変換
# ---------------------------------------------------------------------------
def assign_analysis_category(df_positions: pd.DataFrame) -> pd.DataFrame:
    """
    SC_Primary_Position から分析カテゴリ (CB/SB/CMF/SH/ST/FW) を付与する。

    LF/RF の特別処理:
      position_group が 'Center Forward' なら FW、それ以外なら SH
    """
    df = df_positions.copy()

    def _map_position(row: pd.Series) -> tuple[str, str, str]:
        pos = row["SC_Primary_Position"]
        pgroup = row["SC_Primary_Position_Group"]

        # LF/RF の特別処理 (2024: LF/RF, 2025: Left Forward/Right Forward)
        forward_positions = {"LF", "RF", "Left Forward", "Right Forward"}
        if pos in forward_positions and pgroup == "Center Forward":
            code = "FW"
        else:
            code = POSITION_TO_ANALYSIS.get(pos, "UNKNOWN")

        jp = ANALYSIS_CODE_TO_JP.get(code, "不明")
        source_desc = f"{pos} (Position Group: {pgroup})"
        return code, jp, source_desc

    results = df.apply(_map_position, axis=1, result_type="expand")
    df["analysis_position_code"] = results[0]
    df["analysis_position_jp"] = results[1]
    df["analysis_position_source"] = results[2]

    return df


# ---------------------------------------------------------------------------
# Step 4: 変換マップ CSV の作成
# ---------------------------------------------------------------------------
def build_analysis_mapping_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    """実データに基づく position → analysis_position_code の全組み合わせマップを生成。"""
    df = df_raw[["position", "position_group"]].drop_duplicates().sort_values(
        ["position_group", "position"]
    )

    records = []
    for _, row in df.iterrows():
        pos = row["position"]
        pgroup = row["position_group"]

        forward_positions = {"LF", "RF", "Left Forward", "Right Forward"}
        if pos in forward_positions and pgroup == "Center Forward":
            code = "FW"
        else:
            code = POSITION_TO_ANALYSIS.get(pos, "UNKNOWN")

        records.append({
            "sc_position": pos,
            "sc_position_group": pgroup,
            "analysis_position_code": code,
            "analysis_position_jp": ANALYSIS_CODE_TO_JP.get(code, "不明"),
        })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Step 5: 既存マッピング CSV とのマージ
# ---------------------------------------------------------------------------
def merge_with_existing_mapping(
    df_positions: pd.DataFrame,
    valid_mapping_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    既存 valid_name_mapping.csv と、復元した細分類ポジションを SC_Name でマージ。

    join key: valid_mapping の SC_Name = df_positions の player_name_raw_skillcorner
    方式: LEFT JOIN (既存マッピング基準)

    Returns:
        (merged_df, quality_report_df)
    """
    df_existing = pd.read_csv(valid_mapping_path)
    existing_count = len(df_existing)
    existing_columns = list(df_existing.columns)

    print(f"\n既存マッピング: {existing_count} 件")
    print(f"細分類ポジション集計: {len(df_positions)} 件")

    # join key の確認
    join_key_left = "SC_Name"
    join_key_right = "player_name_raw_skillcorner"

    # player_name_normalized を追加（SC_Name と同じ値をセット）
    df_positions["player_name_normalized"] = df_positions[join_key_right]
    df_positions["season_scope"] = "2024-2025"

    # LEFT JOIN
    df_merged = pd.merge(
        df_existing,
        df_positions,
        left_on=join_key_left,
        right_on=join_key_right,
        how="left",
    )

    # join 品質集計
    joined_count = df_merged[join_key_right].notna().sum()
    unjoined_count = df_merged[join_key_right].isna().sum()
    join_rate = joined_count / existing_count * 100 if existing_count > 0 else 0

    # 重複チェック
    dup_count = int(df_merged.duplicated(subset=[join_key_left], keep=False).sum())

    # 未結合選手
    unjoined_players = df_merged.loc[
        df_merged[join_key_right].isna(), [join_key_left, "FB_Name", "SC_Position_Group"]
    ].copy()

    print(f"\nJoin 結果:")
    print(f"  結合成功: {joined_count} / {existing_count} ({join_rate:.1f}%)")
    print(f"  未結合: {unjoined_count} 件")
    print(f"  重複行: {dup_count} 件")

    # join_key_right 列は冗長なので削除
    cols_to_drop = [join_key_right]
    df_merged = df_merged.drop(columns=[c for c in cols_to_drop if c in df_merged.columns])

    # Quality Report
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
            "value": f"{join_key_left} = {join_key_right}",
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

    # 未結合選手リストを quality report に追記
    for _, row in unjoined_players.iterrows():
        quality_records.append({
            "metric": "unjoined_player",
            "value": row[join_key_left],
            "detail": f"FB_Name={row.get('FB_Name', 'N/A')}, SC_PosGroup={row.get('SC_Position_Group', 'N/A')}",
        })

    df_quality = pd.DataFrame(quality_records)

    return df_merged, df_quality


# ---------------------------------------------------------------------------
# Step 6: レポート出力
# ---------------------------------------------------------------------------
def print_final_report(
    df_raw: pd.DataFrame,
    df_positions: pd.DataFrame,
    df_merged: pd.DataFrame,
) -> None:
    """最終レポートをコンソールに出力する。"""
    print("\n" + "=" * 70)
    print("SkillCorner 細分類ポジション復元レポート")
    print("=" * 70)

    # ユニークポジション一覧
    unique_positions = sorted(df_raw["position"].dropna().unique())
    unique_pgroups = sorted(df_raw["position_group"].dropna().unique())
    print(f"\n■ SC細分類ポジション (position) ユニーク値 ({len(unique_positions)}種):")
    for p in unique_positions:
        count = (df_raw["position"] == p).sum()
        print(f"    {p}: {count} レコード")

    print(f"\n■ SC Position Group ユニーク値 ({len(unique_pgroups)}種):")
    for pg in unique_pgroups:
        count = (df_raw["position_group"] == pg).sum()
        print(f"    {pg}: {count} レコード")

    # Attacking Midfield (AM) の存在確認
    am_records = (df_raw["position"] == "AM").sum()
    am_players = df_raw.loc[df_raw["position"] == "AM", "player_name"].nunique()
    print(f"\n■ Attacking Midfield (AM) の状況:")
    print(f"    レコード数: {am_records}")
    print(f"    ユニーク選手数: {am_players}")

    # LW/RW vs LM/RM vs LF/RF
    for pos_pair, label in [("LW|RW", "Left/Right Winger"), ("LM|RM", "Left/Right Midfield"), ("LF|RF", "Left/Right Forward"), ("LWB|RWB", "Wing Back")]:
        codes = pos_pair.split("|")
        mask = df_raw["position"].isin(codes)
        rec_count = mask.sum()
        player_count = df_raw.loc[mask, "player_name"].nunique()
        print(f"    {label} ({pos_pair}): {rec_count} レコード, {player_count} 選手")

    # 分析カテゴリ分布
    if "analysis_position_code" in df_positions.columns:
        print(f"\n■ 分析カテゴリ分布 (Primary Position ベース):")
        cat_counts = df_positions["analysis_position_code"].value_counts().sort_index()
        for code, cnt in cat_counts.items():
            jp = ANALYSIS_CODE_TO_JP.get(code, "?")
            print(f"    {code} ({jp}): {cnt} 選手")

        # ST の独立分析可否
        st_count = int(cat_counts.get("ST", 0))
        print(f"\n■ ST 独立分析の所見:")
        if st_count >= 15:
            print(f"    ST = {st_count} 選手 → 独立分析に十分な数")
        elif st_count >= 5:
            print(f"    ST = {st_count} 選手 → 分析は可能だがサンプル数は少なめ")
        elif st_count > 0:
            print(f"    ST = {st_count} 選手 → サンプル数が極めて少なく、独立分析は困難")
        else:
            print(f"    ST = 0 選手 → raw データに AM ポジションが存在しないため独立不可")

    # 復元できたもの
    print(f"\n■ 今回の復元で追加された情報:")
    print(f"    - SC_Primary_Position: 細分類ポジション (例: LCB, RW, DM)")
    print(f"    - SC_Secondary_Position: 2番目に多いポジション")
    print(f"    - 各ポジションの出場分数・シェア")
    print(f"    - analysis_position_code: 6分類カテゴリ (CB/SB/CMF/SH/ST/FW)")
    print(f"    - analysis_position_source: 変換元の SC position")
    print(f"\n■ 既存 merged CSV で失われていたもの:")
    print(f"    - Position Group (5分類) のみ保持されていた")
    print(f"    - 試合別の細分類 position (LCB/RCB/DM/AM 等) が欠落")
    print(f"    - ST を独立分析するための Attacking Midfield の識別ができなかった")

    print("\n" + "=" * 70)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=== SkillCorner 細分類ポジション復元処理 開始 ===\n")

    # Step 1: Raw データ読み込み
    print("--- Step 1: Raw SC データ読み込み ---")
    df_raw = load_raw_sc_position_data()

    # Step 2: 選手別ポジション集計
    print("\n--- Step 2: 選手別ポジション集計 ---")
    df_positions = aggregate_positions_by_player(df_raw)
    print(f"  集計選手数: {len(df_positions)}")

    # Step 3: 分析カテゴリ付与
    print("\n--- Step 3: 分析カテゴリ付与 ---")
    df_positions = assign_analysis_category(df_positions)

    # Step 4: 変換マップ生成
    print("\n--- Step 4: 変換マップ生成 ---")
    df_analysis_map = build_analysis_mapping_table(df_raw)
    print(f"  変換マップエントリ数: {len(df_analysis_map)}")

    # Step 5: 既存マッピングとのマージ
    print("\n--- Step 5: 既存マッピングとのマージ ---")
    df_merged, df_quality = merge_with_existing_mapping(
        df_positions, VALID_MAPPING_FILE
    )

    # Step 6: ファイル保存
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

    # Step 7: レポート
    print_final_report(df_raw, df_positions, df_merged)

    print("\n=== 処理完了 ===")


if __name__ == "__main__":
    main()
