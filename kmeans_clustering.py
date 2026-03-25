from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / "csv"

df = pd.read_csv(CSV_DIR / "clustering_base_data.csv")

# 2. 愛媛FCの要望に合わせた9変数をリストアップ
selected_features = [
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

# 3. 分析用のデータ(X)として、厳選した列だけを抜き出す
X = df[selected_features]

# 4. 欠損値(NaN)を0で埋める
X = X.fillna(0)

# 5. データのスケール（単位）を統一する準備
scaler = StandardScaler()

# 6. スケールを統一（標準化）を実行
X_scaled = scaler.fit_transform(X)

# 7. K-Meansモデルの準備（愛媛FCの3軸＋万能型の「4」グループを想定）
kmeans = KMeans(n_clusters=4, random_state=42)

# 8. AIにクラスター分けを実行させ、結果を新しい列に保存
df["Cluster_Refined"] = kmeans.fit_predict(X_scaled)

# 9. 新しいクラスター分けの結果をファイルに保存
output_file = CSV_DIR / "kmeans_results_refined.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False, encoding="utf-8-sig")

# 10. 各グループの人数を画面に表示
print("【再構築したクラスターの人数】")
print(df["Cluster_Refined"].value_counts().sort_index())
