import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. データの読み込み
df = pd.read_csv('kmeans_results_refined')

# 2. 特徴量のリストを作成（空のリストを用意）
features = []

# 3. 列名を1つずつ確認して特徴量（指標）だけを追加
for col in df.columns:
    if '_per90' in col or '(%)' in col or 'M/min' in col or 'PSV' in col:
        features.append(col)

# 4. 分析用の入力データ(X)を作成
X = df[features]

# 5. 欠損値(NaN)を0で埋める
X = X.fillna(0)

# 6. ランダムフォレストのモデルを準備
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# 7. クラスター1, 2, 3について順番に分析（ループ処理）
for cluster_id in [0, 1, 2, 3]:
    print(f"\n==========================")
    print(f" Cluster {cluster_id} の分析")
    print(f"==========================")
    
    # このクラスターに該当するかどうか(True/False)を判定
    is_target_cluster = (df['Cluster'] == cluster_id)
    
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
    
    # 上位10個を画面に表示する
    print("\n--- 判別に重要な変数 トップ10 ---")
    print(imp_series.head(10))
    
    # このクラスターに属する選手だけを絞り込む
    cluster_players = df[df['Cluster'] == cluster_id]
    
    # 選手名の列を取り出す
    player_names = cluster_players['FB_Name']
    
    # ランダムに5名だけを抽出する
    sample_players = player_names.sample(n=5, random_state=42)
    
    # リスト形式に変換して表示する
    print("\n--- 代表選手 (ランダム5名) ---")
    print(sample_players.tolist())