import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_DIR = PROJECT_ROOT / 'csv'

# 1. データの読み込み
df = pd.read_csv(CSV_DIR / 'kmeans_results_refined.csv')

# 2. 厳選した9つの特徴量リスト
features = [
    'PA内シュート_per90', 
    'PA内シュート決定率(%)', 
    'Explosive Acceleration to Sprint Count TIP_per90',
    'ボールゲイン_per90', 
    'Sprint Count OTIP_per90', 
    'M/min OTIP',
    '空中戦勝率(%)', 
    'パス_per90', 
    'PSV-99'
]

# 3. データの準備（標準化するために特徴量の列だけを取り出し、欠損を0にする）
X = df[features].fillna(0)

# 4. 標準化の実行（単位の違う指標を足し合わせるため、スケールを揃える）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. 標準化したデータを新しいデータフレーム（表）にする
df_scaled = pd.DataFrame(X_scaled, columns=features)

# 6. 計算用の表に、元の選手名とクラスター番号をくっつける
df_scaled['FB_Name'] = df['FB_Name']
df_scaled['Cluster_Refined'] = df['Cluster_Refined']

# 7. クラスター3（得点特化）の評価スコアを計算する（PA内シュート + 決定率）
df_scaled['Score_C3'] = df_scaled['PA内シュート_per90'] + df_scaled['PA内シュート決定率(%)']

# 8. クラスター1（守備特化）の評価スコアを計算する（奪取 + 守備スプリント + 守備移動距離）
df_scaled['Score_C1'] = df_scaled['ボールゲイン_per90'] + df_scaled['Sprint Count OTIP_per90'] + df_scaled['M/min OTIP']

# 9. クラスター2（起点特化）の評価スコアを計算する（空中戦 + パス）
df_scaled['Score_C2'] = df_scaled['空中戦勝率(%)'] + df_scaled['パス_per90']

# 10. クラスター0（万能型）の評価スコアを計算する（全9指標の合計）
df_scaled['Score_C0'] = df_scaled[features].sum(axis=1)

# 11. 結果を出力する
print("\n--- Cluster 3 (得点特化) 優秀選手 TOP 5 ---")
c3_players = df_scaled[df_scaled['Cluster_Refined'] == 3]
c3_top5 = c3_players.sort_values('Score_C3', ascending=False).head(5)
print(c3_top5[['FB_Name', 'Score_C3']])

print("\n--- Cluster 1 (守備特化) 優秀選手 TOP 5 ---")
c1_players = df_scaled[df_scaled['Cluster_Refined'] == 1]
c1_top5 = c1_players.sort_values('Score_C1', ascending=False).head(5)
print(c1_top5[['FB_Name', 'Score_C1']])

print("\n--- Cluster 2 (起点特化) 優秀選手 TOP 5 ---")
c2_players = df_scaled[df_scaled['Cluster_Refined'] == 2]
c2_top5 = c2_players.sort_values('Score_C2', ascending=False).head(5)
print(c2_top5[['FB_Name', 'Score_C2']])

print("\n--- Cluster 0 (万能型) 優秀選手 TOP 5 ---")
c0_players = df_scaled[df_scaled['Cluster_Refined'] == 0]
c0_top5 = c0_players.sort_values('Score_C0', ascending=False).head(5)
print(c0_top5[['FB_Name', 'Score_C0']])
