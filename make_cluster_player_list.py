import argparse
import csv
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="クラスターごとの選手一覧を見やすいCSVとMarkdownにまとめる"
    )
    parser.add_argument(
        "--input",
        default=str(CSV_DIR / "kmeans_results_refinedのコピー.csv"),
        help="入力CSVファイル",
    )
    parser.add_argument(
        "--output-csv",
        default=str(CSV_DIR / "cluster_player_list_refined.csv"),
        help="横並び一覧CSVの出力先",
    )
    parser.add_argument(
        "--output-md",
        default=str(PROJECT_ROOT / "cluster_player_list_refined.md"),
        help="クラスター別Markdown一覧の出力先",
    )
    parser.add_argument(
        "--cluster-col",
        default="Cluster_Refined",
        help="クラスター番号が入っている列名",
    )
    parser.add_argument(
        "--name-col",
        default="選手名",
        help="一覧に表示する選手名の列名",
    )
    return parser.parse_args()


def load_rows(input_path: Path):
    with input_path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))

    if not rows:
        raise ValueError("入力CSVが空です")

    if len(rows) >= 2 and len(rows[0]) == 1:
        header = rows[1]
        data_rows = rows[2:]
    else:
        header = rows[0]
        data_rows = rows[1:]

    return header, data_rows


def group_players(header, data_rows, cluster_col, name_col):
    try:
        cluster_index = header.index(cluster_col)
        name_index = header.index(name_col)
    except ValueError as error:
        raise ValueError(f"必要な列が見つかりません: {error}") from error

    grouped_players = defaultdict(list)
    for row in data_rows:
        if len(row) <= max(cluster_index, name_index):
            continue

        cluster_id = row[cluster_index].strip()
        player_name = row[name_index].strip()
        if not cluster_id or not player_name:
            continue

        grouped_players[cluster_id].append(player_name)

    return dict(sorted(grouped_players.items(), key=lambda item: int(item[0])))


def write_wide_csv(output_path: Path, grouped_players):
    headers = [
        f"Cluster {cluster_id} ({len(players)}人)"
        for cluster_id, players in grouped_players.items()
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in zip_longest(*grouped_players.values(), fillvalue=""):
            writer.writerow(row)


def write_markdown(output_path: Path, grouped_players):
    lines = ["# Cluster別 選手一覧", ""]

    for cluster_id, players in grouped_players.items():
        lines.append(f"## Cluster {cluster_id}（{len(players)}人）")
        lines.append("")
        for index, player_name in enumerate(players, start=1):
            lines.append(f"{index}. {player_name}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_csv_path = Path(args.output_csv)
    output_md_path = Path(args.output_md)

    header, data_rows = load_rows(input_path)
    grouped_players = group_players(
        header=header,
        data_rows=data_rows,
        cluster_col=args.cluster_col,
        name_col=args.name_col,
    )

    write_wide_csv(output_csv_path, grouped_players)
    write_markdown(output_md_path, grouped_players)

    print(f"CSVを保存しました: {output_csv_path}")
    print(f"Markdownを保存しました: {output_md_path}")


if __name__ == "__main__":
    main()
