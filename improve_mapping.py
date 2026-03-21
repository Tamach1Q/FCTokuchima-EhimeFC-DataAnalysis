from __future__ import annotations

import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import pykakasi


SC_UNIQUE_PATH = Path("sc_unique_players.csv")
FB_UNIQUE_PATH = Path("fb_unique_players.csv")
SC_DATA_DIR = Path("生データ/skill corner")
FB_DATA_DIR = Path("生データ/football box")
MAPPING_OUTPUT_PATH = Path("cf_name_mapping.csv")
DETAIL_OUTPUT_PATH = Path("cf_name_mapping_fixed.csv")
SIMILARITY_THRESHOLD = 80


# Skill Corner の英語表記を Football Box 側のチーム名へ寄せる変換マスタ
TEAM_MAPPING = {
    "AC Parceiro Nagano": "長野",
    "AFC Blaublitz Akita": "秋田",
    "Albirex Niigata": "新潟",
    "Avispa Fukuoka": "福岡",
    "Cerezo Osaka": "C大阪",
    "Ehime FC": "愛媛",
    "FC Azul Claro Numazu": "沼津",
    "FC Gifu": "岐阜",
    "FC Imabari": "今治",
    "FC Machida Zelvia": "町田",
    "FC Osaka": "FC大阪",
    "FC Ryūkyū": "琉球",
    "FC Tokyo": "FC東京",
    "Fagiano Okayama": "岡山",
    "Fujieda MYFC": "藤枝",
    "Fukushima United FC": "福島",
    "Gainare Tottori": "鳥取",
    "Gamba Osaka": "G大阪",
    "Giravanz Kitakyushu": "北九州",
    "Hokkaido Consadole Sapporo": "札幌",
    "Ishikawa FC Zweigen Kanazawa": "金沢",
    "Iwaki SC": "いわき",
    "JEF United Ichihara Chiba": "千葉",
    "Jubilo Iwata": "磐田",
    "Kagoshima United FC": "鹿児島",
    "Kamatamare Sanuki": "讃岐",
    "Kashima Antlers": "鹿島",
    "Kashiwa Reysol": "柏",
    "Kataller Toyama": "富山",
    "Kawasaki Frontale": "川崎F",
    "Kochi United SC": "高知",
    "Kyoto Sanga FC": "京都",
    "MIO Biwako Shiga": "滋賀",
    "Matsumoto Yamaga FC": "松本",
    "Mito Hollyhock": "水戸",
    "Montedio Yamagata": "山形",
    "Nagoya Grampus": "名古屋",
    "Nara Club": "奈良",
    "Oita Trinita": "大分",
    "Omiya Ardija": "大宮",
    "Reilac Shiga FC": "滋賀",
    "Renofa Yamaguchi": "山口",
    "Roasso Kumamoto": "熊本",
    "SC Sagamihara": "相模原",
    "Sagan Tosu": "鳥栖",
    "Sanfrecce Hiroshima": "広島",
    "Shimizu S-Pulse": "清水",
    "Shonan Bellmare": "湘南",
    "Tegevajaro Miyazaki FC": "宮崎",
    "ThespaKusatsu Gunma": "群馬",
    "Tochigi City": "栃木C",
    "Tochigi SC": "栃木SC",
    "Tokushima Vortis": "徳島",
    "Tokyo Verdy": "東京V",
    "Urawa Red Diamonds": "浦和",
    "V-Varen Nagasaki": "長崎",
    "Vanraure Hachinohe": "八戸",
    "Vegalta Sendai": "仙台",
    "Ventforet Kofu": "甲府",
    "Vissel Kobe": "神戸",
    "Yokohama F. Marinos": "横浜FM",
    "Yokohama FC": "横浜FC",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    normalized = unicodedata.normalize("NFKC", str(value)).strip().lower()
    return " ".join(normalized.split())


def normalize_roman_name(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    keep = []
    for char in text:
        if char.isalnum():
            keep.append(char)
    return "".join(keep)


def roman_name_variants(value: object) -> set[str]:
    raw_text = unicodedata.normalize("NFKC", str(value)).strip() if pd.notna(value) else ""
    if not raw_text:
        return set()

    tokens = []
    for token in raw_text.split():
        normalized_token = normalize_roman_name(token)
        if normalized_token:
            tokens.append(normalized_token)

    variants = set()
    normalized_full = normalize_roman_name(raw_text)
    if normalized_full:
        variants.add(normalized_full)
    if len(tokens) >= 2:
        variants.add("".join(tokens))
        variants.add("".join(reversed(tokens)))
    return {variant for variant in variants if variant}


def normalize_team_name(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip() if pd.notna(value) else ""
    if not text:
        return ""
    if text in TEAM_MAPPING:
        return TEAM_MAPPING[text]
    return text


def build_sc_player_teams() -> dict[str, set[str]]:
    player_teams: dict[str, set[str]] = {}

    for csv_file in SC_DATA_DIR.rglob("*.csv"):
        try:
            df = pd.read_csv(csv_file, usecols=["Player", "Team", "Position"])
        except Exception:
            continue

        df = df[df["Position"] == "Center Forward"]
        for row in df.itertuples(index=False):
            player = str(row.Player).strip() if pd.notna(row.Player) else ""
            team = normalize_team_name(row.Team)
            if not player or not team:
                continue
            player_teams.setdefault(player, set()).add(team)

    return player_teams


def build_fb_player_teams() -> dict[str, set[str]]:
    player_teams: dict[str, set[str]] = {}

    for excel_file in FB_DATA_DIR.rglob("*.xlsx"):
        if "エリア進入" not in unicodedata.normalize("NFKC", excel_file.name):
            continue

        try:
            df = pd.read_excel(excel_file, sheet_name=0, usecols=["選手名", "チーム名", "Pos"])
        except Exception:
            continue

        df = df[df["Pos"] == "FW"]
        for row in df.itertuples(index=False):
            player = str(row.選手名).strip() if pd.notna(row.選手名) else ""
            team = normalize_team_name(row.チーム名)
            if not player or not team:
                continue
            player_teams.setdefault(player, set()).add(team)

    return player_teams


def build_fb_name_index(fb_names: pd.Series, kakasi: pykakasi.kakasi) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}

    for fb_name in fb_names.dropna():
        name = str(fb_name).strip()
        romaji = "".join(item["hepburn"] for item in kakasi.convert(name))
        indexed[name] = {
            "normalized_name": normalize_roman_name(romaji),
        }

    return indexed


def calculate_similarity(left: str, right: str) -> int:
    if not left or not right:
        return 0
    return int(round(SequenceMatcher(None, left, right).ratio() * 100))


def best_name_similarity(sc_variants: set[str], fb_normalized_name: str) -> int:
    if not sc_variants or not fb_normalized_name:
        return 0
    return max(calculate_similarity(sc_variant, fb_normalized_name) for sc_variant in sc_variants)


def match_players(
    sc_players: pd.DataFrame,
    fb_players: pd.DataFrame,
    sc_player_teams: dict[str, set[str]],
    fb_player_teams: dict[str, set[str]],
) -> pd.DataFrame:
    kakasi = pykakasi.kakasi()
    fb_name_index = build_fb_name_index(fb_players["FB_Name"], kakasi)
    fb_names = sorted(fb_name_index.keys())

    results: list[dict[str, object]] = []

    for sc_name in sc_players["SC_Name"].dropna():
        sc_name = str(sc_name).strip()
        sc_teams = sc_player_teams.get(sc_name, set())
        sc_name_variants = roman_name_variants(sc_name)

        best_match = ""
        best_score = 0
        best_shared_teams: set[str] = set()
        score_tie = False

        for fb_name in fb_names:
            fb_teams = fb_player_teams.get(fb_name, set())
            shared_teams = sc_teams & fb_teams
            if not shared_teams:
                continue

            score = best_name_similarity(
                sc_name_variants,
                str(fb_name_index[fb_name]["normalized_name"]),
            )

            if score > best_score:
                best_match = fb_name
                best_score = score
                best_shared_teams = shared_teams
                score_tie = False
            elif score == best_score and score > 0:
                score_tie = True

        is_confirmed = best_score >= SIMILARITY_THRESHOLD and not score_tie and bool(best_match)
        results.append(
            {
                "SC_Name": sc_name,
                "FB_Name": best_match if is_confirmed else "",
                "Match_Score": best_score,
                "Status": "確定" if is_confirmed else "",
                "SC_Teams": " / ".join(sorted(sc_teams)),
                "FB_Teams": " / ".join(sorted(fb_player_teams.get(best_match, set()))) if best_match else "",
                "Shared_Teams": " / ".join(sorted(best_shared_teams)),
                "Tie_On_Best_Score": score_tie,
            }
        )

    return pd.DataFrame(results)


def validate_team_mapping(sc_player_teams: dict[str, set[str]]) -> None:
    sc_teams = sorted({team for teams in sc_player_teams.values() for team in teams})
    unmapped = sorted(team for team in sc_teams if team not in set(TEAM_MAPPING.values()))
    if unmapped:
        raise ValueError(f"未対応のSCチーム名があります: {unmapped}")


def main() -> None:
    print("=== チーム一致込みの名寄せを開始 ===")

    sc_players = pd.read_csv(SC_UNIQUE_PATH)
    fb_players = pd.read_csv(FB_UNIQUE_PATH)
    print(f"SC unique players: {len(sc_players)}")
    print(f"FB unique players: {len(fb_players)}")

    print("\n=== 所属チームを再構築中 ===")
    sc_player_teams = build_sc_player_teams()
    fb_player_teams = build_fb_player_teams()
    validate_team_mapping(sc_player_teams)
    print(f"SC team index: {len(sc_player_teams)} players")
    print(f"FB team index: {len(fb_player_teams)} players")

    print("\n=== チーム一致候補だけで名前類似度を計算中 ===")
    result_df = match_players(sc_players, fb_players, sc_player_teams, fb_player_teams)

    confirmed_df = result_df[["SC_Name", "FB_Name"]].copy()
    confirmed_count = (result_df["Status"] == "確定").sum()
    unresolved_count = len(result_df) - confirmed_count

    confirmed_df.to_csv(MAPPING_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    result_df.sort_values(["Status", "Match_Score", "SC_Name"], ascending=[False, False, True]).to_csv(
        DETAIL_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n=== 保存完了 ===")
    print(f"{MAPPING_OUTPUT_PATH}: {len(confirmed_df)} rows")
    print(f"{DETAIL_OUTPUT_PATH}: {len(result_df)} rows")
    print(f"確定: {confirmed_count}")
    print(f"未確定: {unresolved_count}")
    print("\n確定サンプル:")
    preview = result_df[result_df["Status"] == "確定"][["SC_Name", "FB_Name", "Match_Score", "Shared_Teams"]].head(10)
    if preview.empty:
        print("  該当なし")
    else:
        print(preview.to_string(index=False))


if __name__ == "__main__":
    main()
