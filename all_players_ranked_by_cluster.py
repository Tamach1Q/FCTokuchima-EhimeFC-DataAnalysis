from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "csv"

# 1. データの読み込み
df = pd.read_csv(CSV_DIR / "kmeans_results_refined.csv")

# 2. 特徴量リスト
features = [
    "PA内シュート_per90",
    "PA内シュート決定率(%)",
    "Explosive Acceleration to Sprint Count TIP_per90",
    "ボールゲイン_per90",
    "Sprint Count OTIP_per90",
    "M/min OTIP",
    "空中戦勝率(%)",
    "パス_per90",
    "PSV-99",
]

# 3. 標準化（Zスコア）の実行
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df[features].fillna(0)), columns=features)
df_scaled["FB_Name"] = df["FB_Name"]
df_scaled["Cluster_Refined"] = df["Cluster_Refined"]

# 4. 各クラスターの専用スコアを計算
df_scaled["Score_C3"] = (
    df_scaled["PA内シュート_per90"] + df_scaled["PA内シュート決定率(%)"]
)
df_scaled["Score_C1"] = (
    df_scaled["ボールゲイン_per90"]
    + df_scaled["Sprint Count OTIP_per90"]
    + df_scaled["M/min OTIP"]
)
df_scaled["Score_C2"] = df_scaled["空中戦勝率(%)"] + df_scaled["パス_per90"]
df_scaled["Score_C0"] = df_scaled[features].sum(axis=1)

# 5. 全選手をクラスターごとに分け、スコア順に並び替え（.head() を削除して全件取得）
c3 = (
    df_scaled[df_scaled["Cluster_Refined"] == 3]
    .sort_values("Score_C3", ascending=False)
    .reset_index(drop=True)
)
c1 = (
    df_scaled[df_scaled["Cluster_Refined"] == 1]
    .sort_values("Score_C1", ascending=False)
    .reset_index(drop=True)
)
c2 = (
    df_scaled[df_scaled["Cluster_Refined"] == 2]
    .sort_values("Score_C2", ascending=False)
    .reset_index(drop=True)
)
c0 = (
    df_scaled[df_scaled["Cluster_Refined"] == 0]
    .sort_values("Score_C0", ascending=False)
    .reset_index(drop=True)
)

# 6. 一番人数の多いクラスター（今回は92人）に合わせて行数を決める
max_len = max(len(c0), len(c1), len(c2), len(c3))

# 7. 全件横並びのランキング表を作成
ranked_df = pd.DataFrame({"順位": range(1, max_len + 1)})

# 各クラスターの選手とスコアを追加（人数が足りない部分は自動で空欄になる）
ranked_df["得点特化(C3) 選手"] = c3["FB_Name"]
ranked_df["得点スコア"] = c3["Score_C3"].round(2)

ranked_df["守備職人(C1) 選手"] = c1["FB_Name"]
ranked_df["守備スコア"] = c1["Score_C1"].round(2)

ranked_df["起点特化(C2) 選手"] = c2["FB_Name"]
ranked_df["起点スコア"] = c2["Score_C2"].round(2)

ranked_df["万能型(C0) 選手"] = c0["FB_Name"]
ranked_df["総合スコア"] = c0["Score_C0"].round(2)

# 8. 空欄部分（NaN）を綺麗な空白文字に置き換える
ranked_df = ranked_df.fillna("")

# 9. CSVファイルとして出力
output_file = CSV_DIR / "all_players_ranked_by_cluster.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
ranked_df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(
    "✅ 全選手の完全版ランキングCSV（all_players_ranked_by_cluster.csv）を作成しました！"
)
