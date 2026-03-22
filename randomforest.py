import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. バランス型K-Meansの結果データを読み込む
df = pd.read_csv('kmeans_results_refined.csv')

# 2. 愛媛FCの要望に合わせた「厳選9変数」をリストとして準備する
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

# 3. 分析用の入力データ(X)として、厳選した列だけを抜き出す
X = df[features]

# 4. 欠損値(NaN)を0で埋める
X = X.fillna(0)

# 5. ランダムフォレストのモデルを準備する
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# 6. 新しいクラスター0〜3について順番に分析する（ループ処理）
for cluster_id in [0, 1, 2, 3]:
    print(f"\n==========================")
    print(f" Cluster {cluster_id} の分析")
    print(f"==========================")
    
    # このクラスターに該当するかどうか(True/False)を判定する
    is_target_cluster = (df['Cluster_Refined'] == cluster_id)
    
    # True/Falseを1/0の数値に変換して正解ラベル(y)にする
    y = is_target_cluster.astype(int)
    
    # ランダムフォレストに学習させる
    rf.fit(X, y)
    
    # 学習結果から「特徴量の重要度」を取り出す
    importances = rf.feature_importances_
    
    # 重要度の数値と変数名を紐付ける
    imp_series = pd.Series(importances, index=features)
    
    # 重要度が高い順（降順）に並び替える
    imp_series = imp_series.sort_values(ascending=False)
    
    # 厳選した9変数のうち、上位5個を画面に表示する
    print("\n--- 判別に重要な変数 トップ5 ---")
    print(imp_series.head(5))
    
    # このクラスターに属する選手だけを絞り込む
    cluster_players = df[df['Cluster_Refined'] == cluster_id]
    
    # 選手名の列を取り出す
    player_names = cluster_players['FB_Name']
    
    # ランダムに最大5名を抽出する
    sample_players = player_names.sample(n=min(5, len(player_names)), random_state=42)
    
    # リスト形式に変換して表示する
    print("\n--- 代表選手 (ランダム5名) ---")
    print(sample_players.tolist())