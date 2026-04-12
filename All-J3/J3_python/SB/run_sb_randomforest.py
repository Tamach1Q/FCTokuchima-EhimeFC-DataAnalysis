"""
今回は未実行。
SB のクラスタ結果を入力に、one-vs-rest で RandomForest を回すための雛形。
"""

from __future__ import annotations

import csv
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = CURRENT_DIR / "output"
INPUT_CLUSTERED_CSV = OUTPUT_DIR / "SB_clustered_players.csv"


def load_clustered_players(csv_path: Path) -> list[dict[str, str]]:
    """将来の学習入力となる clustered_players.csv を読む。"""

    if not csv_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_training_data(rows: list[dict[str, str]]) -> None:
    """
    TODO:
    - raw_* / win_* / z_* のどれを説明変数に使うか確定する
    - cluster_id を目的変数にし、cluster ごとの one-vs-rest ラベルを作る
    - 学習用/検証用の分割方針を決める
    - 不均衡クラス対策が必要か確認する
    """

    raise NotImplementedError("RandomForest 学習処理は次工程で実装します。")


def main() -> None:
    rows = load_clustered_players(INPUT_CLUSTERED_CSV)
    print(f"[SB][RF] 入力件数: {len(rows)}")
    print(f"[SB][RF] 入力ファイル: {INPUT_CLUSTERED_CSV}")
    print("[SB][RF] 今回は未実行です。TODO を参照してください。")


if __name__ == "__main__":
    main()
