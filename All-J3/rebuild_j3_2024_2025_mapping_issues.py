from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from generate_j3_mapping_issue_matches import (
    load_fb_players,
    load_sc_players,
    normalize_spaces,
)


PROJECT_ROOT = Path(__file__).resolve().parent
J3_DIR = PROJECT_ROOT / "J3_csv"
VALID_PATH = J3_DIR / "j3_2024_2025_valid_name_mapping.csv"
OUTPUT_PATH = J3_DIR / "j3_2024_2025_mapping_issues.csv"

FIELDNAMES = [
    "Issue_Type",
    "Name_Type",
    "Unmatched_Name",
    "Source_Data",
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

MAPPING_SOURCE = "valid_mapping_unmatched_list"
MIN_MINUTES_THRESHOLD = 300.0


def load_valid_name_sets() -> tuple[set[str], set[str]]:
    with VALID_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    valid_fb = {
        normalize_spaces(row.get("FB_Name", ""))
        for row in rows
        if normalize_spaces(row.get("FB_Name", ""))
    }
    valid_sc = {
        normalize_spaces(row.get("SC_Name", ""))
        for row in rows
        if normalize_spaces(row.get("SC_Name", ""))
    }
    return valid_fb, valid_sc


def fb_issue_rows(valid_fb_names: set[str]) -> list[dict[str, object]]:
    fb_players = load_fb_players()
    rows: list[dict[str, object]] = []
    for normalized_name, player in fb_players.items():
        if normalized_name in valid_fb_names:
            continue
        fb_pos = player["pos"].most_common(1)[0][0] if player["pos"] else ""
        if fb_pos == "GK":
            continue
        fb_minutes = round(sum(player["apps"].values()), 2)
        if fb_minutes < MIN_MINUTES_THRESHOLD:
            continue
        rows.append(
            {
                "Issue_Type": "fb_unmatched",
                "Name_Type": "漢字名",
                "Unmatched_Name": player["raw_name"],
                "Source_Data": "football box",
                "FB_Name": player["raw_name"],
                "FB_Pos": fb_pos,
                "FB_Minutes": fb_minutes,
                "SC_Name": "",
                "SC_Position_Group": "",
                "SC_Minutes": "",
                "Mapping_Source": MAPPING_SOURCE,
                "Top_Score": "",
                "Gap_to_Second": "",
                "Name_Score": "",
                "Vector_Score": "",
                "Minutes_Score": "",
                "Candidate_Count": "",
                "Notes": "football box 側のみ未マッチ",
            }
        )
    rows.sort(key=lambda row: (-float(row["FB_Minutes"]), normalize_spaces(row["FB_Name"])))
    return rows


def sc_issue_rows(valid_sc_names: set[str]) -> list[dict[str, object]]:
    sc_players = load_sc_players()
    rows: list[dict[str, object]] = []
    for normalized_name, player in sc_players.items():
        if normalized_name in valid_sc_names:
            continue
        sc_pos = player["pos"].most_common(1)[0][0] if player["pos"] else ""
        if sc_pos == "Goalkeeper":
            continue
        sc_minutes = round(sum(player["apps"].values()), 2)
        if sc_minutes < MIN_MINUTES_THRESHOLD:
            continue
        rows.append(
            {
                "Issue_Type": "sc_unmatched",
                "Name_Type": "ローマ字名",
                "Unmatched_Name": player["raw_name"],
                "Source_Data": "skill corner",
                "FB_Name": "",
                "FB_Pos": "",
                "FB_Minutes": "",
                "SC_Name": player["raw_name"],
                "SC_Position_Group": sc_pos,
                "SC_Minutes": sc_minutes,
                "Mapping_Source": MAPPING_SOURCE,
                "Top_Score": "",
                "Gap_to_Second": "",
                "Name_Score": "",
                "Vector_Score": "",
                "Minutes_Score": "",
                "Candidate_Count": "",
                "Notes": "skill corner 側のみ未マッチ",
            }
        )
    rows.sort(key=lambda row: (-float(row["SC_Minutes"]), normalize_spaces(row["SC_Name"])))
    return rows


def main() -> None:
    valid_fb_names, valid_sc_names = load_valid_name_sets()
    output_rows = [*fb_issue_rows(valid_fb_names), *sc_issue_rows(valid_sc_names)]

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(output_rows)

    counts = Counter(row["Issue_Type"] for row in output_rows)
    print(f"wrote: {OUTPUT_PATH}")
    print(f"rows: {len(output_rows)}")
    print(f"fb_unmatched: {counts['fb_unmatched']}")
    print(f"sc_unmatched: {counts['sc_unmatched']}")


if __name__ == "__main__":
    main()
