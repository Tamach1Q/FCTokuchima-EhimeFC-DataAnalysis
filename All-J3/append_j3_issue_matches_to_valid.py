from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from generate_j3_mapping_issue_matches import (
    FB_DIR,
    SC_COLUMN_ALIASES,
    SC_DIR,
    TARGET_LEAGUE,
    TEAM_NAME_MAP,
    YEARS,
    normalize_spaces,
    parse_num,
    xlsx_rows,
)

TODAY = "2026-04-09"
ISSUE_MATCHES_PATH = (
    Path(__file__).resolve().parent / "J3_csv" / "j3_2024_2025_mapping_issue_name_matches.csv"
)
VALID_PATH = (
    Path(__file__).resolve().parent / "J3_csv" / "j3_2024_2025_valid_name_mapping.csv"
)

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


def load_confirmed_matches() -> list[dict[str, str]]:
    with ISSUE_MATCHES_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def aggregate_fb(match_lookup: dict[str, dict[str, str]]) -> dict[str, dict]:
    fb_target_set = set(match_lookup)
    fb_agg = {name: {"選手名": match_lookup[name]["FB_Name"]} for name in fb_target_set}
    fb_pos_counter = {name: Counter() for name in fb_target_set}
    fb_mean_sums = {name: defaultdict(float) for name in fb_target_set}
    fb_mean_counts = {name: defaultdict(int) for name in fb_target_set}

    for year in YEARS:
        for path in sorted((FB_DIR / year / TARGET_LEAGUE).glob("*.xlsx")):
            rows = list(xlsx_rows(path))
            if not rows:
                continue

            cols = set(rows[0].keys())
            sum_cols = [c for c in FB_SUM_VARS if c in cols]
            mean_cols = [c for c in FB_MEAN_VARS if c in cols]
            has_minutes = "出場時間" in cols
            has_pos = "Pos" in cols

            for row in rows:
                name = normalize_spaces(row.get("選手名", ""))
                if name not in fb_target_set:
                    continue

                if has_pos and row.get("Pos"):
                    fb_pos_counter[name][normalize_spaces(row["Pos"])] += 1
                if has_minutes:
                    fb_agg[name]["出場時間"] = fb_agg[name].get("出場時間", 0.0) + parse_num(
                        row.get("出場時間")
                    )
                for col in sum_cols:
                    fb_agg[name][col] = fb_agg[name].get(col, 0.0) + parse_num(row.get(col))
                for col in mean_cols:
                    fb_mean_sums[name][col] += parse_num(row.get(col))
                    fb_mean_counts[name][col] += 1

    for name in fb_target_set:
        fb_agg[name]["ポジション"] = (
            fb_pos_counter[name].most_common(1)[0][0] if fb_pos_counter[name] else ""
        )
        for col in FB_MEAN_VARS:
            count = fb_mean_counts[name][col]
            fb_agg[name][col] = fb_mean_sums[name][col] / count if count else 0.0
        minutes = fb_agg[name].get("出場時間", 0.0)
        for col in FB_SUM_VARS:
            fb_agg[name].setdefault(col, 0.0)
            fb_agg[name][f"{col}_per90"] = (
                fb_agg[name][col] / minutes * 90 if minutes > 0 else 0.0
            )

    return fb_agg


def aggregate_sc(match_lookup: dict[str, dict[str, str]]) -> dict[str, dict]:
    sc_target_set = set(match_lookup)
    sc_player_rows = defaultdict(list)
    sc_raw_name_variants = defaultdict(set)

    for year in YEARS:
        for path in sorted((SC_DIR / year / TARGET_LEAGUE).glob("*.csv")):
            with path.open(encoding="utf-8-sig", newline="") as f:
                for raw in csv.DictReader(f):
                    row = {}
                    for canonical, aliases in SC_COLUMN_ALIASES.items():
                        row[canonical] = next(
                            (
                                raw[a]
                                for a in aliases
                                if a in raw and raw[a] not in (None, "")
                            ),
                            "",
                        )
                    player_name = normalize_spaces(row["Player"])
                    if player_name not in sc_target_set:
                        continue
                    row["season"] = year
                    sc_player_rows[player_name].append(row)
                    sc_raw_name_variants[player_name].add(row["Player"])

    sc_meta = {}
    for player_name, rows in sc_player_rows.items():
        meta = {
            "Player": match_lookup[player_name]["Selected_SC_Name"],
            "Minutes": 0.0,
            "Minutes TIP": 0.0,
            "Minutes OTIP": 0.0,
            "PSV-99": 0.0,
            "_raw_variants": sorted(sc_raw_name_variants[player_name]),
        }
        pos_counter = Counter()
        mmin_vals = []
        mmin_otip_vals = []
        for row in rows:
            mins = parse_num(row["Minutes"])
            meta["Minutes"] += mins
            meta["Minutes TIP"] += parse_num(row.get("Minutes TIP"))
            meta["Minutes OTIP"] += parse_num(row.get("Minutes OTIP"))
            mmin_vals.append(parse_num(row.get("M/min")))
            mmin_otip_vals.append(parse_num(row.get("M/min OTIP")))
            meta["PSV-99"] = max(meta["PSV-99"], parse_num(row.get("PSV-99")))
            pos = normalize_spaces(row.get("Position Group", ""))
            if pos:
                pos_counter[pos] += 1
            for col in SC_SUM_VARS_TIP + SC_SUM_VARS_OTIP + SC_SUM_VARS_ALL:
                meta[col] = meta.get(col, 0.0) + parse_num(row.get(col))

        meta["Position Group"] = pos_counter.most_common(1)[0][0] if pos_counter else ""
        meta["M/min"] = sum(mmin_vals) / len(mmin_vals) if mmin_vals else 0.0
        meta["M/min OTIP"] = (
            sum(mmin_otip_vals) / len(mmin_otip_vals) if mmin_otip_vals else 0.0
        )
        for col in SC_SUM_VARS_TIP:
            meta[f"{col}_per90"] = (
                meta[col] / meta["Minutes TIP"] * 90 if meta["Minutes TIP"] > 0 else 0.0
            )
        for col in SC_SUM_VARS_OTIP:
            meta[f"{col}_per90"] = (
                meta[col] / meta["Minutes OTIP"] * 90
                if meta["Minutes OTIP"] > 0
                else 0.0
            )
        for col in SC_SUM_VARS_ALL:
            meta[f"{col}_per90"] = (
                meta[col] / meta["Minutes"] * 90 if meta["Minutes"] > 0 else 0.0
            )
        sc_meta[player_name] = meta

    return sc_meta


def main() -> None:
    confirmed_rows = load_confirmed_matches()
    fb_match_lookup = {
        normalize_spaces(row["FB_Name"]): row for row in confirmed_rows if row["Selected_SC_Name"]
    }
    sc_match_lookup = {
        normalize_spaces(row["Selected_SC_Name"]): row
        for row in confirmed_rows
        if row["Selected_SC_Name"]
    }

    fb_agg = aggregate_fb(fb_match_lookup)
    sc_meta = aggregate_sc(sc_match_lookup)

    with VALID_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        valid_header = reader.fieldnames
        valid_rows = list(reader)

    existing_fb = {normalize_spaces(row["FB_Name"]) for row in valid_rows}
    existing_sc = {normalize_spaces(row["SC_Name"]) for row in valid_rows}

    append_rows = []
    for confirmed in confirmed_rows:
        fb_name_raw = confirmed["FB_Name"]
        sc_name_raw = confirmed["Selected_SC_Name"]
        fb_key = normalize_spaces(fb_name_raw)
        sc_key = normalize_spaces(sc_name_raw)

        if fb_key in existing_fb:
            raise RuntimeError(f"FB_Name already exists in valid mapping: {fb_name_raw}")
        if sc_key in existing_sc:
            raise RuntimeError(f"SC_Name already exists in valid mapping: {sc_name_raw}")
        if fb_key not in fb_agg:
            raise RuntimeError(f"FB aggregate not found: {fb_name_raw}")
        if sc_key not in sc_meta:
            raise RuntimeError(f"SC aggregate not found: {sc_name_raw}")

        fb_row = fb_agg[fb_key]
        sc_row = sc_meta[sc_key]

        output = {col: "" for col in valid_header}
        output["対象年度"] = "2024-2025"
        output["対象リーグ"] = TARGET_LEAGUE
        output["FB_Name"] = fb_name_raw
        output["SC_Name"] = sc_name_raw
        output["FB_Pos"] = fb_row.get("ポジション", confirmed.get("FB_Pos", ""))
        output["SC_Position_Group"] = sc_row.get("Position Group", "")
        output["FB_Minutes"] = fb_row.get("出場時間", 0.0)
        output["SC_Minutes"] = sc_row.get("Minutes", 0.0)
        output["Mapping_Source"] = "manual_j3_issue_confirmed"
        output["Top_Score"] = confirmed.get("Auto_Score", "")
        output["Gap_to_Second"] = confirmed.get("Gap_to_Second", "")

        notes = [
            f"j3_2024_2025_mapping_issue_name_matches 手動確定 ({TODAY})",
            f"confidence={confirmed.get('Confidence', '')}",
        ]
        if confirmed.get("Issue_SC_Name"):
            notes.append(f"issues元候補: {confirmed['Issue_SC_Name']}")
        raw_variants = [normalize_spaces(v) for v in sc_row.get("_raw_variants", [])]
        raw_variants = sorted({v for v in raw_variants if v and v != sc_name_raw})
        if raw_variants:
            notes.append(f"SC元データ名: {' / '.join(raw_variants)}")
        output["Notes"] = "; ".join(notes)

        for col in valid_header:
            if col in fb_row:
                output[col] = fb_row[col]
            if col in sc_row:
                output[col] = sc_row[col]

        output["選手名"] = fb_name_raw
        output["出場時間"] = fb_row.get("出場時間", 0.0)
        output["ポジション"] = fb_row.get("ポジション", output["FB_Pos"])
        output["Player"] = sc_name_raw
        output["Minutes"] = sc_row.get("Minutes", 0.0)
        output["Minutes TIP"] = sc_row.get("Minutes TIP", 0.0)
        output["Minutes OTIP"] = sc_row.get("Minutes OTIP", 0.0)
        output["M/min"] = sc_row.get("M/min", 0.0)
        output["M/min OTIP"] = sc_row.get("M/min OTIP", 0.0)
        output["PSV-99"] = sc_row.get("PSV-99", 0.0)

        for col in FB_SUM_VARS + FB_MEAN_VARS + [f"{c}_per90" for c in FB_SUM_VARS]:
            if col in output:
                output[col] = fb_row.get(col, 0.0)
        for col in SC_SUM_VARS_TIP + SC_SUM_VARS_OTIP + SC_SUM_VARS_ALL + [
            f"{c}_per90" for c in SC_SUM_VARS_TIP + SC_SUM_VARS_OTIP + SC_SUM_VARS_ALL
        ]:
            if col in output:
                output[col] = sc_row.get(col, 0.0)

        append_rows.append(output)

    all_rows = valid_rows + append_rows
    with VALID_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=valid_header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"appended: {len(append_rows)}")
    print(f"valid_rows_after: {len(all_rows)}")


if __name__ == "__main__":
    main()
