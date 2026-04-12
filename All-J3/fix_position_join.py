"""
SkillCorner ポジションjoin 改善スクリプト
==========================================

目的:
  現在の j3_2024_2025_valid_name_mapping_with_positions.csv で
  未結合の22件を、名前正規化 + alias対応で改善する。

改善方法:
  1. 両テーブルの名前列を正規化 (NFKC, 空白圧縮, casefold等)
  2. 正規化済みキーで再join
  3. それでも残るものはalias mapで対応
  4. join_method を exact / normalized / alias / unresolved で区別

制約:
  - 行数647は絶対に増やさない
  - 1選手1行を壊さない
  - 安全でないfuzzy matchはしない
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# パス設定
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "J3_csv"

# 入力ファイル
VALID_MAPPING_FILE = CSV_DIR / "j3_2024_2025_valid_name_mapping.csv"
SC_POSITIONS_FILE = CSV_DIR / "sc_detailed_positions_2024_2025.csv"

# 出力ファイル
OUTPUT_MERGED = CSV_DIR / "j3_2024_2025_valid_name_mapping_with_positions.csv"
OUTPUT_REPORT = CSV_DIR / "sc_position_join_quality_report.csv"
ALIAS_MAP_FILE = CSV_DIR / "sc_name_alias_map.csv"

# ---------------------------------------------------------------------------
# 名前正規化関数
# ---------------------------------------------------------------------------
def normalize_name(name: str) -> str:
    """
    名前を正規化して比較用キーを生成する。
    
    処理内容:
    - Unicode NFKC 正規化
    - 先頭末尾の空白削除
    - 全角空白を半角空白に変換
    - 改行・タブを空白扱いにして除去
    - 連続する空白を1個に圧縮
    - ハイフン類を '-' に統一
    - casefold で大文字小文字の差を吸収
    """
    if pd.isna(name) or not isinstance(name, str):
        return ""
    
    # 1. Unicode NFKC 正規化
    s = unicodedata.normalize("NFKC", name)
    
    # 2. 改行・タブを空白に変換
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    
    # 3. 全角空白を半角空白に変換
    s = s.replace("\u3000", " ")
    
    # 4. ハイフン類を統一 (EN DASH, EM DASH, MINUS, etc.)
    s = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uff0d]", "-", s)
    
    # 5. 連続する空白を1個に圧縮
    s = re.sub(r"\s+", " ", s)
    
    # 6. 先頭末尾の空白削除
    s = s.strip()
    
    # 7. casefold で大文字小文字の差を吸収
    s = s.casefold()
    
    return s


# ---------------------------------------------------------------------------
# Alias マップの定義と保存
# ---------------------------------------------------------------------------
def build_alias_map() -> dict[str, str]:
    """
    merged側(SC_Name) → SC細分類側(player_name_raw_skillcorner) のaliasマップ。
    
    これは正規化後も一致しない名前差異を解消するためのもの。
    すべて実データで同一人物であることを確認済みのペアのみ。
    """
    aliases = {
        # merged側のSC_Name (正規化前) → SC細分類側のplayer_name_raw_skillcorner (正規化前)
        # の対応。正規化後のキーで適用するため、値も正規化して比較する。
        
        # 1. Rensuke Kawana → Rennosuke Kawana
        #    理由: mapping_issues に "SC元データ名: Rennosuke Kawana" と記載あり。
        #    川名連介 = Rensuke/Rennosuke は同一人物。
        "rensuke kawana": "rennosuke kawana",
        
        # 2. In Ju Mun → In-Ju Mun  
        #    理由: ハイフンありの In-Ju Mun が正規化で in-ju mun になるが、
        #    merged側の In Ju Mun は in ju mun になる。
        #    文仁柱 = In Ju Mun / In-Ju Mun は同一人物。
        "in ju mun": "in-ju mun",
        
        # 3. Joao → Joao Vitor Gaudencio Nunes
        #    理由: ジョアオ = Joao で、SC細分類側は Joao Vitor Gaudencio Nunes。
        #    J3に他のJoaoはいない（一意に特定可能）。
        "joao": "joao vitor gaudencio nunes",
        
        # 4. Justin Toshiki Kinjo → Justin Kinjo
        #    理由: 金城ジャスティン俊樹 = Justin Toshiki Kinjo / Justin Kinjo は同一人物。
        #    SC細分類側では Justin Kinjo で登録。
        "justin toshiki kinjo": "justin kinjo",
        
        # 5. Thales → Thales Procopio Castro de Paula
        #    理由: ターレス = Thales で、SC細分類側はフルネーム。
        #    J3に他のThalesはいない（一意に特定可能）。
        "thales": "thales procopio castro de paula",
        
        # 6. Haru Kano → Haru Kano Haru Kano
        #    理由: SC細分類側でデータ汚れにより名前が重複。
        #    加納大 = Haru Kano で、SC側に他のKanoはいない。
        #    SC元データの player_name_raw_skillcorner が "Haru Kano Haru Kano"。
        #    Position Group = Center Forward で一致。一意に特定可能。
        "haru kano": "haru kano haru kano",
        
        # 7. Yoshihito Kondo → Yoshihito  Kondo
        #    理由: mapping_issues に "SC元データ名: Yoshihito  Kondo" と記載。
        #    ただしこれは空白2連続なので正規化で解消される「はず」だが、
        #    念のため alias にも登録しておく。
        # → 正規化で解消されるため alias は不要。
        #   (正規化後は両方 "yoshihito kondo" になる)
        
        # 8. Toya Izumi → Toya  Izumi
        #    理由: SC側に "Toya  Izumi" (空白2つ) が存在。
        #    泉柊椰 = Toya Izumi で、SC_PosGroup = Full Back で一致。
        # → 正規化で解消されるため alias は不要。
    }
    
    return aliases


def save_alias_map(aliases: dict[str, str], filepath: Path) -> None:
    """aliasマップをCSVとして保存する。"""
    rows = []
    # 説明コメントを付与
    descriptions = {
        "rensuke kawana": "川名連介: Rensuke/Rennosuke の表記揺れ",
        "in ju mun": "文仁柱: ハイフン有無の差",
        "joao": "ジョアオ: 短縮名 → フルネーム",
        "justin toshiki kinjo": "金城ジャスティン俊樹: ミドルネーム有無",
        "thales": "ターレス: 短縮名 → フルネーム",
        "haru kano": "加納大: SC側データ汚れ (名前重複)",
    }
    
    for merged_name, sc_name in aliases.items():
        rows.append({
            "merged_name_normalized": merged_name,
            "sc_name_normalized": sc_name,
            "description": descriptions.get(merged_name, ""),
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"  aliasマップ保存: {filepath} ({len(df)} 件)")


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("SkillCorner ポジションjoin 改善スクリプト")
    print("=" * 60)
    
    # ----- 1. データ読み込み -----
    print("\n[1] データ読み込み")
    
    df_merged_base = pd.read_csv(VALID_MAPPING_FILE, encoding="utf-8-sig")
    print(f"  merged base (valid_name_mapping): {len(df_merged_base)} rows")
    assert len(df_merged_base) == 647, f"行数が647ではありません: {len(df_merged_base)}"
    
    df_sc = pd.read_csv(SC_POSITIONS_FILE, encoding="utf-8-sig")
    print(f"  SC positions: {len(df_sc)} rows")
    
    # 列名の確認
    # merged側のjoinキー: SC_Name
    # SC側のjoinキー: player_name_raw_skillcorner
    merged_name_col = "SC_Name"
    sc_name_col = "player_name_raw_skillcorner"
    
    print(f"  merged側 joinキー列: {merged_name_col}")
    print(f"  SC側 joinキー列: {sc_name_col}")
    
    # SC側のposition関連列を特定
    sc_pos_cols = [c for c in df_sc.columns if c != sc_name_col]
    # player_name_normalized と season_scope は結合時に除外(merged側と重複の可能性)
    sc_join_cols = [c for c in sc_pos_cols 
                    if c not in ("player_name_normalized", "season_scope")]
    print(f"  SC側から結合する列数: {len(sc_join_cols)}")
    
    # ----- 2. 正規化キーの生成 -----
    print("\n[2] 正規化キーの生成")
    
    df_merged_base["join_name_normalized"] = df_merged_base[merged_name_col].apply(normalize_name)
    df_sc["join_name_normalized"] = df_sc[sc_name_col].apply(normalize_name)
    
    # 正規化前の名前も保持
    df_merged_base["raw_name_original"] = df_merged_base[merged_name_col]
    
    # 正規化キーの重複チェック (SC側)
    sc_dup = df_sc[df_sc.duplicated(subset=["join_name_normalized"], keep=False)]
    if len(sc_dup) > 0:
        print(f"  [WARNING] SC側に正規化後の重複あり: {len(sc_dup)} rows")
        for name in sc_dup["join_name_normalized"].unique():
            print(f"    - {name}")
    else:
        print(f"  SC側の正規化キー重複: なし ✓")
    
    # SC側の正規化キー辞書を構築 (正規化キー → 元行)
    sc_lookup = {}
    for idx, row in df_sc.iterrows():
        nk = row["join_name_normalized"]
        if nk and nk not in sc_lookup:
            sc_lookup[nk] = row
    print(f"  SC lookup辞書サイズ: {len(sc_lookup)}")
    
    # ----- 3. alias マップの構築 -----
    print("\n[3] alias マップの構築")
    
    aliases = build_alias_map()
    save_alias_map(aliases, ALIAS_MAP_FILE)
    
    # ----- 4. 3段階 join の実行 -----
    print("\n[4] 3段階 join の実行")
    
    # 結果を格納するリスト
    join_methods: list[str] = []
    alias_applied_list: list[str] = []
    alias_target_list: list[str] = []
    join_status_list: list[str] = []
    matched_sc_rows: list[dict | None] = []
    
    exact_count = 0
    normalized_count = 0
    alias_count = 0
    unresolved_count = 0
    
    for idx, row in df_merged_base.iterrows():
        original_name = row[merged_name_col]
        normalized_key = row["join_name_normalized"]
        
        matched_row = None
        method = "unresolved"
        alias_applied = ""
        alias_target_name = ""
        
        # Step 1: exact match (元の名前そのまま)
        exact_match = df_sc[df_sc[sc_name_col] == original_name]
        if len(exact_match) == 1:
            matched_row = exact_match.iloc[0]
            method = "exact"
            exact_count += 1
        elif len(exact_match) > 1:
            # 複数一致 → 最初のものを使用 (通常ありえない)
            matched_row = exact_match.iloc[0]
            method = "exact"
            exact_count += 1
        else:
            # Step 2: normalized match
            if normalized_key in sc_lookup:
                matched_row = sc_lookup[normalized_key]
                method = "normalized"
                normalized_count += 1
            else:
                # Step 3: alias match
                if normalized_key in aliases:
                    alias_target_normalized = aliases[normalized_key]
                    if alias_target_normalized in sc_lookup:
                        matched_row = sc_lookup[alias_target_normalized]
                        method = "alias"
                        alias_applied = "yes"
                        alias_target_name = str(matched_row[sc_name_col])
                        alias_count += 1
                    else:
                        # alias先が見つからない
                        method = "unresolved"
                        unresolved_count += 1
                        alias_applied = "alias_target_not_found"
                        alias_target_name = alias_target_normalized
                else:
                    method = "unresolved"
                    unresolved_count += 1
        
        join_methods.append(method)
        alias_applied_list.append(alias_applied)
        alias_target_list.append(alias_target_name)
        join_status_list.append("matched" if matched_row is not None else "unmatched")
        matched_sc_rows.append(
            {c: matched_row[c] for c in sc_join_cols} if matched_row is not None else None
        )
    
    # ----- 5. 結果の組み立て -----
    print("\n[5] 結果の組み立て")
    
    # SC列を追加
    for col in sc_join_cols:
        df_merged_base[col] = [
            r[col] if r is not None else None for r in matched_sc_rows
        ]
    
    # メタ列を追加
    df_merged_base["join_method"] = join_methods
    df_merged_base["join_status"] = join_status_list
    df_merged_base["alias_applied"] = alias_applied_list
    df_merged_base["alias_target"] = alias_target_list
    
    # 行数チェック
    assert len(df_merged_base) == 647, f"行数が変わっています: {len(df_merged_base)}"
    
    # 重複チェック
    dup_check = df_merged_base[df_merged_base.duplicated(subset=[merged_name_col, "対象年度"], keep=False)]
    print(f"  重複行: {len(dup_check)} (0が正常)")
    
    # ----- 6. 出力 -----
    print("\n[6] ファイル出力")
    
    # merged CSV 出力
    df_merged_base.to_csv(OUTPUT_MERGED, index=False, encoding="utf-8-sig")
    print(f"  修正版 merged CSV: {OUTPUT_MERGED}")
    print(f"  行数: {len(df_merged_base)}")
    
    # ----- 7. 品質レポート生成 -----
    print("\n[7] 品質レポート生成")
    
    total = len(df_merged_base)
    matched = total - unresolved_count
    
    report_rows = [
        {"metric": "existing_mapping_count", "value": total, "detail": "既存マッピング件数"},
        {"metric": "position_data_count", "value": len(df_sc), "detail": "SC細分類ポジション集計件数"},
        {"metric": "join_key", "value": f"{merged_name_col} → {sc_name_col}", "detail": "使用した結合キー"},
        {"metric": "joined_count", "value": matched, "detail": "結合成功件数"},
        {"metric": "unjoined_count", "value": unresolved_count, "detail": "未結合件数"},
        {"metric": "join_rate_pct", "value": round(matched / total * 100, 1), "detail": "結合成功率 (%)"},
        {"metric": "duplicate_rows", "value": len(dup_check), "detail": "重複行数 (0が正常)"},
        {"metric": "method_exact", "value": exact_count, "detail": "exact match 件数"},
        {"metric": "method_normalized", "value": normalized_count, "detail": "normalized match 件数 (空白正規化で救済)"},
        {"metric": "method_alias", "value": alias_count, "detail": "alias match 件数"},
        {"metric": "method_unresolved", "value": unresolved_count, "detail": "unresolved 件数"},
    ]
    
    # 未結合一覧
    unresolved_rows = df_merged_base[df_merged_base["join_status"] == "unmatched"]
    for _, urow in unresolved_rows.iterrows():
        report_rows.append({
            "metric": "unjoined_player",
            "value": urow[merged_name_col],
            "detail": f"FB_Name={urow['FB_Name']}, SC_PosGroup={urow['SC_Position_Group']}",
        })
    
    # alias適用一覧
    alias_rows = df_merged_base[df_merged_base["alias_applied"] == "yes"]
    for _, arow in alias_rows.iterrows():
        report_rows.append({
            "metric": "alias_applied",
            "value": f"{arow[merged_name_col]} → {arow['alias_target']}",
            "detail": f"FB_Name={arow['FB_Name']}",
        })
    
    # normalized match 一覧
    norm_rows = df_merged_base[df_merged_base["join_method"] == "normalized"]
    for _, nrow in norm_rows.iterrows():
        report_rows.append({
            "metric": "normalized_match",
            "value": nrow[merged_name_col],
            "detail": f"FB_Name={nrow['FB_Name']}, 正規化キー={nrow['join_name_normalized']}",
        })
    
    report_df = pd.DataFrame(report_rows)
    report_df.to_csv(OUTPUT_REPORT, index=False, encoding="utf-8-sig")
    print(f"  品質レポート: {OUTPUT_REPORT}")
    
    # ----- 8. サマリー出力 -----
    print("\n" + "=" * 60)
    print("修正結果サマリー")
    print("=" * 60)
    
    print(f"\n■ 修正前の件数:")
    print(f"  total rows:  647")
    print(f"  matched:     625")
    print(f"  unmatched:   22")
    
    print(f"\n■ 修正後の件数:")
    print(f"  total rows:  {total}")
    print(f"  matched:     {matched}")
    print(f"  unmatched:   {unresolved_count}")
    
    print(f"\n■ join_method 別件数:")
    print(f"  exact:       {exact_count}")
    print(f"  normalized:  {normalized_count}")
    print(f"  alias:       {alias_count}")
    print(f"  unresolved:  {unresolved_count}")
    
    print(f"\n■ 空白正規化だけで救済できた件数: {normalized_count}")
    print(f"■ alias で救済できた件数: {alias_count}")
    print(f"■ 重複結合の発生: {'なし ✓' if len(dup_check) == 0 else f'あり ✗ ({len(dup_check)} 件)'}")
    print(f"■ 行数 647 維持: {'✓' if total == 647 else '✗'}")
    
    if unresolved_count > 0:
        print(f"\n■ 未結合の残件一覧 ({unresolved_count} 件):")
        for _, urow in unresolved_rows.iterrows():
            print(f"  - {urow[merged_name_col]} (FB: {urow['FB_Name']}, PG: {urow['SC_Position_Group']})")
    
    if alias_count > 0:
        print(f"\n■ alias を適用した一覧 ({alias_count} 件):")
        for _, arow in alias_rows.iterrows():
            print(f"  - {arow[merged_name_col]} → {arow['alias_target']}")
    
    if normalized_count > 0:
        print(f"\n■ 正規化で救済した一覧 ({normalized_count} 件):")
        for _, nrow in norm_rows.iterrows():
            print(f"  - {nrow[merged_name_col]} (正規化キー: {nrow['join_name_normalized']})")
    
    print("\n完了！")


if __name__ == "__main__":
    main()
