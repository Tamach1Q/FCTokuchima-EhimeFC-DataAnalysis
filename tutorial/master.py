import glob
import os
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

# ==========================================
# 1. リーグとチーム名の情報を取得する
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "csv"
BASE_DIR = "/Users/machidanoboruyuu/Library/CloudStorage/GoogleDrive-kmc2434@kamiyama.ac.jp/.shortcut-targets-by-id/15hhq0OywBt77uy9iydunzXsnyWMxZPhe/生データ/"
FB_DIR = os.path.join(BASE_DIR, "football box")

print("生データからリーグとチーム情報を検索中...")

# エラーを避けるため、サマリーファイルだけを抽出
all_fb_files = glob.glob(os.path.join(FB_DIR, "**", "*.xlsx"), recursive=True)
fb_files = [f for f in all_fb_files if "サマリー" in os.path.basename(f)]

info_list = []
for f in fb_files:
    try:
        # 一旦読み込んで、必要な列が含まれているかチェック
        df_temp = pd.read_excel(f, engine="openpyxl")
        req_cols = ["選手名", "チーム名", "大会", "試合日"]
        if set(req_cols).issubset(df_temp.columns):
            info_list.append(df_temp[req_cols])
    except Exception:
        continue

if len(info_list) == 0:
    print("【エラー】データを読み込めませんでした。")
    exit()

# 結合して最新の所属データを取得
df_info_all = pd.concat(info_list, ignore_index=True)
df_latest_info = df_info_all.sort_values("試合日", ascending=False).drop_duplicates(
    subset=["選手名"], keep="first"
)

# ==========================================
# 2. クラスターデータと結合し、スコアを計算
# ==========================================
df_kmeans = pd.read_csv(CSV_DIR / "kmeans_results_refined.csv")
df_merged = pd.merge(
    df_kmeans, df_latest_info, left_on="FB_Name", right_on="選手名", how="inner"
)

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

# 標準化（Zスコア）
scaler = StandardScaler()
df_scaled = pd.DataFrame(
    scaler.fit_transform(df_merged[features].fillna(0)), columns=features
)

# 各クラスターの専用スコアを計算
df_merged["Score_C3"] = (
    df_scaled["PA内シュート_per90"] + df_scaled["PA内シュート決定率(%)"]
)
df_merged["Score_C1"] = (
    df_scaled["ボールゲイン_per90"]
    + df_scaled["Sprint Count OTIP_per90"]
    + df_scaled["M/min OTIP"]
)
df_merged["Score_C2"] = df_scaled["空中戦勝率(%)"] + df_scaled["パス_per90"]
df_merged["Score_C0"] = df_scaled[features].sum(axis=1)

# ==========================================
# 3. 縦長のデータベース（マスター表）を作成
# ==========================================
final_data = []

# 選手ごとに所属クラスターを判定し、該当するスコアを採用する
for index, row in df_merged.iterrows():
    cluster = row["Cluster_Refined"]
    if cluster == 3:
        c_name = "得点特化(C3)"
        score = row["Score_C3"]
    elif cluster == 1:
        c_name = "守備職人(C1)"
        score = row["Score_C1"]
    elif cluster == 2:
        c_name = "起点特化(C2)"
        score = row["Score_C2"]
    else:
        c_name = "万能型(C0)"
        score = row["Score_C0"]

    final_data.append(
        {
            "クラスター": c_name,
            "選手名": row["FB_Name"],
            "所属チーム": row["チーム名"],
            "リーグ": row["大会"],
            "評価スコア": round(score, 2),
        }
    )

df_final = pd.DataFrame(final_data)

# クラスター名とスコア（降順）で並び替え
df_final = df_final.sort_values(
    by=["クラスター", "評価スコア"], ascending=[True, False]
)

# 各クラスター内での順位を計算して追加
df_final["クラスター内順位"] = df_final.groupby("クラスター").cumcount() + 1

# 列の並び順を綺麗に整える
df_final = df_final[
    ["クラスター", "クラスター内順位", "選手名", "所属チーム", "リーグ", "評価スコア"]
]

# CSV出力
output_file = CSV_DIR / "scouting_master_database.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(output_file, index=False, encoding="utf-8-sig")

print(
    f"✅ マスターデータ（{output_file}）を作成しました！Excelで開いてフィルターを活用してください。"
)
