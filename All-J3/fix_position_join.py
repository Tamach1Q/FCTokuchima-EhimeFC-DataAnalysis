"""
SkillCorner ポジション join 改善スクリプト
=========================================

目的:
  - canonical name + team/season signature を優先して再joinする
  - alias は表記揺れだけに限定する
  - join_method_detail で composite / name-only fallback を明示する
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from rebuild_sc_detailed_positions import (
    CSV_DIR,
    build_team_season_lookup,
    canonicalize_sc_player_name,
    canonicalize_team_name,
    load_raw_sc_position_data,
    normalize_name,
)

# ---------------------------------------------------------------------------
# パス設定
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

VALID_MAPPING_FILE = CSV_DIR / "j3_2024_2025_valid_name_mapping.csv"
SC_POSITIONS_FILE = CSV_DIR / "sc_detailed_positions_2024_2025.csv"

OUTPUT_MERGED = CSV_DIR / "j3_2024_2025_valid_name_mapping_with_positions.csv"
OUTPUT_REPORT = CSV_DIR / "sc_position_join_quality_report.csv"
ALIAS_MAP_FILE = CSV_DIR / "sc_name_alias_map.csv"


def build_alias_map() -> dict[str, str]:
    """正規化後も一致しない実データ確認済みの alias のみを保持する。"""
    return {
        "rensuke kawana": "rennosuke kawana",
        "in ju mun": "in-ju mun",
        "joao": "joao vitor gaudencio nunes",
        "justin toshiki kinjo": "justin kinjo",
        "thales": "thales procopio castro de paula",
    }


def save_alias_map(aliases: dict[str, str], filepath: Path) -> None:
    descriptions = {
        "rensuke kawana": "川名連介: Rensuke/Rennosuke の表記揺れ",
        "in ju mun": "文仁柱: ハイフン有無の差",
        "joao": "ジョアオ: 短縮名 → フルネーム",
        "justin toshiki kinjo": "金城ジャスティン俊樹: ミドルネーム有無",
        "thales": "ターレス: 短縮名 → フルネーム",
    }
    rows = [
        {
            "merged_name_normalized": merged_name,
            "sc_name_normalized": sc_name,
            "description": descriptions.get(merged_name, ""),
        }
        for merged_name, sc_name in aliases.items()
    ]
    pd.DataFrame(rows).to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"  aliasマップ保存: {filepath} ({len(rows)} 件)")


def build_expected_sc_lookup() -> dict[str, dict[str, str]]:
    """
    valid_mapping 側の SC_Name から期待される team/season signature を復元する。
    """
    df_raw = load_raw_sc_position_data().copy()
    df_raw["minutes_full_all"] = pd.to_numeric(df_raw["minutes_full_all"], errors="coerce").fillna(0)
    df_raw["source_year"] = df_raw["source_year"].astype(str)
    df_raw["player_name_raw_skillcorner"] = df_raw["player_name"].fillna("").astype(str)
    df_raw["player_name_normalized"] = df_raw["player_name_raw_skillcorner"].apply(
        canonicalize_sc_player_name
    )
    df_raw["team_name_canonical"] = df_raw["team_name"].apply(canonicalize_team_name)

    lookup_df = build_team_season_lookup(
        df_raw,
        player_col="player_name_normalized",
        season_col="source_year",
        team_col="team_name_canonical",
        minutes_col="minutes_full_all",
    )
    lookup_df["join_name_normalized"] = lookup_df["player_name_normalized"].apply(normalize_name)
    return {
        row["join_name_normalized"]: {
            "player_name_normalized": row["player_name_normalized"],
            "dominant_team_name": row["dominant_team_name"],
            "team_season_key": row["team_season_key"],
            "team_season_signature": row["team_season_signature"],
        }
        for _, row in lookup_df.iterrows()
    }


def pick_single_row(candidates: pd.DataFrame) -> pd.Series | None:
    if candidates.empty:
        return None
    if len(candidates) == 1:
        return candidates.iloc[0]
    sorted_candidates = candidates.sort_values(
        ["sc_total_minutes", "player_name_raw_skillcorner"],
        ascending=[False, True],
    )
    return sorted_candidates.iloc[0]


def main() -> None:
    print("=" * 60)
    print("SkillCorner ポジションjoin 改善スクリプト")
    print("=" * 60)

    print("\n[1] データ読み込み")
    df_merged_base = pd.read_csv(VALID_MAPPING_FILE, encoding="utf-8-sig")
    df_sc = pd.read_csv(SC_POSITIONS_FILE, encoding="utf-8-sig")
    print(f"  merged base: {len(df_merged_base)} rows")
    print(f"  SC positions: {len(df_sc)} rows")
    assert len(df_merged_base) == 647, f"行数が647ではありません: {len(df_merged_base)}"

    merged_name_col = "SC_Name"
    sc_name_col = "player_name_raw_skillcorner"
    sc_join_cols = [col for col in df_sc.columns if col != sc_name_col]
    print(f"  SC側から結合する列数: {len(sc_join_cols)}")

    print("\n[2] 正規化キーと期待シグネチャの生成")
    aliases = build_alias_map()
    save_alias_map(aliases, ALIAS_MAP_FILE)

    df_merged_base["raw_name_original"] = df_merged_base[merged_name_col]
    df_merged_base["join_name_normalized"] = df_merged_base[merged_name_col].apply(normalize_name)

    df_sc["join_name_normalized"] = df_sc["player_name_normalized"].apply(normalize_name)

    expected_lookup = build_expected_sc_lookup()

    expected_target_keys: list[str] = []
    expected_team_keys: list[str] = []
    expected_team_signatures: list[str] = []
    expected_dominant_teams: list[str] = []
    canonicalization_notes: list[str] = []

    for _, row in df_merged_base.iterrows():
        normalized_key = row["join_name_normalized"]
        lookup_entry = expected_lookup.get(normalized_key)
        lookup_key = normalized_key

        if lookup_entry is None and normalized_key in aliases:
            lookup_key = aliases[normalized_key]
            lookup_entry = expected_lookup.get(lookup_key)

        if lookup_entry is None:
            expected_target_keys.append("")
            expected_team_keys.append("")
            expected_team_signatures.append("")
            expected_dominant_teams.append("")
            canonicalization_notes.append("")
            continue

        expected_target_keys.append(lookup_key)
        expected_team_keys.append(lookup_entry["team_season_key"])
        expected_team_signatures.append(lookup_entry["team_season_signature"])
        expected_dominant_teams.append(lookup_entry["dominant_team_name"])
        if normalize_name(row[merged_name_col]) != normalize_name(lookup_entry["player_name_normalized"]):
            canonicalization_notes.append(
                f"{row[merged_name_col]} -> {lookup_entry['player_name_normalized']}"
            )
        else:
            canonicalization_notes.append("")

    df_merged_base["expected_sc_target_key"] = expected_target_keys
    df_merged_base["expected_team_season_key"] = expected_team_keys
    df_merged_base["expected_team_season_signature"] = expected_team_signatures
    df_merged_base["expected_dominant_team_name"] = expected_dominant_teams
    df_merged_base["canonicalization_note"] = canonicalization_notes

    print("\n[3] composite join 実行")
    join_methods: list[str] = []
    join_method_details: list[str] = []
    alias_applied_list: list[str] = []
    alias_target_list: list[str] = []
    join_status_list: list[str] = []
    matched_sc_rows: list[dict[str, object] | None] = []

    composite_exact_count = 0
    composite_normalized_count = 0
    normalized_only_count = 0
    alias_count = 0
    unresolved_count = 0

    for _, row in df_merged_base.iterrows():
        original_name = row[merged_name_col]
        normalized_key = row["join_name_normalized"]
        expected_signature = row["expected_team_season_signature"]

        matched_row = None
        method = "unresolved"
        method_detail = "unresolved"
        alias_applied = ""
        alias_target_name = ""

        exact_candidates = df_sc[df_sc[sc_name_col] == original_name]
        if expected_signature:
            composite_exact = exact_candidates[
                exact_candidates["team_season_signature"] == expected_signature
            ]
        else:
            composite_exact = exact_candidates
        matched_row = pick_single_row(composite_exact)
        if matched_row is not None:
            method = "exact"
            method_detail = "composite_exact" if expected_signature else "normalized_only"
            if method_detail == "composite_exact":
                composite_exact_count += 1
            else:
                normalized_only_count += 1
        else:
            normalized_candidates = df_sc[df_sc["join_name_normalized"] == normalized_key]
            composite_normalized = (
                normalized_candidates[
                    normalized_candidates["team_season_signature"] == expected_signature
                ]
                if expected_signature
                else normalized_candidates
            )
            matched_row = pick_single_row(composite_normalized)
            if matched_row is not None:
                method = "normalized"
                method_detail = (
                    "composite_normalized" if expected_signature else "normalized_only"
                )
                if method_detail == "composite_normalized":
                    composite_normalized_count += 1
                else:
                    normalized_only_count += 1
            else:
                unique_normalized = pick_single_row(normalized_candidates)
                if unique_normalized is not None and len(normalized_candidates) == 1:
                    matched_row = unique_normalized
                    method = "normalized"
                    method_detail = "normalized_only"
                    normalized_only_count += 1
                else:
                    alias_target_key = aliases.get(normalized_key, "")
                    if alias_target_key:
                        alias_candidates = df_sc[df_sc["join_name_normalized"] == alias_target_key]
                        if expected_signature:
                            alias_candidates = alias_candidates[
                                alias_candidates["team_season_signature"] == expected_signature
                            ]
                        matched_row = pick_single_row(alias_candidates)
                        if matched_row is None and alias_target_key:
                            fallback_alias = df_sc[df_sc["join_name_normalized"] == alias_target_key]
                            if len(fallback_alias) == 1:
                                matched_row = fallback_alias.iloc[0]
                        if matched_row is not None:
                            method = "alias"
                            method_detail = "alias"
                            alias_applied = "yes"
                            alias_target_name = str(matched_row[sc_name_col])
                            alias_count += 1
                        else:
                            unresolved_count += 1
                            alias_applied = "alias_target_not_found"
                            alias_target_name = alias_target_key
                    else:
                        unresolved_count += 1

        join_methods.append(method)
        join_method_details.append(method_detail)
        alias_applied_list.append(alias_applied)
        alias_target_list.append(alias_target_name)
        join_status_list.append("matched" if matched_row is not None else "unmatched")
        matched_sc_rows.append(
            {col: matched_row[col] for col in sc_join_cols} if matched_row is not None else None
        )

    print("\n[4] 結果の組み立て")
    for col in sc_join_cols:
        df_merged_base[col] = [row[col] if row is not None else None for row in matched_sc_rows]

    df_merged_base["join_method"] = join_methods
    df_merged_base["join_method_detail"] = join_method_details
    df_merged_base["join_status"] = join_status_list
    df_merged_base["alias_applied"] = alias_applied_list
    df_merged_base["alias_target"] = alias_target_list

    assert len(df_merged_base) == 647, f"行数が変わっています: {len(df_merged_base)}"
    dup_check = df_merged_base[
        df_merged_base.duplicated(subset=[merged_name_col, "対象年度"], keep=False)
    ]
    print(f"  重複行: {len(dup_check)} (0が正常)")

    print("\n[5] ファイル出力")
    df_merged_base.to_csv(OUTPUT_MERGED, index=False, encoding="utf-8-sig")
    print(f"  修正版 merged CSV: {OUTPUT_MERGED}")

    total = len(df_merged_base)
    matched = total - unresolved_count
    name_only_count = normalized_only_count

    unresolved_rows = df_merged_base[df_merged_base["join_status"] == "unmatched"]
    alias_rows = df_merged_base[df_merged_base["alias_applied"] == "yes"]
    normalized_only_rows = df_merged_base[
        df_merged_base["join_method_detail"] == "normalized_only"
    ]
    canonicalized_rows = df_merged_base[
        df_merged_base["canonicalization_note"].fillna("") != ""
    ]

    report_rows = [
        {"metric": "existing_mapping_count", "value": total, "detail": "既存マッピング件数"},
        {"metric": "position_data_count", "value": len(df_sc), "detail": "SC細分類ポジション集計件数"},
        {
            "metric": "join_key",
            "value": "SC_Name + team_season_signature -> player_name_normalized + team_season_signature",
            "detail": "優先結合キー",
        },
        {"metric": "joined_count", "value": matched, "detail": "結合成功件数"},
        {"metric": "unjoined_count", "value": unresolved_count, "detail": "未結合件数"},
        {"metric": "join_rate_pct", "value": round(matched / total * 100, 1), "detail": "結合成功率 (%)"},
        {"metric": "duplicate_rows", "value": len(dup_check), "detail": "重複行数 (0が正常)"},
        {"metric": "method_composite_exact", "value": composite_exact_count, "detail": "exact + team/season signature 件数"},
        {"metric": "method_composite_normalized", "value": composite_normalized_count, "detail": "normalized + team/season signature 件数"},
        {"metric": "method_normalized_only", "value": normalized_only_count, "detail": "name only fallback 件数"},
        {"metric": "method_alias", "value": alias_count, "detail": "alias match 件数"},
        {"metric": "method_unresolved", "value": unresolved_count, "detail": "unresolved 件数"},
        {"metric": "name_only_count", "value": name_only_count, "detail": "README に明記すべき name only fallback 件数"},
    ]

    for _, row in canonicalized_rows.iterrows():
        report_rows.append(
            {
                "metric": "canonicalized_sc_name",
                "value": row["canonicalization_note"],
                "detail": f"FB_Name={row['FB_Name']}",
            }
        )

    for _, row in normalized_only_rows.iterrows():
        report_rows.append(
            {
                "metric": "normalized_only_match",
                "value": row[merged_name_col],
                "detail": f"FB_Name={row['FB_Name']}, expected_signature={row['expected_team_season_signature']}",
            }
        )

    for _, row in alias_rows.iterrows():
        report_rows.append(
            {
                "metric": "alias_applied",
                "value": f"{row[merged_name_col]} -> {row['alias_target']}",
                "detail": f"FB_Name={row['FB_Name']}",
            }
        )

    for _, row in unresolved_rows.iterrows():
        report_rows.append(
            {
                "metric": "unjoined_player",
                "value": row[merged_name_col],
                "detail": f"FB_Name={row['FB_Name']}, expected_signature={row['expected_team_season_signature']}",
            }
        )

    pd.DataFrame(report_rows).to_csv(OUTPUT_REPORT, index=False, encoding="utf-8-sig")
    print(f"  品質レポート: {OUTPUT_REPORT}")

    print("\n" + "=" * 60)
    print("修正結果サマリー")
    print("=" * 60)
    print(f"  total rows:            {total}")
    print(f"  matched:               {matched}")
    print(f"  unmatched:             {unresolved_count}")
    print(f"  composite_exact:       {composite_exact_count}")
    print(f"  composite_normalized:  {composite_normalized_count}")
    print(f"  normalized_only:       {normalized_only_count}")
    print(f"  alias:                 {alias_count}")
    print(f"  name only fallback:    {name_only_count}")
    print(f"  行数 647 維持:         {'✓' if total == 647 else '✗'}")
    print(f"  重複結合の発生:        {'なし ✓' if len(dup_check) == 0 else f'あり ✗ ({len(dup_check)} 件)'}")

    if not canonicalized_rows.empty:
        print("\n■ canonical 化された名前:")
        for _, row in canonicalized_rows.iterrows():
            print(f"  - {row['canonicalization_note']}")

    print("\n完了！")


if __name__ == "__main__":
    main()
