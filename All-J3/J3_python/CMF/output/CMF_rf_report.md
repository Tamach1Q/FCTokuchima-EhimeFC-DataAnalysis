# CMF RandomForest Report

## 入力ファイル
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_clustered_players.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_cluster_centers_z.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_cluster_summary.csv`
- `/Users/machidanoboruyuu/Desktop/FCTokushima-EhimeFC-DataAnalysis/All-J3/J3_python/CMF/output/CMF_kmeans_report.md`

## 使用した z 列
- `z_running_distance_full_all_per_match` (走行距離_per_match)
- `z_ball_gains_per90` (ボール奪取_per90)
- `z_interceptions_per90` (インターセプト_per90)
- `z_pass_success_rate_pct` (パス成功率)
- `z_forward_pass_success_rate_pct` (前進パス成功率)
- `z_short_pass_share_pct` (ショートパス比率)
- `z_long_pass_share_pct` (ロングパス比率)
- `z_opponent_half_gain_share_pct` (敵陣奪回比率)

## データ概要
- サンプル数: 32
- cluster_id 一覧: 0, 1, 2
- cluster ごとの positive / negative 件数:
  - Cluster 0: 9 / 23
  - Cluster 1: 18 / 14
  - Cluster 2: 5 / 27

## RandomForest 設定
- `RandomForestClassifier(n_estimators=1000, random_state=42, class_weight="balanced", min_samples_leaf=2, max_depth=None, n_jobs=-1)`
- one-vs-rest で各 cluster を個別に二値分類
- permutation importance: scoring=`roc_auc`, `n_repeats=30`, `random_state=42`
- 評価指標: train ROC AUC, StratifiedKFold ROC AUC
- 注記: 今回の主目的は予測精度の最適化ではなく、各クラスタを説明する変数の解釈です。

## Cluster 別結果
### Cluster 0
- positive / negative: 9 / 23
- train AUC: 1.0000
- CV AUC: 0.9600 ± 0.0800 (StratifiedKFold(5))
- KMeans candidate_expression: ボックストゥボックス寄り / ボールハント寄り
- ラベル候補: ゲームオーガナイザー型候補 / ボックストゥボックス型候補
- KMeans 解釈との整合性コメント: KMeans の「ボックストゥボックス寄り / ボールハント寄り」候補と概ね整合します。RF でも パス成功率が低い、敵陣奪回比率が低い、前進パス成功率が低い が主な分離軸で、ゲームメイク寄り / ボックストゥボックス寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. パス成功率 (`z_pass_success_rate_pct`) / center_z=-1.170 / permutation_importance_mean=0.0316 / std=0.0258
  - 2. 敵陣奪回比率 (`z_opponent_half_gain_share_pct`) / center_z=-0.864 / permutation_importance_mean=0.0018 / std=0.0029
  - 3. 前進パス成功率 (`z_forward_pass_success_rate_pct`) / center_z=-0.810 / permutation_importance_mean=0.0000 / std=0.0000
  - 4. ロングパス比率 (`z_long_pass_share_pct`) / center_z=+0.803 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. ボール奪取_per90 (`z_ball_gains_per90`) / center_z=+0.425 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. パス成功率 (`z_pass_success_rate_pct`) / center_z=-1.170 / impurity_importance=0.3000
  - 2. 前進パス成功率 (`z_forward_pass_success_rate_pct`) / center_z=-0.810 / impurity_importance=0.1636
  - 3. 敵陣奪回比率 (`z_opponent_half_gain_share_pct`) / center_z=-0.864 / impurity_importance=0.1601
  - 4. ロングパス比率 (`z_long_pass_share_pct`) / center_z=+0.803 / impurity_importance=0.1161
  - 5. ボール奪取_per90 (`z_ball_gains_per90`) / center_z=+0.425 / impurity_importance=0.0803
- 推薦スコア候補: `z_long_pass_share_pct + z_ball_gains_per90` を主軸にしつつ、低値が効く z_pass_success_rate_pct は補助条件として併用するのが自然です。

### Cluster 1
- positive / negative: 18 / 14
- train AUC: 1.0000
- CV AUC: 0.9611 ± 0.0484 (StratifiedKFold(5))
- KMeans candidate_expression: ボックストゥボックス寄り / ボールハント寄り
- ラベル候補: 平均型候補
- KMeans 解釈との整合性コメント: KMeans の平均型候補と整合します。RF では パス成功率が高い、敵陣奪回比率が高い、走行距離_per_matchが高い が上位ですが、いずれも specialized cluster 側の極端さを弾く軸として効いており、単一ラベルより『平均型候補』として扱う方が自然です。
- permutation importance 上位5:
  - 1. パス成功率 (`z_pass_success_rate_pct`) / center_z=+0.244 / permutation_importance_mean=0.0118 / std=0.0104
  - 2. 敵陣奪回比率 (`z_opponent_half_gain_share_pct`) / center_z=+0.352 / permutation_importance_mean=0.0034 / std=0.0048
  - 3. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=+0.402 / permutation_importance_mean=0.0000 / std=0.0000
  - 4. ロングパス比率 (`z_long_pass_share_pct`) / center_z=+0.071 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. 前進パス成功率 (`z_forward_pass_success_rate_pct`) / center_z=+0.042 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. 敵陣奪回比率 (`z_opponent_half_gain_share_pct`) / center_z=+0.352 / impurity_importance=0.2014
  - 2. パス成功率 (`z_pass_success_rate_pct`) / center_z=+0.244 / impurity_importance=0.1813
  - 3. 走行距離_per_match (`z_running_distance_full_all_per_match`) / center_z=+0.402 / impurity_importance=0.1202
  - 4. ロングパス比率 (`z_long_pass_share_pct`) / center_z=+0.071 / impurity_importance=0.1184
  - 5. 前進パス成功率 (`z_forward_pass_success_rate_pct`) / center_z=+0.042 / impurity_importance=0.1032
- 推薦スコア候補: 平均型候補は 2〜3 変数の単純加算より、`CMF_cluster_centers_z.csv` の cluster 1 中心への距離ベースが適切です。

### Cluster 2
- positive / negative: 5 / 27
- train AUC: 1.0000
- CV AUC: 1.0000 ± 0.0000 (StratifiedKFold(5))
- KMeans candidate_expression: ゲームメイク寄り / ボールハント寄り
- ラベル候補: ゲームオーガナイザー型候補
- KMeans 解釈との整合性コメント: KMeans の「ゲームメイク寄り / ボールハント寄り」候補と概ね整合します。RF でも ショートパス比率が高い、ロングパス比率が低い、前進パス成功率が高い が主な分離軸で、ゲームメイク寄り の解釈が妥当です。
- permutation importance 上位5:
  - 1. ショートパス比率 (`z_short_pass_share_pct`) / center_z=+1.934 / permutation_importance_mean=0.0007 / std=0.0022
  - 2. ロングパス比率 (`z_long_pass_share_pct`) / center_z=-1.699 / permutation_importance_mean=0.0000 / std=0.0000
  - 3. 前進パス成功率 (`z_forward_pass_success_rate_pct`) / center_z=+1.309 / permutation_importance_mean=0.0000 / std=0.0000
  - 4. ボール奪取_per90 (`z_ball_gains_per90`) / center_z=-0.909 / permutation_importance_mean=0.0000 / std=0.0000
  - 5. パス成功率 (`z_pass_success_rate_pct`) / center_z=+1.230 / permutation_importance_mean=0.0000 / std=0.0000
- impurity importance 上位5:
  - 1. ショートパス比率 (`z_short_pass_share_pct`) / center_z=+1.934 / impurity_importance=0.2558
  - 2. ロングパス比率 (`z_long_pass_share_pct`) / center_z=-1.699 / impurity_importance=0.2325
  - 3. 前進パス成功率 (`z_forward_pass_success_rate_pct`) / center_z=+1.309 / impurity_importance=0.1705
  - 4. ボール奪取_per90 (`z_ball_gains_per90`) / center_z=-0.909 / impurity_importance=0.1113
  - 5. パス成功率 (`z_pass_success_rate_pct`) / center_z=+1.230 / impurity_importance=0.0912
- 推薦スコア候補: `z_short_pass_share_pct + z_forward_pass_success_rate_pct` を主軸にしつつ、低値が効く z_long_pass_share_pct は補助条件として併用するのが自然です。

## 全体所見
- 平均型候補は Cluster 1 です。他クラスタとの分岐で目立った変数は z_pass_success_rate_pct, z_opponent_half_gain_share_pct, z_running_distance_full_all_per_match でした。
- Cluster 0 の specialized な分離軸は z_pass_success_rate_pct, z_opponent_half_gain_share_pct, z_forward_pass_success_rate_pct でした。
- Cluster 2 の specialized な分離軸は z_short_pass_share_pct, z_long_pass_share_pct, z_forward_pass_success_rate_pct でした。
- ラベル解釈は断定ではなく候補です。KMeans 中心の高低と RF の判別寄与が同時に揃う変数を優先して読んでいます。

## 推薦スコア設計メモ
- Cluster 0: `z_long_pass_share_pct + z_ball_gains_per90` を主候補。
- Cluster 1: 平均型候補のため、単純加算ではなくクラスタ中心への距離ベース推奨。
- Cluster 2: `z_short_pass_share_pct + z_forward_pass_success_rate_pct` を主候補。

## CV 安定性メモ
- 変動がやや大きかった cluster: 0
