import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# データの読み込み
df = pd.read_csv('kmeans_results.csv')
features = [col for col in df.columns if '_per90' in col or '(%)' in col or 'M/min' in col or 'PSV' in col]
X = df[features].fillna(0)
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Cluster 0 だけを分析
print(f"\n==========================")
print(f" Cluster 0 の分析")
print(f"==========================")

y = (df['Cluster'] == 0).astype(int)
rf.fit(X, y)
imp_series = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)

print("\n--- 判別に重要な変数 トップ10 ---")
print(imp_series.head(10))

print("\n--- 代表選手 (ランダム5名) ---")
print(df[df['Cluster'] == 0]['FB_Name'].sample(n=5, random_state=42).tolist())