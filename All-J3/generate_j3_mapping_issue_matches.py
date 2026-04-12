from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parent
J3_DIR = PROJECT_ROOT / "J3_csv"
ISSUES_PATH = J3_DIR / "j3_2024_2025_mapping_issues.csv"
OUTPUT_PATH = J3_DIR / "j3_2024_2025_mapping_issue_name_matches.csv"

BASE_DIR = Path(
    "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ"
)
FB_DIR = BASE_DIR / "football box"
SC_DIR = BASE_DIR / "skill corner"
YEARS = ("2024", "2025")
TARGET_LEAGUE = "J3"
POS_WEIGHT = 2.0

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
    "Player": ["Player", "player_name"],
    "Team": ["Team", "team_name"],
    "Date": ["Date", "match_date"],
    "Position Group": ["Position Group", "position_group"],
    "Minutes": ["Minutes", "minutes_full_all"],
}

POS_GROUP_MAP = {
    "GK": {"Goalkeeper"},
    "DF": {"Central Defender", "Full Back", "Wing Back"},
    "MF": {
        "Midfield",
        "Wide Midfield",
        "Attacking Midfield",
        "Defensive Midfield",
        "Wing Back",
        "Full Back",
        "Wide Attacker",
    },
    "FW": {"Center Forward", "Wide Attacker", "Attacking Midfield"},
}


def normalize_spaces(value: str) -> str:
    return " ".join(str(value).replace("\u3000", " ").split())


def parse_num(value) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return 0.0


def col_idx(ref: str) -> int:
    match = re.match(r"([A-Z]+)", ref)
    n = 0
    for ch in match.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def xlsx_rows(path: Path):
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as zf:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", ns):
                shared_strings.append(
                    "".join((t.text or "") for t in si.iterfind(".//a:t", ns))
                )

        worksheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
        headers = None
        for row in worksheet.findall(".//a:sheetData/a:row", ns):
            values = {}
            for cell in row.findall("a:c", ns):
                idx = col_idx(cell.attrib["r"])
                cell_type = cell.attrib.get("t")
                value = ""
                if cell_type == "inlineStr":
                    inline = cell.find("a:is", ns)
                    if inline is not None:
                        value = "".join(
                            (t.text or "") for t in inline.iterfind(".//a:t", ns)
                        )
                else:
                    v = cell.find("a:v", ns)
                    if v is not None and v.text is not None:
                        value = v.text
                        if cell_type == "s":
                            value = shared_strings[int(value)]
                values[idx] = value

            if headers is None:
                headers = [values.get(i, "") for i in range(max(values) + 1)]
                continue

            if not values:
                continue

            yield {
                headers[i]: values.get(i, "")
                for i in range(len(headers))
                if headers[i]
            }


def load_issues() -> list[dict[str, str]]:
    with ISSUES_PATH.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_fb_players() -> dict[str, dict]:
    players: dict[str, dict] = {}
    for year in YEARS:
        path = FB_DIR / year / TARGET_LEAGUE / "選手データ_基本サマリー_試合別.xlsx"
        for row in xlsx_rows(path):
            name = normalize_spaces(row.get("選手名", ""))
            team = normalize_spaces(row.get("チーム名", ""))
            date = normalize_spaces(row.get("試合日", ""))
            if not name or not team or not date:
                continue

            player = players.setdefault(
                name,
                {
                    "raw_name": row.get("選手名", ""),
                    "apps": {},
                    "teams": Counter(),
                    "pos": Counter(),
                },
            )
            player["apps"][f"{date}|{team}"] = parse_num(row.get("出場時間"))
            player["teams"][f"{year}|{team}"] += 1
            if row.get("Pos"):
                player["pos"][normalize_spaces(row["Pos"])] += 1
    return players


def load_sc_players() -> dict[str, dict]:
    players: dict[str, dict] = {}
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

                    name = normalize_spaces(row["Player"])
                    team_en = normalize_spaces(row["Team"])
                    date = normalize_spaces(row["Date"])
                    if not name or not team_en or not date:
                        continue

                    team_jp = TEAM_NAME_MAP.get(team_en)
                    if not team_jp:
                        continue

                    player = players.setdefault(
                        name,
                        {
                            "raw_name": row["Player"],
                            "apps": {},
                            "teams": Counter(),
                            "pos": Counter(),
                        },
                    )
                    player["apps"][f"{date.replace('-', '')}|{team_jp}"] = parse_num(
                        row["Minutes"]
                    )
                    player["teams"][f"{year}|{team_jp}"] += 1
                    if row["Position Group"]:
                        player["pos"][normalize_spaces(row["Position Group"])] += 1
    return players


def build_team_candidate_map(sc_players: dict[str, dict]) -> dict[str, set[str]]:
    team_to_players: dict[str, set[str]] = defaultdict(set)
    for player_name, player in sc_players.items():
        for year_team in player["teams"]:
            team_to_players[year_team].add(player_name)
    return team_to_players


def pos_match_score(fb_pos: str, sc_pos: str) -> float:
    allowed = POS_GROUP_MAP.get(fb_pos)
    if not allowed or not sc_pos:
        return 0.5
    return 1.0 if sc_pos in allowed else 0.0


def confidence_label(score: float, gap: float) -> str:
    if score >= 85 and gap >= 8:
        return "high"
    if score >= 75 and gap >= 5:
        return "medium"
    return "review"


def rank_candidates(
    fb_name: str,
    fb_players: dict[str, dict],
    sc_players: dict[str, dict],
    team_to_sc_players: dict[str, set[str]],
) -> list[dict[str, object]]:
    fb_player = fb_players[fb_name]
    candidate_names: set[str] = set()
    for year_team in fb_player["teams"]:
        candidate_names |= team_to_sc_players.get(year_team, set())

    ranked = []
    for sc_name in candidate_names:
        sc_player = sc_players[sc_name]

        fb_keys = set(fb_player["apps"])
        sc_keys = set(sc_player["apps"])
        overlap_keys = fb_keys & sc_keys
        union_keys = fb_keys | sc_keys
        if not union_keys:
            continue

        coverage_fb = len(overlap_keys) / len(fb_keys) if fb_keys else 0.0
        coverage_sc = len(overlap_keys) / len(sc_keys) if sc_keys else 0.0
        jaccard = len(overlap_keys) / len(union_keys) if union_keys else 0.0

        minute_similarity = (
            sum(
                1
                - abs(fb_player["apps"][key] - sc_player["apps"][key])
                / max(fb_player["apps"][key], sc_player["apps"][key], 1)
                for key in overlap_keys
            )
            / len(overlap_keys)
            if overlap_keys
            else 0.0
        )

        fb_total = sum(fb_player["apps"].values())
        sc_total = sum(sc_player["apps"].values())
        total_ratio = min(fb_total, sc_total) / max(fb_total, sc_total, 1)

        fb_pos = fb_player["pos"].most_common(1)[0][0] if fb_player["pos"] else ""
        sc_pos = sc_player["pos"].most_common(1)[0][0] if sc_player["pos"] else ""
        pos_score = pos_match_score(fb_pos, sc_pos)

        same_team_ratio = len(set(fb_player["teams"]) & set(sc_player["teams"])) / max(
            len(set(fb_player["teams"]) | set(sc_player["teams"])),
            1,
        )

        score = (
            35 * coverage_fb
            + 20 * coverage_sc
            + 15 * jaccard
            + 15 * minute_similarity
            + 5 * total_ratio
            + POS_WEIGHT * pos_score
            + 5 * same_team_ratio
        )

        ranked.append(
            {
                "score": score,
                "sc_name_normalized": normalize_spaces(sc_player["raw_name"]),
                "sc_name_raw": sc_player["raw_name"],
                "fb_pos": fb_pos,
                "sc_pos": sc_pos,
                "overlap_match_count": len(overlap_keys),
                "fb_match_count": len(fb_keys),
                "sc_match_count": len(sc_keys),
                "minute_similarity": minute_similarity,
                "fb_teams": sorted(fb_player["teams"]),
                "sc_teams": sorted(sc_player["teams"]),
            }
        )

    ranked.sort(key=lambda row: row["score"], reverse=True)
    return ranked


def main() -> None:
    issues = load_issues()
    fb_players = load_fb_players()
    sc_players = load_sc_players()
    team_to_sc_players = build_team_candidate_map(sc_players)

    output_rows = []
    for issue in issues:
        fb_name_normalized = normalize_spaces(issue["FB_Name"])
        ranked = rank_candidates(
            fb_name_normalized,
            fb_players,
            sc_players,
            team_to_sc_players,
        )
        if not ranked:
            output_rows.append(
                {
                    "FB_Name": issue["FB_Name"],
                    "Selected_SC_Name": "",
                    "Confidence": "missing_candidate",
                    "Auto_Score": "",
                    "Gap_to_Second": "",
                    "Issue_SC_Name": normalize_spaces(issue["SC_Name"]),
                    "Top2_SC_Name": "",
                    "FB_Teams": "",
                    "SC_Teams": "",
                    "Overlap_Matches": "",
                    "FB_Match_Count": "",
                    "SC_Match_Count": "",
                    "Minute_Similarity": "",
                    "FB_Pos": issue["FB_Pos"],
                    "SC_Position_Group": "",
                    "Selection_Source": "match_date_vector_low_pos_weight",
                }
            )
            continue

        top1 = ranked[0]
        top2 = ranked[1] if len(ranked) > 1 else None
        gap = top1["score"] - (top2["score"] if top2 else 0.0)
        output_rows.append(
            {
                "FB_Name": issue["FB_Name"],
                "Selected_SC_Name": top1["sc_name_normalized"],
                "Confidence": confidence_label(top1["score"], gap),
                "Auto_Score": f"{top1['score']:.2f}",
                "Gap_to_Second": f"{gap:.2f}",
                "Issue_SC_Name": normalize_spaces(issue["SC_Name"]),
                "Top2_SC_Name": top2["sc_name_normalized"] if top2 else "",
                "FB_Teams": "; ".join(top1["fb_teams"]),
                "SC_Teams": "; ".join(top1["sc_teams"]),
                "Overlap_Matches": str(top1["overlap_match_count"]),
                "FB_Match_Count": str(top1["fb_match_count"]),
                "SC_Match_Count": str(top1["sc_match_count"]),
                "Minute_Similarity": f"{top1['minute_similarity']:.3f}",
                "FB_Pos": top1["fb_pos"] or issue["FB_Pos"],
                "SC_Position_Group": top1["sc_pos"],
                "Selection_Source": "match_date_vector_low_pos_weight",
            }
        )

    fieldnames = [
        "FB_Name",
        "Selected_SC_Name",
        "Confidence",
        "Auto_Score",
        "Gap_to_Second",
        "Issue_SC_Name",
        "Top2_SC_Name",
        "FB_Teams",
        "SC_Teams",
        "Overlap_Matches",
        "FB_Match_Count",
        "SC_Match_Count",
        "Minute_Similarity",
        "FB_Pos",
        "SC_Position_Group",
        "Selection_Source",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    confidence_counts = Counter(row["Confidence"] for row in output_rows)
    print(f"wrote: {OUTPUT_PATH}")
    print(f"rows: {len(output_rows)}")
    print(f"confidence: {dict(confidence_counts)}")


if __name__ == "__main__":
    main()
